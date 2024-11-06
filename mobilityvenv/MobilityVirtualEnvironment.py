# ****************************************************
# Module Purpose: Simulates the behavior of the real City system (Bologna neighborhoods)
#                 characterized by roads equipped with traffic flow sensors.
#                 The traffic Loop sensors measure the number of passing cars
#                 on a road during a given time slot. This simulation uses
#                 real traffic data obtained from Bologna Open Data.
#
#                 Each device has a unique ID and an API key (alphanumeric string
#                 randomly generated). These are required to register the device
#                 to FIWARE IoT Agent, which is responsible for handling the
#                 devices' registration and sending their measurements to
#                 the Digital Twin system.
#
# Inputs:   (function --setupPhysicalSystem--) agentInstance: The IoT Agent entity to
#                      which devices will register, and through which they will send
#                      their measurements.
#           (function --startPhysicalSystem--) roads: The road dictionary, previously created
#                     in the setupPhysicalSystem function, describing the real city as
#                     roads, their sensors and actuators.
#
# Returns: (function --setupPhysicalSystem--) A dictionary of roads, each associated with one or
#                    more traffic loop sensors. The roads and their associated devices
#                    are initialized and returned along with the list of files processed,
#                    allowing further processing or simulation of data transmission.
# ****************************************************


from libraries.constants import *
from mobilityvenv.PhysicalSystemConnector import *
from libraries.classes.Agent import Agent
import datetime


selectedTimeSlot = "00:00-01:00"
tempTimeSlot = str(datetime.time(0).strftime("%H:00"))+'-'+str(datetime.time(1).strftime("%H:00"))
tlColumnsNames = ["index", "road_name", "ID_loop",  "geopoint", "direction"]


def setupPhysicalSystem(agentInstance: Agent) -> tuple[dict,list]:
    road = {}
    roadSensorIndex = {}
    trafficLoop = {}
    naturalNumber = 1
    keyLength = 26

    [trafficData, files] = readingFiles(tlPath)
    for i, file in enumerate(files):
        # TODO: ID_univoco_stazione_spira should not be read.
        trafficData[file] = trafficData[file][["index", "Nome via", "ID_univoco_stazione_spira", "geopoint", "direzione"]]
        trafficData[file].columns = tlColumnsNames

    # Initialization of Physical System entities (road) and attached devices (traffic loop sensors)
    # TODO: traffic lights should be attached to the respective road as actuators.
    for i, file in enumerate(files):
        if not agentInstance.isServiceGroupRegistered("TrafficLoopDevices"):
            trafficLoopKey = generate_random_key(keyLength)
        else:
            trafficLoopKey = agentInstance.getServiceGroupKey("TrafficLoopDevices")

        for key, rows in trafficData[file].iterrows():
            roadName = rows['road_name']
            if roadName not in road:
                roadPartialIdentifier = "R{:03d}".format(naturalNumber)
                road[roadName] = PhysicalSystemConnector(roadPartialIdentifier, roadName)
                roadSensorIndex[roadName] = 0
                naturalNumber += 1
            # Attaching the sensor to the road, checking if it already exists.
            trafficLoopID = str(rows['ID_loop'])
            trafficLoopPartialIdentifier = "TL{}".format(trafficLoopID)
            if not road[roadName].sensorExist(trafficLoopPartialIdentifier):
                trafficLoop[roadSensorIndex[roadName]] = Sensor(device_partialid=trafficLoopPartialIdentifier,
                                                                devicekey=trafficLoopKey, name="TL",
                                                                sensortype="Traffic Loop")
                trafficLoop[roadSensorIndex[roadName]].setDataCallback(agentInstance.retrievingData)
                road[roadName].addSensor(trafficLoop[roadSensorIndex[roadName]])
                roadSensorIndex[roadName] += 1

            if not agentInstance.isDeviceRegistered(trafficLoopPartialIdentifier):
                road[roadName].saveConnectedDevice(outputPath)


    # Device and Measurement Registration to the IoT Agent
    deviceEntityType = "Device"
    for i in road:
        for sensor in road[i].sensors:
            if not agentInstance.isDeviceRegistered(str(sensor.devicePartialID)):
                # Service Group Registration
                agentResponse = agentInstance.serviceGroupRegistration(api_key=sensor.apiKey, entity_type=deviceEntityType)
                if agentResponse is not None:
                    entityType = "Device"
                    timezone = "Europe/Rome"
                    staticAttribute = "urn:ngsi-ld:Road:{}".format(road[i].partialIdentifier)
                    if sensor.name == "TL":
                        measurementType = "trafficFlow"
                        agentInstance.measurementRegistration(measure_type=measurementType,
                                                              device_id=sensor.devicePartialID,
                                                              entity_type=entityType, timezone=timezone,
                                                              controlled_asset=staticAttribute)
                    else:
                        raise TypeError("Only Traffic Flow sensors are allowed")
    return road, files

def startPhysicalSystem(roads: dict[int, PhysicalSystemConnector]):
    """
    Starts the simulation of data transmission for each Road containing one or more Traffic Loop sensors.

    :param roads: A dictionary of roads initialized in the setupPhysicalSystem function.
    """

    [trafficData, files] = readingFiles(tlPath)
    for i, file in enumerate(files):
        tlColumnsNames = ["index", "date", "flow", "road_name", "ID_loop", "geopoint", "direction"]
        for i in range(23):
            # the time slot column reports the number of cars that passed through a traffic loop sensor during that time frame (the traffic flow in that slot)
            tempTimeSlot = str(datetime.time(i).strftime("%H:00")) + '-' + str(datetime.time(i+1).strftime("%H:00"))
            tempData = trafficData[file][["index", "data", tempTimeSlot, "Nome via", "ID_univoco_stazione_spira", "geopoint", "direzione"]]
            tempData.columns = tlColumnsNames
            processingTlData(tempTimeSlot, tempData, roads)
            time.sleep(10)
