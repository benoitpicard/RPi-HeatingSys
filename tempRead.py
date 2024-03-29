#!/usr/bin/env python3

# READ TEMP AND HUMIDITY SENSOR, RETURN RESULTS IN CSV FILE
# T:Temp, H:Humidity, A:Air, F:Floor, M:Main, U:Upstair, W:Water

# Import main modules
import time
import numpy as np
import pandas as pd
from w1thermsensor import W1ThermSensor, Sensor
#import board
import sys, traceback
# Import code functions
from utilitiesHSC import tryReadCSV

# --- Initialisation ---
file_tempSensor="/home/pi/RPi-HeatingSys-Data/dataTempSensor.csv"
file_valveCmd="/home/pi/RPi-HeatingSys-Data/valveCmd.csv"
file_maxLines=100
reset_tempData=True
exitFlag=False

# --- SENSOR LIST (DS18B20) ---
# RPi pin no default in used (GPIO4) for 1-wire protocol
TS1_Name=['TA_U','TF_U','TA_M','TF_M','TA_G','TF_G','TW_IN','TW_OUT','TA_OUT']
TS1_Unit=['C','C','C','C','C','C','C','C','C']
TS1_ID=['01144bf1efaa', #'TA_U'
    '01145167b9aa', #'TF_U'
    '000005675be3', #'TA_M'
    '01144b8b70aa', #'TF_M'
    '48e13793adff', #'TA_G'
    '54e1379c71ff', #'TF_G'
    '0114515ff8aa', #'TW_IN'
    '0114515740aa', #'TW_OUT'
    'e3e1379c0cff'  #'TA_OUT'
    ]
TS1_Count=len(TS1_Name)

# --- DS18B20 SETUP ---
DS18B20_SENS=[]
for iS in range(TS1_Count):
    DS18B20_SENS.append(W1ThermSensor(Sensor.DS18B20, TS1_ID[iS]))

# --- DHT SETUP --- REMOVED AS OF JAN01 2023 --- SEE GITHUB COMMIT FOR PREVIOUS CODE

print('[%.19s] tempRead.py: Setup completed, starting measurement' % pd.to_datetime('today'))
# --- INFINITE LOOP ---
try:
    while True:

        # Run near continuous:
        time.sleep(0.5)
        
        # Init to NaN
        TS1_Data=np.empty(TS1_Count)
        TS1_Data[:]=np.nan
        
        # DS18B20 SENSOR READ
        attemptCount=5
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
                time.sleep(0.1)
            time.sleep(.1)
                
        # GROUP DATA WITH DATE
        TS_Name=['DateTime']+TS1_Name
        TS_Unit=['']+TS1_Unit
        TS_ColName=[]
        for iN in range(len(TS_Name)):
            TS_ColName.append(TS_Name[iN]+' ('+ TS_Unit[iN]+')')
            
        TS_Data=[np.concatenate(([pd.to_datetime('today')],TS1_Data))]
        
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
            temp_df,errorActive=tryReadCSV(file_tempSensor,TS_ColName[0],pd)
            if errorActive:
                print('   --- abort loop ---')
                break
            newLine_df=(pd.DataFrame(TS_Data,columns=TS_ColName)).set_index(TS_ColName[0])
            #temp_df=read_df.append(newLine_df,sort=False)
            temp_df = pd.concat([temp_df, newLine_df])
            
            # remove 1st line if too long
            dfCount=len(temp_df.index)+1
            if dfCount+1>file_maxLines:
                temp_df=temp_df.drop(temp_df.index[[0]])
                
            temp_df.to_csv(file_tempSensor,mode='w',header=True,index=True)
            
        # ABORT METHOD REMOVED, ASSUME TEMP SENSOR IS SAFE TO EXECUTE EVEN WHEN SYSTEM IS NOT CONTROLLING 
        # # Abort method: if valveCmd.csv contains the exitflag
        # # Reading csv file with trials to avoid simulatneous reading errors
        # read_valveCmd,errorActive=tryReadCSV(file_valveCmd,'',pd)
        # if errorActive:
            # print('   --- abort loop ---')
            # break
        # exitFlag=read_valveCmd.loc[0,'ExitFlag']==1
        # # exit control through valveCmd csv:
        # if exitFlag:
            # print('[%.19s] tempRead.py: ExitFlag read at 1 (exiting infinite loop)' % pd.to_datetime('today'))
            # break

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