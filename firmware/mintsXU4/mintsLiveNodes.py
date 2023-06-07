from cmath import nan
from datetime import datetime, timedelta
from os import name
import time
import random
import pandas as pd
#import pyqtgraph as pg
from collections import deque
#from pyqtgraph.Qt import QtGui, QtCore
from mintsXU4 import mintsSensorReader as mSR
from mintsXU4 import mintsDefinitions as mD
from mintsXU4 import mintsProcessing as mP
from mintsXU4 import mintsLatest as mL
from mintsXU4 import mintsNow as mN

# from dateutil import tz
import numpy as np
#from pyqtgraph import AxisItem
from time import mktime
import statistics
from collections import OrderedDict
# import pytz
import sys

nodeIDs              = mD.mintsDefinitions['nodeIDs']
airMarID             = mD.mintsDefinitions['airmarID']
climateTargets       = mD.mintsDefinitions['climateTargets']
liveSpanSec          = mD.mintsDefinitions['liveSpanSec']

rawPklsFolder        = mD.rawPklsFolder
referencePklsFolder  = mD.referencePklsFolder
mergedPklsFolder     = mD.mergedPklsFolder
modelsPklsFolder     = mD.modelsPklsFolder
liveFolder           = mD.liveFolder

class node:
    def __init__(self,nodeID):
        self.nodeID = nodeID
        print("============MINTS============")
        print("NODEID: " + nodeID)

        # Only consider the last 10 models created
        lastRecords = 10
        
        self.evenState       = True
        self.initRunPM       = True
        self.initRunClimate  = True
        self.initRunGPS      = True
        self.climateMdlAvail = False

        self.pmSensor,self.climateSensor,self.gpsSensor   = mN.getSensorsV2(nodeID)
        self.latitudeHC,self.longitudeHC, self.altitudeHC = mN.getGPS(nodeID)
        self.mdlDict = {}

        # Load All Climate Models 
        climateMdlSum = 0

        readPath           = mP.getPathGenericParent(modelsPklsFolder,"climateCalibStats","csv");
        climateCalibStats  = pd.read_csv(readPath)
        nodeIDStats        = climateCalibStats[climateCalibStats['nodeID'] == self.nodeID ]
        nodeIDStats        = nodeIDStats[nodeIDStats['climateSensor'] == self.climateSensor ]
        for targets in climateTargets:
            target = targets['target']
            nodeIDStatsTarget = nodeIDStats[target == nodeIDStats['target']].tail(lastRecords)
            print(nodeIDStatsTarget)
            if nodeIDStatsTarget.empty:
                mxInd = nan
                dateNow = nan
                self.mdlDict[target + "_str" ] = nan
                self.mdlDict[target + "_MDL" ] = nan
            else:
                print("Reading Climate Models for : " + target )
                climateMdlSum = climateMdlSum + 1
                self.climateMdlAvail = True
                mxInd = nodeIDStatsTarget['r2Test'].idxmax()
                dateNow = nodeIDStatsTarget[nodeIDStatsTarget.index == mxInd ]['dateNow'].item()
                self.mdlDict[target + "_str" ] = target + "_" + dateNow
                self.mdlDict[target + "_MDL" ] = pd.read_pickle(mP.getPathGeneric(modelsPklsFolder,nodeID,target+"_MDL_"+dateNow,"pkl"))
        
        self.climateMdlAvail = climateMdlSum==len(climateTargets)
        print("climate model availabilty:" + str(self.climateMdlAvail))

        self.lastPMDateTime      = datetime(2010, 1, 1, 0, 0, 0, 0)
        self.lastClimateDateTime = datetime(2010, 1, 1, 0, 0, 0, 0)
        self.lastGPSDateTime     = datetime(2010, 1, 1, 0, 0, 0, 0)

 
        self.pc0_1          = []
        self.pc0_3          = []
        self.pc0_5          = []
        self.pc1_0          = []
        self.pc2_5          = []
        self.pc5_0          = []
        self.pc10_0         = []
        self.pm0_1          = []
        self.pm0_3          = []
        self.pm0_5          = []
        self.pm1_0          = []
        self.pm2_5          = []
        self.pm5_0          = []
        self.pm10_0         = []
        self.dateTimePM     = []

        # if self.climateSensor  in {"BME280", "BME680", "BME688CNR"}:
        self.temperature         = []
        self.pressure            = []
        self.humidity            = []
        self.dateTimeClimate     = []

        # if self.gpsSensor  in {"GPGGAPL", "GPGGALR"}:
        self.altitude       = []
        self.latitude       = []
        self.longitude      = []
        self.dateTimeGPS    = []

    def nodeReaderPM(self,jsonData):
        try:
            self.dataInPM       = jsonData
            self.ctNowPM        = datetime.strptime(self.dataInPM['dateTime'],'%Y-%m-%d %H:%M:%S.%f')
            # print(self.ctNowPM)

            if (self.ctNowPM>self.lastPMDateTime):
                self.currentUpdatePM()
        except Exception as e:
            print("[ERROR] Could not read JSON data, error: {}".format(e))

    def nodeReaderClimate(self,jsonData):
        try:
            self.dataInClimate  = jsonData
            self.ctNowClimate   = datetime.strptime(self.dataInClimate['dateTime'],'%Y-%m-%d %H:%M:%S.%f')
            if (self.ctNowClimate>self.lastClimateDateTime):
                self.currentUpdateClimate()
        except Exception as e:
            print("[ERROR] Could not read JSON data, error: {}".format(e))
    
    def nodeReaderGPS(self,jsonData):
        try:
            self.dataInGPS  = jsonData
            self.ctNowGPS   = datetime.strptime(self.dataInGPS['dateTime'],'%Y-%m-%d %H:%M:%S.%f')
            if (self.ctNowGPS>self.lastGPSDateTime ):
                self.currentUpdateGPS()
        except Exception as e:
            print("[ERROR] Could not read JSON data, error: {}".format(e))
 
    # def nodeReader(self):
    #     try:
    #         self.dataInPM       = mL.readJSONLatestAllMQTT(self.nodeID,self.pmSensor)[0]
    #         self.ctNowPM        = datetime.strptime(self.dataInPM['dateTime'],'%Y-%m-%d %H:%M:%S.%f')
    #         if (self.ctNowPM>self.lastPMDateTime):
    #             self.pmUpdater()
    #     except Exception as e:
    #         print("[ERROR] Could not read JSON data, error: {}".format(e))
        
    #     try:
    #         self.dataInClimate  = mL.readJSONLatestAllMQTT(self.nodeID,self.climateSensor)[0]
    #         self.ctNowClimate   = datetime.strptime(self.dataInClimate['dateTime'],'%Y-%m-%d %H:%M:%S.%f')
    #         if (self.ctNowClimate>self.lastClimateDateTime):
    #             self.climateUpdater() 
    #     except Exception as e:
    #         print("[ERROR] Could not read JSON data, error: {}".format(e))
        
    #     try:
    #         self.dataInGPS  = mL.readJSONLatestAllMQTT(self.nodeID,"GPSGPGGA2")[0]
    #         self.ctNowGPS   = datetime.strptime(self.dataInGPS['dateTime'],'%Y-%m-%d %H:%M:%S.%f')
    #         if (self.ctNowGPS>self.lastGPSDateTime ):
    #             self.gpsUpdater() 
    #     except Exception as e:
    #         print("[ERROR] Could not read JSON data, error: {}".format(e))

    # def pmUpdater(self):
    #     # print("PM UPDATER")
    #     # if(self.getState(self.ctNowPM)!=self.evenState):
    #     #     self.changeState()
    #     self.currentUpdatePM()
    #     return;

    # def climateUpdater(self):
    #     # # print("CLIMATE UPDATER")
    #     # if(self.getState(self.ctNowClimate)!=self.evenState):
    #     #     self.changeState()
    #     self.currentUpdateClimate()
    #     return;

    # def gpsUpdater(self):
    #     # # print("GPS UPDATER")
    #     # if(self.getState(self.ctNowGPS)!=self.evenState):
    #     #     self.changeState()
    #     self.currentUpdateGPS()
    #     return;

    def getStateV2(self,timeIn):
        # print("GET STATE")
        # Zero State means current time is on an even minute
        # for example minutes are odd and seconds are more than 30 or 
        # minutes are even seconds are less  or equal to 30 
        # print("Current State")
        stateOut = int((timeIn + liveSpanSec/2)/liveSpanSec);
        # print(stateOut)
        return stateOut;


    # def getState(self,timeIn):
    #     # print("GET STATE")
    #     # Zero State means current time is on an even minute
    #     # for example minutes are odd and seconds are more than 30 or 
    #     # minutes are even seconds are less  or equal to 30 
    #     print("Current State")
    #     print((not(self.isEven(timeIn.minute)) and timeIn.second > 30) and (self.isEven(timeIn.minute) and timeIn.second <= 30))
    #     return (not(self.isEven(timeIn.minute)) and timeIn.second > 30) and (self.isEven(timeIn.minute) and timeIn.second <= 30) ;

    # def isEven(self,numberIn):
    #     return  numberIn % 2 == 0;

    def getTimeV2(self):
        # print("Get time V2")
        checkTime = datetime.utcfromtimestamp(self.getStateV2(self.dateTimePM[-1].timestamp())*liveSpanSec)
        self.dateTimeStrCSV = str(checkTime.year).zfill(4)+ \
                "-" + str(checkTime.month).zfill(2) + \
                "-" + str(checkTime.day).zfill(2) + \
                " " + str(checkTime.hour).zfill(2) + \
                ":" + str(checkTime.minute).zfill(2) + \
                ":" + str(checkTime.second).zfill(2) + '.000'
        # print(self.dateTimeStrCSV)    
        return ;

    # def getTime(self):
    #     # print("GET TIME")
    #     checkTime  = self.dateTimePM[-1]+ timedelta(seconds=30)
    #     self.dateTimeStrCSV = str(checkTime.year).zfill(4)+ \
    #             "-" + str(checkTime.month).zfill(2) + \
    #             "-" + str(checkTime.day).zfill(2) + \
    #             " " + str(checkTime.hour).zfill(2) + \
    #             ":" + str(checkTime.minute).zfill(2) + \
    #             ":" + "00.000"               
    #     return ;
    
    def getValidity(self):
        # print("Getting Validity")     
        return len(self.pm0_1)>=1;



    def changeStateV2(self):
        if self.getValidity():
            # print("Is Valid")
            self.getAverageAll()
            self.getTimeV2()
            self.doCSV()
        # self.evenState = not(self.evenState)
        self.clearAll()      


    # def changeState(self):
    #     if self.getValidity():
    #         print("Is Valid")
    #         self.getAverageAll()
    #         self.getTime()
    #         # self.doCSV()
    #     # self.evenState = not(self.evenState)
    #     self.clearAll()        

    def currentUpdatePM(self):
        print("PM Data Read")
        print(self.dataInPM)
        # At this point I need to consider the sensor, 
        # but since both the IPS7100 and the IPS7100 has the
        # same outputs, there is no need 
        if self.pmSensor  in {"IPS7100", "IPS7100CNR"}:
            self.pc0_1.append(float(self.dataInPM['pc0_1']))
            self.pc0_3.append(float(self.dataInPM['pc0_3']))
            self.pc0_5.append(float(self.dataInPM['pc0_5']))
            self.pc1_0.append(float(self.dataInPM['pc1_0']))
            self.pc2_5.append(float(self.dataInPM['pc2_5']))
            self.pc5_0.append(float(self.dataInPM['pc5_0']))
            self.pc10_0.append(float(self.dataInPM['pc10_0']))
            self.pm0_1.append(float(self.dataInPM['pm0_1']))
            self.pm0_3.append(float(self.dataInPM['pm0_3']))
            self.pm0_5.append(float(self.dataInPM['pm0_5']))
            self.pm1_0.append(float(self.dataInPM['pm1_0']))
            self.pm2_5.append(float(self.dataInPM['pm2_5']))
            self.pm5_0.append(float(self.dataInPM['pm5_0']))
            self.pm10_0.append(float(self.dataInPM['pm10_0']))
            timeIn = datetime.strptime(self.dataInPM['dateTime'],'%Y-%m-%d %H:%M:%S.%f')
            self.dateTimePM.append(timeIn)
            self.lastPMDateTime = timeIn

    def currentUpdateClimate(self):
        print("Climate Data Read")
        print(self.dataInClimate)
        # At this point I need to consider the sensor, 
        if self.climateSensor  in {"BME688CNR","BME280"}:        
            self.temperature.append(float(self.dataInClimate['temperature']))
            self.pressure.append(float(self.dataInClimate['pressure']))
            self.humidity.append(float(self.dataInClimate['humidity']))
            timeIn = datetime.strptime(self.dataInClimate['dateTime'],'%Y-%m-%d %H:%M:%S.%f')
            self.dateTimeClimate.append(timeIn)
            self.lastClimateDateTime = timeIn
        
    def currentUpdateGPS(self):
        print("GPS Data Read")
        print(self.dataInGPS)
        if self.gpsSensor in {"GPGGAPL","GPGGA"}:      
            self.latitude.append(float(self.dataInGPS['latitude']))
            self.longitude.append(float(self.dataInGPS['longitude']))
            self.altitude.append(float(self.dataInGPS['altitude']))
            timeIn  = datetime.strptime(self.dataInGPS['dateTime'],'%Y-%m-%d %H:%M:%S.%f')
            self.dateTimeGPS.append(timeIn)
            self.lastGPSDateTime = timeIn


    def clearAll(self):
        self.pc0_1      = []
        self.pc0_3      = []
        self.pc0_5      = []
        self.pc1_0      = []
        self.pc2_5      = []
        self.pc5_0      = []
        self.pc10_0     = []

        self.pm0_1      = []
        self.pm0_3      = []
        self.pm0_5      = []
        self.pm1_0      = []
        self.pm2_5      = []
        self.pm5_0      = []
        self.pm10_0     = []        
        self.dateTimePM = []

        self.temperature       = []
        self.pressure          = []
        self.humidity          = []
        self.dateTimeClimate   = []

        self.altitude          = []
        self.longitude         = []
        self.latitude          = []
        self.dateTimeGPS       = []


    def getAverageAll(self):
        if(len(self.pc0_1)>0):
            self.pc0_1Avg      = statistics.mean(self.pc0_1)
            self.pc0_3Avg      = statistics.mean(self.pc0_3)
            self.pc0_5Avg      = statistics.mean(self.pc0_5)
            self.pc1_0Avg      = statistics.mean(self.pc1_0)
            self.pc2_5Avg      = statistics.mean(self.pc2_5)
            self.pc5_0Avg      = statistics.mean(self.pc5_0)
            self.pc10_0Avg     = statistics.mean(self.pc10_0)

            self.pm0_1Avg      = statistics.mean(self.pm0_1)
            self.pm0_3Avg      = statistics.mean(self.pm0_3)
            self.pm0_5Avg      = statistics.mean(self.pm0_5)
            self.pm1_0Avg      = statistics.mean(self.pm1_0)
            self.pm2_5Avg      = statistics.mean(self.pm2_5)
            self.pm5_0Avg      = statistics.mean(self.pm5_0)
            self.pm10_0Avg     = statistics.mean(self.pm10_0)       
        
        if(len(self.temperature)>0):
            self.temperatureAvg  = statistics.mean(self.temperature)
            self.pressureAvg     = statistics.mean(self.pressure)
            self.humidityAvg     = statistics.mean(self.humidity)
        else:
            self.temperatureAvg  = -1
            self.pressureAvg     = -1
            self.humidityAvg     = -1
      

        if (len(self.altitude)>0):
            self.altitudeAvg  = statistics.mean(self.altitude)
            self.longitudeAvg = statistics.mean(self.longitude)
            self.latitudeAvg  = statistics.mean(self.latitude)
        else:
            self.altitudeAvg  = self.altitudeHC
            self.longitudeAvg = self.longitudeHC
            self.latitudeAvg  = self.latitudeHC



    def doCSV(self):
        if (self.climateMdlAvail):
            if(len(self.temperature)>0):
                temperatureCalibrated = mN.c2F(self.mdlDict["WIMDA_airTemperature_MDL"].predict(np.array(self.temperatureAvg).reshape(1,-1))[0])
                pressureCalibrated    = mN.b2MB(self.mdlDict["YXXDR_barrometricPressureBars_MDL"].predict(np.array(self.pressureAvg).reshape(1,-1))[0])
                humidityCalibrated    = self.mdlDict["WIMDA_relativeHumidity_MDL"].predict(np.array(self.humidityAvg).reshape(1,-1))[0]
                dewPointCalibrated    = mN.c2F(self.mdlDict["WIMDA_dewPoint_MDL"].predict(np.array([self.temperatureAvg,self.pressureAvg,self.humidityAvg]).reshape(1,-1))[0])
            else:
                temperatureCalibrated = -1.0
                pressureCalibrated    = -1.0
                humidityCalibrated    = -1.0
                dewPointCalibrated    = -1.0
        else:
            temperatureCalibrated = -2.0
            pressureCalibrated    = -2.0
            humidityCalibrated    = -2.0
            dewPointCalibrated    = -2.0        

        self.getTimeV2()

        sensorDictionary = OrderedDict([
                ("dateTime"         ,self.dateTimeStrCSV),
                ("nodeID"           ,self.nodeID),
                ("climateSensor"    ,self.climateSensor),
                ("pmSensor"         ,self.pmSensor),                                
                ("Latitude"         ,self.latitudeAvg),                
                ("Longitude"        ,self.longitudeAvg),
                ("Altitude"         ,self.altitudeAvg),
                ("PC0_1"            ,self.pc0_1Avg),
                ("PC0_3"            ,self.pc0_3Avg),
                ("PC0_5"            ,self.pc0_5Avg),
                ("PC1_0"            ,self.pc1_0Avg),
                ("PC2_5"            ,self.pc2_5Avg),
                ("PC5_0"            ,self.pc5_0Avg),
                ("PC10_0"           ,self.pc10_0Avg),
                ("PM0_1"            ,self.pm0_1Avg),
                ("PM0_3"            ,self.pm0_3Avg),
                ("PM0_5"            ,self.pm0_5Avg),
                ("PM1"              ,self.pm1_0Avg),
                ("PM2_5"            ,self.pm2_5Avg),
                ("PM5_0"            ,self.pm5_0Avg),
                ("PM10"             ,self.pm10_0Avg),
                ("Temperature"      ,temperatureCalibrated),
                ("Pressure"         ,pressureCalibrated),
                ("Humidity"         ,humidityCalibrated),
                ("DewPoint"         ,dewPointCalibrated),            
                ("nopGPS"           ,len(self.dateTimeGPS)),
                ("nopPM"            ,len(self.dateTimePM)),
                ("nopClimate"       ,len(self.dateTimeClimate)),
                ("temperatureMDL"   ,self.mdlDict["WIMDA_airTemperature_str"]),
                ("pressureMDL"      ,self.mdlDict["YXXDR_barrometricPressureBars_str"]),
                ("humidityMDL"      ,self.mdlDict["WIMDA_relativeHumidity_str"]),
                ("dewPointMDL"      ,self.mdlDict["WIMDA_dewPoint_str"]),                
               ])
        
        print()        
        print("===============MINTS===============")
        print(sensorDictionary)
        mP.writeCSV3( mN.getWritePathDateCSV(liveFolder,self.nodeID,\
            datetime.strptime(self.dateTimeStrCSV,'%Y-%m-%d %H:%M:%S.%f'),\
                "calibrated"),sensorDictionary)
        print("CSV Written")
        mL.writeMQTTLatestRepublish(sensorDictionary,"mintsCalibrated",self.nodeID)


    # def update(self):
    #     self.currentTime=  datetime.now()
    #     self.nodeReader()

