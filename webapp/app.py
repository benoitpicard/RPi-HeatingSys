from flask import Flask
import pandas as pd
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
    #valveCmd status
    outStr=''
	file_valveCmd="../../RPi-HeatingSys-Data/valveCmd.csv"
	read_valveCmd=pd.read_csv(file_valveCmd)
	valveName=['V1U','V2M','V3G','V4E']
	outStr=outStr+str('[%.19s] => current time' % ,pd.to_datetime('today'))
    outStr=outStr+str('\n[%.19s] ' % read_valveCmd['DateTime'].loc[0])
	for iP in range(4):
		#Get Relay Status
		valveCmd=read_valveCmd.loc[0,valveName[iP]]
		outStr=outStr+valveName[iP]+ '=' + str(valveCmd) + '  '
	outStr=outStr+'=> valveCmd.csv'
    
    #controlSys status
    nowDateTime=pd.to_datetime('today')
    fileDay=nowDateTime.strftime('%Y%m%d')
    file_controlSys='../RPi-HeatingSys-Data/DATA/'+fileDay+'_HSC_Data.csv'
    read_controlSys=pd.read_csv(file_controlSys)
    controlSysCount=len(read_controlSys.index)
    currentData=read_controlSys.loc[controlSysCount-1,:]
    outStr=outStr+'\n'+currentData.to_string()
	return outStr

@app.route('/data')
def data():

    return 'data test1'

@app.route('/today')
def today():
    nowDateTime=pd.to_datetime('today')
    file_controlSys='../RPi-HeatingSys-Data/DATA/'+fileDay+'_HSC_Data.csv'
    fileDay=nowDateTime.strftime('%Y%m%d')
    return 'data test1'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')