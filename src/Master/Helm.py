import time
import cmd
from bitstring import BitArray
import sys
sys.path.append("../Dependencies/PythonSharedBuffers/src")

from Master import *
from Serialization import *
from Constants import *

import pydsm

SERVERID = 42
CLIENTID = 103

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

client.setLocalBufferContents(MASTER_CONTROL,      Pack(controlInput))
client.setLocalBufferContents(MASTER_SENSOR_RESET, Pack(sensorReset))

def update():
    controlInput.mode = BitArray(mode).uint
    client.setLocalBufferContents(MASTER_CONTROL, Pack(controlInput))

def resetSensor(arg):
    sensorReset.pos[xaxis] = arg[xaxis]
    sensorReset.pos[yaxis] = arg[yaxis]
    sensorReset.pos[zaxis] = arg[zaxis]
    sensorReset.reset = not sensorReset.reset
    client.setLocalBufferContents(MASTER_SENSOR_RESET, Pack(sensorReset))

def lpx(pos, time):
    controlInput.linear[xaxis].pos[0] = pos
    controlInput.linear[xaxis].pos[1] = time
    mode[MODE_LINEAR_X] = POS
    update()

def lpy(pos, time):
    controlInput.linear[yaxis].pos[0] = pos
    controlInput.linear[yaxis].pos[1] = time
    mode[MODE_LINEAR_Y] = POS
    update()

def lpz(pos, time):
    controlInput.linear[zaxis].pos[0] = pos
    controlInput.linear[zaxis].pos[1] = time
    mode[MODE_LINEAR_Z] = POS
    update()

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

def apx(pos, time):
    controlInput.angular[xaxis].pos[0] = pos
    controlInput.angular[xaxis].pos[1] = time
    mode[MODE_ANGULAR_X] = POS
    update()

def apy(pos, time):
    controlInput.angular[yaxis].pos[0] = pos
    controlInput.angular[yaxis].pos[1] = time
    mode[MODE_ANGULAR_Y] = POS
    update()

def apz(pos, time):
    controlInput.angular[zaxis].pos[0] = pos
    controlInput.angular[zaxis].pos[1] = time
    mode[MODE_ANGULAR_Z] = POS
    update()

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

    def do_lpy(self, arg):
        'set linear position y'
        lpy(*parse(arg))

    def do_lpz(self, arg):
        'set linear position z'
        lpz(*parse(arg))

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

    def do_apy(self, arg):
        'set angular position y'
        apy(*parse(arg))

    def do_apz(self, arg):
        'set angular position z'
        apz(*parse(arg))

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
