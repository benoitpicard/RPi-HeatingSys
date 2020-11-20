#!/usr/bin/env python3

# READ TEMP AND HUMIDITY SENSOR, RETURN RESULTS IN CSV FILE
# T:Temp, H:Humidity, A:Air, F:Floor, M:Main, U:Upstair, W:Water

# Import main modules
import time
import numpy as np
import pandas as pd
from w1thermsensor import W1ThermSensor
import board
import adafruit_dht # source: https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/python-setup
import psutil
import sys, traceback
# Import code functions
from utilitiesHSC import tryReadCSV

# --- Initialisation ---
file_tempSensor="../RPi-HeatingSys-Data/dataTempSensor.csv"
file_valveCmd="../RPi-HeatingSys-Data/valveCmd.csv"
file_maxLines=100
reset_tempData=True
exitFlag=False

# --- SENSOR LIST (DS18B20) ---
# RPi pin no default in used (GPIO4) for 1-wire protocol
TS1_Name=['TA_U','TF_U','TA_M','TF_M','TW_IN','TW_OUT']
TS1_Unit=['C','C','C','C','C','C']
TS1_ID=['01144bf1efaa', #'TA_U'
    '01145167b9aa', #'TF_U'
    '000005675be3', #'TA_M'
    '01144b8b70aa', #'TF_M'
    '0114515ff8aa', #'TW_IN'
    '0114515740aa'  #'TW_OUT'
    ]
TS1_Name=['TA_U','TA_M']
TS1_Unit=['C','C']
TS1_ID=['01144bf1efaa', #'TA_U'
    '000005675be3', #'TA_M'
    ]
TS1_Count=len(TS1_Name)

# --- DS18B20 SETUP ---
DS18B20_SENS=[]
for iS in range(TS1_Count):
    DS18B20_SENS.append(W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, TS1_ID[iS]))

# --- DHT SETUP --- 
#   issue with PulseIn process being stuck after closing first iteration: 'kill' #https://github.com/adafruit/Adafruit_CircuitPython_DHT/issues/27
for proc in psutil.process_iter():
    if proc.name() == 'libgpiod_pulsein' or proc.name() == 'libgpiod_pulsei':
        proc.kill()
#   setup name
TS2_Name=['TA_UD','HA_UD','TA_MD','HA_MD']
TS2_Unit=['C','%','C','%']
TS2_Count=len(TS2_Name)
DHT_SENS=[]
DHT_SENS.append(adafruit_dht.DHT11(board.D12))
DHT_SENS.append(adafruit_dht.DHT11(board.D16))

print('[%.19s] tempRead.py: Setup completed, starting measurement' % pd.to_datetime('today'))
# --- INFINITE LOOP ---
try:
    while True:

        # Run near continuous:
        time.sleep(0.5)
        
        # Init to NaN
        TS1_Data=np.empty(TS1_Count)
        TS1_Data[:]=np.nan
        TS2_Data=np.empty(TS2_Count)
        TS2_Data[:]=np.nan
        
        # DS18B20 SENSOR READ
        attemptCount=3
        for iS in range(TS1_Count):
            for attempt in range(attemptCount):
                try:
                    TS1_Data[iS]=DS18B20_SENS[iS].get_temperature()
                    break
                except:
                    print('[%.19s] Error reading sensor %s (attempt#%d)' % 
                        (pd.to_datetime('today'),TS1_ID[iS],attempt))
                    #traceback.print_exc(file=sys.stdout)
                    #if attempt<attemptCount-1:
                    #    print('   --- continuing ---')
                    pass
                time.sleep(0.5)
            time.sleep(0.1)
                
        # DHT SENSOR READ
        #for iS in range(TS2_Count):
        #    for attempt in range(10):
        #        try:
        #            TS2_Data[iS*2]=DHT_SENS[iS].temperature
        #            TS2_Data[iS*2+1]=DHT_SENS[iS].humidity
        #            break
        #        except:
        #            pass
        #        time.sleep(0.5)
        #    time.sleep(0.1)
        
        # GROUP DATA WITH DATE
        TS_Name=['DateTime']+TS1_Name+TS2_Name
        TS_Unit=['']+TS1_Unit+TS2_Unit
        TS_ColName=[]
        for iN in range(len(TS_Name)):
            TS_ColName.append(TS_Name[iN]+' ('+ TS_Unit[iN]+')')
            
        TS_Data=[np.concatenate(([pd.to_datetime('today')],TS1_Data,TS2_Data))]
        
        #Write to CSV
        #   if new start, overwrite file
        #   else append last and check linecount, if too long, drop 1st line
        
        if reset_tempData:  
            # Create Pandas DataFrame with header
            temp_df=(pd.DataFrame(TS_Data,columns=TS_ColName)).set_index(TS_ColName[0])
            temp_df.to_csv(file_tempSensor,mode='w',header=True,index=True)
            
            reset_tempData=False
        else:
            # Read CSV as pandas DataFrame
            read_df,errorActive=tryReadCSV(file_tempSensor,TS_ColName[0],pd)
            if errorActive:
                print('   --- abort loop ---')
                break
            newLine_df=(pd.DataFrame(TS_Data,columns=TS_ColName)).set_index(TS_ColName[0])
            temp_df=read_df.append(newLine_df,sort=False)
            
            # remove 1st line if too long
            dfCount=len(temp_df.index)+1
            if dfCount+1>file_maxLines:
                temp_df=temp_df.drop(temp_df.index[[0]])
                
            temp_df.to_csv(file_tempSensor,mode='w',header=True,index=True)
            
        # Abort method: if valveCmd.csv contains the exitflag
        # Reading csv file with trials to avoid simulatneous reading errors
        read_valveCmd,errorActive=tryReadCSV(file_valveCmd,'',pd)
        if errorActive:
            print('   --- abort loop ---')
            break
        exitFlag=read_valveCmd.loc[0,'ExitFlag']==1
        # exit control through valveCmd csv:
        if exitFlag:
            print('[%.19s] tempRead.py: ExitFlag read at 1 (exiting infinite loop)' % pd.to_datetime('today'))
            break

except:
    #retry reading (sometime fails due to simulatneous file writing by tempRead.py)
    print('[%.19s] tempRead.py: error in execution, exiting' % pd.to_datetime('today'))
    traceback.print_exc(file=sys.stdout)
                

if not exitFlag:
    # Ensure not continuous heating: request an exit on valveCmd.py too 
    read_valveCmd,errorActive=tryReadCSV(file_valveCmd,'',pd) #read csv with pandas
    new_valveCmd=read_valveCmd
    new_valveCmd.loc[0,'ExitFlag']=1
    new_valveCmd.loc[0,'DateTime']=pd.to_datetime('today')
    new_valveCmd.to_csv(file_valveCmd,mode='w',header=True,index=False)
    print('[%.19s] tempRead.py: ExitFlag in valveCmd csv set to 1' % pd.to_datetime('today'))
    
print('[%.19s] tempRead.py: function exit' % pd.to_datetime('today'))   