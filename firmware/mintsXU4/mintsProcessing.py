# ***************************************************************************
#  mintsXU4
#   ---------------------------------
#   Written by: Lakitha Omal Harindha Wijeratne
#   - for -
#   Mints: Multi-scale Integrated Sensing and Simulation
#      & 
#   TRECIS: Texas Research and Education Cyberinfrastructure Services (TRECIS) NSF Award #2019135
#   The University of Texas at Dallas
# 
#   The authors acknowledge the Texas Research and Education Cyberinfrastructure Services 
#   (TRECIS) Center, # NSF Award #2019135, and The University of Texas at Dallas for 
#   providing {HPC, visualization, database, or grid} resources and support that have 
#   contributed to the research results reported within this project. 
#   URL: https://trecis.cyberinfrastructure.org/
#   ---------------------------------
#   Date: March 15, 2023
#   ---------------------------------
#   This module is written for generic implimentation of MINTS projects
#   --------------------------------------------------------------------------
#   https://github.com/mi3nts
#   http://utdmints.info/
#   
#   TRECIS URL: https://trecis.cyberinfrastructure.org/
#  ***************************************************************************

from numpy import float64
import serial
import datetime
import os
import csv

import deepdish as dd
#from airMarML import BME280
# from mintsXU4 import mintsLatest as mL
from mintsXU4 import mintsDefinitions as mD
from getmac import get_mac_address
import time
import serial
import pynmea2
from collections import OrderedDict
import netifaces as ni
import math
import pandas as pd
#import feather
import glob
from functools import reduce
from sklearn.linear_model import LinearRegression
#import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split



macAddress       = mD.macAddress
dataFolder       = mD.dataFolder
rawFolder        = mD.rawFolder
timeSpan         = mD.timeSpan
referenceFolder  = mD.referenceFolder
modelsPklsFolder     = mD.modelsPklsFolder
dataFolderMQTT          = mD.dataFolderMQTT
dataFolderMQTTReference = mD.dataFolderMQTTReference
latestOn       = mD.latestOn
mqttOn         = mD.mqttOn
mergedPklsFolder     = mD.mergedPklsFolder

def superReaderV2(nodeID,sensorID):
    if sensorID == "BME280":
        floatSum  = 3
        floatSum2 = -1         
    elif sensorID == "BME680":
        floatSum  = 4
        floatSum2 = -1         
    elif sensorID == "BME688CNR":
        floatSum  = 7
        floatSum2 = -1         
    elif sensorID == "GPGGALR":
        floatSum  = 6   
        floatSum2 = -1   
    elif sensorID == "GPGGAPL":
        floatSum  = 5   
        floatSum2 = -1          
    elif sensorID == "GPSGPGGA2":
        floatSum  = 9   
        floatSum2 = -1        
    elif sensorID == "SCD30":
        floatSum  = 3       
        floatSum2 = -1 
    elif sensorID == "WIMDA":
        floatSum  = 12   
        floatSum2 = 16
    elif sensorID == "YXXDR":
        floatSum  = 4  
        floatSum2 = -1                      
    else: 
        return []
    dataIn = sensorReaderV2(nodeID,sensorID,floatSum,floatSum2)
    if(len(dataIn))>0:
        dataIn = sensorReaderPost(dataIn,sensorID)
        return dataIn;
    return [];

def superReader(nodeID,sensorID):
    if sensorID == "BME280":
        floatSum = 3
    elif sensorID == "BME680":
        floatSum = 4
    elif sensorID == "GPGGALR":
        floatSum = 6   
    elif sensorID == "WIMDA":
        floatSum = 12       
    elif sensorID == "YXXDR":
        floatSum = 4             
    else: 
        return []
        
    dataIn = sensorReader(nodeID,sensorID,floatSum)
    if(len(dataIn))>0:
        dataIn = sensorReaderPost(dataIn,sensorID)
        return dataIn;
    return [];

