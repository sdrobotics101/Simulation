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

import pydsm

COUNT_THRESH = 5
DEPTH_THRESH_ABOVE = 0.35
DEPTH_THRESH_BELOW = 0.35
TARGET_DEPTH = 1.0
FORWARD_VEL = 100

XAXIS = 0
YAXIS = 1
ZAXIS = 2

SERVER_ID = MASTER_SERVER_ID
CLIENT_ID = 93

SENSOR_IP = "10.0.0.43"
SENSOR_ID = 43

NAVIGATION_IP = "10.0.0.44"
NAVIGATION_ID = 44

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

kill.isKilled = False

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
time.sleep(0.1)
print("Registered remote buffers: angular,linear,kill")

ABOVE = True
BELOW = False
def waitForDepth(depth_threshold, count_threshold, condition):
    print("Waiting for depth " + \
          ("ABOVE " if condition == ABOVE else "BELOW ") + \
          str(depth_threshold) + \
          " for " + \
          str(count_threshold) + \
          " counts")
    count = 0
    while count < count_threshold:
        linearData, active = client.getRemoteBufferContents("linear", SENSOR_IP, SENSOR_ID)
        if active:
            linear = Unpack(Linear, linearData)
            depth = linear.pos[ZAXIS]
            # ABOVE - check that robot is above a certain depth
            # BELOW - check that robot is below a certain depth
            if condition == ABOVE:
                count = count + 1 if depth < depth_threshold else 0
            else:
                count = count + 1 if depth > depth_threshold else 0
        else:
            count = 0
        time.sleep(1)
    print("Finished waiting")

KILLED   = True
UNKILLED = False
def waitForKill(state):
    print("Waiting for " + \
          ("KILL" if state == KILLED else "UNKILL"))
    while True:
        killData, active = client.getRemoteBufferContents("kill", ipaddress, serverid)
        if active:
            kill = Unpack(Kill, killData)
            if kill.isKilled == state:
                break
        time.sleep(1)
    print("Finished waiting")

# Point and shoot follows the following logic:
#     start:
#         wait for depth below point - user wants to lock heading
#         lock heading
#         set control buffer
#         wait for unkill - robot started
#         wait for kill - run complete
#         unset control buffer
#         wait for depth above point - robot reset at the surface
#         goto start


while True:
    # wait for depth to be below point
    waitForDepth(DEPTH_THRESH_BELOW, COUNT_THRESH, BELOW)
    # get heading data from sensor
    angularData, active = client.getRemoteBufferContents("angular", SENSOR_IP, SENSOR_ID)
    if active:
        angular = Unpack(Angular, angularData)

        # get heading

        # w = angular.pos[QUAT_W]
        # x = angular.pos[QUAT_X]
        # y = angular.pos[QUAT_Y]
        # z = angular.pos[QUAT_Z]
        # x = -x
        # y = -y
        # z = -z

        # t3 = (2 * ((w * z) + (x * y)))
        # t4 = (1 - (2 * ((y * y) + (z * z))))

        # heading = 180 * math.atan2(t3, t4) / math.pi

        # sensor was rigged to publish euler angles through acc field
        heading = angular.acc[ZAXIS]
        print("Following heading: " + str(heading))

        # set control buffer
        controlInput.angular[ZAXIS].pos[0] = heading
        controlInput.linear[XAXIS].vel = FORWARD_VEL
        controlInput.linear[ZAXIS].pos[0] = TARGET_DEPTH

        # write control buffer
        client.setLocalBufferContents("control", Pack(controlInput))

        # wait for unkill - robot started
        waitForKill(UNKILLED)

        # wait for kill - diver stopped robot
        waitForKill(KILLED)

        # unset control buffer
        controlInput.angular[ZAXIS].pos[0] = 0
        controlInput.linear[XAXIS].vel = 0
        controlInput.linear[ZAXIS].pos[0] = 0

        # write control buffer
        client.setLocalBufferContents("control", Pack(controlInput))

        # wait for depth to be above point
        waitForDepth(DEPTH_THRESH_ABOVE, COUNT_THRESH, ABOVE)
