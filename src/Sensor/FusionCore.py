import time
import sys
sys.path.append("../Dependencies/PythonSharedBuffers/src")

from Sensor import *
from Serialization import *

import pydsm

linear  = Linear()
angular = Angular()

for i in range(3):
    linear.pos[i] = 0
    linear.vel[i] = 0
    linear.acc[i] = 0
    angular.pos[i] = 0
    angular.vel[i] = 0
    angular.acc[i] = 0
angular.pos[3] = 1

client = pydsm.Client(43, 100, True)

client.registerLocalBuffer("linear", sizeof(Linear), False)
client.registerLocalBuffer("angular", sizeof(Angular), False)
time.sleep(0.1)

if (client.setLocalBufferContents("linear", Pack(linear))):
    print("set linear")
if (client.setLocalBufferContents("angular", Pack(angular))):
    print("set angular")

try:
    while True:
        pass
except:
    pass
