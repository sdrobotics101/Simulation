import time
import sys
sys.path.append("../Dependencies/PythonSharedBuffers/src")

from Sensor import *
from Serialization import *

import pydsm

linear  = Linear()
angular = Angular()

# X, Y, Z
linear.pos[0] = 0
linear.pos[1] = 0
linear.pos[2] = 0

linear.vel[0] = 0
linear.vel[1] = 0
linear.vel[2] = 0

linear.acc[0] = 0
linear.acc[1] = 0
linear.acc[2] = 0

angular.vel[0] = 0
angular.vel[0] = 0
angular.vel[0] = 0

angular.acc[0] = 0
angular.acc[0] = 0
angular.acc[0] = 0

# W, X, Y, Z
angular.pos[0] = 1
angular.pos[1] = 0
angular.pos[2] = 0
angular.pos[3] = 0

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
