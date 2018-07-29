import time
import cmd
from bitstring import BitArray
import sys
import math
sys.path.append("../Dependencies/PythonSharedBuffers/src")
sys.path.append("../../../DistributedSharedMemory")

from Master import *
from Serialization import *
from Constants import *

from Sensor import *
from QuaternionFuncs import *

import pydsm

def quaternion_to_euler_angle(q):
    w, x, y, z = q
    ysqr = y * y
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + ysqr)
    ex = math.degrees(math.atan2(t0, t1))
    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    ey = math.degrees(math.asin(t2))
    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (ysqr + z * z)
    ez = math.degrees(math.atan2(t3, t4))
    return ex, ey, ez

SERVERID = MASTER_SERVER_ID
CLIENTID = 100

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
for i in range(3):
    angular.pos[i] = 0
    angular.vel[i] = 0
    angular.acc[i] = 0
    linear.pos[i]  = 0
    linear.vel[i]  = 0
    linear.acc[i]  = 0
angular.pos[0] = 1
angular.pos[3] = 0

# Default values
# Angular X POS 0 0
# Angular Y POS 0 0
# Angular Z POS 0 0
# Linear  X VEL 0
# Linear  Y VEL 0
# Linear  Z POS 0 0
controlInput.angular[xaxis].pos[0] = 0
controlInput.angular[xaxis].pos[1] = 0

controlInput.angular[yaxis].pos[0] = 0
controlInput.angular[yaxis].pos[1] = 0

controlInput.angular[zaxis].pos[0] = 0
controlInput.angular[zaxis].pos[1] = 0

controlInput.linear[xaxis].vel = 0

controlInput.linear[yaxis].vel = 0

controlInput.linear[zaxis].pos[0] = 0
controlInput.linear[zaxis].pos[1] = 0

mode = [0,0,POS,VEL,VEL,POS,POS,POS]
controlInput.mode = BitArray(mode).uint

sensorReset.pos[xaxis] = 0
sensorReset.pos[yaxis] = 0
sensorReset.pos[zaxis] = 0
sensorReset.reset      = False

client = pydsm.Client(SERVERID, CLIENTID, True)

client.registerLocalBuffer(MASTER_CONTROL,      sizeof(ControlInput), False)
client.registerLocalBuffer(MASTER_SENSOR_RESET, sizeof(SensorReset),  False)
time.sleep(0.1)

client.registerRemoteBuffer("angular", "10.0.0.43", 43)
client.registerRemoteBuffer("linear", "10.0.0.43", 43)
time.sleep(0.1)

client.setLocalBufferContents(MASTER_CONTROL,      Pack(controlInput))
client.setLocalBufferContents(MASTER_SENSOR_RESET, Pack(sensorReset))

def update():
    controlInput.mode = BitArray(mode).uint
    client.setLocalBufferContents(MASTER_CONTROL, Pack(controlInput))

def resetSensor(x, y ,z):
    sensorReset.pos[xaxis] = x
    sensorReset.pos[yaxis] = y
    sensorReset.pos[zaxis] = z
    sensorReset.reset = not sensorReset.reset
    client.setLocalBufferContents(MASTER_SENSOR_RESET, Pack(sensorReset))

def lpx(pos, t = 0):
    controlInput.linear[xaxis].pos[0] = pos
    controlInput.linear[xaxis].pos[1] = t
    mode[MODE_LINEAR_X] = POS
    update()

def rlpx(pos, t = 0):
    linearData, active = client.getRemoteBufferContents("linear", "10.0.0.43", 43)
    if (active):
        linear = Unpack(Linear, linearData)
        controlInput.linear[xaxis].pos[0] = linear.pos[xaxis] + pos
        controlInput.linear[xaxis].pos[1] = t
        mode[MODE_LINEAR_X] = POS
        update()
        print("New setpoint: "+str(controlInput.linear[xaxis].pos[0]))
    else:
        print("No sensor input")

def lpy(pos, t = 0):
    controlInput.linear[yaxis].pos[0] = pos
    controlInput.linear[yaxis].pos[1] = t
    mode[MODE_LINEAR_Y] = POS
    update()

