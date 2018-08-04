import sys

sys.path.insert(0, "DistributedSharedMemory/build")
sys.path.insert(0, "PythonSharedBuffers/src")

import pydsm
import time
from Sensor import *
from Master import *
from Vision import *

if __name__ == "__main__":
     #register or remote need time.sleep(0.1)
    print("Deadreckoning through the gate")
    time.sleep(23)
    print("Through the gate")
    
    print("establishing the client")
    #listen to the sensor, motor and vision
    client = pydsm.Client(MASTER_SERVER_ID, 66, True)
    client.registerLocalBuffer(MASTER_CONTROL, sizeof(ControlInput), False)
    client.registerLocalBuffer(MASTER_GOALS, sizeof(Goals), False)
    client.registerLocalBuffer(MASTER_SENSOR_RESET, sizeof(SensorReset), False)
    time.sleep(1)

    control_input = ControlInput()
    goals = Goals()
    sensor_reset = SensorReset()
    client.setLocalBufferContents(MASTER_CONTROL, Pack(control_input))
    client.setLocalBufferContents(MASTER_GOALS, Pack(goals))
    client.setLocalBufferContents(MASTER_SENSOR_RESET, Pack(sensor_reset))

    print("eastablishing the sensor, motor and vision")
    #tells dsm what you are listening or publishing
    client.registerRemoteBuffer(SENSORS_LINEAR, sizeof(Linear), False)
    client.registerRemoteBuffer(SENSORS_ANGULAR, sizeof(Angular), False)
    client.registerRemoteBuffer(MOTOR_KILL, sizeof(Kill), False)
    client.registerRemoteBuffer(TARGET_LOCATION, sizeof(LocationArray), False)
    time.sleep(1)
    print("connection established")
    
    while True:
        count = 0
        local_confidence = 100 #same as the original setting from vision
        while True:
            #in this while looop, need to constantly check the vision confidence level
            data, active = client.getRemoteBufferContents(TARGET_LOCATION, FORWARD_VISION_SERVER_IP, FORWARD_VISION_SERVER_ID)
            time.sleep(0.1)
            if active:
                local_confidence = Unpack(LocationAndRotation, confidence)
            else:
                print("inactive forward vision")
                continue
            if local_confidence != 100:
                count+=1    #one iteration
                if count > 25: #if 25 continuous data reading not 100, then its a solid reading
                    print("confident about the data from vision")
                    # need to stop the AUV
                    pos, active = client.getRemoteBufferContents(SENSORS_LINEAR, SENSOR_SERVER_IP, SENSOR_SERVER_ID)
                    time.sleep(0.1)
                    current_location = Unpack(Linear, pos)
                    current_z = current_location.pos[ZAXIS]
                    controlInput.linear[XAXIS].vel = 0
                    controlInput.linear[YAXIS].vel = 0
                    controlInput.linear[ZAXIS].pos[POSITION] = current_z
                    controlInput.linear[ZAXIS].pos[TIME] = 0
                    client.setLocalBufferContents(MASTER_CONTROL, Pack(controlInput))
                    print("stopped the AUV")
                    break
            else:
                local_confidence = 100
                count = 0
                continue

        print("Receiving buoys' location and update the location")
        data, active = client.getRemoteBufferContents(TARGET_LOCATION, FORWARD_VISION_SERVER_IP, FORWARD_VISION_SERVER_ID)
        time.sleep(0.1)
        #time to gather the x, y,z from the vision and pack it down to the vision
        #NOT in north east down
        target_x = Unpack(LocationAndRotation, x)
        target_y = Unpack(LocationAndRotation, y)
        target_z = Unpack(LocationAndRotation, z)
        #convert them to the North east down
        x = -target_x
        y = -target_y
        z = -target_z
        print("received the x,y,x for buoy")
       
        print("Receiving the current location")
        pos, active = client.getRemoteBufferContents(SENSORS_LINEAR, SENSOR_SERVER_IP, SENSOR_SERVER_ID)
        time.sleep(0.1)
        current_location = Unpack(Linear, pos)
        current_x = current_location.pos[XAXIS]
        current_y = current_location.pos[YAXIS]
        current_z = current_location.pos[ZAXIS]
        print("received the current location")
        
        
        controlInput.linear[XAXIS].vel = 0 #the robot shouldn't move forward or backward
        controlInput.linear[YAXIS].vel = 0
        controlInput.linear[ZAXIS].pos[POSITION] = z-current_z #the amount of depth need to move
        controlInput.linear[ZAXIS].pos[TIME] = 0
        client.setLocalBufferContents(MASTER_CONTROL, Pack(controlInput))
        time.sleep(0.1)
        print("reaching the buoy targeted depth")
        
        print("calculating the heading towards the buoy")
        t3 = (2 * ((w * z) + (x * y)))
        t4 = (1 - (2 * ((y * y) + (z * z))))
        heading = 180 * math.atan2(t3, t4) / math.pi
        #from Rahul point and shoot to update the heading from the North East Down convention
        #XAXIS is roll
        #YAXIS is pitch
        #ZAXIS is yaw
        controlInput.angular[ZAXIS].pos[0] = heading
        controlInput.angular[ZAXIS].pos[1] = 0
        client.setLocalBufferContents(MASTER_CONTROL, Pack(controlInput))
        time.sleep(0.1)
        print("packed back to the angular sensor in yaw")


