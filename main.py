import serial # Import Serial Library
from pushover import Pushover # Import Pushover Library
import time # Import Time Library
import yaml
from yaml.loader import SafeLoader
with open('config.yaml') as config_file:
    data = yaml.load(config_file, Loader=SafeLoader)
    print(data)




""" 
print("Starting")
connected = False
COMPortName = "COM4" # Change this to your COM port name
print("Trying to open + " + COMPortName)
ser = serial.Serial(COMPortName, 1440, timeout=1)
print("Connected")
print("Opened COM4")
print("Entering main loop")
ser.write(b'SYN\n')
while True:
    try:
        readOut = ser.readline().decode('ascii')
    except:
        pass 
"""