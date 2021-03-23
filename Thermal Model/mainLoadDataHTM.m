% Rear temperature data and thermal modeling
% Home data

% Author: Benoit Picard

clear variables
% close all
home

%% Change warnings
warning('OFF', 'MATLAB:table:ModifiedAndSavedVarnames')

%% Start Up
home;
disp('-------------------')
disp('HomeThermalModel: Data Loading & Averaging')
launchScript = clock;
lastTime = launchScript;
c2s=[0  0   24*60*60   60*60  60  1];
tic
fprintf('Date: %2d/%2d/%4d   Time: %02d:%02d:%02.0f\n', launchScript(2),launchScript(3),launchScript(1),launchScript(4),launchScript(5),floor(launchScript(6)))
disp(' ')


%% Loading data 

% Inputs files info
filepath='C:\Users\picb2501\OneDrive\Projects\RasberryPi\RPi-HeatingSys-Data\DATA';
dateStart=datetime('2020-11-30');
dateEnd=datetime('2021-03-19');

% Loop through each files
for iD=1:days(dateEnd-dateStart)
    
    %Gen filename
    filename=[datestr(dateStart+days(iD-1),'yyyymmdd'),'_HSC_Data.csv'];
    
    %Read data, in data and convert to structure
    t=readtable(fullfile(filepath,filename));
    s=table2struct(t);
    
    %Fix date entry
    for iL=1:numel(s)
        s(iL).DateTime=datetime(s(iL).DateTime(1:19),'InputFormat','yyyy-MM-dd HH:mm:ss');
    end
    
    %Concatenate with previous data
    if iD==1
        data=s;
    else
        data=[data;s];
    end

end

fprintf('    File loaded (%.0f)\n',days(dateEnd-dateStart))

%% Aeraging specified channels

% Setup channels to keep and averaging window
cList={'DateTime';
    'TA_U_C_';
    'TF_U_C_';
    'TA_M_C_';
    'TF_M_C_';
    'V1U';
    'V2M';
    'WT_TIME';
    'WT_OUT_C_';
    'WT_SOLARRAD_W_m_2_';
    'WT_WIND_m_s_'
    };
meanTime=minutes(2);
avgWin=10; %data points
avgWinTime=meanTime*avgWin;

avgCount=floor(numel(data)/avgWin);
avgData=struct;

% Generate averaged datapoints
for iA=1:avgCount
    
    %data Index: LB Low Bound, HB, High bound
    dILB=(iA-1)*10+1;
    dIHB=iA*10;
    
    % Averaging Loop
    for iC=1:numel(cList)
        avgData(iA).(cList{iC})=mean([data(dILB:dIHB).(cList{iC})]);
    end
    
    % Valid flag
    avgData(iA).validTime=abs(mean(diff([data(dILB:dIHB).DateTime]))-minutes(2))< ...
        minutes(0.1);
    avgData(iA).validFlag=avgData(iA).validTime==1;
end

fprintf('    Data averaged (%.0f)\n',avgCount)


%% SaveData

savepath='C:\Users\picb2501\OneDrive\Projects\RasberryPi\RPi-HeatingSys-Data\MODELING DATA';
savefile='20210320_compiled_data';

savevars={
    'avgData'
    'dateStart'
    'dateEnd'
    };
save(fullfile(savepath,savefile),savevars{:})

fprintf('    Data saved (%s)\n',savefile)

%% End

disp(' ')
endScript = clock;
fprintf('Date: %d/%d/%d   Time: %02d:%02d:%02.0f\n', endScript(2),endScript(3),endScript(1),endScript(4),endScript(5),floor(endScript(6)))
tElapsed=sum((endScript-launchScript).*c2s);
fprintf('Time Elapsed: %2.1fs\n',tElapsed)
disp('End')
disp('-------------------')
