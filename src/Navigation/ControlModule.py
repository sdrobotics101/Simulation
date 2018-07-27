import time
import sys
sys.path.append("../Dependencies/PythonSharedBuffers/src")

from Navigation import *
from Serialization import *
from Constants import *

import pydsm

SERVERID = MOTOR_SERVER_ID
CLIENTID = 101

angular = PhysicalOutput()
linear  = PhysicalOutput()
for i in range(3):
    angular.force[i]  = 0
    angular.torque[i] = i
    linear.force[i]   = i+3
    linear.torque[i]  = 0

client = pydsm.Client(SERVERID, CLIENTID, True)

client.registerLocalBuffer("angular", sizeof(PhysicalOutput), False)
client.registerLocalBuffer("linear", sizeof(PhysicalOutput), False)
time.sleep(0.1)

if (client.setLocalBufferContents("angular", Pack(angular))):
    print("set angular")
if (client.setLocalBufferContents("linear", Pack(linear))):
    print("set linear")

try:
    while True:
        pass
except:
    pass
