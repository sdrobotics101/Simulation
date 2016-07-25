import time
import cmd
import sys
sys.path.append("../Dependencies/PythonSharedBuffers/src")

from Sensor import *
from Serialization import *
from Constants import *

import pydsm

SERVERID = SENSOR_SERVER_ID
CLIENTID = 102

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

client = pydsm.Client(SERVERID, CLIENTID, True)

client.registerLocalBuffer(SENSORS_ANGULAR, sizeof(Angular), False)
client.registerLocalBuffer(SENSORS_LINEAR,  sizeof(Linear),  False)
time.sleep(0.1)

client.setLocalBufferContents(SENSORS_ANGULAR, Pack(angular))
client.setLocalBufferContents(SENSORS_LINEAR,  Pack(linear))

def update():
    client.setLocalBufferContents(SENSORS_ANGULAR, Pack(angular))
    client.setLocalBufferContents(SENSORS_LINEAR,  Pack(linear))

def ap(w, x, y, z):
    angular.pos[QUAT_W] = w
    angular.pos[QUAT_X] = x
    angular.pos[QUAT_Y] = y
    angular.pos[QUAT_Z] = z
    update()

def av(x, y, z):
    angular.vel[xaxis] = x
    angular.vel[yaxis] = y
    angular.vel[zaxis] = z
    update()

def aa(pos, time):
    angular.acc[xaxis] = x
    angular.acc[yaxis] = y
    angular.acc[zaxis] = z
    update()

def lp(x, y, z):
    linear.pos[xaxis] = x
    linear.pos[yaxis] = y
    linear.pos[zaxis] = z
    update()

def lv(x, y, z):
    linear.vel[xaxis] = x
    linear.vel[yaxis] = y
    linear.vel[zaxis] = z
    update()

def la(x, y, z):
    linear.acc[xaxis] = x
    linear.acc[yaxis] = y
    linear.acc[zaxis] = z
    update()

class Sensor(cmd.Cmd):
    intro = 'Sensor'
    prompt = '(sensor) '

    def do_ap(self, arg):
        'set angular position'
        ap(*parse(arg))

    def do_av(self, arg):
        'set angular velocity'
        av(*parse(arg))

    def do_aa(self, arg):
        'set angular acceleration'
        aa(*parse(arg))

    def do_lp(self, arg):
        'set linear position'
        lp(*parse(arg))

    def do_lv(self, arg):
        'set linear velocity'
        lv(*parse(arg))

    def do_la(self, arg):
        'set linear acceleration'
        la(*parse(arg))

    def do_exit(self, arg):
        'exit Sensor CLI'
        print('Exiting')
        return True

def parse(arg):
    'Convert a series of zero or more numbers to an argument tuple'
    return tuple(map(float, arg.split()))

if __name__ == '__main__':
    running = True
    while(running):
        try:
            Sensor().cmdloop()
            running = False
        except:
            print('Error')
            running = True
