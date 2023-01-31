#!/usr/bin/env python3

# Control logic for the central heating system, run every 2 minutes
#   Import temperature data from csv (created by tempRead.py)
#   Import control logic from csv
#   Assign relay control to csv (used by valveControl.py)

# Import main modules
import time
import numpy as np
import pandas as pd
import os, sys, traceback
# Import code functions
from utilitiesHSC import getSetpointTemp
from utilitiesHSC import tryReadCSV

# Initialization
file_tempSensor="/home/pi/RPi-HeatingSys-Data/dataTempSensor.csv"
file_tempSetpoint="/home/pi/RPi-HeatingSys-Data/tempSetpoint.csv"
file_valveCmd="/home/pi/RPi-HeatingSys-Data/valveCmd.csv"
file_tempWeather="/home/pi/RPi-HeatingSys-Data/dataTempWeather.csv"
lastDateTime=pd.to_datetime('today')
exitFlag=False

# Setup
typeDayRef=['Week','Week','Week','Week','Week','WeekEnd','WeekEnd'] #[Monday,Tuesday,Wednesday,Thrusday,Friday,Saturday,Sunday
typeZone=['Upstair','Main','Garage']
valveName=['V1U','V2M','V3G']

print('[%.19s] funcHSC.py: Setup completed, starting control' % pd.to_datetime('today'))

