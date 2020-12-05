#!/usr/bin/env python3

# GET TEMP AND WIND STATUS FOR OUTSIDE CONDITIONS (WEB BASED:weatherbit.io), RETURN RESULTS IN CSV FILE

# Import main modules
import time
import numpy as np
import pandas as pd
import requests
import sys, traceback
# Import code functions
from utilitiesHSC import tryReadCSV

# --- Initialisation ---
file_tempWeather="../RPi-HeatingSys-Data/dataTempWeather.csv"
file_valveCmd="../RPi-HeatingSys-Data/valveCmd.csv"
file_maxLines=100
reset_tempData=True
exitFlag=False


# --- Weather Tracking Info List ---
# Ref match weatherbit fields (up to 2 layers)
WT_Name=['WT_TIME','WT_STA','WT_OUT','WT_APP','WT_CLOUDS','WT_SOLARRAD','WT_COND','WT_WIND','WT_RH']
WT_Unit=['','name','C','C','%','W/m^2','code','m/s','%']
WT_Ref=['ob_time','station','temp','app_temp','clouds','solar_rad',['weather','code'],'wind_spd','rh']
WT_Count=len(WT_Name)
WT_TimeZoneOffset=-5 #hours from Greenwich
WT_ColName=[]
for iN in range(WT_Count):
    if WT_Unit[iN]!='':
        WT_ColName.append(WT_Name[iN]+' ('+ WT_Unit[iN]+')')
    else:
        WT_ColName.append(WT_Name[iN])
    
    
WT_CurrentBaseURL = "https://api.weatherbit.io/v2.0/current?"
WT_ForecastBaseURL = "https://api.weatherbit.io/v2.0/forecast/hourly?"
WT_Key = '9be0fe524ef44be28c838addf54f55e5' #key for Benoit Picard free account

WT_params = { # not used
  'city': 'Sherbrooke',
  'country' : 'CA',
  'key' : WT_Key
  }
WT_LatLon ={
  'lat': 45.374398,
  'lon' : -71.960889,
  'key' : WT_Key
}
queryLatLon=WT_CurrentBaseURL
for key, value in WT_LatLon.items(): #build request like 'https://api.weatherbit.io/v2.0/current?lat=45.374398&lon=-71.960889&key=9be0fe524ef44be28c838addf54f55e5'
    queryLatLon += key + '=' + str(value) + '&'
queryLatLon=queryLatLon[0:-1] #remove last &

print('[%.19s] getOutTemp.py: Setup completed, starting weather reporting' % pd.to_datetime('today'))
# --- INFINITE LOOP ---
try:
    while True:

        # Run first, then every 20min:
        time.sleep(0.1)
        sleepMinutes=20
        
        # Init to NaN
        WT_Data=['']* WT_Count

        # External Temp from weatherbit, free account (500 call/day)
        attemptCount=2
        for attempt in range(attemptCount):
        
            try:
                # Get data from Weatherbit
                Data = requests.get(queryLatLon)
                Weather = Data.json()
                
                for iW in range(WT_Count):
                    if type(WT_Ref[iW]) is str:
                        WT_Data[iW]=Weather['data'][0][WT_Ref[iW]]
                    elif type(WT_Ref) is list: #assume a list with 2 fields
                        WT_Data[iW]=Weather['data'][0][WT_Ref[iW][0]][WT_Ref[iW][1]]
            except:
                print('[%.19s] Error getting weather data (attempt#%d/%d)' % 
                    (pd.to_datetime('today'),attempt,attemptCount))
                pass

 
        #Write to CSV
        #   if new start, overwrite file
        #   else append last and check linecount, if too long, drop 1st line
        
        if reset_tempData:  
            # Create Pandas DataFrame with header
            temp_df=(pd.DataFrame([WT_Data],columns=WT_ColName)).set_index(WT_ColName[0])
            temp_df.index = pd.to_datetime(temp_df.index)+ pd.Timedelta(hours=WT_TimeZoneOffset) #remove timezone delta
            temp_df.to_csv(file_tempWeather,mode='w',header=True,index=True)
            
            reset_tempData=False
        else:
            # Read CSV as pandas DataFrame
            read_df,errorActive=tryReadCSV(file_tempWeather,WT_ColName[0],pd)
            if errorActive:
                print('   --- abort loop ---')
                break
            newLine_df=(pd.DataFrame([WT_Data],columns=WT_ColName)).set_index(WT_ColName[0])
            newLine_df.index = pd.to_datetime(newLine_df.index)+ pd.Timedelta(hours=WT_TimeZoneOffset) #remove timezone delta
            temp_df=read_df.append(newLine_df,sort=False)
            
            # remove 1st line if too long
            dfCount=len(temp_df.index)+1
            if dfCount+1>file_maxLines:
                temp_df=temp_df.drop(temp_df.index[[0]])
                
            temp_df.to_csv(file_tempWeather,mode='w',header=True,index=True)
            
        # Abort method: if valveCmd.csv contains the exitflag
        # Reading csv file with trials to avoid simulatneous reading errors
        read_valveCmd,errorActive=tryReadCSV(file_valveCmd,'',pd)
        if errorActive:
            print('   --- abort loop ---')
            break
        exitFlag=read_valveCmd.loc[0,'ExitFlag']==1
        # exit control through valveCmd csv:
        if exitFlag:
            print('[%.19s] getOutTemp.py: ExitFlag read at 1 (exiting infinite loop)' % pd.to_datetime('today'))
            break
       
        # Sleep
        time.sleep(sleepMinutes*60)

except:
    #retry reading (sometime fails due to simulatneous file writing by getOutTemp.py)
    print('[%.19s] getOutTemp.py: error in execution, exiting' % pd.to_datetime('today'))
    traceback.print_exc(file=sys.stdout)
                

print('[%.19s] getOutTemp.py: function exit' % pd.to_datetime('today'))   