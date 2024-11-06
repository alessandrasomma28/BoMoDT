import sys

from libraries.classes.SumoSimulator import Simulator
from libraries.classes.Planner import Planner
from libraries.classes.DataManager import DataManager
from typing import Optional
from libraries import constants
import os
import subprocess
from subprocess import Popen
from PIL import Image
import pytz
from datetime import datetime


class DigitalTwinManager:
    """
    The DigitalTwinManager class orchestrates the interaction between historical traffic data, sumoenv simulations,
    and traffic planning to create a digital twin environment. This class is essential for running simulations
    based on real-world data to support traffic flow analysis.

    Attributes:
       sumoSimulator (Simulator): An instance of the Simulator class, which runs the sumoenv simulation.
       planner (Planner): An instance of the Planner class, responsible for scenario planning.
       dtDataManager (DataManager): An instance of the DataManager class, which handles data retrieval and storage.

    Methods:
       - __init__: Initializes the DigitalTwinManager by setting up the DataManager, Simulator, and Planner instances.
       - simulateBasicScenarioForOneHourSlot: Simulates a basic scenario for a one-hour time slot using historical data.
   """

    sumoSimulator: Simulator
    planner: Planner
    dtDataManager: DataManager

    def __init__(self, dataManager: DataManager, sumoConfigurationPath: str, sumoLogFile: str):
        """
        Initializes the DigitalTwinManager by creating instances of the DataManager, sumoenv simulator, and Planner.

        :param dataManager: Optional name for the DataManager (default is "DataManager").
        :param sumoConfigurationPath: Path to the sumoenv configuration file.
        :param sumoLogFile: Path to the log file for sumoenv.
        """
        # TODO: manage the possibility to get as input directly the simulator and the planner instances.
        self.dtDataManager = dataManager
        self.sumoSimulator = Simulator(configurationPath=sumoConfigurationPath, logFile=sumoLogFile)
        self.planner = Planner(simulator=self.sumoSimulator)

    def simulateBasicScenarioForOneHourSlot(self, timeslot: str, date: str, entityType: str, totalVehicles: int,
                                            minLoops: int, congestioned: bool, activeGui: bool=False, timecolumn: Optional[str] = "timeslot"):
        """
        Simulates a basic traffic scenario for a one-hour time slot, retrieving historical data and using it to
        define the simulation parameters.

        :param timeslot: The time slot for which historical traffic data is retrieved (e.g., "00:00-01:00").
        :param date: The date on which the traffic data is based (e.g., "2024-02-01").
        :param entityType: The type of entity being simulated (e.g., "roadsegment" or "device").
        :param totalVehicles: The total number of vehicles to include in the simulation.
        :param minLoops: The minimum number of simulation loops to perform.
        :param congestioned: A boolean flag to indicate if the simulation should include congestion.
        :param activeGui: Whether to activate the sumoenv graphical user interface (GUI) during the simulation.
        :param timecolumn: The name of the time column in the database used to retrieve historical data (default is "timeslot").

        :return: A string representing the folder where the scenario is stored.
        """
        if entityType.lower() in ["road segment", "roadsegment"]:
            timescaleManager = self.dtDataManager.getDBManagerByType("TimescaleDBManager")
            df = timescaleManager.retrieveHistoricalDataForTimeslot(timeslot=timeslot, date=date, entityType=entityType, timecolumn=timecolumn)
            scenarioFolder = self.planner.planBasicScenarioForOneHourSlot(df, entityType=entityType, totalVehicles=totalVehicles,
                                                                         minLoops=minLoops, congestioned=False, activeGui=activeGui)
            return scenarioFolder


    def generateGraphs(self, scenarioFolder: str):
        """
        Generate some graphs based on the simulation outcome. The generated graphs show some info about the trajectory
        taken by the vehicles, the time spent in running/halted state and the depart delay time.
        :param scenarioFolder: the folder where the simulated scenario output is stored
        :return:
        """
        graphScript = constants.sumoToolsPath + '/visualization/plotXMLAttributes.py'
        scenarioFolder = os.path.abspath(scenarioFolder)

        trajectory_cmd = [sys.executable, graphScript, "-x", "x", "-y", "y", "-o", scenarioFolder + "/traj_out.png",
                          scenarioFolder + "/fcd.xml", "--blind"]
        running_halted_cmd = [sys.executable, graphScript, scenarioFolder + "/summary.xml", "-x", "time", "-y",
                              "running,halting", "-o", scenarioFolder + "/plot_running.png", "--legend", "--blind"]
        depart_delay_cmd = [sys.executable, graphScript, "-i", "id", "-x", "depart", "-y", "departDelay",
                            "--scatterplot", "--xlabel", '"depart time [s]"', "--ylabel", '"depart delay [s]"',
                            "--ylim", "0,40", "--xticks", "0,1200,200,10", "--yticks", "0,40,5,10", "--xgrid",
                            "--ygrid", "--title", '"depart delay over depart time"', "--titlesize", "16",
                            scenarioFolder + "/tripinfos.xml", "--blind", "-o", scenarioFolder + "/departDelay.png"]

        commands = [trajectory_cmd, running_halted_cmd, depart_delay_cmd]
        procs = [Popen(i) for i in commands]
        for p in procs:
            p.wait()


    def showGraphs(self, scenarioFolder: str, saveSummary = False):
        """
        Groups the graphs previously generated and stored in the scenarioFolder and show them in one figure
        :param scenarioFolder: the folder where the simulated scenario output is stored
        :return:
        """
        scenarioFolder = os.path.abspath(scenarioFolder)

        # Graph list
        images = [scenarioFolder + '/traj_out.png', scenarioFolder + '/plot_running.png',scenarioFolder + '/departDelay.png']
        imgs = [Image.open(img) for img in images]

        # Group figures in one image
        widths, heights = zip(*(i.size for i in imgs))
        total_width = sum(widths)  # For horizontal concat
        max_height = max(heights)
        new_image = Image.new('RGB', (total_width, max_height))
        x_offset = 0
        for img in imgs:
            new_image.paste(img, (x_offset, 0))  # Incolla nella nuova immagine
            x_offset += img.width
        # Show Grouped image
        new_image.show()
        # Save new image
        if saveSummary:
            new_image.save(scenarioFolder + '/summary_image.png')

