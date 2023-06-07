
#!/usr/bin/python

import sys
import yaml
import os

from mintsXU4 import mintsDefinitions as mD

nodeIDs              = mD.mintsDefinitions['nodeIDs']
airMarID             = mD.mintsDefinitions['airmarID']
dataFolder           = mD.dataFolder  + "/ref/"

print()
print("MINTS")
print()

sysStr = 'rsync -avzrtu -e "ssh" ' +  "--include='*.csv' --include='*/' --exclude='*' /home/mints/Downloads/reference/" + airMarID + " " + dataFolder
print(sysStr)
os.system(sysStr)
