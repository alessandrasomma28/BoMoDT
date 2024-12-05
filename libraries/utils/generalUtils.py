import os
import pandas as pd
import string
import secrets
import time
from datetime import datetime, timedelta
import random
from threading import Event

def readingFiles(folder: str):
    """
    Read all CSV files in the specified folder, using the file names as dictionary keys.

    Each CSV file is read with `;` as the separator, and the data is stored in a dictionary with
    the file names (without extensions) as keys. It also returns a list of these file names.

    :param folder: Path to the folder containing CSV files.
    :return: Tuple of two elements:
             - data (dict): Dictionary where each key is a file name (without extension), and each value is the data
               from the corresponding CSV file as a DataFrame.
             - files (list): List of file names (without extensions) for the loaded CSV files.
    """
    files = os.listdir(folder)
    data = {}

    for i, file in enumerate(files):
        file_path = os.path.join(folder, file)
        key = os.path.splitext(file)[0]  # Remove .csv extension to use file name as dictionary key
        data[key] = pd.read_csv(file_path, sep=';')  # Read CSV with ; as the separator
        files[i] = key  # Replace the original file name in `files` with the name without extension

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


firstTimeslotEvent = Event()
def processingTlData(timeSlot, trafficData, roads: dict, firstTimeSlot : str ="00:00-01:00"):
    allFirstTimeslotDataSent = (timeSlot == firstTimeSlot)
    for index, row in trafficData.iterrows():
        trafficFlow = row["flow"]
        raw_coordinates = row["geopoint"]
        longitude, latitude = map(float, raw_coordinates.split(','))
        coordinates=[longitude,latitude]
        direction = str(row["direction"])
        roadName = row['road_name']
        date = row['date']
        if roadName in roads:
            trafficLoopIdentifier= "TL{}".format(str(row["ID_loop"]))
            trafficLoopSensor = roads[roadName].getSensor(trafficLoopIdentifier)
            if trafficLoopSensor is not None and trafficLoopSensor.name == "TL":
                trafficLoopSensor.sendData(date, timeSlot, trafficFlow, coordinates, direction,
                                           device_id=trafficLoopSensor.devicePartialID,
                                           device_key=trafficLoopSensor.apiKey)
                # If this row is not part of the first timeslot, unset the flag
        if timeSlot != firstTimeSlot:
            allFirstTimeslotDataSent = False

        time.sleep(1) #simulating a sort of delay among entries
        # If this is the first timeslot and all rows are processed, set the event
    if allFirstTimeslotDataSent:
        firstTimeslotEvent.set()
        print(f"All data for the first timeslot ({firstTimeSlot}) across the dataset has been sent.")

#Function to convert geopoint format having a number without dots
def convert_format(value):
    return value.replace('.', '')  # Rimuovi solo il primo punto

# Function to convert a date expressed as a string in ISO format
import random
from datetime import datetime, timedelta

def convertDate(date: str, timeslot: str):
    """
    Convert a date and timeslot into an ISO 8601 formatted datetime string with a random delay.

    :param date: Date in 'yyyy-mm-dd' format.
    :param timeslot: Time slot in 'HH:MM-HH:MM' 24-hour format.
    :return: ISO 8601 formatted datetime string with a random delay.
    """
    # Parse the date in 'yyyy-mm-dd' format
    year, month, day = map(int, date.split("-"))
    # Extract start and end times in 24-hour format
    start_time, end_time = timeslot.split("-")
    end_hour_24 = int(end_time.split(":")[0])
    # Generate a random delay in minutes (between 0 and 10)
    random_delay = random.randint(0, 10)
    # Combine date and end time to create a datetime object for the end time of the timeslot
    base_time = datetime(year, month, day, end_hour_24, 0)
    # Add the random delay in minutes to the base time
    final_time = base_time + timedelta(minutes=random_delay)
    # Format as ISO 8601 with 24-hour time
    d = final_time.strftime("%Y-%m-%dT%H:%M:%S") + "Z"
    return d

