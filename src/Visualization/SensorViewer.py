import argparse
import curses
import time
import sys
sys.path.append("../Dependencies/PythonSharedBuffers/src")

from Sensor import *
from Serialization import *
from Constants import *

import pydsm

SERVERID = 254
CLIENTID = 101

data = Data()
for i in range(3):
    data.accelerometer[i] = 0
    data.gyro[i] = 0
    data.magnetometer[i] = 0
    data.isEnabled[i] = False
data.pressureSensor = 0
data.isEnabled[3] = False

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

def main(stdscr):
    try:
        global data
        global linear
        global angular

        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        while(True):
            stdscr.clear()

            dataData, active = client.getRemoteBufferContents("data", ipaddress, serverid)
            if (active):
                stdscr.addstr(0, 0, "DATA", curses.color_pair(2))
                data = Unpack(Data, dataData)
            else:
                stdscr.addstr(0, 0, "DATA", curses.color_pair(1))
                for i in range(4):
                    data.isEnabled[i] = False
            if (data.isEnabled[0]):
                stdscr.addstr(1, 1, "ACCL:", curses.color_pair(2))
            else:
                stdscr.addstr(1, 1, "ACCL:", curses.color_pair(3))
            if (data.isEnabled[1]):
                stdscr.addstr(5, 1, "GYRO:", curses.color_pair(2))
            else:
                stdscr.addstr(5, 1, "GYRO:", curses.color_pair(3))
            if (data.isEnabled[2]):
                stdscr.addstr(9, 1, "MAGN:", curses.color_pair(2))
            else:
                stdscr.addstr(9, 1, "MAGN:", curses.color_pair(3))
            if (data.isEnabled[3]):
                stdscr.addstr(13, 1, "PRES:", curses.color_pair(2))
            else:
                stdscr.addstr(13, 1, "PRES:", curses.color_pair(3))

            stdscr.addstr(2, 2, "X: "+str(round(data.accelerometer[xaxis], 2)))
            stdscr.addstr(3, 2, "Y: "+str(round(data.accelerometer[yaxis], 2)))
            stdscr.addstr(4, 2, "Z: "+str(round(data.accelerometer[zaxis], 2)))
            stdscr.addstr(6, 2, "X: "+str(round(data.gyro[xaxis], 2)))
            stdscr.addstr(7, 2, "Y: "+str(round(data.gyro[yaxis], 2)))
            stdscr.addstr(8, 2, "Z: "+str(round(data.gyro[zaxis], 2)))
            stdscr.addstr(10, 2, "X: "+str(round(data.magnetometer[xaxis], 2)))
            stdscr.addstr(11, 2, "Y: "+str(round(data.magnetometer[yaxis], 2)))
            stdscr.addstr(12, 2, "Z: "+str(round(data.magnetometer[zaxis], 2)))
            stdscr.addstr(14, 2, "P: "+str(round(data.pressureSensor, 2)))

            angularData, active = client.getRemoteBufferContents("angular", ipaddress, serverid)
            if (active):
                stdscr.addstr(0, 20, "ANGULAR", curses.color_pair(2))
                angular = Unpack(Angular, angularData)
            else:
                stdscr.addstr(0, 20, "ANGULAR", curses.color_pair(1))

            stdscr.addstr(1, 21, "POS")
            stdscr.addstr(2, 22, "W: "+str(round(angular.pos[QUAT_W], 2)))
            stdscr.addstr(3, 22, "X: "+str(round(angular.pos[QUAT_X], 2)))
            stdscr.addstr(4, 22, "Y: "+str(round(angular.pos[QUAT_Y], 2)))
            stdscr.addstr(5, 22, "Z: "+str(round(angular.pos[QUAT_Z], 2)))

            stdscr.addstr(6, 21, "VEL")
            stdscr.addstr(7, 22, "X: "+str(round(angular.vel[xaxis], 2)))
            stdscr.addstr(8, 22, "Y: "+str(round(angular.vel[yaxis], 2)))
            stdscr.addstr(9, 22, "Z: "+str(round(angular.vel[zaxis], 2)))

            stdscr.addstr(10, 21, "ACC")
            stdscr.addstr(11, 22, "X: "+str(round(angular.acc[xaxis], 2)))
            stdscr.addstr(12, 22, "Y: "+str(round(angular.acc[yaxis], 2)))
            stdscr.addstr(13, 22, "Z: "+str(round(angular.acc[zaxis], 2)))

            linearData, active = client.getRemoteBufferContents("linear", ipaddress, serverid)
            if (active):
                stdscr.addstr(0, 40, "LINEAR", curses.color_pair(2))
                linear = Unpack(Linear, linearData)
            else:
                stdscr.addstr(0, 40, "LINEAR", curses.color_pair(1))

            stdscr.addstr(1, 41, "POS")
            stdscr.addstr(2, 42, "X: "+str(round(linear.pos[xaxis], 2)))
            stdscr.addstr(3, 42, "Y: "+str(round(linear.pos[yaxis], 2)))
            stdscr.addstr(4, 42, "Z: "+str(round(linear.pos[zaxis], 2)))

            stdscr.addstr(5, 41, "VEL")
            stdscr.addstr(6, 42, "X: "+str(round(linear.vel[xaxis], 2)))
            stdscr.addstr(7, 42, "Y: "+str(round(linear.vel[yaxis], 2)))
            stdscr.addstr(8, 42, "Z: "+str(round(linear.vel[zaxis], 2)))

            stdscr.addstr(9, 41, "ACC")
            stdscr.addstr(10, 42, "X: "+str(round(linear.acc[xaxis], 2)))
            stdscr.addstr(11, 42, "Y: "+str(round(linear.acc[yaxis], 2)))
            stdscr.addstr(12, 42, "Z: "+str(round(linear.acc[zaxis], 2)))

            stdscr.refresh()
            time.sleep(0.1)
    except KeyboardInterrupt:
        return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sensor Viewer")
    parser.add_argument('ipaddress', nargs=1, help='ipaddress of remote server')
    parser.add_argument('serverid', nargs=1, type=int, help='server ID of remote server')
    args = parser.parse_args()

    global ipaddress
    global serverid
    ipaddress = str(args.ipaddress[0])
    serverid = int(args.serverid[0])

    client.registerRemoteBuffer("data", ipaddress, serverid)
    client.registerRemoteBuffer("angular", ipaddress, serverid)
    client.registerRemoteBuffer("linear", ipaddress, serverid)
    time.sleep(0.1)

    curses.wrapper(main)
