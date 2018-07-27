import argparse
import curses
import time
import sys
sys.path.append("../Dependencies/PythonSharedBuffers/src")
sys.path.append("../../../DistributedSharedMemory")

from Navigation import *
from Serialization import *

import pydsm

SERVERID = 254
CLIENTID = 100

outputs = Outputs()
for i in range(8):
    outputs.motors[i] = 0

health = Health()
health.saturated = 0
health.direction = 0

angular = PhysicalOutput()
linear  = PhysicalOutput()
for i in range(3):
    angular.force[i]  = 0
    angular.torque[i] = 0
    linear.force[i]   = 0
    linear.torque[i]  = 0

kill = Kill()
kill.isKilled = False

client = pydsm.Client(SERVERID, CLIENTID, True)

def main(stdscr):
    try:
        global outputs
        global health
        global angular
        global linear
        global kill

        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        while(True):
            stdscr.clear()

            outputsData, active = client.getRemoteBufferContents("outputs", ipaddress, serverid)
            if (active):
                stdscr.addstr(0, 0, "OUTPUTS", curses.color_pair(2))
                outputs = Unpack(Outputs, outputsData)
            else:
                stdscr.addstr(0, 0, "OUTPUTS", curses.color_pair(1))
            for i in range(8):
                stdscr.addstr(i+1, 0, str(i)+": "+str(round(outputs.motors[i], 2)))

            healthData, active = client.getRemoteBufferContents("health", ipaddress, serverid)
            if (active):
                stdscr.addstr(0, 20, "HEALTH", curses.color_pair(2))
                health = Unpack(Health, healthData)
            else:
                stdscr.addstr(0, 20, "HEALTH", curses.color_pair(1))
            for i in range(8):
                stdscr.addstr(i+1, 20, str(i)+":")
                if health.saturated & (1 << i):
                    if health.direction & (1 << i):
                        stdscr.addstr(i+1, 23, "+", curses.color_pair(1))
                    else:
                        stdscr.addstr(i+1, 23, "-", curses.color_pair(1))
                else:
                    stdscr.addstr(i+1, 23, ".", curses.color_pair(2))

            angularData, active = client.getRemoteBufferContents("angular", ipaddress, serverid)
            if (active):
                stdscr.addstr(0, 40, "ANGULAR", curses.color_pair(2))
                angular = Unpack(PhysicalOutput, angularData)
            else:
                stdscr.addstr(0, 40, "ANGULAR", curses.color_pair(1))
            stdscr.addstr(1, 40, "TX: "+str(round(angular.torque[0], 2)))
            stdscr.addstr(2, 40, "TY: "+str(round(angular.torque[1], 2)))
            stdscr.addstr(3, 40, "TZ: "+str(round(angular.torque[2], 2)))

            linearData, active = client.getRemoteBufferContents("linear", ipaddress, serverid)
            if (active):
                stdscr.addstr(0, 60, "LINEAR", curses.color_pair(2))
                linear = Unpack(PhysicalOutput, linearData)
            else:
                stdscr.addstr(0, 60, "LINEAR", curses.color_pair(1))
            stdscr.addstr(1, 60, "FX: "+str(round(linear.force[0], 2)))
            stdscr.addstr(2, 60, "FY: "+str(round(linear.force[1], 2)))
            stdscr.addstr(3, 60, "FZ: "+str(round(linear.force[2], 2)))

            killData, active = client.getRemoteBufferContents("kill", ipaddress, serverid)
            if (active):
                kill = Unpack(Kill, killData)
                if (kill.isKilled):
                    stdscr.addstr(0, 80, "KILLED", curses.color_pair(1))
                else:
                    stdscr.addstr(0, 80, "ACTIVE", curses.color_pair(2))
            else:
                stdscr.addstr(0, 80, "INACTIVE", curses.color_pair(3))

            stdscr.refresh()
            time.sleep(0.1)
    except KeyboardInterrupt:
        return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Navigation Viewer")
    parser.add_argument('ipaddress', nargs=1, help='ipaddress of remote server')
    parser.add_argument('serverid', nargs=1, type=int, help='server ID of remote server')
    args = parser.parse_args()

    global ipaddress
    global serverid
    ipaddress = str(args.ipaddress[0])
    serverid = int(args.serverid[0])

    client.registerRemoteBuffer("outputs", ipaddress, serverid)
    client.registerRemoteBuffer("health", ipaddress, serverid)
    client.registerRemoteBuffer("angular", ipaddress, serverid)
    client.registerRemoteBuffer("linear", ipaddress, serverid)
    client.registerRemoteBuffer("kill", ipaddress, serverid)
    time.sleep(0.1)

    curses.wrapper(main)
