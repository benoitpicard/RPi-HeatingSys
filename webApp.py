# Import main modules
from flask import Flask, render_template
import pandas as pd
import numpy as np

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
    figObj=genFigHHMM(read_controlSys,xList,yLists,'','')
    filePath='./static/'
    figPath=[]
    for iFO in range(len(figObj)):
        figPath.append(filePath+'plot'+str(iFO+1)+'.jpg')
        figObj[iFO].savefig(figPath[iFO]) #to save to local folder 
    
    timeStr=nowDateTime.strftime('%H:%M:%S')
    return render_template('data.html',imgs=figPath,currentTime=timeStr)

@app.route('/<name>')
def blank(name):

    return render_template('blank.html',name=name)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', use_reloader=False)