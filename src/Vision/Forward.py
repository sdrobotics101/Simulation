import time
import cmd
import sys
sys.path.append("../Dependencies/PythonSharedBuffers/src")

from Vision import *
from Serialization import *
from Constants import *

import pydsm

SERVERID = FORWARD_VISION_SERVER_ID
CLIENTID = 100

locationArray = LocationArray()
for i in range(3):
    locationArray.locations[i].x = 0
    locationArray.locations[i].y = 0
    locationArray.locations[i].z = 0
    locationArray.locations[i].confidence = 0
    locationArray.locations[i].loctype    = NONE

client = pydsm.Client(SERVERID, CLIENTID, True)

client.registerLocalBuffer(TARGET_LOCATION, sizeof(LocationArray), False)
time.sleep(0.1)

client.setLocalBufferContents(TARGET_LOCATION, Pack(locationArray))

def update():
    client.setLocalBufferContents(TARGET_LOCATION, Pack(locationArray))

# set location
def sl(i, x, y, z):
    locationArray.locations[i].x = x
    locationArray.locations[i].y = y
    locationArray.locations[i].z = z
    update()

# set confidence
def sc(i, confidence):
    locationArray.locations[i].confidence = confidence
    update()

# set type
def st(i, loctype):
    locationArray.locations[i].loctype = loctype
    update()

class Forward(cmd.Cmd):
    intro = 'Forward Vision'
    prompt = '(forward) '

    def do_sl(self, arg):
        'set location'
        sl(*parse(arg))

    def do_sc(self, arg):
        'set confidence'
        sc(*parse(arg))

    def do_st(self, arg):
        'set type'
        st(*parse(arg))

    def do_exit(self, arg):
        'exit Forward Vision CLI'
        print('Exiting')
        return True

def parse(arg):
    'Convert a series of zero or more numbers to an argument tuple'
    return tuple(map(float, arg.split()))

if __name__ == '__main__':
    running = True
    while(running):
        try:
            Forward().cmdloop()
            running = False
        except:
            print('Error')
            running = True
