# Extract Temperature setpoint from pandas structure dataframe
def getSetpointTemp(dfSetpoint,Zone,nowDateTime,typeDayRef,pd):
    # --- Get previous setpoint based on given time ---
    # ---   (returns the last time that has past)
    # Slice Setpoint DataFrame by Week/End and Zone
    DayRef=typeDayRef[nowDateTime.weekday()]
    dfSS=dfSetpoint[(dfSetpoint['Day']==DayRef) &
        (dfSetpoint['Zone']==Zone)]
    # Convert to timedelta for easy comparison
    dfSS['Time']=pd.to_timedelta(dfSS['Time'])
    nowTimeD=pd.to_timedelta(nowDateTime-pd.Timestamp.normalize(nowDateTime))
    dfSL=dfSS[dfSS.Time<nowTimeD]
    # Find index of last valid setpoint
    lastIndexPS=len(dfSL.index)
    if lastIndexPS>0:
        indexPS=lastIndexPS-1
    else:
        indexPS=len(dfSS.index)-1
    # Return setpoint
    TA=dfSS.iloc[indexPS]['TA (C)']
    TF=dfSS.iloc[indexPS]['TF (C)']
    return TA, TF

# Read CSV with pandas with try/except loop
def tryReadCSV(file_name,index,pd):
    attemptCount=5
    for attempt in range(attemptCount):
        try:
            #read csv with pandas and replace index with date
            readCSV=pd.read_csv(file_name)
            if index!='':
                readCSV=readCSV.set_index(index)
            errorActive=False
            break
        except:
            #retry reading (sometime fails due to simulatneous read/write callback)
            print('[%.19s] %s: error reading file_tempSensor (attempt#%d)' % 
                (pd.to_datetime('today'),sys.argv[0],attempt))
            traceback.print_exc(file=sys.stdout)
            if attempt<attemptCount-1:
                print('   --- continuing ---')
            errorActive=True
            time.sleep(0.1)
    return readCSV, errorActive