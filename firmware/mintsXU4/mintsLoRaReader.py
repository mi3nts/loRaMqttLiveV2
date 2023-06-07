# ***************************************************************************
#  mintsXU4
#   ---------------------------------
#   Written by: Lakitha Omal Harindha Wijeratne
#   - for -
#   Mints: Multi-scale Integrated Sensing and Simulation
#   ---------------------------------
#   Date: March 28, 2022
#   ---------------------------------
#   This module is written for generic implimentation of MINTS projects
#   --------------------------------------------------------------------------
#   https://github.com/mi3nts
#   http://utdmints.info/
#  ***************************************************************************

from cmath import nan
import serial
import datetime
import os
import csv
#import deepdish as dd
from mintsXU4 import mintsLatest as mL
from mintsXU4 import mintsDefinitions as mD
from mintsXU4 import mintsSensorReader as mSR
from getmac import get_mac_address
import time
import serial
import pynmea2
from collections import OrderedDict
import netifaces as ni
import math
import base64
import json
import struct

macAddress     = mD.macAddress
dataFolder     = mD.dataFolder
dataFolderMQTT = mD.dataFolderMQTT
dataFolderMQTTReference = mD.dataFolderMQTTReference
latestOn       = mD.latestOn
mqttOn         = mD.mqttOn
decoder        = json.JSONDecoder(object_pairs_hook=OrderedDict)

def sensorReceiveLoRa(dateTime,nodeID,sensorID,framePort,base16Data):
    sensorDictionary =  OrderedDict([
                ("dateTime" , str(dateTime))])
    if(sensorID=="IPS7100CNR"):
        sensorDictionary = IPS7100CNRLoRaReturn(dateTime,framePort,base16Data)
    if(sensorID=="IPS7100"):
        sensorDictionary = IPS7100LoRaReturn(dateTime,framePort,base16Data)        
    if(sensorID=="BME688CNR"):
        sensorDictionary =BME688CNRLoRaReturn(dateTime,framePort,base16Data)      
    if(sensorID=="BME280"):
        sensorDictionary =BME280LoRaReturn(dateTime,framePort,base16Data)                
    if(sensorID=="GPGGAPL"):
        sensorDictionary =GPGGAPLLoRaReturn(dateTime,framePort,base16Data) 
    if(sensorID=="GPGGALR"):
        sensorDictionary =GPGGALRLoRaReturn(dateTime,framePort,base16Data)         
    return sensorDictionary;

def IPS7100LoRaReturn(dateTime,framePort,base16Data):
    if(framePort == 15 and len(base16Data) ==112) :
        sensorDictionary =  OrderedDict([
                ("dateTime" , str(dateTime)), 
        		("pc0_1"  ,struct.unpack('<L',bytes.fromhex(base16Data[0:8]))[0]),
            	("pc0_3"  ,struct.unpack('<L',bytes.fromhex(base16Data[8:16]))[0]),
                ("pc0_5"  ,struct.unpack('<L',bytes.fromhex(base16Data[16:24]))[0]),
                ("pc1_0"  ,struct.unpack('<L',bytes.fromhex(base16Data[24:32]))[0]),
            	("pc2_5"  ,struct.unpack('<L',bytes.fromhex(base16Data[32:40]))[0]),
        		("pc5_0"  ,struct.unpack('<L',bytes.fromhex(base16Data[40:48]))[0]), 
            	("pc10_0" ,struct.unpack('<L',bytes.fromhex(base16Data[48:56]))[0]),
        		("pm0_1"  ,struct.unpack('<f',bytes.fromhex(base16Data[56:64]))[0]), 
            	("pm0_3"  ,struct.unpack('<f',bytes.fromhex(base16Data[64:72]))[0]),
                ("pm0_5"  ,struct.unpack('<f',bytes.fromhex(base16Data[72:80]))[0]),
                ("pm1_0"  ,struct.unpack('<f',bytes.fromhex(base16Data[80:88]))[0]),
            	("pm2_5"  ,struct.unpack('<f',bytes.fromhex(base16Data[88:96]))[0]),
        		("pm5_0"  ,struct.unpack('<f',bytes.fromhex(base16Data[96:104]))[0]), 
            	("pm10_0" ,struct.unpack('<f',bytes.fromhex(base16Data[104:112]))[0])
        ])
    # print(sensorDictionary)        
    return sensorDictionary;



