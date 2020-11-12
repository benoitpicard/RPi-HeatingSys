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
file_tempSensor="../RPi-HeatingSys-Data/dataTempSensor.csv"
file_tempSetpoint="../RPi-HeatingSys-Data/tempSetpoint.csv"
file_valveCmd="../RPi-HeatingSys-Data/valveCmd.csv"
lastDateTime=pd.to_datetime('today')
exitFlag=False

# Setup
typeDayRef=['Week','Week','Week','Week','Week','WeekEnd','WeekEnd']
typeZone=['Upstair','Main']
valveName=['V1U','V2M']

print('[%.19s] funcHSC.py: Setup completed, starting control' % pd.to_datetime('today'))

# --- START INFINITE LOOP ---
try:
    while True:
        time.sleep(120)
        
        # --- Import Data & Average ---
        # Reading csv file with trials to avoid simulatneous reading errors
        read_tempSensor,errorActive=tryReadCSV(file_tempSensor,'DateTime ()')
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
        
        # --- Import control setpoint ---
        # Reading csv file with trials to avoid simulatneous reading errors
        read_tempSetpoint,errorActive=tryReadCSV(file_tempSetpoint,'')
        if errorActive:
            print('   --- abort loop ---')
            break
        # Read and fit into array by zone
        targetTemp={}
        NameList=[]
        DataList=()
        for Zone in typeZone:
            # Get target temperature from each zone
            targetTemp[Zone]=getSetpointTemp(read_tempSetpoint,Zone,nowDateTime,typeDayRef)
            # Prepare Data for a Pandas Serie
            NameList=NameList+[('TA_'+Zone[0]+'_TG (C)'),('TF_'+Zone[0]+'_TG (C)')]
            DataList=DataList+targetTemp[Zone]  
        # Assign Target to Pandas Serie
        temp_Target=pd.Series(DataList,NameList)
        
        # --- Control logic ---
        # Reading csv file with trials to avoid simulatneous reading errors
        read_valveCmd,errorActive=tryReadCSV(file_valveCmd,'')
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
                # add time info and force relay exitflag off
                new_valveCmd.loc[0,'ExitFlag']=0
                new_valveCmd.loc[0,'DateTime']=nowDateTime
        
        # --- Save data to recording file ---
        # Combine data
        dataAll=pd.concat([temp_Meas,temp_Target,new_valveCmd.iloc[0]])
        dataAll=dataAll.to_frame().T.set_index('DateTime')
        # Save to file - Check Date and reset for new filename each day (or if file not found)
        fileDay=nowDateTime.strftime('%Y%m%d')
        file_controlSys='../RPi-HeatingSys-Data/DATA/'+fileDay+'_HSC_Data_.csv'
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
