#!/usr/bin/env python3

# READ CSV COMMAND (FIRST LINE) AND CONTROL OUTPUT TO RELAY BOARD

import RPi.GPIO as GPIO
import csv
import time

file_valveCmd="../RPi-HeatingSys-Data/valveCmd.csv"

# RELAY SETUP
GPIO.setmode(GPIO.BOARD)
# Relay1: GPIO5 PIN29 - V1T UPSTAIR HEATING
# Relay2: GPIO6 PIN31 - V2M MAIN FLOOR HEATING
# Relay3: GPIO13 PIN33 - V3G GARAGE HEATING
# Relay4: GPIO19 PIN35 - NOT USED
RelayPinNo=(29,31,33,35)
for pinNo in RelayPinNo:
    GPIO.setup(pinNo,GPIO.OUT)
    GPIO.output(pinNo,GPIO.HIGH)

# READ CMD FROM CSV EVERY ~10 SECONDS
try:
    while True:
    
        time.sleep(10)
        
        with open(file_valveCmd) as csvFile:
            csv_reader = csv.reader(csvFile)
            csv_headings = next(csv_reader) #read 1st csv line
            cmd_line = next(csv_reader) #read second csv line (cmd)
        
        for iP in range(4):
            #Get RelayPinNo
            pinNo=RelayPinNo[iP]
            cmd_OnOff=cmd_line[iP+3]
            if cmd_OnOff=='1':
                GPIO.output(pinNo,GPIO.LOW)
            elif cmd_OnOff=='0':
                GPIO.output(pinNo,GPIO.HIGH)
            else:
                GPIO.output(pinNo,GPIO.HIGH)
                print("Wrong input, forced pin %d off" % (iP+1))
         
        if cmd_line[1]=='1': # exit loop
            break
             
except KeyboardInterrupt:
    print("Manual Quit: OK")
except:
    print("Something else went wrong")
finally:
    print("Exiting RELAY control")
    GPIO.cleanup()