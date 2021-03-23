% Load thermal averaged data and generate Neural Net model
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
disp('HomeThermalModel: Prepare inputs and NN model')
launchScript = clock;
lastTime = launchScript;
c2s=[0  0   24*60*60   60*60  60  1];
tic
fprintf('Date: %2d/%2d/%4d   Time: %02d:%02d:%02.0f\n', launchScript(2),launchScript(3),launchScript(1),launchScript(4),launchScript(5),floor(launchScript(6)))
disp(' ')


%% Loading data 

% Inputs files info
filepath='C:\Users\picb2501\OneDrive\Projects\RasberryPi\RPi-HeatingSys-Data\MODELING DATA';
filename='20210320_compiled_data.mat';

load(fullfile(filepath,filename))
dataCount=numel(avgData);

fprintf('    File loaded (%.0f lines)\n',dataCount)

%% Prepare input & output arrays

% INIT
VALIDIN=false(dataCount,1);
VALIDOUT=false(dataCount,1);
TimeShiftErrorBand=minutes(2);
ForecastErrorBand=hours(2);
DataTime=[avgData.DateTime]';

% INPUTS:
InputVarWTM={ %with time shift
    'TA_U_C_'
    'TF_U_C_'
    'TA_M_C_'
    'TF_M_C_'
    'V1U'
    'V2M'
    };
TimeShiftIn=[hours(0) hours(-1) hours(-2)];
TimeShiftName={'0h','1h','2h'};
InputVarNoTM={ %without time shift
    'WT_OUT_C_'
    'WT_SOLARRAD_W_m_2_'
    'WT_WIND_m_s_'
    };
%   
SizeWTM=numel(InputVarWTM)*numel(TimeShiftIn);
InCount=SizeWTM+numel(InputVarNoTM);
INPUT=nan(dataCount,InCount);
inNames=cell(InCount,1);

for iD=1:dataCount
    for iTS=1:numel(TimeShiftIn)
        
        % With Time Shift
        timeError=DataTime-(avgData(iD).DateTime+TimeShiftIn(iTS));
        indexInput=find(abs(timeError)<TimeShiftErrorBand);

        if ~isempty(indexInput)
            VALIDIN(iD)=true;
            for iIV=1:numel(InputVarWTM)
                INPUT(iD,(iTS-1)*numel(InputVarWTM)+iIV)= ...
                    avgData(indexInput).(InputVarWTM{iIV});
                %naming
                if isempty(inNames{(iTS-1)*numel(InputVarWTM)+iIV})
                    inNames{(iTS-1)*numel(InputVarWTM)+iIV}= ...
                        [InputVarWTM{iIV},TimeShiftName{iTS}];
                end
            end
        else
            VALIDIN(iD)=false;
        end
        
        % No time shift
        for iIV=1:numel(InputVarNoTM)
            INPUT(iD,SizeWTM+iIV)= ...
                avgData(iD).(InputVarNoTM{iIV});
            %naming
            if isempty(inNames{SizeWTM+iIV})
                inNames{SizeWTM+iIV}=InputVarNoTM{iIV};
            end
        end
        
        % Validation for temperature forecast valid date
        if abs(avgData(iD).DateTime-avgData(iD).WT_TIME)>ForecastErrorBand
            VALIDIN(iD)=false;
        end
        % Need all numerical values is array (no nans)
        if any(isnan(INPUT(iD,:)))
            VALIDIN(iD)=false;
        end
    end
end
fprintf('    Inputs generated (%.0f inputs)\n',InCount)


% OUTPUTS - INSIDE TEMPERATURE (4 LOCATIONS) IN 2 HOURS:
OutCount=4;
OUTPUT=nan(dataCount,OutCount);
TimeShiftOut=hours(2);
for iD=1:dataCount
    timeError=DataTime-(avgData(iD).DateTime+TimeShiftOut);
    indexOutput=find(abs(timeError)<TimeShiftErrorBand);
    if ~isempty(indexOutput)
        VALIDOUT(iD)=true;
        OUTPUT(iD,1)=avgData(indexOutput).TA_U_C_;
        OUTPUT(iD,2)=avgData(indexOutput).TF_U_C_;
        OUTPUT(iD,3)=avgData(indexOutput).TA_M_C_;
        OUTPUT(iD,4)=avgData(indexOutput).TF_M_C_;
    end
end
fprintf('    Outputs generated (%.0f outputs)\n',OutCount)

% VALIDATION
VALID=VALIDIN & VALIDOUT;

%% Generate & Save Neural Net
nodes=[10];
inData=INPUT(VALID,:)';
outData=OUTPUT(VALID,:)';
outNames={'TA_U','TF_U','TA_M','TF_M'};
fig=1;
trainInfo=struct;
trainInfo.trainFcn = 'trainlm'; %default: 'trainlm', usually best: 'trainbr'
trainInfo.epochs = 400; %default: 1000
save2funcFolder='C:\Users\picb2501\OneDrive\Projects\RasberryPi\RPi-HeatingSys-Data\MODELING DATA\NN';

% [func,nnet,ntr,rmse]=createNN_v1(nodes,inData,outData,outNames,fig, ...
%     trainInfo,save2funcFolder);

func=cell(4,1);
nnet=cell(4,1);
ntr=cell(4,1);
rmse=cell(4,1);
for iOC=1:OutCount
    [func{iOC},nnet{iOC},ntr{iOC},rmse{iOC}]= ...
        createNN_v1(nodes,inData,outData(iOC,:),outNames{iOC},fig, ...
        trainInfo,save2funcFolder);
end 
%Eval model
for iOC=1:OutCount
    outModel.(outNames{iOC})=func{iOC}(inData)';
    outDataS.(outNames{iOC})=outData(iOC,:)';
end 
for iIC=1:InCount
    inDataS.(inNames{iIC})=inData(iIC,:)';
end
outModel.DateTime=DataTime(VALID,:);

fprintf('    Metamodel generated (%.0f models)\n',OutCount)



savepath='C:\Users\picb2501\OneDrive\Projects\RasberryPi\RPi-HeatingSys-Data\MODELING DATA';
% savefile='20210320_modelV3_2L_20_10';
savefile='20210320_modelV1B_1L_10';

savevars={
    'func'
    'rmse'
    'inDataS'
    'outModel'
    'outDataS'
    };
save(fullfile(savepath,savefile),savevars{:})

fprintf('    Data saved\n')


%% End

disp(' ')
endScript = clock;
fprintf('Date: %d/%d/%d   Time: %02d:%02d:%02.0f\n', endScript(2),endScript(3),endScript(1),endScript(4),endScript(5),floor(endScript(6)))
tElapsed=sum((endScript-launchScript).*c2s);
fprintf('Time Elapsed: %2.1fs\n',tElapsed)
disp('End')
disp('-------------------')
