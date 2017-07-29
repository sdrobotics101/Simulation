import time
import sys
import math
from bitstring import BitArray
sys.path.append("../Dependencies/PythonSharedBuffers/src")
sys.path.append("../../../DistributedSharedMemory")

from Master import *
from Sensor import *
from Serialization import *
from Constants import *

import pydsm

WAIT_THRESH = 5
DEPTH_THRESH = 0.35
TARGET_DEPTH = 1.0
FORWARD_VEL = 320

XAXIS = 0
YAXIS = 1
ZAXIS = 2

SERVER_ID = 42
CLIENT_ID = 93

SENSOR_IP = "10.0.0.43"
SENSOR_ID = 43

NAVIGATION_IP = "10.0.0.43"
NAVIGATION_ID = 43

# Bit indices for mode byte
MODE_ANGULAR_X = 7
MODE_ANGULAR_Y = 6
MODE_ANGULAR_Z = 5
MODE_LINEAR_X  = 4
MODE_LINEAR_Y  = 3
MODE_LINEAR_Z  = 2

# Set bit on for position, off for velocity
POS = 1
VEL = 0

controlInput = ControlInput()
sensorReset = SensorReset()
angular = Angular()
linear = Linear()

# Default values
# Angular X POS 0 0
# Angular Y POS 0 0
# Angular Z POS 0 0
# Linear  X VEL 0
# Linear  Y VEL 0
# Linear  Z POS 0 0
controlInput.angular[XAXIS].pos[0] = 0
controlInput.angular[XAXIS].pos[1] = 0

controlInput.angular[YAXIS].pos[0] = 0
controlInput.angular[YAXIS].pos[1] = 0

controlInput.angular[ZAXIS].pos[0] = 0
controlInput.angular[ZAXIS].pos[1] = 0

controlInput.linear[XAXIS].vel = 0

controlInput.linear[YAXIS].vel = 0

controlInput.linear[ZAXIS].pos[0] = 0
controlInput.linear[ZAXIS].pos[1] = 0

mode = [0,0,POS,VEL,VEL,POS,POS,POS]
controlInput.mode = BitArray(mode).uint

sensorReset.pos[XAXIS] = 0
sensorReset.pos[YAXIS] = 0
sensorReset.pos[ZAXIS] = 0
sensorReset.reset      = False

for i in range(3):
    angular.pos[i] = 0
    angular.vel[i] = 0
    angular.acc[i] = 0
    linear.pos[i]  = 0
    linear.vel[i]  = 0
    linear.acc[i]  = 0
angular.pos[0] = 1
angular.pos[3] = 0

client = pydsm.Client(SERVER_ID, CLIENT_ID, True)
print("instantiated client")

client.registerLocalBuffer(MASTER_SENSOR_RESET, sizeof(SensorReset),  False)
time.sleep(0.1)
client.setLocalBufferContents(MASTER_SENSOR_RESET, Pack(sensorReset))
print("created local buffer: sensorreset")

client.registerRemoteBuffer("angular", SENSOR_IP, SENSOR_ID)
client.registerRemoteBuffer("linear", SENSOR_IP, SENSOR_ID)
time.sleep(0.1)
print("registered remote buffers: angular,linear")

def waitForDepth():
    count = 0
    while count < WAIT_THRESH:
        linearData, active = client.getRemoteBufferContents("linear", SENSOR_IP, SENSOR_ID)
        if active:
            linear = Unpack(Linear, linearData)
            depth = linear.pos[ZAXIS]
            print("depth: " + str(depth))
            if depth > DEPTH_THRESH:
                count = count + 1
                print("count: " + str(count))
            else:
                count = 0
                print("reset count")
        else:
            print("inactive: linear")
            count = 0
        time.sleep(1)
    return

while True:
    waitForDepth()
    print("finished waiting for depth")
    angularData, active = client.getRemoteBufferContents("angular", SENSOR_IP, SENSOR_ID)
    if active:
        angular = Unpack(Angular, angularData)
        w = angular.pos[QUAT_W]
        x = angular.pos[QUAT_X]
        y = angular.pos[QUAT_Y]
        z = angular.pos[QUAT_Z]
        x = -x
        y = -y
        z = -z

        t3 = (2 * ((w * z) + (x * y)))
        t4 = (1 - (2 * ((y * y) + (z * z))))

        heading = 180 * math.atan2(t3, t4) / math.pi
        print("heading: " + str(heading))

        controlInput.angular[ZAXIS].pos[0] = heading
        controlInput.angular[ZAXIS].pos[1] = 0

        controlInput.linear[XAXIS].vel = FORWARD_VEL

        controlInput.linear[ZAXIS].pos[0] = TARGET_DEPTH
        controlInput.linear[ZAXIS].pos[1] = 0

        client.registerLocalBuffer("control", sizeof(ControlInput), False)
        time.sleep(0.1)
        client.setLocalBufferContents("control", Pack(controlInput))
        print("set control buffer")

        while True:
            time.sleep(10)
    else:
        print("inactive: angular")
