import re
import struct
import time

import serial

dose_rate_index = [19, 18, 17, 16]
cps_index = [23, 22, 21, 20]
dose_index = [47, 46, 45, 44]
duration_index = [51, 50, 49, 48]


def main():
    dose_rate_str = ""
    cps_str = ""
    dose_str = ""
    duration_str = ""

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

                # parse and rearrange data
                for index in range(0, 4):
                    # read hex numbers for dose rate
                    text = hex(response_bytes[dose_rate_index[index]])
                    # split hex number at X
                    z = re.split("x", text)
                    # check for length and add missing leading zero if needed
                    if len(z[1]) == 1:
                        z[1] = f"0{z[1]}"
                    # add bits to string
                    if len(dose_rate_str) == 0:
                        dose_rate_str = z[1]
                    else:
                        dose_rate_str = dose_rate_str+z[1]

                    # read and rearrange hex numbers for counts per second
                    cps_text = hex(response_bytes[cps_index[index]])
                    zz = re.split("x", cps_text)
                    if len(zz[1]) == 1:
                        zz[1] = f"0{zz[1]}"
                    if len(cps_str) == 0:
                        cps_str = zz[1]
                    else:
                        cps_str = cps_str+zz[1]

                    # read and rearrange hex numbers for accumulated dose
                    dose_text = hex(response_bytes[dose_index[index]])
                    zzz = re.split("x", dose_text)
                    if len(zzz[1]) == 1:
                        zzz[1] = f"0{zzz[1]}"
                    if len(dose_str) == 0:
                        dose_str = zzz[1]
                    else:
                        dose_str = dose_str+zzz[1]

                    # read and rearrange hex numbers for duration of accumulated dose
                    duration_text = hex(response_bytes[duration_index[index]])
                    zzzz = re.split("x", duration_text)
                    if len(zzzz[1]) == 1:
                        zzzz[1] = "0"+zzzz[1]
                    if len(dose_str) == 0:
                        duration_str = zzzz[1]
                    else:
                        duration_str = f"{duration_str}{zzzz[1]}"

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
                print(f"Error during communication: {e}")

    except serial.SerialException as e:
        print(f"Error opening serial connection on {port}: {e}")


if __name__ == "__main__":
    start_time = time.time()
    while True:
        main()
        time.sleep(1 - ((time.time() - start_time) % 1))
