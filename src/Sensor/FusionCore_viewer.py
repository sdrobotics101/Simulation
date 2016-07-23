import time
import sys
sys.path.append("../Dependencies/PythonSharedBuffers/src")

from Sensor import *
from Serialization import *

import pydsm

linear  = Linear()
angular = Angular()

client = pydsm.Client(254, 200, True)

client.registerRemoteBuffer("linear", "127.0.0.1", 43)
time.sleep(0.1)

data, active = client.getRemoteBufferContents("linear", "127.0.0.1", 43)

linear = Unpack(Linear, data)
print(linear.pos[0])
print(linear.pos[1])
print(linear.pos[2])
print(linear.vel[0])
print(linear.vel[1])
print(linear.vel[2])
print(linear.acc[0])
print(linear.acc[1])
print(linear.acc[2])