def IPS7100CNRLoRaReturn(dateTime,framePort,base16Data):
    if(framePort == 17 and len(base16Data) ==112) :
        sensorDictionary =  OrderedDict([
                ("dateTime" , str(dateTime)), 
        		("pc0_1"  ,struct.unpack('<L',bytes.fromhex(base16Data[0:8]))[0]),
            	("pc0_3"  ,struct.unpack('<L',bytes.fromhex(base16Data[8:16]))[0]),
                ("pc0_5"  ,struct.unpack('<L',bytes.fromhex(base16Data[16:24]))[0]),
                ("pc1_0"  ,struct.unpack('<L',bytes.fromhex(base16Data[24:32]))[0]),
            	("pc2_5"  ,struct.unpack('<L',bytes.fromhex(base16Data[32:40]))[0]),
        		("pc5_0"  ,struct.unpack('<L',bytes.fromhex(base16Data[40:48]))[0]), 
            	("pc10_0" ,struct.unpack('<L',bytes.fromhex(base16Data[48:56]))[0]),
        		("pm0_1"  ,struct.unpack('<f',bytes.fromhex(base16Data[56:64]))[0]), 
            	("pm0_3"  ,struct.unpack('<f',bytes.fromhex(base16Data[64:72]))[0]),
                ("pm0_5"  ,struct.unpack('<f',bytes.fromhex(base16Data[72:80]))[0]),
                ("pm1_0"  ,struct.unpack('<f',bytes.fromhex(base16Data[80:88]))[0]),
            	("pm2_5"  ,struct.unpack('<f',bytes.fromhex(base16Data[88:96]))[0]),
        		("pm5_0"  ,struct.unpack('<f',bytes.fromhex(base16Data[96:104]))[0]), 
            	("pm10_0" ,struct.unpack('<f',bytes.fromhex(base16Data[104:112]))[0])
        ])
    # print(sensorDictionary)        
    return sensorDictionary;

def BME688CNRLoRaReturn(dateTime,framePort,base16Data):
    if(framePort == 25 and len(base16Data) ==56):
        sensorDictionary =  OrderedDict([
                ("dateTime"    , str(dateTime)), 
                ("temperature" ,struct.unpack('<f',bytes.fromhex(base16Data[0:8]))[0]),
                ("humidity"    ,struct.unpack('<f',bytes.fromhex(base16Data[8:16]))[0]),
                ("pressure"    ,struct.unpack('<f',bytes.fromhex(base16Data[16:24]))[0]),
                ("vocAqi"      ,struct.unpack('<f',bytes.fromhex(base16Data[24:32]))[0]),
                ("bvocEq"      ,struct.unpack('<f',bytes.fromhex(base16Data[32:40]))[0]),
                ("gasEst"      ,struct.unpack('<f',bytes.fromhex(base16Data[40:48]))[0]), 
                ("co2Eq"       ,struct.unpack('<f',bytes.fromhex(base16Data[48:56]))[0]),
          ])
    # print(sensorDictionary)        
    return sensorDictionary;

def BME280LoRaReturn(dateTime,framePort,base16Data):
    if(framePort == 21 and len(base16Data) ==24):
        sensorDictionary =  OrderedDict([
                ("dateTime"    , str(dateTime)), 
        		("temperature" ,struct.unpack('<f',bytes.fromhex(base16Data[0:8]))[0]),
            	("pressure"    ,struct.unpack('<f',bytes.fromhex(base16Data[8:16]))[0]),
                ("humidity"    ,struct.unpack('<f',bytes.fromhex(base16Data[16:24]))[0]),
          ])
    # print(sensorDictionary)        
    return sensorDictionary;

