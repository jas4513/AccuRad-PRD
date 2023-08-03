import re
import struct
import time

import serial

DOSE_RATE_INDEX = [19, 18, 17, 16]
CPS_INDEX = [23, 22, 21, 20]
DOSE_INDEX = [47, 46, 45, 44]
DURATION_INDEX = [51, 50, 49, 48]
PORT = "COM8"
REQUEST_DATA_MESSAGE = bytes.fromhex(
    '23 21 41 63 63 75 52 61 64 21 23 0A 00 01 00 7E 04 00 11 A7 1E 43 E7')
BAUDRATE = 115200
TIMEOUT = 1
BYTES_TO_READ = 800


def response_bytes_to_hex_string(index_list, response_bytes):
    result_str = ""

    # Parse and rearrange data
    for index in index_list:
        # Use f-string formatting to add the hex value to the result string.
        # The f-string automatically converts the bytes to a string.
        # Our formatting specification after the colon tells tells the f-string to
        # convert to a hex string, and then pad the string with leading zeros.
        result_str = f"{result_str}{response_bytes[index]:02x}"
        # After having a better understanding of how this is used, I don't think
        # we need to convert this to a string. We can just use the bytes directly.
        #
        # result = b''
        # for index in index_list:
        #   result = result + response_bytes[index]
        # return result
        #
        # I'm not making this change because I can see an argument that
        # converting to hex is simpler to reason about.

    return result_str


def microsevert_to_mrem(uSv):
    return uSv / 10


def main():
    try:
        with serial.Serial(port=PORT, baudrate=BAUDRATE, timeout=TIMEOUT) as serial_connection:
            try:
                # Write the data
                serial_connection.write(REQUEST_DATA_MESSAGE)
                # Read the response
                response_bytes = serial_connection.read(BYTES_TO_READ)

            except serial.SerialException as e:
                print(f"Error during communication: {e}")

            dose_rate_str = response_bytes_to_hex_string(
                DOSE_RATE_INDEX, response_bytes)
            cps_str = response_bytes_to_hex_string(CPS_INDEX, response_bytes)
            dose_str = response_bytes_to_hex_string(DOSE_INDEX, response_bytes)
            duration_str = response_bytes_to_hex_string(
                DURATION_INDEX, response_bytes)

            # convert dose rate from hex to float
            uSv_rate = struct.unpack('!f', bytes.fromhex(dose_rate_str))[0]
            print(f"Dose rate: {microsevert_to_mrem(uSv_rate)} mrem/hr")
            # convert counts per second from hex to float, and then print
            print(f"CPS: {struct.unpack('!f', bytes.fromhex(cps_str))[0]}")
            # convert accumulated dose from hex to float
            uSv = struct.unpack('!f', bytes.fromhex(dose_str))[0]
            print(f"Dose {microsevert_to_mrem(uSv)} mrem")
            # convert duration of accumulated dose from hex to float (in seconds)
            seconds = struct.unpack('!f', bytes.fromhex(duration_str))[0]
            # convert seconds to hours
            hours = seconds/3600
            print(f"Duration: {hours} hours")

    except serial.SerialException as e:
        print(f"Error opening serial connection on {PORT}: {e}")


if __name__ == "__main__":
    start_time = time.time()

    while True:
        main()
        time_since_start = time.time() - start_time
        ms_in_time_since_start = time_since_start % 1
        ms_left_in_time_since_start = 1 - ms_in_time_since_start
        # This has us wait until the next second to run the loop again
        # Why?
        time.sleep(ms_left_in_time_since_start)
