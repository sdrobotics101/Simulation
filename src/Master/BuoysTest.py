import time
import sys
import math
from bitstring import BitArray
sys.path.append("../Dependencies/PythonSharedBuffers/src")
sys.path.append("../../../DistributedSharedMemory")

from Master import *
from Sensor import *
from Navigation import *
from Serialization import *
from Constants import *
from Vision import *

import pydsm

TARGET_DEPTH = 1.5 # meters
FORWARD_SLOW_VEL = 0 # raw
SETTLING_TIME = 5 # seconds

XAXIS = 0
YAXIS = 1
ZAXIS = 2

SERVER_ID = MASTER_SERVER_ID
CLIENT_ID = 139

SENSOR_IP = "10.0.0.43"
SENSOR_ID = 43

NAVIGATION_IP = "10.0.0.44"
NAVIGATION_ID = 44

FORWARD_IP = "10.0.0.45"
FORWARD_ID = 45

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
kill = Kill()
location = Location()

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

kill.isKilled = True

location.x = 0
location.y = 0
location.z = 0
location.confidence = 0
location.loc_type = 0

client = pydsm.Client(SERVER_ID, CLIENT_ID, True)

client.registerLocalBuffer("control", sizeof(ControlInput), False)
client.registerLocalBuffer(MASTER_SENSOR_RESET, sizeof(SensorReset),  False)
time.sleep(0.5)
client.setLocalBufferContents("control", Pack(controlInput))
client.setLocalBufferContents(MASTER_SENSOR_RESET, Pack(sensorReset))
print("Created local buffers: control, sensorreset")

client.registerRemoteBuffer("angular", SENSOR_IP, SENSOR_ID)
client.registerRemoteBuffer("linear", SENSOR_IP, SENSOR_ID)
client.registerRemoteBuffer("kill", NAVIGATION_IP, NAVIGATION_ID)
client.registerRemoteBuffer("targetlocation", FORWARD_IP, FORWARD_ID)
time.sleep(0.5)
print("Registered remote buffers: angular,linear,kill,targetlocation")

KILLED   = True
UNKILLED = False
def waitForKill(state):
    print("Waiting for " + \
          ("KILL" if state == KILLED else "UNKILL"))
    while True:
        killData, active = client.getRemoteBufferContents("kill", NAVIGATION_IP, NAVIGATION_ID)
        if active:
            kill = Unpack(Kill, killData)
            if kill.isKilled == state:
                break
        time.sleep(1)
    print("Finished waiting")

def isRobotKilled():
    global kill
    killData, active = client.getRemoteBufferContents("kill", NAVIGATION_IP, NAVIGATION_ID)
    if active:
        kill = Unpack(Kill, killData)
        return kill.isKilled
    else:
        return True

angularData, active = client.getRemoteBufferContents("angular", SENSOR_IP, SENSOR_ID)
if active:
    angular = Unpack(Angular, angularData)
else:
    print("no sensor input")
    exit(0)

# set control buffer
controlInput.angular[ZAXIS].pos[0] = angular.acc[ZAXIS]
controlInput.linear[ZAXIS].pos[0] = TARGET_DEPTH

# write control buffer
client.setLocalBufferContents("control", Pack(controlInput))
print("set control buffer")

# wait for unkill - robot started
waitForKill(UNKILLED)

# wait for robot to settle
time.sleep(SETTLING_TIME)

# attempt buoys
while not isRobotKilled():
    locationData, loc_active = client.getRemoteBufferContents("targetlocation", FORWARD_IP, FORWARD_ID)
    angularData, ang_active = client.getRemoteBufferContents("angular", SENSOR_IP, SENSOR_ID)
    linearData, lin_active = client.getRemoteBufferContents("linear", SENSOR_IP, SENSOR_ID)
    if loc_active and ang_active and lin_active:
        location = Unpack(Location, locationData)
        angular = Unpack(Angular, angularData)
        linear = Unpack(Linear, linearData)
        if location.y or location.z:
            controlInput.linear[XAXIS].vel = 0

            controlInput.linear[ZAXIS].pos[0] = controlInput.linear[ZAXIS].pos[0] + (0.1 * location.z)
            if controlInput.linear[ZAXIS].pos[0] > 3:
                controlInput.linear[ZAXIS].pos[0] = 3
            if controlInput.linear[ZAXIS].pos[0] < 1:
                controlInput.linear[ZAXIS].pos[0] = 1

            controlInput.angular[ZAXIS].pos[0] = controlInput.angular[ZAXIS].pos[0] + (10 * location.y)
            while controlInput.angular[ZAXIS].pos[0] > 180:
                controlInput.angular[ZAXIS].pos[0] = controlInput.angular[ZAXIS].pos[0] - 360
            while controlInput.angular[ZAXIS].pos[0] < -180:
                controlInput.angular[ZAXIS].pos[0] = controlInput.angular[ZAXIS].pos[0] + 360
        else:
            controlInput.linear[XAXIS].vel = FORWARD_SLOW_VEL
    else:
        controlInput.linear[XAXIS].vel = 0
    client.setLocalBufferContents("control", Pack(controlInput))
    time.sleep(1)

# unset control buffer
controlInput.angular[ZAXIS].pos[0] = 0
controlInput.linear[XAXIS].vel = 0
controlInput.linear[ZAXIS].pos[0] = 0

# write control buffer
client.setLocalBufferContents("control", Pack(controlInput))
