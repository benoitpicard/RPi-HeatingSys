# Import main modules
from flask import Flask, render_template
import pandas as pd
import numpy as np
from datetime import date, timedelta

# Import code functions
from utilitiesHSC import tryReadCSV
from utilitiesHSC import tryReadCSV_p
from utilitiesHSC import genFigHHMM

# Web server application 
app = Flask(__name__)

# Initialisation
file_tempSensor="/home/pi/RPi-HeatingSys-Data/dataTempSensor.csv"
file_tempSetpoint="/home/pi/RPi-HeatingSys-Data/tempSetpoint.csv"
file_valveCmd="/home/pi/RPi-HeatingSys-Data/valveCmd.csv"
nowDateTime=pd.to_datetime('today')
fileDay=nowDateTime.strftime('%Y%m%d')
file_controlSys='/home/pi/RPi-HeatingSys-Data/DATA/'+fileDay+'_HSC_Data.csv'
file_figLocation='./static/'

@app.route('/')
def index():

    # Get latest data:
    nowDateTime=pd.to_datetime('today')
    fileDay=nowDateTime.strftime('%Y%m%d')
    file_controlSys='/home/pi/RPi-HeatingSys-Data/DATA/'+fileDay+'_HSC_Data.csv'
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
    file_controlSys='/home/pi/RPi-HeatingSys-Data/DATA/'+fileDay+'_HSC_Data.csv'
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
    file_controlSys='/home/pi/RPi-HeatingSys-Data/DATA/'+fileDay+'_HSC_Data.csv'
    read_controlSys,errorActive=tryReadCSV_p(file_controlSys,'',pd,5,'DateTime')
    read_controlSys['TW_dT (C)']=read_controlSys['TW_IN (C)']-read_controlSys['TW_OUT (C)']
    read_controlSys['TW_dTon (C)']=read_controlSys['TW_dT (C)']
    read_controlSys.loc[(read_controlSys['V1U']==0) &
                        (read_controlSys['V2M']==0) & 
                        (read_controlSys['V3G']==0),'TW_dTon (C)']=np.nan
                        
    xList=['DateTime','DateTime','DateTime']
    yLists=[[['TA_M (C)','TF_M (C)','TA_M_TG (C)'],['V2M']], 
            [['TA_U (C)','TF_U (C)','TA_U_TG (C)'],['V1U']],
            [['TA_G (C)','TF_G (C)','TA_G_TG (C)'],['V3G']],
            [['TW_IN (C)','TW_OUT (C)'],['TW_dT (C)','TW_dTon (C)']]]
    figPath=genFigHHMM(read_controlSys,xList,yLists,'','',file_figLocation)
   
    timeStr=nowDateTime.strftime('%H:%M:%S')
    return render_template('data.html',imgs=figPath,currentTime=timeStr)

@app.route('/dataYesterday')
def data_ys():

    # Get latest data:
    nowDateTime=pd.to_datetime('today')-timedelta(days=1)
    fileDay=nowDateTime.strftime('%Y%m%d')
    file_controlSys='/home/pi/RPi-HeatingSys-Data/DATA/'+fileDay+'_HSC_Data.csv'
    read_controlSys,errorActive=tryReadCSV_p(file_controlSys,'',pd,5,'DateTime')
    read_controlSys['TW_dT (C)']=read_controlSys['TW_IN (C)']-read_controlSys['TW_OUT (C)']
    read_controlSys['TW_dTon (C)']=read_controlSys['TW_dT (C)']
    read_controlSys.loc[(read_controlSys['V1U']==0) &
                        (read_controlSys['V2M']==0) & 
                        (read_controlSys['V3G']==0),'TW_dTon (C)']=np.nan
                        
    xList=['DateTime','DateTime','DateTime']
    yLists=[[['TA_M (C)','TF_M (C)','TA_M_TG (C)'],['V2M']], 
            [['TA_U (C)','TF_U (C)','TA_U_TG (C)'],['V1U']],
            [['TA_G (C)','TF_G (C)','TA_G_TG (C)'],['V3G']],
            [['TW_IN (C)','TW_OUT (C)'],['TW_dT (C)','TW_dTon (C)']]]
    figPath=genFigHHMM(read_controlSys,xList,yLists,'','',file_figLocation)
   
    timeStr=nowDateTime.strftime('%H:%M:%S')
    return render_template('data.html',imgs=figPath,currentTime=timeStr)

@app.route('/test')
def test():
    return render_template('t2.html')

@app.route('/<name>')
def blank(name):

    return render_template('blank.html',name=name)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', use_reloader=False)