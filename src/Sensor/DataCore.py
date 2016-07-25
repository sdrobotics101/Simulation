import time
import sys
sys.path.append("../Dependencies/PythonSharedBuffers/src")

from Sensor import *
from Serialization import *
from Constants import *

import pydsm

SERVERID = SENSOR_SERVER_ID
CLIENTID = 100

data = Data()

data.accelerometer[0] = 0
data.accelerometer[1] = 0
data.accelerometer[2] = 9.81

data.gyro[0] = 0
data.gyro[1] = 0
data.gyro[2] = 0

data.magnetometer[0] = 0.5
data.magnetometer[1] = 0
data.magnetometer[2] = 0.5

data.pressureSensor = 1000

data.isEnabled[0] = True
data.isEnabled[1] = True
data.isEnabled[2] = True
data.isEnabled[3] = True

client = pydsm.Client(SERVERID, CLIENTID, True)

client.registerLocalBuffer("data", sizeof(Data), False)
time.sleep(0.1)

if (client.setLocalBufferContents("data", Pack(data))):
    print("set data")

try:
    while True:
        pass
except:
    pass