def rlpy(pos, t = 0):
    linearData, active = client.getRemoteBufferContents("linear", "10.0.0.43", 43)
    if (active):
        linear = Unpack(Linear, linearData)
        controlInput.linear[yaxis].pos[0] = linear.pos[yaxis] + pos
        controlInput.linear[yaxis].pos[1] = t
        mode[MODE_LINEAR_Y] = POS
        update()
        print("New setpoint: "+str(controlInput.linear[yaxis].pos[0]))
    else:
        print("No sensor input")

def lpz(pos, t = 0):
    controlInput.linear[zaxis].pos[0] = pos
    controlInput.linear[zaxis].pos[1] = t
    mode[MODE_LINEAR_Z] = POS
    update()

def rlpz(pos, t = 0):
    linearData, active = client.getRemoteBufferContents("linear", "10.0.0.43", 43)
    if (active):
        linear = Unpack(Linear, linearData)
        controlInput.linear[zaxis].pos[0] = linear.pos[zaxis] + pos
        controlInput.linear[zaxis].pos[1] = t
        mode[MODE_LINEAR_Z] = POS
        update()
        print("New setpoint: "+str(controlInput.linear[zaxis].pos[0]))
    else:
        print("No sensor input")

def lvx(vel):
    controlInput.linear[xaxis].vel = vel
    mode[MODE_LINEAR_X] = VEL
    update()

def lvy(vel):
    controlInput.linear[yaxis].vel = vel
    mode[MODE_LINEAR_Y] = VEL
    update()

def lvz(vel):
    controlInput.linear[zaxis].vel = vel
    mode[MODE_LINEAR_Z] = VEL
    update()

def apx(pos, t = 0):
    controlInput.angular[xaxis].pos[0] = pos
    controlInput.angular[xaxis].pos[1] = t
    mode[MODE_ANGULAR_X] = POS
    update()

def rapx(pos, t = 0):
    angularData, active = client.getRemoteBufferContents("angular", "10.0.0.43", 43)
    if (active):
        angular = Unpack(Angular, angularData)
        # orientation = (angular.pos[QUAT_W],
        #                angular.pos[QUAT_X],
        #                angular.pos[QUAT_Y],
        #                angular.pos[QUAT_Z])
        # try:
        #     orientation = q_conjugate(normalize(orientation))
        # except ZeroDivisionError:
        #     orientation = (1, 0, 0, 0)

        # euler = quaternion_to_euler_angle(orientation)

        # sensor was rigged to output euler angles through acc field
        controlInput.angular[xaxis].pos[0] = angular.acc[xaxis] + pos
        controlInput.angular[xaxis].pos[1] = t
        while controlInput.angular[xaxis].pos[0] > 180:
            controlInput.angular[xaxis].pos[0] = controlInput.angular[xaxis].pos[0] - 360
        while controlInput.angular[xaxis].pos[0] < -180:
            controlInput.angular[xaxis].pos[0] = controlInput.angular[xaxis].pos[0] + 360
        mode[MODE_ANGULAR_X] = POS
        update()
        print("New setpoint: "+str(controlInput.angular[xaxis].pos[0]))
    else:
        print("No sensor input")

def apy(pos, t = 0):
    controlInput.angular[yaxis].pos[0] = pos
    controlInput.angular[yaxis].pos[1] = t
    mode[MODE_ANGULAR_Y] = POS
    update()

def rapy(pos, t = 0):
    angularData, active = client.getRemoteBufferContents("angular", "10.0.0.43", 43)
    if (active):
        angular = Unpack(Angular, angularData)
        # orientation = (angular.pos[QUAT_W],
        #                angular.pos[QUAT_X],
        #                angular.pos[QUAT_Y],
        #                angular.pos[QUAT_Z])
        # try:
        #     orientation = q_conjugate(normalize(orientation))
        # except ZeroDivisionError:
        #     orientation = (1, 0, 0, 0)

        # euler = quaternion_to_euler_angle(orientation)

        # sensor was rigged to output euler angles through acc field
        controlInput.angular[yaxis].pos[0] = angular.acc[yaxis] + pos
        controlInput.angular[yaxis].pos[1] = t
        while controlInput.angular[yaxis].pos[0] > 180:
            controlInput.angular[yaxis].pos[0] = controlInput.angular[yaxis].pos[0] - 360
        while controlInput.angular[yaxis].pos[0] < -180:
            controlInput.angular[yaxis].pos[0] = controlInput.angular[yaxis].pos[0] + 360
        mode[MODE_ANGULAR_Y] = POS
        update()
        print("New setpoint: "+str(controlInput.angular[yaxis].pos[0]))
    else:
        print("No sensor input")

