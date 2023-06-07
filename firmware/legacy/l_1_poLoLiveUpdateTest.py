# MQTT Client demo
# Continuously monitor two different MQTT topics for data,
# check if the received data matches two predefined 'commands'
import paho.mqtt.client as mqtt
import datetime
import yaml
import collections
import json

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
fileIn              = mD.mintsDefinitionsFile
fileInLoRa          = mD.loRaNodesFile
tlsCert             = mD.tlsCert

# credentials     = yaml.load(open(mqttCredentialsFile),Loader=yaml.FullLoader)
transmitDetail      = yaml.load(open(fileIn),Loader=yaml.FullLoader)
transmitDetailLoRa  = yaml.load(open(fileInLoRa),Loader=yaml.FullLoader)


tlsCert             = mD.tlsCert
portIDs             = transmitDetailLoRa['portIDs']

credentials  = yaml.load(open(mqttCredentialsFile),Loader=yaml.FullLoader)
connected    = False  # Stores the connection status
broker       = mqttBroker  
port         = mqttPort  # Secure port
mqttUN       = credentials['mqtt']['username'] 
mqttPW       = credentials['mqtt']['password'] 
currentState    = True
transmitters = transmitDetail['nodeIDs']
sensors      = transmitDetail['sensors']
initMessege  = True
decoder = json.JSONDecoder(object_pairs_hook=collections.OrderedDict)
nodeObjects  = []

def isEven(numberIn):
    return  numberIn % 2 == 0;

def getState(timeIn):
    # print("GET STATE")
    # Zero State means current time is on an even minute
    # for example minutes are odd and seconds are more than 30 or 
    # minutes are even seconds are less  or equal to 30 
    currentState = (not(isEven(timeIn.minute)) and timeIn.second > 30) or (isEven(timeIn.minute) and timeIn.second <= 30)
    print("Current Time State: " + str(currentState))
    return currentState;

# def nodeIDMapper(nodeID):
def getNodeIndex(nodeID):
    indexOut = 0
    for transmitter in transmitters:
        if (nodeID == transmitter['nodeID']):
            return indexOut; 
        indexOut = indexOut +1
    return -1;


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    topic = "utd/lora/app/2/device/+/event/up"
    client.subscribe(topic)
    print("Subscrbing to Topic: "+ topic)
    for transmitter in transmitters:
        nodeID = transmitter['nodeID']
        print("Appending  Node")
        nodeObjects.append(mLN.node(nodeID))
    
    
    
def on_message(client, userdata, msg):
    global currentState
#    try:
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
    sensorDictionary = mLR.sensorReceiveLoRa(dateTime,nodeID,sensorID,framePort,base16Data)
       
    dateTimeNow   = datetime.datetime.strptime(sensorDictionary["dateTime"], '%Y-%m-%d %H:%M:%S.%f')
        
 
    if currentState != getState(dateTimeNow):
         currentState = getState(dateTimeNow)
         print("State Changed")
         for nodeObject in nodeObjects:
             nodeObject.changeState()


                
    nodeIndex = getNodeIndex(nodeID)
    if nodeIndex > 0 :  
        dateTime = datetime.datetime.strptime(sensorDictionary["dateTime"], '%Y-%m-%d %H:%M:%S.%f')
        if sensorID == transmitters[nodeIndex]['pmSensor']:
            nodeObjects[nodeIndex].nodeReaderPM(sensorDictionary)
        if sensorID == transmitters[nodeIndex]['climateSensor']:
            nodeObjects[nodeIndex].nodeReaderClimate(sensorDictionary)
        if sensorID == "GPGGALR":
            nodeObjects[nodeIndex].nodeReaderGPS(sensorDictionary)

                


#    except Exception as e:
#        print("[ERROR] Could not publish data, error: {}".format(e))


# Create an MQTT client and attach our routines to it.
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(mqttUN,mqttPW)
client.connect(broker, port, 60)
client.loop_forever()



