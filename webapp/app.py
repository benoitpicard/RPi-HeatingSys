from flask import Flask
import pandas as pd
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
file_valveCmd="../../RPi-HeatingSys-Data/valveCmd.csv"
read_valveCmd=pd.read_csv(file_valveCmd)
valveName=['V1U','V2M','V3G','V4E']
outStr=str('[%.19s] ' % pd.to_datetime('today'))
for iP in range(4):
	#Get Relay Status
	pinNo=RelayPinNo[iP]
	valveCmd=read_valveCmd.loc[0,valveName[iP]]
	outStr=outStr+valveName[iP]+ '_' + valveCmd
    return outStr

@app.route('/test')
def index():
    return 'test1'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')