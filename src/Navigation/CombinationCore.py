import time
import sys
sys.path.append("../Dependencies/PythonSharedBuffers/src")

from Navigation import *
from Serialization import *

import pydsm

outputs = Outputs()

for i in range(8):
    outputs.motors[i] = i/10.0

client = pydsm.Client(44, 102, True)

client.registerLocalBuffer("outputs", sizeof(Outputs), False)
time.sleep(0.1)

if (client.setLocalBufferContents("outputs", Pack(outputs))):
    print("set outputs")

try:
    while True:
        pass
except:
    pass
