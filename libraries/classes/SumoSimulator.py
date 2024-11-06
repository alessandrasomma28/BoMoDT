# ****************************************************
# Module Purpose:
#   This library defines the Simulator class, which is responsible for interacting with the sumoenv Simulator.
#   The Simulator class manages the running of the simulation, from its start to its completion.
#
#   It provides various methods for controlling the simulation, gathering data on vehicles, induction loops,
#   and managing traffic lights using the libtraci library for communication with the sumoenv Simulator and the
#   running simulation inside it.
#
# ****************************************************

from libraries.constants import *
from statistics import mean
import os
# These libraries are quite the same. They include most of the commands available in the traci library, but the
# time performance better. Libtraci addresses some limitation of the libsumo library, in particular the multiple client
# communication with the simulation.
import libtraci
import traci.constants as tc


class Simulator:
    """
    The Simulator class provides an interface to interact with the sumoenv traffic simulation
    environment using the libtraci library.

    Attributes:
        configurationPath (str): Path to the sumoenv configuration file.
        routePath (str): Path to the route file used in the simulation.
        logFile (str): Path to the file where logs are saved.
        listener (libtraci.StepListener): A listener object for simulation steps.
        vehicleSummary (dict): A dictionary to store vehicle data summaries.

    Class Methods:
        - __init__: Constructor to initialize a new instance of the Simulator class.
        - start: Method to start the sumoenv simulation with or without the GUI.
        - startBasic: Method to start the basic sumoenv simulation configuration.
        - startCongestioned: Method to start the sumoenv simulation with congestion.
        - step: Method to execute a defined number of simulation steps.
        - oneHourStep: Method to advance the simulation by one hour (3600 seconds).
        - resume: Method to resume the simulation until no more vehicles remain.
        - end: Method to end the simulation and close the connection to sumoenv.
        - getRemainingVehicles: Method to retrieve the number of remaining vehicles in the simulation.
        - changeRoutePath: Method to change the route path for the simulation.
        - getVehiclesSummary: Method to gather and return vehicle statistics from the simulation.
        - getDetectorList: Method to get a list of all induction loop detectors.
        - getAverageOccupationTime: Method to calculate the average occupation time for all detectors.
        - getInductionLoopSummary: Method to calculate summary statistics for induction loops.
        - findLinkedTLS: Method to find traffic light systems (TLS) linked to a detector.
        - subscribeToInductionLoop: Method to subscribe to induction loop data.
        - checkSubscription: Method to monitor subscription results for induction loops and modify traffic light programs.
        - getTLSList: Method to retrieve a list of all traffic light systems (TLS).
        - checkTLS: Method to check if a given TLS exists in the simulation.
        - setTLSProgram: Method to set the traffic light program for a TLS or all TLSs.
    ""
    """

    def __init__(self, configurationPath: str, logFile: str):
        """
        Initializes the Simulator with the given configuration file and log file.

        :param configurationPath: Path to the sumoenv configuration file.
        :param logFile: Path to the log file where simulation logs will be saved.
        """
        self.configurationPath = configurationPath
        # TODO: check if this routePath variable is needed.
        self.routePath = configurationPath
        staticpath = os.path.abspath(self.configurationPath + "static")
        if not os.path.exists(staticpath):
            print("Error: the given path does not exist.")
            return

        os.environ["STATICPATH"] = staticpath
        self.logFile = logFile
        self.listener = ValueListener()
        libtraci.addStepListener(self.listener)

    def start(self, activeGui=False):
        """
        Starts the sumoenv simulation with or without the graphical user interface (GUI) based on the activeGui parameter.
        If a simulation is already loaded, it will be overwritten.

        :param activeGui: If True, starts the simulation with the sumoenv GUI (sumo-gui).
                         If False, starts the simulation without the GUI (sumo). Default is False.
        :raises RuntimeError: If there is an issue starting the sumoenv simulation.
        """
        if libtraci.simulation.isLoaded():
            print("Warning: there was a previous simulation loaded. It will be overwritten")
        command = ["sumo-gui" if activeGui else "sumo", "-c", self.configurationPath + "run.sumocfg"]
        libtraci.start(command, traceFile=self.logFile)
        print("Note that a simulation step is equivalent to " + str(libtraci.simulation.getDeltaT()) + " seconds")
        self.resume()

    def startBasic(self, activeGui=False):
        """
        Starts the sumoenv simulation with a basic configuration.
        If a simulation is already loaded, it will be overwritten.

        :param activeGui: If True, starts the simulation with the sumoenv GUI (sumo-gui).
                         If False, starts the simulation without the GUI (sumo). Default is False.
        :raises RuntimeError: If there is an issue starting the sumoenv simulation.
        """

        # TODO: CHECK PERCHE' SEMBRA NON FUNZIONARE
        if libtraci.simulation.isLoaded():
            print("Warning: there was a previous simulation loaded. It will be overwritten")
        command = ["sumo-gui" if activeGui else "sumo", "-c", self.configurationPath + "/basic/run.sumocfg"]
        libtraci.start(command, traceFile=self.logFile)
        self.resume()

    def startCongestioned(self, activeGui=False):
        """
        Starts the sumoenv simulation with a congestioned scenario.
        If a simulation is already loaded, it will be overwritten.

        :param activeGui: If True, starts the simulation with the sumoenv GUI (sumo-gui).
                         If False, starts the simulation without the GUI (sumo). Default is False.
        :raises RuntimeError: If there is an issue starting the sumoenv simulation.
        """

        if libtraci.simulation.isLoaded():
            print("Warning: there was a previous simulation loaded. It will be overwritten")
        command = ["sumo-gui" if activeGui else "sumo", "-c", self.configurationPath + "/congestioned/run.sumocfg"]
        libtraci.start(command, traceFile=self.logFile)
        self.resume()

    def step(self, quantity=1):
        """
        Executes a defined number of steps in the simulation (by default one step).
        Typically, one step corresponds to one second of simulation time.

        :param quantity: The number of steps to execute. Default is 1.
        :raises RuntimeError: If the simulation encounters an issue during stepping.
        """
        step = 0
        while step < quantity and self.getRemainingVehicles() > 0:
            libtraci.simulationStep()
            self.vehiclesSummary = self.getVehiclesSummary()
            self.checkSubscription()
            self.getInductionLoopSummary()
            # self.setTLSProgram("219", "utopia")
            print(self.getRemainingVehicles())
            step += 1

    def oneHourStep(self):
        """
        Executes a one-hour simulation step. This advances the simulation by 3600 seconds if there are vehicles
        still in the simulation.

        :raises RuntimeError: If there is an issue performing the one-hour step.
        """
        if libtraci.simulation.getMinExpectedNumber() > 0:
            libtraci.simulationStep(3600)

    def resume(self):
        """
        Resumes the simulation, running continuously until no more vehicles remain in the simulation.
        After the simulation completes, the connection to sumoenv is closed.

        :raises RuntimeError: If the simulation fails to resume or end.
        """
        while libtraci.simulation.getMinExpectedNumber() > 0:
            self.step()
        self.end()

    def end(self):
        """
        Ends the simulation and closes the connection to sumoenv.

        :return: True if the connection was successfully closed, False otherwise.
        :raises RuntimeError: If there is an issue closing the connection.
        """
        return libtraci.close()

    def getRemainingVehicles(self):
        """
        Returns the number of vehicles remaining in the simulation, including vehicles waiting to start.

        :return (int): The number of remaining vehicles.
        """
        return libtraci.simulation.getMinExpectedNumber()

    def changeRoutePath(self, routePath: str):
        """
        Changes the route path for the simulator.

        This function checks if the provided route path is absolute. If it is not an absolute path,
        it converts it to an absolute path based on the current working directory.
        After ensuring that the path exists, it updates the simulator's route path and the
        environment variable 'ROUTEFILENAME' to reflect the new path.

        :param routePath: The absolute route file path.
        :raises FileNotFoundError: If the given route path does not exist

        """
        if not os.path.exists(routePath):
            print("Error: the given path does not exist.")
            return
        self.routePath = routePath
        os.environ["SIMULATIONPATH"] = routePath
        print("The path was set to " + routePath)

    ### VEHICLE FUNCTIONS
    def getVehiclesSummary(self):
        """
        Retrieves a summary of statistics for all vehicles currently in the simulation. The statistics include
        average speed, time lost, distance traveled, departure delay, and waiting time.

        :return (dict): A dictionary containing average statistics for the vehicles in the simulation.
        :raises RuntimeError: If there are no vehicles in the simulation.
        """

        vehicleSummary = {}
        vehiclesList = libtraci.vehicle.getIDList()
        summary = []
        if len(vehiclesList) > 1:
            for vehicleID in vehiclesList:
                element = {}
                element["speed"] = libtraci.vehicle.getSpeed(vehicleID)
                element["timeLost"] = libtraci.vehicle.getTimeLoss(vehicleID)
                element["distance"] = libtraci.vehicle.getDistance(vehicleID)
                element["departDelay"] = libtraci.vehicle.getDepartDelay(vehicleID)
                element["totalWaitingTime"] = libtraci.vehicle.getAccumulatedWaitingTime(vehicleID)
                summary.append(element)

            vehicleSummary["averageSpeed"] = mean(element["speed"] for element in summary)
            vehicleSummary["averageTimeLost"] = mean(element["timeLost"] for element in summary)
            vehicleSummary["averageDepartDelay"] = mean(element["departDelay"] for element in summary)
            vehicleSummary["averageWaitingTime"] = mean(element["totalWaitingTime"] for element in summary)
            # print("The Average Speed of Vehicles is: " + str(vehicleSummary["averageSpeed"]) + " m/s.")
            # print("The Average Time lost is " + str(vehicleSummary["averageTimeLost"]) + " seconds.")
            # print("The Average depart delay is " + str(vehicleSummary["averageDepartDelay"]) + " seconds.")
            # print("The Average time waited is " + str(vehicleSummary["averageWaitingTime"]) + " seconds.")
            self.vehicleSummary = vehicleSummary
            return vehicleSummary
        print("There are no vehicles ")
        return None

    # def updateSummary(self):
    #     # Not sure if it's useful include this data inside Simulator class
    #     self.vehicleSummary = self.getVehiclesSummary()

    ### INDUCTION LOOP FUNCTIONS
    def getDetectorList(self):
        """
        Returns a list of all induction loop detectors in the simulation.

        :return (list): A list of detector IDs.
        """
        return libtraci.inductionloop.getIDList()

    def getAverageOccupationTime(self):
        """
        Calculates and returns the average occupation time for all induction loop detectors in the simulation.

        :return (float): The average occupation time for the detectors.
        """
        detectorList = self.getDetectorList()
        intervalOccupancies = []
        for detector in detectorList:
            intervalOccupancies.append(libtraci.inductionloop.getIntervalOccupancy(detector))
        average = mean(intervalOccupancies)
        return average

    def getInductionLoopSummary(self):
        """
        Retrieves and calculates a summary of statistics for all induction loops in the simulation, including
        interval occupancy, mean speed, and vehicle numbers.

        :return (dict): A dictionary containing average statistics for the induction loops.
        """
        detectorList = self.getDetectorList()
        detectors = []
        inductionLoopSummary = {}
        for det in detectorList:
            element = {}
            element["intervalOccupancy"] = libtraci.inductionloop.getIntervalOccupancy(det)
            element["meanSpeed"] = libtraci.inductionloop.getIntervalMeanSpeed(det)
            element["vehicleNumber"] = libtraci.inductionloop.getIntervalVehicleNumber(det)
            detectors.append(element)
        inductionLoopSummary["averageIntervalOccupancy"] = mean(element["intervalOccupancy"] for element in detectors)
        inductionLoopSummary["averageMeanSpeed"] = mean(element["meanSpeed"] for element in detectors)
        inductionLoopSummary["averageVehicleNumber"] = mean(element["vehicleNumber"] for element in detectors)
        return inductionLoopSummary

    def findLinkedTLS(self, detectorID: str):
        """
        Finds the traffic light systems (TLS) linked to a given detector by matching the lane controlled by the detector.

        :param detectorID: The ID of the detector.
        :return (list): A list of TLS IDs linked to the detector.
        """
        lane = libtraci.inductionloop.getLaneID(detectorID)
        tls = self.getTLSList()
        found = []
        for element in tls:
            lanes = libtraci.trafficlight.getControlledLanes(element)
            if lane in lanes:
                found.append(element)

        return found

    def subscribeToInductionLoop(self, inductionLoopID, value: str):
        """
        Subscribes to an induction loop to monitor specified parameters (occupancy, speed, vehicle number).

        :param inductionLoopID: The ID of the induction loop.
        :param value: The parameter to subscribe to ('intervalOccupancy', 'meanSpeed', 'vehicleNumber').
        :raises ValueError: If the specified value is not a valid parameter for subscription.
        """
        if value == "intervalOccupancy":
            libtraci.inductionloop.subscribe(inductionLoopID, [libtraci.constants.VAR_INTERVAL_OCCUPANCY])
        elif value == "meanSpeed":
            libtraci.inductionloop.subscribe(inductionLoopID, [libtraci.constants.VAR_INTERVAL_SPEED])
        elif value == "vehicleNumber":
            libtraci.inductionloop.subscribe(inductionLoopID, [libtraci.constants.VAR_INTERVAL_NUMBER])

    def checkSubscription(self):
        """
        Checks the subscription results for all induction loops and modifies traffic light programs if
        vehicle numbers or occupancy exceed specified thresholds.
        """
        results = libtraci.inductionloop.getAllSubscriptionResults()
        for key, value in results.items():
            #checking if vehicle number is high
            if libtraci.constants.VAR_INTERVAL_NUMBER in value and value[libtraci.constants.VAR_INTERVAL_NUMBER] > 10:
                tlsIDs = self.findLinkedTLS(key)
                for element in tlsIDs:
                    self.setTLSProgram(element, "utopia")
                    print("New program is " + str(libtraci.trafficlight.getProgram(element)))
            if libtraci.constants.VAR_INTERVAL_OCCUPANCY in value and value[
                libtraci.constants.VAR_INTERVAL_OCCUPANCY] > 30:
                print("value in excess")

    ### TLS FUNCTIONS
    def getTLSList(self):
        """
        Retrieves a list of all traffic light systems (TLS) in the simulation.

        :return (list): A list of TLS IDs.
        """
        return libtraci.trafficlight_getIDList()

    def checkTLS(self, tlsID):
        """
        Checks if a given traffic light system (TLS) exists in the simulation.

        :param tlsID: The ID of the traffic light system.
        :return (bool): True if the TLS exists, False otherwise.
        """
        tls = self.getTLSList()
        if tlsID in tls:
            return True
        else:
            return False

    def setTLSProgram(self, trafficLightID: str, programID: str, all=False):
        """
        Sets the traffic light program for one or all traffic light systems (TLS).

        :param trafficLightID: The ID of the TLS to change the program for.
        :param programID: The ID of the new traffic light program.
        :param all: If True, sets the program for all TLS in the simulation. Default is False.
        :raises RuntimeError: If there is an issue changing the traffic light program.
        """
        ### NOTE: There is still no check of existence of specific program inside the additional file
        if all:
            tls = self.getTLSList()
            for traffic_light in tls:
                libtraci.trafficlight.setProgram(traffic_light, programID)
            print("The program of all traffic lights is changed to" + str(programID))
        elif self.checkTLS(trafficLightID):
            libtraci.trafficlight.setProgram(trafficLightID, programID)
            print("The program of the TLS " + str(trafficLightID) + " is changed to " + str(programID))


class ValueListener(libtraci.StepListener):
    """
    A class for defining actions to be executed at every simulation step via the libtraci step listener.
    """
    def step(self, t=0):
        """
        Method called at every simulation step. It allows custom operations to be performed.

        :param t: The simulation time for the current step. Default is 0.
        :return (bool): True to indicate the listener should remain active for the next step.
        """

        # do something after every call to simulationStep
        # print("ExampleListener called with parameter %s." % t)
        # Here it is possible to get every kind of info required during onestep.

        # indicate that the step listener should stay active in the next step
        return True
