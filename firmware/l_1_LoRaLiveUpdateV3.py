# MQTT Client demo
# Continuously monitor two different MQTT topics for data,
# check if the received data matches two predefined 'commands'
import paho.mqtt.client as mqtt
import datetime
import yaml
import collections
import json
import time
from mintsXU4 import mintsSensorReader as mSR
from mintsXU4 import mintsDefinitions as mD
from mintsXU4 import mintsLatest as mL
from mintsXU4 import mintsLoRaReader as mLR
from collections import OrderedDict
import struct
from mintsXU4 import mintsLiveNodes as mLN

mqttPort            = mD.mqttPortLoRa
mqttBroker          = mD.mqttBrokerLoRa
mqttCredentialsFile = mD.mqttLoRaCredentialsFile
mintsDefinitions    = mD.mintsDefinitions
portIDs             = mD.portIDs

tlsCert             = mD.tlsCert

portIDs             = portIDs['portIDs']

credentials  = yaml.load(open(mqttCredentialsFile),Loader=yaml.FullLoader)
connected    = False  # Stores the connection status
broker       = mqttBroker  
port         = mqttPort  # Secure port
mqttUN       = credentials['mqtt']['username'] 
mqttPW       = credentials['mqtt']['password'] 

currentState = 0


nodeIDs      = mintsDefinitions['nodeIDs']
sensors      = mintsDefinitions['sensors']
liveSpanSec  = mintsDefinitions['liveSpanSec']

initMessege  = True
decoder = json.JSONDecoder(object_pairs_hook=collections.OrderedDict)
nodeObjects  = []

def isEven(numberIn):
    return  numberIn % 2 == 0;


# This functioin depends on the averaged value which can either be 30 or 60 seconds which is not ideal 
# How can I have a function that is not dependant averaged times 0




def getStateV2(timeIn):
    stateOut = int((timeIn + liveSpanSec/2)/liveSpanSec);
    # print("Current State")
    # print(stateOut)
    return stateOut;

def getNodeIndexV2(nodeID):
# Need to be capable of detecting a valid pck file
    indexOut = 0
    for nodeIDsIn in nodeIDs:
        if (nodeID == nodeIDsIn['nodeID']):
            return indexOut; 
        indexOut = indexOut +1
    return -1;



def getNodeIndex(nodeID):
    indexOut = 0
    for nodeIDsIn in nodeIDs:
        if (nodeID == nodeIDsIn['nodeID']):
            return indexOut; 
        indexOut = indexOut +1
    return -1;


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    topic = "utd/lora/app/2/device/+/event/up"
    client.subscribe(topic)
    print("Subscrbing to Topic: "+ topic)
    for nodeIDsIn in nodeIDs:
        nodeID = nodeIDsIn['nodeID']
        print("Appending  Node: " + nodeID)
        nodeObjects.append(mLN.node(nodeID))
    
def on_message(client, userdata, msg):
 
    global currentState
    try:
        print()
        print(" - - - MINTS DATA RECEIVED - - - ")
        # print(msg.payload)
        dateTime,gatewayID,nodeID,sensorID,framePort,base16Data = \
            mLR.loRaSummaryReceive(msg,portIDs)
        print("Node ID         : " + nodeID)
        print("Gateway ID      : " + gatewayID)
        print("Sensor ID       : " + sensorID)
        print("Date Time       : " + str(dateTime))
        print("Port ID         : " + str(framePort))
        print("Base 16 Data    : " + base16Data)

        # This function does not write any CSVs - It only returns the sensor dictionary
        sensorDictionary = mLR.sensorReceiveLoRa(dateTime,nodeID,sensorID,framePort,base16Data)
        # print(sensorDictionary)

        dateTimeNow   = datetime.datetime.strptime(sensorDictionary["dateTime"], '%Y-%m-%d %H:%M:%S.%f')
        # print(dateTimeNow)
        currentTimeInSec = dateTimeNow.timestamp()
        # The current state is determined by the number of seconds elapsed since 1970 
        liveState        = getStateV2(currentTimeInSec)

        if currentState != liveState:
            currentState = liveState
            print()
            print(" - - - ==== - - - ==== Status Changed ==== - - - ==== - - - ")
            for nodeObject in nodeObjects:
                nodeObject.changeStateV2()

        nodeIndex = getNodeIndex(nodeID)

        if nodeIndex > 0  and nodeObjects[nodeIndex].climateMdlAvail:
            print("Reading data for Node ID:" + nodeID + " with Node Index " + str(nodeIndex))
            if sensorID == nodeIDs[nodeIndex]['pmSensor']:
                nodeObjects[nodeIndex].nodeReaderPM(sensorDictionary)
            if sensorID == nodeIDs[nodeIndex]['climateSensor']:
                nodeObjects[nodeIndex].nodeReaderClimate(sensorDictionary)
            if sensorID == nodeIDs[nodeIndex]['gpsSensor']:
                nodeObjects[nodeIndex].nodeReaderGPS(sensorDictionary)

                


    except Exception as e:
        print("[ERROR] Could not publish data, error: {}".format(e))


# Create an MQTT client and attach our routines to it.
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(mqttUN,mqttPW)
client.connect(broker, port, 60)
client.loop_forever()