# --- START INFINITE LOOP ---
try:
    while True:
        time.sleep(119)
        
        # --- Import Data & Average ---
        # Reading csv file with trials to avoid simulatneous reading errors
        read_tempSensor,errorActive=tryReadCSV(file_tempSensor,'DateTime ()',pd)
        if errorActive:
            print('   --- abort loop ---')
            break

        read_tempSensor.index=pd.to_datetime(read_tempSensor.index) #convert read string date to pandas date
        #   Get data in current time window
        nowDateTime=pd.to_datetime('today')
        boolCurWindow=np.logical_and(read_tempSensor.index>=lastDateTime,read_tempSensor.index<nowDateTime);
        #   Average data in Pandas Serie
        temp_Meas=read_tempSensor[boolCurWindow].mean()
        temp_Meas['dataAvg (Count)']=np.sum(boolCurWindow)
        
        # --- Import Weather Current Data ---
        # Reading csv file with trials to avoid simulatneous reading errors
        read_tempWeather,errorActive=tryReadCSV(file_tempWeather,'',pd)
        read_tempWeather.index=pd.to_datetime(read_tempWeather.index) #convert read string date to pandas date
        
        # --- Import AUTO/Default setpoint from csv schedule ---
        # Reading csv file with trials to avoid simulatneous reading errors
        read_tempSetpoint,errorActive=tryReadCSV(file_tempSetpoint,'',pd)
        if errorActive:
            print('   --- abort loop ---')
            break
        # Read and fit into array by zone
        targetTemp={}
        NameList=[]
        DataList=()
        for Zone in typeZone:
            # Get target temperature from each zone
            targetTemp[Zone]=getSetpointTemp(read_tempSetpoint,Zone,nowDateTime,typeDayRef,pd)
            # Prepare Data for a Pandas Serie
            NameList=NameList+[('TA_'+Zone[0]+'_TG (C)'),('TF_'+Zone[0]+'_TG (C)')]
            DataList=DataList+targetTemp[Zone]  
        # Assign Target to Pandas Serie
        temp_Target=pd.Series(DataList,NameList)
        
        # --- Mode Selection ---
        # Mode selection to match HomeKit toolkit:
        #   Each zone have 2 (Air & Floor)
        #       for air temperature:
        #           0 (OFF) : Away Mode, Set air target to 16
        #           1 (HEAT): Manual Mode, Set to entered value (add schedule?)
        #           3 (AUTO): Default to CSV schedule (maybe need to save it in the future?)
        #       for floor temperature:
        #           0 (OFF) : Water flow for sector is OFF
        #           1 (HEAT): Manual Mode, Set to ON for 1 hour
        #           3 (AUTO): Water flow for sector is ON (setpoint not used)
        
        # Minimal implementation as of jan 2023: manual mode not yet implemented
        NameList=[]
        DataList=()
        for Zone in typeZone:
            # Prepare Data for a Pandas Serie
            NameList=NameList+[('TA_'+Zone[0]+'_MODE'),('TF_'+Zone[0]+'_MODE')]
            DataList=DataList+(3,0)
        # Assign Mode to Pandas Serie
        temp_Mode=pd.Series(DataList,NameList)
        
        # --- Control logic ---
        # Reading csv file with trials to avoid simulatneous reading errors
        read_valveCmd,errorActive=tryReadCSV(file_valveCmd,'',pd)
        if errorActive:
            print('   --- abort loop ---')
            break
        overrideOff=read_valveCmd.loc[0,'Override']==0
        exitFlag=read_valveCmd.loc[0,'ExitFlag']==1
        # exit control through valveCmd csv:
        if exitFlag:
            break
        # activate relay if air temp below target (basic control logic)
        new_valveCmd=read_valveCmd
        if overrideOff: #only change command if override not active
            for iZ in range(len(typeZone)):
                Zone=typeZone[iZ]
                TA_Read=temp_Meas['TA_'+Zone[0]+' (C)']
                TA_Cmd=targetTemp[Zone][0]
                ValveCmd=int(TA_Read<TA_Cmd) #SIMPLE LOGIC HERE - TO BE UPDATED!
                new_valveCmd.loc[0,valveName[iZ]]=ValveCmd
                # Correct Floor temp mode to AUTO if Valve Command is ON
                if ValveCmd:
                    temp_Mode['TF_'+Zone[0]+'_MODE']=3
                # add time info and force relay exitflag off
                new_valveCmd.loc[0,'ExitFlag']=0
                new_valveCmd.loc[0,'DateTime']=nowDateTime
                # add control for main floor convectair Eco Mode
                if valveName[iZ]=='V2M':
                    new_valveCmd.loc[0,'V4E']=int(TA_Cmd<=20) # SIMPLE LOGIG TO TURN OFF AT NIGHT
        else: #change time even when overrides
            new_valveCmd.loc[0,'DateTime']=nowDateTime
        
        # --- Save data to recording file ---
        # Combine data
        dataAll=pd.concat([temp_Meas,temp_Target,new_valveCmd.iloc[0],read_tempWeather.iloc[-1]])
        dataAll=dataAll.to_frame().T.set_index('DateTime')
        # Save to file - Check Date and reset for new filename each day (or if file not found)
        fileDay=nowDateTime.strftime('%Y%m%d')
        file_controlSys='/home/pi/RPi-HeatingSys-Data/DATA/'+fileDay+'_HSC_Data.csv'
        if not os.path.isfile(file_controlSys):
            # If file does not exist
            dataAll.to_csv(file_controlSys,mode='w',header=True,index=True)
        else:
            # Append to file
            dataAll.to_csv(file_controlSys,mode='a',header=False,index=True)
        
        # --- Save to relay csv ---
        if overrideOff: #change controls only if override is OFF (0)
            new_valveCmd.to_csv(file_valveCmd,mode='w',header=True,index=False)
        
        # --- Prep next loop
        #   Set last date for next iteration
        lastDateTime=nowDateTime
except:
    #retry reading (sometime fails due to simulatneous file writing by tempRead.py)
    print('[%.19s] funcHSC.py: error in execution, exiting' % pd.to_datetime('today'))
    traceback.print_exc(file=sys.stdout)
                

if not exitFlag:
    # Ensure not continuous heating: request an exit on valveCmd.py too 
    read_valveCmd=(pd.read_csv(file_valveCmd)) #read csv with pandas
    new_valveCmd=read_valveCmd
    new_valveCmd.loc[0,'ExitFlag']=1
    new_valveCmd.loc[0,'DateTime']=nowDateTime
    new_valveCmd.to_csv(file_valveCmd,mode='w',header=True,index=False)
    print('[%.19s] funcHSC.py: ExitFlag in valveCmd csv set to 1' % pd.to_datetime('today'))
    
print('[%.19s] funcHSC.py: function exit' % pd.to_datetime('today'))
