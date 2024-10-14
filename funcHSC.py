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
from utilitiesHSC import tryReadCSV, tryReadCSV_p

# Initialization
file_tempSensor="/home/pi/RPi-HeatingSys-Data/dataTempSensor.csv"
file_modeSelect="/home/pi/RPi-HeatingSys-Data/tempSetpointModeSelect.csv"
file_controlSetpoint='/home/pi/RPi-HeatingSys-Data/controlSetpoint.csv'
#file_tempSetpoint="/home/pi/RPi-HeatingSys-Data/tempSetpoint_" #need to add Mode + ".csv"
file_valveCmd="/home/pi/RPi-HeatingSys-Data/valveCmd.csv"
file_tempWeather="/home/pi/RPi-HeatingSys-Data/dataTempWeather.csv"
lastDateTime=pd.to_datetime('today')
exitFlag=False

# Setup
#typeDayRef=['Week','Week','Week','Week','Week','WeekEnd','WeekEnd'] #[Monday,Tuesday,Wednesday,Thrusday,Friday,Saturday,Sunday
typeZone=['Upstair','Main','Garage']
valveName=['V1U','V2M','V3G']
#idName=['TA_U','TA_M','TA_G']

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
        
        # --- Import AwayMode Type from csv input ---
        # Reading csv file with trials to avoid simulatneous reading errors
        read_modeSelect,errorActive=tryReadCSV_p(file_modeSelect,'',pd,5,'DateTime')
        if errorActive:
            print('   --- abort loop ---')
            break
        dfMT=(nowDateTime-read_modeSelect['DateTime'])>pd.to_timedelta(0) #compare DateTime with current time and return true if above 0
        if any(dfMT==True):
            Mode=read_modeSelect.iloc[(dfMT[dfMT==True].index.tolist()[-1])]['Mode'] # return Mode column of last true value
        else: #assume no entry or all future value
            Mode='Schedule'
            
        # # --- Import Setpoint from csv schedule based on select mode ---
        # # Reading csv file with trials to avoid simulatneous reading errors
        #read_controlSetpoint,errorActive=tryReadCSV(file_tempSetpoint+Mode+'.csv','',pd)
        #if errorActive:
        #    print('   --- abort loop ---')
        #    break
        # Read and fit into array by zone
        #targetTemp={}
        #NameList=[]
        #DataList=()
        #for Zone in typeZone:
        #    # Get target temperature from each zone
        #    targetTemp[Zone]=getSetpointTemp(read_controlSetpoint,Zone,nowDateTime,typeDayRef,pd)
        #    # Prepare Data for a Pandas Serie
        #    NameList=NameList+[('TA_'+Zone[0]+'_TG (C)'),('TF_'+Zone[0]+'_TG (C)')]
        #    DataList=DataList+targetTemp[Zone]
        # # Assign Target to Pandas Serie
        #temp_Target=pd.Series(DataList,NameList)
        
        # --- Import Setpoint and Target Mode from HomeKit-updated csv
        # --- Mode Selection ---
        # Mode selection to match HomeKit toolkit:
        #   Each zone have 2 (Air & Floor)
        #       for air temperature:
        #       0    0 (OFF) : Off Mode, Set air target to 12 (freeze protection)
        #       1    1 (HEAT): Manual Mode, Set to entered value
        #       for floor temperature: (not used, only displayed)
        #       0    0 (OFF) : Water flow for sector is OFF (not used)
        #       1    1 (HEAT): Manual Mode, Set to ON for 1 hour (not used)

        read_controlSetpoint,errorActive=tryReadCSV_p(file_controlSetpoint,'ID',pd,5,'ID')
        # Setpoint (Target Temp)
        NameListSetpoint=[]
        DataListSetpoint=[]
        NameListMode=[]
        DataListMode=[]
        for Zone in typeZone:
            # Get target temperature from each zone
            TA_targetTemp=read_controlSetpoint.loc['TA_'+Zone[0],'targetTemperature']
            TA_targetMode=read_controlSetpoint.loc['TA_'+Zone[0],'targetHeatingCoolingState']
            TF_targetTemp=read_controlSetpoint.loc['TF_'+Zone[0],'targetTemperature']
            TF_targetMode=read_controlSetpoint.loc['TF_'+Zone[0],'targetHeatingCoolingState']
            # Prepare Data for a Pandas Serie
            NameListSetpoint=NameListSetpoint+[('TA_'+Zone[0]+'_TG (C)'),('TF_'+Zone[0]+'_TG (C)')]
            NameListMode=NameListMode+[('TA_'+Zone[0]+'_MODE'),('TF_'+Zone[0]+'_MODE')]
            # Modify temp target based on mode
            if TA_targetMode=='0':
                # Off Mode:
                TA_targetTemp=12
            elif Mode=='Away':
                # Away Mode:
                TA_targetTemp=18
            if TF_targetMode=='0':
                # Off Mode:
                TF_targetTemp=12
            elif Mode=='Away':
                # Away Mode:
                TF_targetTemp=18
            # Save Mode & Target
            DataListSetpoint=DataListSetpoint+[TA_targetTemp,TF_targetTemp]
            DataListMode=DataListMode+[TA_targetMode,TF_targetMode]
        # Assign Target to Pandas Serie
        temp_Target=pd.Series(DataListSetpoint,NameListSetpoint)
        temp_Mode=pd.Series(DataListMode,NameListMode)
        
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
        # activate heating if air or floor target is above measured temp
        #    applying hysteresis to avoid short on/off cycle
        hysteresis = 0.1 #degC
        new_valveCmd=read_valveCmd
        if overrideOff: #only change command if override not active
            for iZ in range(len(typeZone)):
                Zone=typeZone[iZ]
                TA_Read=temp_Meas['TA_'+Zone[0]+' (C)']
                TA_Cmd=temp_Target['TA_'+Zone[0]+'_TG (C)']
                TF_Read=temp_Meas['TF_'+Zone[0]+' (C)']
                TF_Cmd=temp_Target['TF_'+Zone[0]+'_TG (C)']
                # Default to previous value
                ValveCmd = new_valveCmd.loc[0,valveName[iZ]]
                # Update control value based on target and hysteresis
                if TA_Read < TA_Cmd - hysteresis or TF_Read < TF_Cmd - hysteresis:
                    ValveCmd = 1
                elif TA_Read > TA_Cmd + hysteresis and TF_Read > TF_Cmd + hysteresis:
                    ValveCmd = 0
                
                # Exception for Zone3: Only active if 1 or 2 are off (since power limited, priority to zone 1 and 2)
                #     exception removed since garage flow is very small and does not affect power allocation much
                #if valveName[iZ]=='V3G':
                #    if new_valveCmd.loc[0,valveName[0]]==1 or new_valveCmd.loc[0,valveName[1]]==1:
                #        ValveCmd=0
                
                # Save to ValveCmd vector
                new_valveCmd.loc[0,valveName[iZ]]=ValveCmd
                # # Correct Floor temp mode to AUTO if Valve Command is ON
                #if ValveCmd:
                #    temp_Mode['TF_'+Zone[0]+'_MODE']=2
                # add time info and force relay exitflag off
                new_valveCmd.loc[0,'ExitFlag']=0
                new_valveCmd.loc[0,'DateTime']=nowDateTime
                # add control for main floor convectair Eco Mode
                if valveName[iZ]=='V2M':
                    new_valveCmd.loc[0,'V4E']=int(TA_Cmd<=20.8) # SIMPLE LOGIG TO TURN IN ECOMODE AT NIGHT
        else: #change time even when overrides
            new_valveCmd.loc[0,'DateTime']=nowDateTime
        #  update temp_Mode for floor stutas based on selection (not since adding manual temp target on floor)
        #for iZ in range(len(typeZone)):
        #    Zone=typeZone[iZ]
        #    temp_Mode['TF_'+Zone[0]+'_MODE']=new_valveCmd.loc[0,valveName[iZ]]
        
        # --- Save Current Temp and Mode to file ---
        # Modify with updated data   
        for Zone in typeZone:
            read_controlSetpoint.loc['TA_'+Zone[0],'currentTemperature']=temp_Meas['TA_'+Zone[0]+' (C)']
            read_controlSetpoint.loc['TF_'+Zone[0],'currentTemperature']=temp_Meas['TF_'+Zone[0]+' (C)']
            read_controlSetpoint.loc['TA_'+Zone[0],'currentHeatingCoolingState']=temp_Mode['TA_'+Zone[0]+'_MODE']
            read_controlSetpoint.loc['TF_'+Zone[0],'currentHeatingCoolingState']=temp_Mode['TF_'+Zone[0]+'_MODE']
            read_controlSetpoint.loc['TA_'+Zone[0],'targetTemperature']=temp_Target['TA_'+Zone[0]+'_TG (C)']
            read_controlSetpoint.loc['TF_'+Zone[0],'targetTemperature']=temp_Target['TF_'+Zone[0]+'_TG (C)']
            read_controlSetpoint.loc['TA_'+Zone[0],'targetHeatingCoolingState']=temp_Mode['TA_'+Zone[0]+'_MODE']
            read_controlSetpoint.loc['TF_'+Zone[0],'targetHeatingCoolingState']=temp_Mode['TF_'+Zone[0]+'_MODE']
        # Save data
        read_controlSetpoint.to_csv(file_controlSetpoint,mode='w',header=True,index=True)     
        
        # --- Save data to recording file ---
        # Combine data
        dataAll=pd.concat([temp_Meas,temp_Mode,temp_Target,new_valveCmd.iloc[0],read_tempWeather.iloc[-1]])
        dataAll=dataAll.to_frame().T.set_index('DateTime')
        # Save to file - Check Date and reset for new filename each day (or if file not found)
        fileDay=nowDateTime.strftime('%Y%m%d')
        file_controlSys='/home/pi/RPi-HeatingSys-Data/DATA/'+fileDay+'_HSC_Data.csv'
        if not os.path.isfile(file_controlSys):
            # If file does not exist
            dataAll.to_csv(file_controlSys,mode='w',header=True,index=True)
        else:
            # Append to file - would need to run a try loop, in case csv file is currently read by webapp
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