def sensorDefinitions(sensorID):
    if sensorID == "WIMDA":
        return {'dateTime','airTemperature','barrometricPressureBars','relativeHumidity','dewPoint'}
    if sensorID == "BME280":
        return {'dateTime','Temperature','Pressure','Humidity'}
    if sensorID == "BME680":
        return {'dateTime','temperature','pressure','humidity'}  
    if sensorID == "BME688CNR":
        return {'dateTime','temperature','pressure','humidity'}            
    if sensorID == "GPGGALR":
        return {'dateTime','Latitude','Longitude'} 
    if sensorID == "GPGGAPL":
        return {'dateTime','latitudeCoordinate','longitudeCoordinate'}     
    if sensorID == "YXXDR":
        return {'dateTime','barrometricPressureBars'}                               
    return [];


def dropIndexDuplicates(dfIn):
    return dfIn[~dfIn.index.duplicated(keep='first')];



def gpsCropCoordinatesV2(mintsData,gpsSensor,latitude,longitude,latRange,longRange):

    if gpsSensor == "GPGGALR":
        mintsData = mintsData[mintsData.GPGGALR_Latitude>latitude-abs(latRange)]
        mintsData = mintsData[mintsData.GPGGALR_Latitude<latitude+abs(latRange)]
        mintsData = mintsData[mintsData.GPGGALR_Longitude>longitude-abs(longRange)]
        mintsData = mintsData[mintsData.GPGGALR_Longitude<longitude+abs(longRange)]
        mintsData = mintsData.drop(['GPGGALR_Latitude','GPGGALR_Longitude'], 1)
        return mintsData;

    if gpsSensor == "GPGGAPL":
        mintsData = mintsData[mintsData.GPGGAPL_latitudeCoordinate>latitude-abs(latRange)]
        mintsData = mintsData[mintsData.GPGGAPL_latitudeCoordinate<latitude+abs(latRange)]
        mintsData = mintsData[mintsData.GPGGAPL_longitudeCoordinate>longitude-abs(longRange)]
        mintsData = mintsData[mintsData.GPGGAPL_longitudeCoordinate<longitude+abs(longRange)]        
        mintsData = mintsData.drop(['GPGGAPL_latitudeCoordinate','GPGGAPL_longitudeCoordinate'], 1)
        return mintsData;
    
    return;

def gpsCropCoordinates(mintsData,latitude,longitude,latRange,longRange):
    mintsData = mintsData[mintsData.GPGGALR_Latitude>latitude-abs(latRange)]
    mintsData = mintsData[mintsData.GPGGALR_Latitude<latitude+abs(latRange)]
    mintsData = mintsData[mintsData.GPGGALR_Longitude>longitude-abs(longRange)]
    mintsData = mintsData[mintsData.GPGGALR_Longitude<longitude+abs(longRange)]
    mintsData.drop('GPGGALR_Latitude', 1)
    mintsData.drop('GPGGALR_Longitude', 1)
    return mintsData;
    

def merger(data_frames):
    print("Merging Data Frames")
    dataIn = []
    for data in data_frames:
        if len(data)>0:
            dataIn.append(data)
    return reduce(lambda  left,right: pd.merge(left,right,on=['dateTime'],
                                             how='inner'), dataIn)
def sensorReader(nodeID,sensorID,floatSum):
    print("Reading " + sensorID + " data from node " + nodeID )
    dataInPre = glob.glob(dataFolder+ "/*/*"+nodeID+"/*/*/*/*"+sensorID+ "*.csv")
    dataInPre.sort()
    dataIn = []

    for f in dataInPre:
        try:
            print("Reading " + f)
            dataFrame = pd.read_csv(f)
            #print(dataFrame.dtypes)
            floatSumNow = sum(dataFrame.dtypes == float64 )

            if(floatSum == floatSumNow):
                dataNow = pd.read_csv(f)
                dataNow['dateTime'] = pd.to_datetime(dataNow['dateTime'])

                dataNow  = dataNow[sensorDefinitions(sensorID)]
                dataNow =dataNow.set_index('dateTime').resample('60S').mean()
                dataIn.append(dataNow)
        except Exception as e:
            print("[ERROR] Could not publish data, error: {}".format(e))
    return pd.concat(dataIn)

