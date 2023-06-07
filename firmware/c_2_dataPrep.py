
# 1 Download the data 
# Create a data frame for Airmar Data 
import pickle
import datetime
import pandas as pd
#import feather
import glob
from collections import OrderedDict
import os
from functools import reduce
from pandas._libs.tslibs import timestamps
from pandas.core.frame import DataFrame
from mintsXU4 import mintsProcessing as mP
from mintsXU4 import mintsDefinitions as mD

nodeIDs              = mD.mintsDefinitions['nodeIDs']
airMarID             = mD.mintsDefinitions['airmarID']
rawPklsFolder        = mD.rawPklsFolder
referencePklsFolder  = mD.referencePklsFolder
mergedPklsFolder     = mD.mergedPklsFolder

# YXXDR     = mP.superReaderV2(airMarID,"YXXDR")
# pd.to_pickle(mP.dropIndexDuplicates(YXXDR) ,mP.getPathGeneric(referencePklsFolder,airMarID,"YXXDR","pkl"))

# WIMDA     = mP.superReaderV2(airMarID,"WIMDA")
# pd.to_pickle(mP.dropIndexDuplicates(WIMDA) ,mP.getPathGeneric(referencePklsFolder,airMarID,"WIMDA","pkl"))

WIMDA  = pd.read_pickle(mP.getPathGeneric(referencePklsFolder,airMarID,"WIMDA","pkl"))
YXXDR  = pd.read_pickle(mP.getPathGeneric(referencePklsFolder,airMarID,"YXXDR","pkl"))

for nodeData in nodeIDs:
    try:
        nodeID        = nodeData['nodeID']
        climateSensor = nodeData['climateSensor']
        print("=====================MINTS=====================")
        print("Prepearing Climate data for Node: " + nodeID +" with Climate Sensor: " + climateSensor)
        print("-----------------------------------------------")
        mP.climateDataPrepV2(nodeData,nodeID,WIMDA,YXXDR)
    except Exception as e:
        print ("Error and type: %s - %s." % (e,type(e)))
