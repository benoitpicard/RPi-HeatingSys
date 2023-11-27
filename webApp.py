# Import main modules
from flask import Flask, render_template, request
import json
import pandas as pd
import numpy as np
from datetime import date, timedelta


# Import code functions
from utilitiesHSC import tryReadCSV
from utilitiesHSC import tryReadCSV_p
from utilitiesHSC import genFigHHMM

# Web server application 
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 10

# Initialisation
file_tempSensor="/home/pi/RPi-HeatingSys-Data/dataTempSensor.csv"
file_tempSetpoint="/home/pi/RPi-HeatingSys-Data/tempSetpoint.csv"
file_modeSelect="/home/pi/RPi-HeatingSys-Data/tempSetpointModeSelect.csv"
file_valveCmd="/home/pi/RPi-HeatingSys-Data/valveCmd.csv"
nowDateTime=pd.to_datetime('today')
fileDay=nowDateTime.strftime('%Y%m%d')
file_controlSys='/home/pi/RPi-HeatingSys-Data/DATA/'+fileDay+'_HSC_Data.csv'
file_figLocation='./static/'

# JSON Encoder
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

@app.route('/')
def index():
    
    # HTML PAGE ROUTE => HOME
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

    # HTML PAGE ROUTE => HOME
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

@app.route('/graph')
def graph():

    # HTML PAGE ROUTE => GRAPH - will be calling /graphdata for client based graphs
    timeStr=nowDateTime.strftime('%H:%M:%S')
    return render_template('graph.html',currentTime=timeStr)
    
@app.route('/graphdata')
def get_data():

    # DATA ROUTE => USED BY HTML PAGE
    # Get latest data:
    nowDateTime=pd.to_datetime('today')
    fileDay=nowDateTime.strftime('%Y%m%d')
    
    file_controlSys='/home/pi/RPi-HeatingSys-Data/DATA/'+fileDay+'_HSC_Data.csv'
    read_controlSys,errorActive=tryReadCSV_p(file_controlSys,'',pd,5,'DateTime')
    
    # Add dT calcs
    read_controlSys['TW_dT (C)']=read_controlSys['TW_IN (C)']-read_controlSys['TW_OUT (C)']
    read_controlSys['TW_dTon (C)']=read_controlSys['TW_dT (C)']
    read_controlSys.loc[(read_controlSys['V1U']==0) &
                        (read_controlSys['V2M']==0) & 
                        (read_controlSys['V3G']==0),'TW_dTon (C)']=np.nan
  
    
    # Add Unit TimeStamp
    read_controlSys['unix_timestamp'] =read_controlSys['DateTime'].astype(np.int64) // 10**6
    
    # Column to extract:
    columns = ['TA_M (C)', 'TF_M (C)', 'TA_M_TG (C)', 'V2M', 'TA_U (C)', 'TF_U (C)', 'TA_U_TG (C)', 'V1U','TA_G (C)', 'TF_G (C)', 'TA_G_TG (C)', 'V3G','TA_OUT (C)','WT_OUT (C)','TW_IN (C)','TW_OUT (C)','TW_dT (C)','TW_dTon (C)']
    dataset = []
    for column in columns:
        outData=read_controlSys[["unix_timestamp",column]].to_json(orient='values')
        dataset.append({'label': column, 'data': json.loads(outData)})

    return json.dumps(dataset)

@app.route('/graphYS')
def graphYS():

    # HTML PAGE ROUTE => GRAPH - will be calling /graphdata for client based graphs
    timeStr=nowDateTime.strftime('%H:%M:%S')
    return render_template('graphYS.html')
    
