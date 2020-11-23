# Import main modules
from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# Import main modules
import time
import numpy as np
import pandas as pd
import os, sys, traceback

# Import code functions
from utilitiesHSC import tryReadCSV

# Web server application 
app = Flask(__name__)

# Initialisation
file_tempSensor="../RPi-HeatingSys-Data/dataTempSensor.csv"
file_tempSetpoint="../RPi-HeatingSys-Data/tempSetpoint.csv"
file_valveCmd="../RPi-HeatingSys-Data/valveCmd.csv"
nowDateTime=pd.to_datetime('today')
fileDay=nowDateTime.strftime('%Y%m%d')
file_controlSys='../RPi-HeatingSys-Data/DATA/'+fileDay+'_HSC_Data.csv'

@app.route('/')
def index():

    # Get latest data:
    nowDateTime=pd.to_datetime('today')
    fileDay=nowDateTime.strftime('%Y%m%d')
    file_controlSys='../RPi-HeatingSys-Data/DATA/'+fileDay+'_HSC_Data.csv'
    read_controlSys,errorActive=tryReadCSV(file_controlSys,'',pd)
    if errorActive:
        currentData=pd.DataFrame({'ERROR' : []}) #blank dataframe
    else:
        controlSysCount=len(read_controlSys.index)
        currentData=read_controlSys[max(0,controlSysCount-3):controlSysCount].copy()
        currentData['DateTime']=currentData['DateTime'].str.slice(0, 19)
    
    # Output to table
    timeStr=nowDateTime.strftime('%H:%M:%S')
    currentData_HTML=currentData.transpose().to_html(border=1,index=True,header=False,classes='w3-table w3-striped w3-border')
    return render_template('home.html',tableHTML_1=currentData_HTML,currentTime=timeStr)
    
@app.route('/home')
def home():

    # Get latest data:
    nowDateTime=pd.to_datetime('today')
    fileDay=nowDateTime.strftime('%Y%m%d')
    file_controlSys='../RPi-HeatingSys-Data/DATA/'+fileDay+'_HSC_Data.csv'
    read_controlSys,errorActive=tryReadCSV(file_controlSys,'',pd)
    if errorActive:
        currentData=pd.DataFrame({'ERROR' : []}) #blank dataframe
    else:
        controlSysCount=len(read_controlSys.index)
        currentData=read_controlSys[max(0,controlSysCount-3):controlSysCount].copy()
        currentData['DateTime']=currentData['DateTime'].str.slice(0, 19)
    
    # Output to table
    timeStr=nowDateTime.strftime('%H:%M:%S')
    currentData_HTML=currentData.transpose().to_html(border=1,index=True,header=False,classes='w3-table w3-striped w3-border')
    return render_template('home.html',tableHTML_1=currentData_HTML,currentTime=timeStr)


@app.route('/<name>')
def blank(name):

    return render_template('blank.html',name=name)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', use_reloader=False)