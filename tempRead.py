#!/usr/bin/env python3

# READ TEMP AND HUMIDITY SENSOR, RETURN RESULTS IN CSV FILE
# T:Temp, H:Humidity, A:Air, F:Floor, M:Main, U:Upstair, W:Water

import time
import numpy as np
import pandas as pd
from w1thermsensor import W1ThermSensor
import board
import adafruit_dht # source: https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/python-setup

# SENSOR LIST (DS18B20)
# RPi pin no default in used (GPIO4) for 1-wire protocol
TS1_Name=['TA_U','TF_U','TA_M','TF_M','TW_IN','TW_OUT']
TS1_Unit=['C','C','C','C','C','C']
TS1_ID=['01144bf1efaa',
    '01145167b9aa',
    '000005675be3',
    '01144b8b70aa',
    '0114515ff8aa',
    '0114515740aa'
    ]
TS1_Count=len(TS1_Name)

# DS18B20 SETUP
DS18B20_SENS=[]
for iS in range(TS1_Count):
    DS18B20_SENS.append(W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, TS1_ID[iS]))

# DHT SETUP
TS2_Name=['TA_UD','HA_UD','TA_MD','HA_MD']
TS2_Unit=['C','%','C','%']
TS2_Count=len(TS2_Name)
DHT_SENS=[]
DHT_SENS.append(adafruit_dht.DHT11(board.D12))
DHT_SENS.append(adafruit_dht.DHT11(board.D16))

# INFINITE LOOP 
while True:

    # Restart every 5s:
    time.sleep(5)
    # Init
    TS1_Data=np.empty(TS1_Count)
    TS1_Data[:]=np.nan
    TS2_Data=np.empty(TS2_Count)
    TS2_Data[:]=np.nan
    
    # DS18B20 SENSOR READ
    for iS in range(TS1_Count):
        for attempt in range(2):
            try:
                TS1_Data[iS]=DS18B20_SENS[iS].get_temperature()
            except:
                continue
            
    # DHT SENSOR READ
    for iS in range(TS2_Count):
        for attempt in range(10):
            try:
                TS2_Data[iS*2]=DHT_SENS[iS].temperature
                TS2_Data[iS*2+1]=DHT_SENS[iS].humidity
            except:
                continue
    
    # GROUP DATA WITH DATE
    TS_NAME=['Date']+TS1_Name+TS2_Name
    TS_Unit=['']+TS1_Unit+TS2_Unit
    TS_Data=[pd.to_datetime('today')]+TS1_Data+TS2_Data
    
    #Write to CSV
    print(TS_Data)
    