def GPGGALRLoRaReturn(dateTime,framePort,base16Data):
    if(framePort == 5 and len(base16Data) ==110):
        sensorDictionary =  OrderedDict([
                ("dateTime"            ,str(dateTime)),
        		("latitude"   ,struct.unpack('<d',bytes.fromhex(base16Data[0:16]))[0]),
            	("longitude"  ,struct.unpack('<d',bytes.fromhex(base16Data[16:32]))[0]),
                ("speed"      ,struct.unpack('<d',bytes.fromhex(base16Data[32:48]))[0]),
                ("altitude"   ,struct.unpack('<d',bytes.fromhex(base16Data[48:64]))[0]),
	            ("course"     ,struct.unpack('<d',bytes.fromhex(base16Data[64:80]))[0]),
            	("hdop"       ,struct.unpack('<d',bytes.fromhex(base16Data[80:96]))[0]),# 42 bytes
                ("year"       ,struct.unpack('<H',bytes.fromhex(base16Data[96:100]))[0]),# 2 bytes
                ("month"      ,struct.unpack('<b',bytes.fromhex(base16Data[100:102]))[0]),
                ("day"        ,struct.unpack('<b',bytes.fromhex(base16Data[102:104]))[0]),
                ("hour"       ,struct.unpack('<b',bytes.fromhex(base16Data[104:106]))[0]),
                ("minute"     ,struct.unpack('<b',bytes.fromhex(base16Data[106:108]))[0]),
                ("second"     ,struct.unpack('<b',bytes.fromhex(base16Data[108:110]))[0]), #5 bytes 
          ])
    # print(sensorDictionary)        
    return sensorDictionary;

def GPGGAPLLoRaReturn(dateTime,framePort,base16Data):
    if(framePort == 106 and len(base16Data) ==66):
        sensorDictionary =  OrderedDict([
                ("dateTime"             ,str(dateTime)),
                ("hour"                 ,struct.unpack('<B',bytes.fromhex(base16Data[0:2]))[0]),
                ("minute"               ,struct.unpack('<B',bytes.fromhex(base16Data[2:4]))[0]),
                ("second"               ,struct.unpack('<B',bytes.fromhex(base16Data[4:6]))[0]),
                ("latitude"             ,struct.unpack('<d',bytes.fromhex(base16Data[6:22]))[0]),
                ("longitude"            ,struct.unpack('<d',bytes.fromhex(base16Data[22:38]))[0]),
                ("gpsQuality"           ,struct.unpack('<B',bytes.fromhex(base16Data[38:40]))[0]),
                ("numberOfSatellites"   ,struct.unpack('<B',bytes.fromhex(base16Data[40:42]))[0]),
                ("HorizontalDilution"   ,struct.unpack('<f',bytes.fromhex(base16Data[42:50]))[0]),
                ("altitude"             ,struct.unpack('<f',bytes.fromhex(base16Data[50:58]))[0]),
                ("undulation"           ,struct.unpack('<f',bytes.fromhex(base16Data[58:66]))[0]),
          ])
    # print(sensorDictionary)        
    return sensorDictionary;

def IPS7100LoRaWrite(dateTime,nodeID,sensorID,framePort,base16Data):
    if(framePort == 15 and len(base16Data) ==112) :
        sensorDictionary =  OrderedDict([
                ("dateTime" , str(dateTime)), 
        		("pc0_1"  ,struct.unpack('<L',bytes.fromhex(base16Data[0:8]))[0]),
            	("pc0_3"  ,struct.unpack('<L',bytes.fromhex(base16Data[8:16]))[0]),
                ("pc0_5"  ,struct.unpack('<L',bytes.fromhex(base16Data[16:24]))[0]),
                ("pc1_0"  ,struct.unpack('<L',bytes.fromhex(base16Data[24:32]))[0]),
            	("pc2_5"  ,struct.unpack('<L',bytes.fromhex(base16Data[32:40]))[0]),
        		("pc5_0"  ,struct.unpack('<L',bytes.fromhex(base16Data[40:48]))[0]), 
            	("pc10_0" ,struct.unpack('<L',bytes.fromhex(base16Data[48:56]))[0]),
        		("pm0_1"  ,struct.unpack('<f',bytes.fromhex(base16Data[56:64]))[0]), 
            	("pm0_3"  ,struct.unpack('<f',bytes.fromhex(base16Data[64:72]))[0]),
                ("pm0_5"  ,struct.unpack('<f',bytes.fromhex(base16Data[72:80]))[0]),
                ("pm1_0"  ,struct.unpack('<f',bytes.fromhex(base16Data[80:88]))[0]),
            	("pm2_5"  ,struct.unpack('<f',bytes.fromhex(base16Data[88:96]))[0]),
        		("pm5_0"  ,struct.unpack('<f',bytes.fromhex(base16Data[96:104]))[0]), 
            	("pm10_0" ,struct.unpack('<f',bytes.fromhex(base16Data[104:112]))[0])
        ])
    # print(sensorDictionary)        
    # loRaWriteFinisher(nodeID,sensorID,dateTime,sensorDictionary)
    return sensorDictionary;

