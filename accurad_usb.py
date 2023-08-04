import struct
import time

import serial

DOSE_RATE_INDEX = [19, 18, 17, 16]
CPS_INDEX = [23, 22, 21, 20]
DOSE_INDEX = [47, 46, 45, 44]
DURATION_INDEX = [51, 50, 49, 48]
PORT = "COM8"
REQUEST_DATA_MESSAGE = bytes.fromhex(
    "23 21 41 63 63 75 52 61 64 21 23 0A 00 01 00 7E 04 00 11 A7 1E 43 E7")
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


def hex_to_float(hex_str):
    return struct.unpack("!f", bytes.fromhex(hex_str))[0]


def seconds_to_hours(seconds):
    return seconds / 3600


def main(serial_connection):
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
    duration_str = response_bytes_to_hex_string(DURATION_INDEX, response_bytes)

    uSv_rate = hex_to_float(dose_rate_str)
    counts_per_second = hex_to_float(cps_str)
    uSv = hex_to_float(dose_str)
    seconds = hex_to_float(duration_str)

    mrem_per_hour = microsevert_to_mrem(uSv_rate)
    mrem = microsevert_to_mrem(uSv)

    duration = seconds_to_hours(seconds)

    print(f"Dose rate: {mrem_per_hour} mrem/hr")
    print(f"CPS: {counts_per_second}")
    print(f"Dose {mrem} mrem")
    print(f"Duration: {duration} hours")


if __name__ == "__main__":
    try:
        with serial.Serial(
            port=PORT, baudrate=BAUDRATE, timeout=TIMEOUT
        ) as serial_connection:
            while True:
                start_time = time.time()

                main(serial_connection)

                time_since_start = time.time() - start_time

                # If the loop took longer than 1 second, we don't want to wait
                if time_since_start >= 1:
                    continue

                # We get the rest of the time left in the second
                ms_left_in_the_second = 1 - time_since_start
                # We aim to get data every second, so we wait the rest of the time
                time.sleep(ms_left_in_the_second)

    except serial.SerialException as e:
        print(f"Error opening serial connection on {PORT}: {e}")
