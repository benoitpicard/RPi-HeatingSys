#!/usr/bin/env python3

# READ CSV COMMAND (FIRST LINE) AND CONTROL OUTPUT TO RELAY BOARD

import RPi.GPIO as GPIO
import csv
import time
import sys, traceback
import pandas as pd

file_valveCmd="../RPi-HeatingSys-Data/valveCmd.csv"

# RELAY SETUP
GPIO.setmode(GPIO.BOARD)
# Relay1: GPIO5 PIN29 - V1U UPSTAIR HEATING
# Relay2: GPIO6 PIN31 - V2M MAIN FLOOR HEATING
# Relay3: GPIO13 PIN33 - V3G GARAGE HEATING
# Relay4: GPIO19 PIN35 - NOT USED
RelayPinNo=(29,31,33,35) #matching order to valve name
valveName=['V1U','V2M','V3G','V4E'] #mathing order to relay pins
for pinNo in RelayPinNo:
    GPIO.setup(pinNo,GPIO.OUT)
    GPIO.output(pinNo,GPIO.HIGH)

print('[%.19s] valveControl.py: Setup completed, starting control' % pd.to_datetime('today'))

# READ CMD FROM CSV EVERY ~10 SECONDS
try:
    while True:
    
        time.sleep(10)
        
        read_valveCmd=(pd.read_csv(file_valveCmd)) #read csv with pandas
        
        # Previous csv reading (not pandas, read only first line)
        #with open(file_valveCmd) as csvFile:
        #    csv_reader = csv.reader(csvFile)
        #    csv_headings = next(csv_reader) #read 1st csv line
        #    cmd_line = next(csv_reader) #read second csv line (cmd)
        #       cmd_OnOff=cmd_line[iP+3] #to be changed to verify header
        
        for iP in range(4):
            #Get RelayPinNo
            pinNo=RelayPinNo[iP]
            valveCmd=new_valveCmd.loc[0,valveName[iP]]
            
            if valveCmd:
                GPIO.output(pinNo,GPIO.LOW)
            elif not valveCmd:
                GPIO.output(pinNo,GPIO.HIGH)
            else:
                GPIO.output(pinNo,GPIO.HIGH)
                print("Wrong input, forced pin %d off (%s)" % (pinNo,valveName[iP]))
         
        if read_valveCmd.loc[0,'ExitFlag']==1: # exit loop
            break
             
except KeyboardInterrupt:
    print("Manual Quit: OK")
except:
    print('[%.19s] valveControl.py: error in execution, exiting' % (pd.to_datetime('today'),attempt))
    traceback.print_exc(file=sys.stdout)

GPIO.cleanup()
print('[%.19s] valveControl.py: Exiting RELAY control (cleanup completed)' % pd.to_datetime('today'))
