#!/usr/bin/python3

import can #type: ignore
import time, datetime, os

source = "./source/log2-engine_on.txt"
known_ids = ["18FEF517", "18FEF117", "18FEFC17", "18FECA17", "0CF00417", "0CF00317", "18FEF217", "18FEE641", "18FEE841", "18FEE717", "18FFAC17", "18FFAD17"]

# Configure
can_bitrate = 25000
can_interface = 'socketcan'
can_channel = 'can0'

with can.Bus() as bus:
    # Using specific buses works similar:
    bus = can.Bus(interface=can_interface, channel=can_channel, bitrate=can_bitrate)

def restart_sock():
    try:
        global bus
        bus.shutdown()
        os.system(f"sudo ip link set down {can_channel}")
        os.system(f"sudo ip link set up {can_channel}")
        bus = can.Bus(interface=can_interface, channel=can_channel, bitrate=can_bitrate)
        print("DONE")
    except OSError as e:
        print(e)

def send_one(id, dt, counter):
    timeNow = datetime.datetime.now()
    idOut = int(id, 16)
    dtOut = bytearray.fromhex(dt)
    msg = can.Message(arbitration_id = idOut, data = dtOut, is_extended_id = True, channel = can_channel)

    retries = 1
    while True:
        
        try:
            bus.send(msg)
            print(f"[{counter}][SUCCESS][{timeNow}] [Message sent on {bus.channel_info}] ~ [{id}][{dt}]")
            break
        except can.CanError as e:
            print(f"[{counter}][ERROR][{timeNow}] [Message NOT sent] [{e}] [{id}][{dt}] ~ [RETRY]")
            time.sleep(0.5)
    
        if retries == 2:
            print(f"[ERROR] [Failed sending message] [RESTARTING SOCKET]")
            restart_sock()
            time.sleep(0.4)
            try:
                bus.send(msg)
                print(f"[SUCCESS][{timeNow}] [Message sent on {bus.channel_info}] ~ [{id}][{dt}]")
            except can.CanError as e:
                print(f"[ERROR] [Failed sending message] {e} ~ [{id}][{dt}]")
            break
                
        retries += 1
    
def main():
    # Directory check
    path = "./output"
    if not os.path.exists(path):
        try:
            os.mkdir(path)
            print("[SUCCESS] [Directory Created]")
        except OSError as e:
            print(f"[ERROR] [{e}]")
            
    fileName = f"./output/{datetime.datetime.now()}-ID LIST TRANSMITTED.txt"
    with open(fileName, "w") as outFile:
        with open(source, mode="r") as file:
            counter = 1
            for lines in file:
                raw = lines.replace(" ", "")
                id = raw[4:12]
                msg = raw[15:31]
                timeStamp = datetime.datetime.now()

                if id in known_ids:
                    outFile.writelines(f"{timeStamp};{id}{msg}\n")
                    
                send_one(id, msg, counter)
                
                if counter == 500:
                    break
                
                counter +=1
                time.sleep(0.035)
            
            bus.shutdown()
            print("DONE")
            print(f"Output File Name: {fileName}")
        
        
if __name__ == "__main__":
    main()
