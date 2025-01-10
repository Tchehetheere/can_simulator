#!/usr/bin/python3

import can #type: ignore
import time, datetime

source = "./source/log2-engine_on.txt"
known_ids = ["18FEF517", "18FEF117", "18FEFC17", "18FECA17", "0CF00417", "0CF00317", "18FEF217", "18FEE641", "18FEE841", "18FEE717", "18FFAC17", "18FFAD17"]


with can.Bus() as bus:
    # Using specific buses works similar:
    bus = can.Bus(interface='socketcan', channel='can0', bitrate=250000)
    
def send_one(id, dt):
    msg = can.Message(arbitration_id = id, data = dt, is_extended_id = True, channel = "can0")
    try:
        bus.send(msg)
        print(f"Message sent on {bus.channel_info}")
    except can.CanError:
        print("Message NOT sent")

def main():
    with open(source, mode="r") as file:
        counter = 1
        for lines in file:
            timeNow = datetime.datetime.now()
            raw = lines.replace(" ", "")
            id = raw[4:12]
            msg = raw[15:31]
            
            idOut = int(id, 16)
            dtOut = bytearray.fromhex(msg)

            # if id not in known_ids:
            #     continue
            
            send_one(idOut, dtOut)
            print(f"[{counter}][{timeNow}] ~ [{id}][{msg}]")
            # print(id)
            counter +=1
            time.sleep(0.5)
        
        bus.shutdown()
        print("DONE")
        
        
if __name__ == "__main__":
    main()
    
