# Import main modules
from flask import Flask, render_template, jsonify
import pandas as pd
import numpy as np
import json

# Import code functions
from utilitiesHSC import tryReadCSV
from utilitiesHSC import tryReadCSV_p
from utilitiesHSC import genFigHHMM

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


@app.route('/data')
def data():

    # Get latest data:
    nowDateTime=pd.to_datetime('today')
    fileDay=nowDateTime.strftime('%Y%m%d')
    file_controlSys='../RPi-HeatingSys-Data/DATA/'+fileDay+'_HSC_Data.csv'
    read_controlSys,errorActive=tryReadCSV_p(file_controlSys,'',pd,5,'DateTime')
    read_controlSys['TW_dT (C)']=read_controlSys['TW_IN (C)']-read_controlSys['TW_OUT (C)']
    read_controlSys['TW_dTon (C)']=read_controlSys['TW_dT (C)']
    read_controlSys.loc[(read_controlSys['V1U']==0) &
                        (read_controlSys['V2M']==0) & 
                        (read_controlSys['V3G']==0),'TW_dTon (C)']=np.nan
                        
    xList=['DateTime','DateTime','DateTime']
    yLists=[[['TA_M (C)','TF_M (C)','TA_M_TG (C)'],['V2M']], 
            [['TA_U (C)','TF_U (C)','TA_U_TG (C)'],['V1U']],
            [['TW_IN (C)','TW_OUT (C)'],['TW_dT (C)','TW_dTon (C)']]]
    figPath=genFigHHMM(read_controlSys,xList,yLists,'','','./static/')
   
    timeStr=nowDateTime.strftime('%H:%M:%S')
    return render_template('data.html',imgs=figPath,currentTime=timeStr)

    
@app.route('/control')
def control():
    return render_template('control.html')

@app.route('/ctrl_refresh', methods = ['POST'])
def ctrl_refresh():
    # Get latest data:
    nowDateTime=pd.to_datetime('today')
    fileDay=nowDateTime.strftime('%Y%m%d')
    file_controlSys='../RPi-HeatingSys-Data/DATA/'+fileDay+'_HSC_Data.csv'
    read_controlSys,errorActive=tryReadCSV(file_controlSys,'',pd)
    currentData=read_controlSys.iloc[-1]
    json_exp=currentData.to_json(orient="index")
        
    return json_exp

@app.route('/ajax', methods = ['POST'])
def ajax_request():

 
    file1 = open(r"aaatest1.txt","a+") 
    file1.write('\najax sent:\n')
    file1.write(str(request.data))
    
    data = json.loads(request.data)
    file1.write('\n'+y['scname'])
    file1.write('\n'+y['secret'])
    file1.close() 

    return '1'

    
@app.route('/<name>')
def blank(name):

    return render_template('blank.html',name=name)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', use_reloader=False)