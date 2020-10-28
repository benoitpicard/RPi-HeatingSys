import RPi.GPIO as GPIO
import time
from w1thermsensor import W1ThermSensor
import numpy as np
import pandas as pd

# RELAY SETUP
GPIO.setmode(GPIO.BOARD)
# Relay1: GPIO5 PIN29
GPIO.setup(29,GPIO.OUT)
GPIO.output(29,GPIO.HIGH)
# Relay2: GPIO6 PIN31
GPIO.setup(31,GPIO.OUT)
GPIO.output(31,GPIO.HIGH)
# Relay3: GPI13 PIN33
GPIO.setup(33,GPIO.OUT)
GPIO.output(33,GPIO.HIGH)
# Relay4: GPI19 PIN35
GPIO.setup(35,GPIO.OUT)
GPIO.output(35,GPIO.HIGH)


# TEMP DS18B20 SETUP
sensor1 = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "01144bf1efaa")
sensor2 = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "01145167b9aa")
sensor3 = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "000005675be3")
sensor4 = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "01144b8b70aa")
sensor5 = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "0114515ff8aa")
sensor6 = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "0114515740aa")

# Saving data to file
csvPath='DATA/20201026_REC.csv'
csvHeader=True
csvMode='w'
data_txt=['date','t1','t2','t3','t4','t5','t6']

try:
    while True:
        data=[]
        for iR in range(10):

            print("Running measurement %d:" % (iR+1))
            t1 = sensor1.get_temperature()
            t2 = sensor2.get_temperature()
            t3 = sensor3.get_temperature()
            t4 = sensor4.get_temperature()
            t5 = sensor5.get_temperature()
            t6 = sensor6.get_temperature()
            data.append([pd.to_datetime('today'),t1,t2,t3,t4,t5,t6])
                
            print("All temperature measurement completed")
            print("%d %d %d %d %d %d" % (t1,t2,t3,t4,t5,t6))

            if t1>27:
                GPIO.output(29,GPIO.LOW)
            else:
                GPIO.output(29,GPIO.HIGH)

            if t2>27:
                GPIO.output(31,GPIO.LOW)
            else:
                GPIO.output(31,GPIO.HIGH)

            if t3>27:
                GPIO.output(33,GPIO.LOW)
            else:
                GPIO.output(33,GPIO.HIGH)

            if t6>27:
                GPIO.output(35,GPIO.LOW)
            else:
                GPIO.output(35,GPIO.HIGH)

            print("ALL GOOD, wait 2s")
            time.sleep(2)

        print("Saving data to %s" % csvPath)
        df=(pd.DataFrame(data,columns=data_txt)).set_index('date')
        df.to_csv(csvPath,mode=csvMode,header=csvHeader)
        csvMode='a'
        csvHeader=False
            
except KeyboardInterrupt:
    print("Quit: Cleanup")
    GPIO.cleanup()