def apz(pos, t = 0):
    controlInput.angular[zaxis].pos[0] = pos
    controlInput.angular[zaxis].pos[1] = t
    mode[MODE_ANGULAR_Z] = POS
    update()

def rapz(pos, t = 0):
    angularData, active = client.getRemoteBufferContents("angular", "10.0.0.43", 43)
    if (active):
        angular = Unpack(Angular, angularData)
        # orientation = (angular.pos[QUAT_W],
        #                angular.pos[QUAT_X],
        #                angular.pos[QUAT_Y],
        #                angular.pos[QUAT_Z])
        # try:
        #     orientation = q_conjugate(normalize(orientation))
        # except ZeroDivisionError:
        #     orientation = (1, 0, 0, 0)

        # euler = quaternion_to_euler_angle(orientation)

        # sensor was rigged to output euler angles through acc field
        controlInput.angular[zaxis].pos[0] = angular.acc[zaxis] + pos
        controlInput.angular[zaxis].pos[1] = t
        while controlInput.angular[zaxis].pos[0] > 180:
            controlInput.angular[zaxis].pos[0] = controlInput.angular[zaxis].pos[0] - 360
        while controlInput.angular[zaxis].pos[0] < -180:
            controlInput.angular[zaxis].pos[0] = controlInput.angular[zaxis].pos[0] + 360
        mode[MODE_ANGULAR_Z] = POS
        update()
        print("New setpoint: "+str(controlInput.angular[zaxis].pos[0]))
    else:
        print("No sensor input")

def avx(vel):
    controlInput.angular[xaxis].vel = vel
    mode[MODE_ANGULAR_X] = VEL
    update()

def avy(vel):
    controlInput.angular[yaxis].vel = vel
    mode[MODE_ANGULAR_Y] = VEL
    update()

def avz(vel):
    controlInput.angular[zaxis].vel = vel
    mode[MODE_ANGULAR_Z] = VEL
    update()

class CubeceptionHelm(cmd.Cmd):
    intro = 'Ahoy'
    prompt = '(voodoo) '

    def do_rs(self, arg):
        'reset linear position'
        resetSensor(*parse(arg))

    def do_lpx(self, arg):
        'set linear position x'
        lpx(*parse(arg))

    def do_rlpx(self, arg):
        'set relative linear position x'
        rlpx(*parse(arg))

    def do_lpy(self, arg):
        'set linear position y'
        lpy(*parse(arg))

    def do_rlpy(self, arg):
        'set relative linear position y'
        rlpy(*parse(arg))

    def do_lpz(self, arg):
        'set linear position z'
        lpz(*parse(arg))

    def do_rlpz(self, arg):
        'set relative linear position z'
        rlpz(*parse(arg))

    def do_lvx(self, arg):
        'set linear velocity x'
        lvx(*parse(arg))

    def do_lvy(self, arg):
        'set linear velocity y'
        lvy(*parse(arg))

    def do_lvz(self, arg):
        'set linear velocity z'
        lvz(*parse(arg))

    def do_apx(self, arg):
        'set angular position x'
        apx(*parse(arg))

    def do_rapx(self, arg):
        'set relative angular position x'
        rapx(*parse(arg))

    def do_apy(self, arg):
        'set angular position y'
        apy(*parse(arg))

    def do_rapy(self, arg):
        'set relative angular position y'
        rapy(*parse(arg))

    def do_apz(self, arg):
        'set angular position z'
        apz(*parse(arg))

    def do_rapz(self, arg):
        'set relative angular position z'
        rapz(*parse(arg))

    def do_avx(self, arg):
        'set angular velocity x'
        avx(*parse(arg))

    def do_avy(self, arg):
        'set angular velocity y'
        avy(*parse(arg))

    def do_avz(self, arg):
        'set angular velocity z'
        avz(*parse(arg))

    def do_exit(self, arg):
        'exit Cubeception Helm'
        print('Walkin\' the plank')
        return True

def parse(arg):
    'Convert a series of zero or more numbers to an argument tuple'
    return tuple(map(float, arg.split()))

if __name__ == '__main__':
    running = True
    while(running):
        try:
            CubeceptionHelm().cmdloop()
            running = False
        except:
            print('Ye scurrvy dog')
            running = True