def sensorReaderV2(nodeID,sensorID,floatSum1,floatSum2):
    print("Reading " + sensorID + " data from node " + nodeID )
    dataInPre = glob.glob(dataFolder+ "/*/*"+nodeID+"/*/*/*/*"+sensorID+ "*.csv")
    dataInPre.sort()
    dataIn = []

    for f in dataInPre:
        try:
            dataNow = pd.read_csv(f)
            floatSumNow = sum(dataNow.dtypes == float64 )
            print("Reading " + f+ ": floatSum ==> " + str(floatSumNow)) 

            if(floatSum1 == floatSumNow):
                dataNow['dateTime'] = pd.to_datetime(dataNow['dateTime'])
                dataNow = dataNow[sensorDefinitions(sensorID)]
                dataNow = dataNow.set_index('dateTime').resample(timeSpan).mean()
                dataIn.append(dataNow)            

        
            if(floatSum2 == floatSumNow):
                dataNow['dateTime'] = pd.to_datetime(dataNow['dateTime'])
                dataNow = dataNow[sensorDefinitions(sensorID)]
                dataNow = dataNow.set_index('dateTime').resample(timeSpan).mean()
                dataIn.append(dataNow)              

        except Exception as e:
            print ("Error and type: %s - %s." % (e,type(e)))

    return pd.concat(dataIn).dropna().sort_index();

def sensorReaderPost(dataIn,sensorID):
    #dataIn.index = pd.to_datetime(dataIn.dateTime)
    dataIn.columns = sensorID+"_" + dataIn.columns 
    print(dataIn)
    return dataIn;


def getPathGenericParent(dataFolder,sensorID,ext):
    writePath = dataFolder+"/"+"MINTS_"+sensorID+"." + ext
    directoryCheck(writePath)
    return writePath;

def getPathGeneric(dataFolder,nodeID,sensorID,ext):
    writePath = dataFolder+"/"+nodeID+"/"+"MINTS_"+ nodeID+ "_"+sensorID+"." + ext
    directoryCheck(writePath)
    return writePath;

def directoryCheck(outputPath):
    exists = os.path.isfile(outputPath)
    directoryIn = os.path.dirname(outputPath)
    # print(directoryIn)

    if not os.path.exists(directoryIn):
        print("Creating Directory @" + directoryIn)
        os.makedirs(directoryIn)
    return exists

def cropLimits(dataIn,variableIn,limitLow,limitHigh):
    dataIn = dataIn[dataIn[variableIn]<=limitHigh]
    dataIn = dataIn[dataIn[variableIn]>=limitLow]
    return dataIn


def writeCSV3(writePath,sensorDictionary):
    exists = directoryCheck(writePath)
    keys =  list(sensorDictionary.keys())
    with open(writePath, 'a') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=keys)
        if(not(exists)):
            # directoryCheck(writePath)
            writer.writeheader()
        writer.writerow(sensorDictionary)

def oobClimateCheck(mintsData,nodeID,climateSensor,dateNow,modelsPklsFolder,sensorDate):
    # Get rid of out of bounds data 
    if climateSensor == "BME688CNR":
        numAll    = len(mintsData)
        mintsData = cropLimits(mintsData,"BME688CNR_temperature",-30,50)
        mintsData = cropLimits(mintsData,"BME688CNR_pressure",950,1050)
        mintsData = cropLimits(mintsData,"BME688CNR_humidity",0,100)
        numLeft   = len(mintsData)

    if climateSensor == "BME680":
        numAll    = len(mintsData)
        mintsData = cropLimits(mintsData,"BME680_temperature",-30,50)
        mintsData = cropLimits(mintsData,"BME680_pressure",95,105)
        mintsData = cropLimits(mintsData,"BME680_humidity",0,100)
        numLeft    = len(mintsData)

    if climateSensor == "BME280":
        numAll       = len(mintsData)
        mintsData    = cropLimits(mintsData,"BME280_Temperature",-30,50)
        mintsData    = cropLimits(mintsData,"BME280_Pressure",950,1050)
        mintsData    = cropLimits(mintsData,"BME280_Humidity",0,100)
        numLeft      = len(mintsData)
    
    validPercentage = (numLeft/numAll)*100

    climateSensorStatus = OrderedDict([
                ("nodeID"            ,nodeID),
                ("climateSensor"     ,climateSensor),
                ("numAll"            ,numAll),
                ("numLeft"           ,numLeft),
                ("validPercentage"   ,validPercentage),
                ("sensorDate"         ,sensorDate),
                ("dateNow"           ,dateNow)
               ])
    # print(climateSensorStatus)
    writePath = getPathGenericParent(modelsPklsFolder,"OOBStats","csv")       
    writeCSV3(writePath,climateSensorStatus)
    return mintsData;