def PMLoRaWrite(dateTime,nodeID,sensorID,framePort,base16Data):
    if(framePort == 2 and len(base16Data) ==4):
        sensorDictionary =  OrderedDict([
                ("dateTime" ,str(dateTime)), 
        		("powerMode",struct.unpack('<b',bytes.fromhex(base16Data[0:2]))[0]),
          ])
    # print(sensorDictionary)        
    # loRaWriteFinisher(nodeID,sensorID,dateTime,sensorDictionary)
    return sensorDictionary;

def loRaWriteFinisher(nodeID,sensorID,dateTime,sensorDictionary):
    writePath = mSR.getWritePathMQTT(nodeID,sensorID,dateTime)
    exists    = mSR.directoryCheck(writePath)
    print(writePath)	
    mSR.writeCSV2(writePath,sensorDictionary,exists)
    mL.writeJSONLatestMQTT(sensorDictionary,nodeID,sensorID)
    return;

def loRaSummaryReceive(message,portIDs):
    nodeID = message.topic.split('/')[5]
    sensorPackage       =  decoder.decode(message.payload.decode("utf-8","ignore"))
    rxInfo              =  sensorPackage['rxInfo'][0]
    txInfo              =  sensorPackage['txInfo']
    loRaModulationInfo  =  txInfo['loRaModulationInfo']
    sensorID            = portIDs[getPortIndex(sensorPackage['fPort'],portIDs)]['sensor']
    dateTime            = datetime.datetime.fromisoformat(sensorPackage['publishedAt'][0:26])
    base16Data          = base64.b64decode(sensorPackage['data'].encode()).hex()
    gatewayID           = base64.b64decode(rxInfo['gatewayID']).hex()
    framePort           = sensorPackage['fPort']
    sensorDictionary =  OrderedDict([
            ("dateTime"        , str(dateTime)),
            ("nodeID"          , nodeID),
            ("sensorID"        , sensorID),
            ("gatewayID"       , gatewayID),
            ("rssi"            , rxInfo["rssi"]),
            ("loRaSNR"         , rxInfo["loRaSNR"]),
            ("channel"         , rxInfo["channel"] ),
            ("rfChain"         , rxInfo["rfChain"] ),
            ("frequency"       , txInfo["frequency"]),
            ("bandwidth"       , loRaModulationInfo["bandwidth"]),
            ("spreadingFactor" , loRaModulationInfo["spreadingFactor"] ),
            ("codeRate"        , loRaModulationInfo["codeRate"] ),
            ("dataRate"        , sensorPackage['dr']),
            ("frameCounters"   , sensorPackage['fCnt']),
            ("framePort"       , framePort),
            ("base64Data"      , sensorPackage['data']),
            ("base16Data"      , base16Data),
            ("devAddr"         , sensorPackage['devAddr']),
            ("deviceAddDecoded", base64.b64decode(sensorPackage['devAddr'].encode()).hex())
        ])
    # loRaWriteFinisher("LoRaNodes","Summary",dateTime,sensorDictionary)
    # loRaWriteFinisher(gatewayID,"Summary",dateTime,sensorDictionary)
    return dateTime,gatewayID,nodeID,sensorID,framePort,base16Data;

def getPortIndex(portIDIn,portIDs):
    indexOut = 0
    for portID in portIDs:
        if (portIDIn == portID['portID']):
            return indexOut; 
        indexOut = indexOut +1