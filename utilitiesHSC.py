import os, sys, traceback, time
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Extract Temperature setpoint from pandas structure dataframe
def getSetpointTemp(dfSetpoint,Zone,nowDateTime,typeDayRef,pd):
    # --- Get previous setpoint based on given time ---
    # ---   (returns the last time that has past)
    # Slice Setpoint DataFrame by Week/End and Zone
    DayRef=typeDayRef[nowDateTime.weekday()]
    dfSS=dfSetpoint[(dfSetpoint['Day']==DayRef) &
        (dfSetpoint['Zone']==Zone)].copy()
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
def tryReadCSV(file_name,index,pd,attemptCount=5,parseCol=''):
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

# Read CSV with pandas with try/except loop, with parsing  
def tryReadCSV_p(file_name,index,pd,attemptCount=5,parseCol=''):
    for attempt in range(attemptCount):
        try:
            #read csv with pandas and replace index with date
            if parseCol!='':
                readCSV=pd.read_csv(file_name,parse_dates=[parseCol])
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
    
# Generate fig
def genFigHHMM(df,xList,yLists,xLabel,yLabels):
    # Sizing def
    SMALL_SIZE = 12
    MEDIUM_SIZE = 14
    BIGGER_SIZE = 16
    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
    figInfo=[]
    for iFig in range(len(yLists)):
        subPlotCnt=len(yLists[iFig])
        fig, axs = plt.subplots(subPlotCnt,1,figsize=(8,10)) #figsize 12,8 makes it 1200x800 pixels
        myFmt = mdates.DateFormatter('%H:%M')
        for iSP in range(subPlotCnt):
            df.plot(x=xList[iFig], y=yLists[iFig][iSP], ax=axs[iSP], legend=True)
            axs[iSP].xaxis.set_major_formatter(myFmt)
        axs[0].set_xlabel('')
        axs[1].set_xlabel('Time of day')
        axs[0].set_ylabel('Temperature (C)')
        axs[1].set_ylabel('On/Off (1/0)')
        fig.tight_layout()
        figInfo.append(fig)
    return figInfo