def getDataSuperReader(nodeID,sensorID,beginDate):
    print("Reading Data for Node : " + nodeID)
    print("Sensor ID             : " + sensorID)    
    print("Begin Date            : " + beginDate)    
    
    startDate         = datetime.datetime.strptime(beginDate, '%Y-%m-%d')
    mintsData         = superReaderV2(nodeID,sensorID)
    print(mintsData)
    mintsData         = mintsData[mintsData.index>startDate]
    
    return mintsData


def climateDataPrepV2(nodeData,nodeID,WIMDA,YXXDR):

    climateData = getDataSuperReader(nodeID,nodeData['climateSensor'],nodeData['climateSensorBegin'])
    gpsData     = getDataSuperReader(nodeID,nodeData['gpsSensor'],nodeData['gpsSensorBegin'])
    mintsData   = merger([climateData, WIMDA,YXXDR, gpsData])

    if len(mintsData.index)>0:
        print("GPS Cropping")
        pd.to_pickle(mintsData,getPathGeneric(mergedPklsFolder,nodeID,"climateData","pkl") )
        
        mintsData = gpsCropCoordinatesV2(mintsData,nodeData['gpsSensor'],32.992179, -96.757777,0.0015,0.0015)
        
        pd.to_pickle(mintsData,getPathGeneric(mergedPklsFolder,nodeID,"climateDataWSTC","pkl") )
        pd.to_pickle(mintsData.dropna(),getPathGeneric(mergedPklsFolder,nodeID,"climateDataWSTCCurrent","pkl") )

        print("-----------------------------------------------")
        print(mintsData)
        print("-----------------------------------------------")

    else:
        print("-----------------------------------------------")
        print("No data for Node ID: "+ nodeID)
        print("-----------------------------------------------")

def climateDataPrep(nodeData,nodeID,climateSensor,WIMDA,YXXDR,mergedPklsFolder):
    dataCropDate  = datetime.datetime.strptime(nodeData['climateSensorBegin'], '%Y-%m-%d')
    print("Reading Data for Node: " + nodeID)
    GPGGALR       = superReader(nodeID,"GPGGALR")
    climateSensor   = superReader(nodeID,climateSensor)
    mintsData = merger([climateSensor, WIMDA,YXXDR, GPGGALR])
    print("GPS Cropping")
    pd.to_pickle(mintsData,getPathGeneric(mergedPklsFolder,nodeID,"climateData","pkl") )
    mintsData = gpsCropCoordinates(mintsData,32.992179, -96.757777,0.0015,0.0015)
    # Remove GPS Data 
    mintsData = mintsData.drop('GPGGALR_Longitude', 1)
    mintsData = mintsData.drop('GPGGALR_Latitude', 1)
    pd.to_pickle(mintsData,getPathGeneric(mergedPklsFolder,nodeID,"climateDataWSTC","pkl") )
    print("Sensor Cropping")
    mintsData = mintsData[mintsData.index>dataCropDate]
    pd.to_pickle(mintsData.dropna(),getPathGeneric(mergedPklsFolder,nodeID,"climateDataWSTCCurrent","pkl") )
    print(mintsData)
    print("-----------------------------------------------")


