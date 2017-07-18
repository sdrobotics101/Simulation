import time
import cmd
import sys
from bitstring import BitArray
sys.path.append("../Dependencies/PythonSharedBuffers/src")

from Navigation import *
from Serialization import *
from Constants import *

import pydsm

SERVERID = MOTOR_SERVER_ID
CLIENTID = 100

LINEAR_NAME  = "linear"
ANGULAR_NAME = "angular"

linearCommand = PhysicalOutput()
linearCommand.force[xaxis]  = 0
linearCommand.force[yaxis]  = 0
linearCommand.force[zaxis]  = 0
linearCommand.torque[xaxis] = 0
linearCommand.torque[yaxis] = 0
linearCommand.torque[zaxis] = 0

angularCommand = PhysicalOutput()
angularCommand.force[xaxis]  = 0
angularCommand.force[yaxis]  = 0
angularCommand.force[zaxis]  = 0
angularCommand.torque[xaxis] = 0
angularCommand.torque[yaxis] = 0
angularCommand.torque[zaxis] = 0

client = pydsm.Client(SERVERID, CLIENTID, True)

client.registerLocalBuffer(LINEAR_NAME, sizeof(linearCommand), False)
client.registerLocalBuffer(ANGULAR_NAME, sizeof(angularCommand), False)
time.sleep(0.1)

client.setLocalBufferContents(LINEAR_NAME, Pack(linearCommand))
client.setLocalBufferContents(ANGULAR_NAME, Pack(angularCommand))

def update():
    client.setLocalBufferContents(LINEAR_NAME, Pack(linearCommand))
    client.setLocalBufferContents(ANGULAR_NAME, Pack(angularCommand))

def lx(force):
    linearCommand.force[xaxis] = force
    update()

def ly(force):
    linearCommand.force[yaxis] = force
    update()

def lz(force):
    linearCommand.force[zaxis] = force
    update()

def ax(torque):
    angularCommand.torque[xaxis] = torque
    update()

def ay(torque):
    angularCommand.torque[yaxis] = torque
    update()

def az(torque):
    angularCommand.torque[zaxis] = torque
    update()

class CubeceptionHelm(cmd.Cmd):
    intro = 'Ahoy'
    prompt = '(voodoo) '

    def do_lx(self, arg):
        'set force x'
        lx(*parse(arg))

    def do_ly(self, arg):
        'set force y'
        ly(*parse(arg))

    def do_lz(self, arg):
        'set force z'
        lz(*parse(arg))

    def do_ax(self, arg):
        'set torque x'
        ax(*parse(arg))

    def do_ay(self, arg):
        'set torque y'
        ay(*parse(arg))

    def do_az(self, arg):
        'set torque z'
        az(*parse(arg))

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
