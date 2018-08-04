import argparse
import curses
import time
import sys
sys.path.append("../Dependencies/PythonSharedBuffers/src")
sys.path.append("../../../DistributedSharedMemory")

from Master import *
from Serialization import *
from Constants import *

import pydsm

import math

SERVERID = 254
CLIENTID = 102

MASTER_IP = 10.0.0.42
MASTER_ID = 42

XAXIS = 0
YAXIS = 1
ZAXIS = 2

controlInput = ControlInput()

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

client = pydsm.Client(SERVERID, CLIENTID, True)

def main(stdscr):
    try:
        global controlInput

        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        while(True):
            stdscr.clear()

            controlInputData, active = client.getRemoteBufferContents("control", ipaddress, serverid)
            if (active):
                stdscr.addstr(0, 0, "CONTROL", curses.color_pair(2))
                controlInput = Unpack(ControlInput, controlInputData)
            else:
                stdscr.addstr(0, 0, "CONTROL", curses.color_pair(1))
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
            stdscr.addstr(1, 1, "ANGULAR:", curses.color_pair(2))
            stdscr.addstr(2, 2, "X: "+str(controlInput.angular[XAXIS].pos[0]))
            stdscr.addstr(3, 2, "Y: "+str(controlInput.angular[YAXIS].pos[1]))
            stdscr.addstr(4, 2, "Z: "+str(controlInput.angular[ZAXIS].pos[2]))

            stdscr.addstr(5, 1, "LINEAR:", curses_color_pair(2))
            stdscr.addstr(6, 2, "X: "+str(controlInput.linear[XAXIS].vel))
            stdscr.addstr(7, 2, "Y: "+str(controlInput.linear[YAXIS].vel))
            stdscr.addstr(8, 2, "Z: "+str(controlInput.linear[ZAXIS].pos[0]))

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

    client.registerRemoteBuffer("control", ipaddress, serverid)
    time.sleep(0.1)

    curses.wrapper(main)
