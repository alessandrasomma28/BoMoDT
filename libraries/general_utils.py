import os
import pandas as pd
import string
import secrets
import time
from datetime import datetime

def readingFiles(folder):
    files = os.listdir(folder)
    data = {}
    for i, file in enumerate(files):
        file_path = os.path.join(folder, file)
        key = os.path.splitext(file)[
            0]  # remove .csv extension to use file name as key value to access the data dictionary
        data[key] = pd.read_csv(file_path)
        files[i] = key
    return data, files

def generate_random_key(length):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))

def loadEnvVar(file_path):
    env_vars = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()  # remove whitespace
            if line and not line.startswith('#'):  # line is not a comment
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()  # removing leading or trailing spaces
    return env_vars

# function to calculate difference between actual and previous date time of dataset entries to properly simulate devices

def convert_float(inp):
    splitted_data = inp.split(",")
    return float(splitted_data[-2]), float(splitted_data[-1])

''' PREVIOUS FUNCTION --> TO BE DELETED
def processingTlData(trafficData, trafficLoop):
    # for key, values in trafficData.items():
        # iterate through registered devices
        for ind, device in trafficLoop.items():
            # look for sensor belonging to device (only one in the traffic loop case)
            for sensor in device.sensors:
                if sensor.name == "TFO":
                    tl = trafficData.loc[trafficData["ID_loop"] == int(sensor.device_partial_id)]
                    flow = tl["flow"].values[0]
                    coordinates = tl["geopoint"].values[0]
                    # coordinates = list(map(float, coordinates))
                    coordinates = convert_float(coordinates)
                    direction = str(tl["direction"].values[0])
                    sensor.send_data(flow, coordinates, direction, device_id=sensor.device_partial_id, device_key=sensor.api_key)
'''

def processingTlData(timeSlot, trafficData, roads: dict):
    for index, row in trafficData.iterrows():
        trafficFlow = row["flow"]
        raw_coordinates = row["geopoint"]
        latitude, longitude = map(float, raw_coordinates.split(','))
        coordinates=[latitude,longitude]
        direction = str(row["direction"])
        roadName = row['road_name']
        if roadName in roads:
            trafficLoopIdentifier= "TL{}".format(str(row["ID_loop"]))
            trafficLoopSensor = roads[roadName].getSensor(trafficLoopIdentifier)
            if trafficLoopSensor is not None and trafficLoopSensor.name == "TL":
                trafficLoopSensor.sendData(timeSlot, trafficFlow, coordinates, direction,
                                           device_id=trafficLoopSensor.devicePartialID,
                                           device_key=trafficLoopSensor.apiKey)
        time.sleep(10) #simulating a sort of delay among entries


#Function to convert geopoint format having a number without dots
def convert_format(value):
    return value.replace('.', '')  # Rimuovi solo il primo punto
