import re
import struct
import time

import serial

dose_rate_index = [19, 18, 17, 16]
cps_index = [23, 22, 21, 20]
dose_index = [47, 46, 45, 44]
duration_index = [51, 50, 49, 48]


def response_bytes_to_hex_string(index_list, response_bytes):
    result_str = ""

    # Parse and rearrange data
    for index in index_list:
        # Use f-string formatting to add the hex value to the result string.
        # The f-string automatically converts the bytes to a string.
        # Our formatting specification after the colon tells tells the f-string to
        # convert to a hex string, and then pad the string with leading zeros.
        result_str = f"{result_str}{response_bytes[index]:02x}"

    return result_str


def main():
    # Select COM Port
    port = "COM8"
    # Message requesting device data
    data_to_send = bytes.fromhex(
        '23 21 41 63 63 75 52 61 64 21 23 0A 00 01 00 7E 04 00 11 A7 1E 43 E7')

    try:
        with serial.Serial(port=port, baudrate=115200, timeout=1) as serial_connection:
            try:
                # Write the data
                serial_connection.write(data_to_send)
                # Read the response
                response_bytes = serial_connection.read(800)

            except serial.SerialException as e:
                print(f"Error during communication: {e}")

            dose_rate_str = response_bytes_to_hex_string(
                dose_rate_index, response_bytes)
            cps_str = response_bytes_to_hex_string(cps_index, response_bytes)
            dose_str = response_bytes_to_hex_string(dose_index, response_bytes)
            duration_str = response_bytes_to_hex_string(
                duration_index, response_bytes)

            # convert dose rate from hex to float
            uSv_rate = struct.unpack('!f', bytes.fromhex(dose_rate_str))[0]
            # convert from microsevert to mrem
            mrem_rate = uSv_rate / 10
            print(f"Dose rate: {mrem_rate} mrem/hr")
            # convert counts per second from hex to float, and then print
            print(f"CPS: {struct.unpack('!f', bytes.fromhex(cps_str))[0]}")
            # convert accumulated dose from hex to float
            uSv = struct.unpack('!f', bytes.fromhex(dose_str))[0]
            # convert uSv to mrem
            mrem = uSv / 10
            print(f"Dose {mrem} mrem")
            # convert duration of accumulated dose from hex to float (in seconds)
            seconds = struct.unpack('!f', bytes.fromhex(duration_str))[0]
            # convert seconds to hours
            hours = seconds/3600
            print(f"Duration: {hours} hours")

    except serial.SerialException as e:
        print(f"Error opening serial connection on {port}: {e}")


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