@app.route('/graphdataYS')
def get_dataYS():

    # DATA ROUTE => USED BY HTML PAGE
    # Get latest data:
    nowDateTime=pd.to_datetime('today')+ timedelta(days=-1)
    fileDay=nowDateTime.strftime('%Y%m%d') 
    
    file_controlSys='/home/pi/RPi-HeatingSys-Data/DATA/'+fileDay+'_HSC_Data.csv'
    read_controlSys,errorActive=tryReadCSV_p(file_controlSys,'',pd,5,'DateTime')
    
    # Add dT calcs
    read_controlSys['TW_dT (C)']=read_controlSys['TW_IN (C)']-read_controlSys['TW_OUT (C)']
    read_controlSys['TW_dTon (C)']=read_controlSys['TW_dT (C)']
    read_controlSys.loc[(read_controlSys['V1U']==0) &
                        (read_controlSys['V2M']==0) & 
                        (read_controlSys['V3G']==0),'TW_dTon (C)']=np.nan
  
    
    # Add Unit TimeStamp
    read_controlSys['unix_timestamp'] =read_controlSys['DateTime'].astype(np.int64) // 10**6
    
    # Column to extract:
    columns = ['TA_M (C)', 'TF_M (C)', 'TA_M_TG (C)', 'V2M', 'TA_U (C)', 'TF_U (C)', 'TA_U_TG (C)', 'V1U','TA_G (C)', 'TF_G (C)', 'TA_G_TG (C)', 'V3G','TA_OUT (C)','WT_OUT (C)','TW_IN (C)','TW_OUT (C)','TW_dT (C)','TW_dTon (C)']
    dataset = []
    for column in columns:
        outData=read_controlSys[["unix_timestamp",column]].to_json(orient='values')
        dataset.append({'label': column, 'data': json.loads(outData)})

    return json.dumps(dataset)


# @app.route('/data')
# def data():
    
    # # HTML PAGE WITH SERVER SITE IMAGE GENERATION
    # # Get latest data:
    # nowDateTime=pd.to_datetime('today')
    # fileDay=nowDateTime.strftime('%Y%m%d')
    # file_controlSys='/home/pi/RPi-HeatingSys-Data/DATA/'+fileDay+'_HSC_Data.csv'
    # read_controlSys,errorActive=tryReadCSV_p(file_controlSys,'',pd,5,'DateTime')
    # read_controlSys['TW_dT (C)']=read_controlSys['TW_IN (C)']-read_controlSys['TW_OUT (C)']
    # read_controlSys['TW_dTon (C)']=read_controlSys['TW_dT (C)']
    # read_controlSys.loc[(read_controlSys['V1U']==0) &
                        # (read_controlSys['V2M']==0) & 
                        # (read_controlSys['V3G']==0),'TW_dTon (C)']=np.nan
                        
    # xList=['DateTime','DateTime','DateTime','DateTime','DateTime']
    # yLists=[[['TA_M (C)','TF_M (C)','TA_M_TG (C)'],['V2M']], 
            # [['TA_U (C)','TF_U (C)','TA_U_TG (C)'],['V1U']],
            # [['TA_G (C)','TF_G (C)','TA_G_TG (C)'],['V3G']],
            # [['TA_OUT (C)','WT_OUT (C)'],['V2M']],
            # [['TW_IN (C)','TW_OUT (C)'],['TW_dT (C)','TW_dTon (C)']]]
    # figPath=genFigHHMM(read_controlSys,xList,yLists,'','',file_figLocation)
   
    # timeStr=nowDateTime.strftime('%H:%M:%S')
    # return render_template('data.html',imgs=figPath,currentTime=timeStr)

# @app.route('/data_ys')
# def data_ys():

    # # HTML PAGE WITH SERVER SITE IMAGE GENERATION
    # # Get latest data:
    # nowDateTime=pd.to_datetime('today')+ timedelta(days=-1)
    # fileDay=nowDateTime.strftime('%Y%m%d')
    # file_controlSys='/home/pi/RPi-HeatingSys-Data/DATA/'+fileDay+'_HSC_Data.csv'
    # read_controlSys,errorActive=tryReadCSV_p(file_controlSys,'',pd,5,'DateTime')
    # read_controlSys['TW_dT (C)']=read_controlSys['TW_IN (C)']-read_controlSys['TW_OUT (C)']
    # read_controlSys['TW_dTon (C)']=read_controlSys['TW_dT (C)']
    # read_controlSys.loc[(read_controlSys['V1U']==0) &
                        # (read_controlSys['V2M']==0) & 
                        # (read_controlSys['V3G']==0),'TW_dTon (C)']=np.nan
                        
    # xList=['DateTime','DateTime','DateTime','DateTime']
    # yLists=[[['TA_M (C)','TF_M (C)','TA_M_TG (C)'],['V2M']], 
            # [['TA_U (C)','TF_U (C)','TA_U_TG (C)'],['V1U']],
            # [['TA_G (C)','TF_G (C)','TA_G_TG (C)'],['V3G']],
            # [['TW_IN (C)','TW_OUT (C)'],['TW_dT (C)','TW_dTon (C)']]]
    # figPath=genFigHHMM(read_controlSys,xList,yLists,'','',file_figLocation)
   
    # timeStr=nowDateTime.strftime('%H:%M:%S')
    # return render_template('data_ys.html',imgs=figPath,currentTime=timeStr)

