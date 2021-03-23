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
rawdatafilename='20210320_compiled_data.mat';

% modelfilename='20210320_modelV1_1L_30.mat';
modelfilename='20210320_modelV1B_1L_10.mat';

load(fullfile(filepath,modelfilename))
fprintf('    File loaded (%s)\n',modelfilename)
% load(fullfile(filepath,rawdatafilename))
% fprintf('    File loaded (%s)\n',rawdatafilename)




%% Select data to evaluate

% manually edit
dateStart=datetime('2020-11-30');
dateEnd=datetime('2021-03-19');

daysPlot=10;

daysData=days(dateEnd-dateStart);
dayOffset=rand(daysPlot,1);
% dayOffset=linspace(0,1,daysPlot);

%% Plot

for iD=1:daysPlot
    
    % Day filter
    datePlot=dateStart+floor(dayOffset(iD)*daysData);
    tlower=datePlot;
    tupper=datePlot+days(1);
    dateFilter=isbetween(outModel.DateTime,tlower,tupper);
    
    figure('Name',datestr(datePlot,'yyyy-mm-dd'), ...
        'NumberTitle','off', ...
        'OuterPosition',[20 40 800 800], ...
        'Color','w');
    outNames={'TA_M','TF_M','TA_U','TF_U'};
    
    for iSP=1:numel(outNames)
        subplot(2,2,iSP)
        hold on
        plot(outModel.DateTime(dateFilter),inDataS.([outNames{iSP},'_C_0h'])(dateFilter),'DisplayName',[outNames{iSP},'_0h'])
        plot(outModel.DateTime(dateFilter),inDataS.([outNames{iSP},'_C_1h'])(dateFilter),'DisplayName',[outNames{iSP},'_1h'])
        plot(outModel.DateTime(dateFilter),inDataS.([outNames{iSP},'_C_2h'])(dateFilter),'DisplayName',[outNames{iSP},'_2h'])
        plot(outModel.DateTime(dateFilter),outDataS.(outNames{iSP})(dateFilter),'DisplayName',[outNames{iSP},'_raw'])
        plot(outModel.DateTime(dateFilter),outModel.(outNames{iSP})(dateFilter),'DisplayName',[outNames{iSP},'_NN'])
        box on
        grid on
        l=legend('Location','Northeast');
        set(l,'interpreter','none')
        ylabel('Temperature (C)')
    end
end

%% End

disp(' ')
endScript = clock;
fprintf('Date: %d/%d/%d   Time: %02d:%02d:%02.0f\n', endScript(2),endScript(3),endScript(1),endScript(4),endScript(5),floor(endScript(6)))
tElapsed=sum((endScript-launchScript).*c2s);
fprintf('Time Elapsed: %2.1fs\n',tElapsed)
disp('End')
disp('-------------------')
