import time
import sys
sys.path.append("../Dependencies/PythonSharedBuffers/src")

from Navigation import *
from Serialization import *

import pydsm

SERVERID = MOTOR_SERVER_ID
CLIENTID = 100

outputs = Outputs()
for i in range(8):
    outputs.motors[i] = i * 10

health = Health()
health.saturated = 0x00
health.direction = 0x00

kill = Kill()
kill.isKilled = True

client = pydsm.Client(SERVERID, 100, True)

client.registerLocalBuffer("outputs", sizeof(Outputs), False)
client.registerLocalBuffer("health", sizeof(Health), False)
client.registerLocalBuffer("kill", sizeof(Kill), False)
time.sleep(0.1)

if (client.setLocalBufferContents("outputs", Pack(outputs))):
    print("set outputs")
if (client.setLocalBufferContents("health", Pack(health))):
    print("set health")
if (client.setLocalBufferContents("kill", Pack(kill))):
    print("set kill")

try:
    while True:
        pass
except:
    pass