# APP ROUTE FOR MODE SELECTION (REQUEST FROM URL ON HOMEBRIDGE
@app.route('/modeSelect')
def modeSelectUdateCSV():
    #Modify temperature control mode
    Mode=request.args.get('value')
    
    if Mode in ["Away", "Schedule"]:
        # Read CSV
        read_modeSelect,errorActive=tryReadCSV_p(file_modeSelect,'',pd,5,'DateTime')
        # Add away condition:
        nowDateTime=pd.to_datetime('today')
        #new_row = {'DateTime': nowDateTime, 'Mode': 'Away'}
        new_row = {'DateTime': nowDateTime, 'Mode': Mode}
        # Add a row
        read_modeSelect = read_modeSelect.append(new_row, ignore_index=True)
        # Write Mode Selection to CSV (append)
        read_modeSelect.tail(1).to_csv(file_modeSelect,mode='a',header=False,index=False)
    
    return Mode
    
app.route('/modeSelectState')
def modeSelectState():
    nowDateTime=pd.to_datetime('today')
    read_modeSelect,errorActive=tryReadCSV_p(file_modeSelect,'',pd,5,'DateTime')
    dfMT=(nowDateTime-read_modeSelect['DateTime'])>pd.to_timedelta(0) #compare DateTime with current time and return true if above 0
    if any(dfMT==True):
        Mode=read_modeSelect.iloc[(dfMT[dfMT==True].index.tolist()[-1])]['Mode'] # return Mode column of last true value
    else: #assume no entry or all future value
        Mode='Schedule'
    if Mode=='Schedule':
        State=1
    else:
        State=0
    
    return State
    
@app.route('/<id>/status')
def status_JSON(id):
    # Prepare JSON response. Format:
    #{
    #    "targetHeatingCoolingState": INT_VALUE,
    #    "targetTemperature": FLOAT_VALUE,
    #    "currentHeatingCoolingState": INT_VALUE,
    #    "currentTemperature": FLOAT_VALUE
    #}
    # Get latest data:
    nowDateTime=pd.to_datetime('today')
    fileDay=nowDateTime.strftime('%Y%m%d')
    file_controlSys='/home/pi/RPi-HeatingSys-Data/DATA/'+fileDay+'_HSC_Data.csv'
    read_controlSys,errorActive=tryReadCSV(file_controlSys,'',pd)
    data={ # return data from last entry in csv file
        "targetHeatingCoolingState": read_controlSys[id+'_MODE'].iloc[-1],
        "targetTemperature": read_controlSys[id+'_TG (C)'].iloc[-1],
        "currentHeatingCoolingState": read_controlSys[id+'_MODE'].iloc[-1],
        "currentTemperature": read_controlSys[id+' (C)'].iloc[-1]
    }
    return json.dumps(data, cls=NpEncoder)
    
@app.route('/<id>/targetHeatingCoolingState')
def controlModeUpdate(id):
    #Modify temperature control mode
    data=request.args.get('value')
    return data
    
@app.route('/<id>/targetTemperature')
def controlTempUpdate(id):
    #Modify temperature setpoint
    data = data=request.args.get('value')
    return data

@app.route('/test')
def test():
    return render_template('t2.html')

@app.route('/<name>')
def blank(name):

    return render_template('blank.html',name=name)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', use_reloader=False) 

# No cacheing at all for API endpoints.
@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store, max-age=10'
    return response