def climateCalibrationV2(nodeID,dateNow, mintsData,climateTargets,climateSensor,sensorDate):
    # print("=====================MINTS=====================")
    # print("Climate data calibraion for Node: " + nodeID +" with Climate Sensor: " + climateSensor)
    # print("-----------------------------------------------")
    
    for targets in climateTargets:
        target = targets['target']
        targetData = mintsData[target]

        print("Running calibraion for : " + target )
        inputData  = mintsData[targets[climateSensor + 'inputs']]
        
        x_train, x_test, y_train, y_test = train_test_split(inputData, targetData, test_size=0.2, random_state=0)
        
        regressor = LinearRegression()
        regressor.fit(x_train, y_train)
   
        y_predicted_train = regressor.predict(x_train)
        y_predicted_test  = regressor.predict(x_test)
        
        rmseTrain  = mean_squared_error(y_train, y_predicted_train, squared=False)
        rmseTest   = mean_squared_error(y_test, y_predicted_test, squared=False)

        r2Test   = r2_score(y_test, y_predicted_test)
        r2Train  = r2_score(y_train, y_predicted_train)

        statsDictionary = OrderedDict([
                ("nodeID"            ,nodeID),
                ("target"            ,target),                
                ("climateSensor"     ,climateSensor),
                ("numCombined"       ,len(mintsData)),
                ("numTrain"          ,len(y_train)),
                ("numTest"           ,len(y_train)),
                ("rmseTrain"         ,rmseTrain),
                ("rmseTest"          ,rmseTest),
                ("r2Train"           ,r2Train),
                ("r2Test"            ,r2Test),
                ("sensorDate"        ,sensorDate),
                ("dateNow"           ,dateNow)
               ])
   
        # print(statsDictionary)
        pd.to_pickle(regressor ,getPathGeneric(modelsPklsFolder,nodeID,target+"_MDL_"+dateNow,"pkl")  )
        writePath = getPathGenericParent(modelsPklsFolder,"climateCalibStats","csv")       
        writeCSV3(writePath,statsDictionary)
  




def climateCalibration(nodeID,dateNow, mintsData,climateTargets,climateSensor,sensorDate):
    # print("=====================MINTS=====================")
    # print("Climate data calibraion for Node: " + nodeID +" with Climate Sensor: " + climateSensor)
    # print("-----------------------------------------------")
    for targets in climateTargets:
        target = targets['target']
        targetData = mintsData[target]
        print("Running calibraion for : " + target )
        if climateSensor == "BME280":
            inputData  = mintsData[targets['BME280inputs']]
        if climateSensor == "BME680":
            inputData  = mintsData[targets['BME680inputs']]        

        x_train, x_test, y_train, y_test = train_test_split(inputData, targetData, test_size=0.2, random_state=0)
        
        regressor = LinearRegression()
        regressor.fit(x_train, y_train)
   
        y_predicted_train = regressor.predict(x_train)
        y_predicted_test  = regressor.predict(x_test)
        
        rmseTrain  = mean_squared_error(y_train, y_predicted_train, squared=False)
        rmseTest   = mean_squared_error(y_test, y_predicted_test, squared=False)

        r2Test   = r2_score(y_test, y_predicted_test)
        r2Train  = r2_score(y_train, y_predicted_train)

        statsDictionary = OrderedDict([
                ("nodeID"            ,nodeID),
                ("target"            ,target),                
                ("climateSensor"     ,climateSensor),
                ("numCombined"       ,len(mintsData)),
                ("numTrain"          ,len(y_train)),
                ("numTest"           ,len(y_train)),
                ("rmseTrain"         ,rmseTrain),
                ("rmseTest"          ,rmseTest),
                ("r2Train"           ,r2Train),
                ("r2Test"            ,r2Test),
                ("sensorDate"        ,sensorDate),
                ("dateNow"           ,dateNow)
               ])
   
        pd.to_pickle(regressor ,getPathGeneric(modelsPklsFolder,nodeID,target+"_MDL_"+dateNow,"pkl")  )

        writePath = getPathGenericParent(modelsPklsFolder,"climateCalibStats","csv")       
        writeCSV3(writePath,statsDictionary)
  
