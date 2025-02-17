import serial
import re
import binascii
import struct
import time



dose_rate_index=[19,18,17,16]
CPS_index=[23,22,21,20]
dose_index=[47,46,45,44]
duration_index=[51,50,49,48]



def open_serial_connection(port):
    try:
        ser = serial.Serial(port=port, baudrate=115200, timeout=1)
        return ser
    except serial.SerialException as e:
        print(f"Error opening serial connection on {port}: {e}")
        return None

def main():
    dose_rate_str=""
    CPS_str=""
    dose_str=""
    duration_str=""

    #Select COM Port
    port = "COM8"
    #Message requesting device data
    data_to_send = bytes.fromhex('23 21 41 63 63 75 52 61 64 21 23 0A 00 01 00 7E 04 00 11 A7 1E 43 E7')
    #print(data_to_send)

    serial_connection = open_serial_connection(port)
    if not serial_connection:
        return
    try:
        # Write the data
        serial_connection.write(data_to_send)
        
        # Read the response
        response_bytes = serial_connection.read(800)

        #parse and rearrange data
        for x in range (0,4):
            #read hex numbers for dose rate
            text=hex(response_bytes[dose_rate_index[x]])
            #split hex number at X
            z=re.split("x", text)
            #check for length and add missing leading zero if needed
            if len(z[1])==1:
                    z[1]="0"+z[1]
            #add bits to string        
            if len(dose_rate_str)==0:
                dose_rate_str=z[1]
            else:
                dose_rate_str=dose_rate_str+z[1]
            #print("Dose rate: " + dose_rate_str + " microSv/hr")

            #read and rearrage hex numbers for counts per second
            CPStext=hex(response_bytes[CPS_index[x]])
            zz=re.split("x", CPStext)
            if len(zz[1])==1:
                    zz[1]="0"+zz[1]
            if len(CPS_str)==0:
                CPS_str=zz[1]
            else:
                CPS_str=CPS_str+zz[1]

            #read and rearrange hex numbers for accumulated dose
            Dosetext=hex(response_bytes[dose_index[x]])
            zzz=re.split("x", Dosetext)
            if len(zzz[1])==1:
                    zzz[1]="0"+zzz[1]
            if len(dose_str)==0:
                dose_str=zzz[1]
            else:
                dose_str=dose_str+zzz[1]

            #read and rearrange hex numbers for duration of accumulated dose
            Durationtext=hex(response_bytes[duration_index[x]])
            zzzz=re.split("x", Durationtext)
            if len(zzzz[1])==1:
                    zzzz[1]="0"+zzzz[1]
            if len(dose_str)==0:
                duration_str=zzzz[1]
            else:
                duration_str=duration_str+zzzz[1]

            #print("CPS: " +CPS_str)
        #print("Dose rate " + hex(response_bytes[19])+hex(response_bytes[18])+hex(response_bytes[17])+hex(response_bytes[16]))
        #print("CPS " + hex(response_bytes[23])+hex(response_bytes[22])+hex(response_bytes[21])+hex(response_bytes[20]))
        # Print the response bytes
        #print("Response bytes:", [hex(byte) for byte in response_bytes])
        
        #convert dose rate from hex to float
        uSv_rate = struct.unpack('!f', bytes.fromhex(dose_rate_str))[0]
        #convert from microsevert to mrem
        mrem_rate = uSv_rate / 10
        print("Dose rate: " + str(mrem_rate) + " mrem/hr")
        #convert counts per second from hex to float, and then print
        print("CPS: " + str(struct.unpack('!f', bytes.fromhex(CPS_str))[0]))
        #convert accumulated dose from hex to float
        uSv = struct.unpack('!f', bytes.fromhex(dose_str))[0]
        #convert uSv to mrem
        mrem = uSv / 10
        print("Dose " + str(mrem) + " mrem") 
        #convert duration of accumulated dose from hex to float (in seconds)
        seconds= struct.unpack('!f', bytes.fromhex(duration_str))[0]
        #convert seconds to hours
        hours=seconds/3600
        print("Duration: " + str(hours) + " hours")


    except serial.SerialException as e:
        print(f"Error during communication: {e}")
    finally:
        serial_connection.close()

if __name__ == "__main__":
    starttime = time.time()
    while True:
        main()
        time.sleep(1 - ((time.time() - starttime) % 1))

