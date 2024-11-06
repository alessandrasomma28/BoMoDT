import os
import sys
import xml.etree.ElementTree as ET
import subprocess
from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename

from libraries.classes.DataManager import *
from libraries import constants
from libraries.classes.SumoSimulator import Simulator


class ScenarioGenerator:
    """
    The ScenarioGenerator class handles traffic route scenarios, allowing them to be created and configured
    for sumoenv simulations. It generates route files and sets up these routes within the simulator.

    Class Attributes:
    - sumoConfiguration (str): Path to the sumoenv configuration file.
    - sim (Simulator): An instance of the Simulator class.

    Class Methods:
    - __init__: Constructor to initialize a new instance of the ScenarioGenerator class.
    - generateRoutes: Method to generate a route file for sumoenv simulation from an edgefile.
    - setScenario: Method to set the current scenario in the simulator using a generated or manual route file.
    """
    sumoConfiguration: str
    sim: Simulator

    def __init__(self, sumocfg: str, sim: Simulator):
        """
        Initializes the ScenarioGenerator with the sumoenv configuration file and the simulator instance.

        :param sumocfg: Path to the sumoenv configuration file.
        :param sim: An instance of the Simulator class.
        """
        self.sumoConfiguration = sumocfg
        self.sim = sim


    def defineScenarioFolder(self, congestioned: bool = False) -> str:
        """
        Defines and creates a folder for the scenario the planner wants to simulate.

        :param congestioned: Boolean flag indicating if the scenario should be congested.
        :return: The path to the folder created for the scenario.
        """
        date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        scenarioFolder = "congestioned" if congestioned else "basic"
        newPath = os.path.join(constants.scenarioCollectionPath, f"{date}_{scenarioFolder}/")
        os.makedirs(newPath, exist_ok=True)
        return newPath


    def generateRoutes(self, edgefile: str, folderPath: str, totalVehicles: int, minLoops: int = 1, congestioned: bool= False) -> str:
        """
        Generates a route file for sumoenv simulation starting from an edgefile that contains vehicle counts.

        :param edgefile: The path to the edgefile containing traffic counts.
        :param totalVehicles: The total number of vehicles to be generated in the route file.
        :param minLoops: Minimum number of loops or counting locations covered by each vehicle route.
        :param congestioned: Boolean flag to indicate whether the generated scenario should be congested.
        :return: The absolute path to the generated route file.
        :raises FileNotFoundError: If the sumoenv tools path does not exist.
        """
        if not edgefile:
            raise ValueError("No edgefile provided.")
        if totalVehicles is None:
            raise ValueError("The total number of vehicles was not defined.")

        if not os.path.exists(constants.sumoToolsPath):
            raise FileNotFoundError("sumoenv tools path does not exist.")


        script1 = constants.sumoToolsPath + "/randomTrips.py"

        arg1 = ""
        if constants.simulationPath.startswith("./"):
            arg1 = constants.simulationPath[2:]
        else:
            arg1 = constants.simulationPath
        arg1 = os.path.join(arg1, "static/joined_lanes.net.xml")
        arg1 = os.path.abspath(arg1)
        print(arg1)
        print(edgefile)

        subprocess.run(['python', script1, "-n", arg1, "-r", folderPath + "sampleRoutes.rou.xml",
                        "--fringe-factor", "10", "--random", "--min-distance", "100", "--random-factor", "200"])

        script2 = constants.sumoToolsPath + "/routeSampler.py"
        if congestioned:
            #TODO: here some actions has to be taken in order to generate a congestioned scenario. Note that using
            # the totalVehicles parameters and the minLoops can generate congestioned traffic even if this parameter
            # is not set.
            subprocess.run([sys.executable,  script2, "-r", folderPath + "sampleRoutes.rou.xml",
                        "--edgedata-files", edgefile, "-o", folderPath +
                        "generatedRoutes.rou.xml", "--total-count", str(totalVehicles), "--optimize",
                        "full", "--min-count", str(minLoops)])
        else:
            subprocess.run([sys.executable,  script2, "-r", folderPath + "sampleRoutes.rou.xml",
                        "--edgedata-files", edgefile, "-o", folderPath +
                        "generatedRoutes.rou.xml", "--total-count", str(totalVehicles), "--optimize",
                        "full", "--min-count", str(minLoops)])
        print("Routes Generated")
        # self.sim.changeRoutePath(newpath + "generatedRoutes.rou.xml")

        relativeRouteFile = folderPath # + "generatedRoutes.rou.xml"
        routeFilePath = os.path.abspath(relativeRouteFile)
        return routeFilePath

    def setScenario(self, routeFilePath=None, manual: bool = False, absolutePath: bool = False):
        """
        Sets the scenario in the simulator by selecting a route file.
        A manual file can also be selected using a file dialog.

        :param routeFilePath: The path to the route file (optional if manual=True).
        :param manual: If True, opens a file dialog for manual route file selection.
        :param absolutePath: Boolean indicating if the provided routeFilePath is an absolute path.
        :raises FileNotFoundError: If the chosen route file does not exist.
        """
        if manual:
            Tk().withdraw()
            routeFilePath = askopenfilename(title="Select a Route File",
                                            filetypes=(("route files", "*.rou.xml"), ("xml files", "*.xml")))
            if not routeFilePath:
                print("No route file was selected.")
                return
            print("The chosen file was " + routeFilePath)

        if routeFilePath:
            if not absolutePath:
                routeFilePath = os.path.abspath(routeFilePath)
            if not os.path.exists(routeFilePath):
                raise FileNotFoundError(f"The route file '{routeFilePath}' does not exist.")
            self.sim.changeRoutePath(routePath=routeFilePath)
        else:
            print("No route file path was provided or selected.")


class Planner:
    """
    The Planner class manages traffic simulations by interacting with the sumoenv simulator and integrating it with a database.
    It also manages the scenario generation based on collected data.

    Class Attributes:
    - simulator (Simulator): An instance of the Simulator class.
    - scenarioGenerator (ScenarioGenerator): An instance of the ScenarioGenerator class.

    Class Methods:
    - __init__: Initializes a new instance of the Planner class.
    - planBasicScenarioForOneHourSlot: Plans a one-hour traffic simulation scenario based on collected data.
    """
    simulator: Simulator
    scenarioGenerator: ScenarioGenerator

    def __init__(self, simulator: Simulator):
        """
        Initializes the Planner with the given simulator instance.

        :param simulator: An instance of the Simulator class.
        """
        self.simulator = simulator
        self.scenarioGenerator = ScenarioGenerator(sumocfg="run.sumocfg", sim=self.simulator)

    def planBasicScenarioForOneHourSlot(self, collectedData: pd.DataFrame, entityType: str, totalVehicles: int,
                                        minLoops: int, congestioned: bool, activeGui: bool=False):
        """
        Plans a basic traffic simulation scenario for a one-hour timeslot based on the collected data.

        :param collectedData: A pandas DataFrame containing the collected traffic data with 'edgeid' and 'trafficflow' columns.
        :param entityType: The type of entity (e.g., "roadsegment").
        :param totalVehicles: The total number of vehicles to simulate.
        :param minLoops: Minimum number of loops or counting locations covered by each vehicle route.
        :param congestioned: Boolean flag to indicate whether the generated scenario should be congested.
        :return: A path to the generated scenario folder.
        :raises ValueError: If edge ID is missing or entity type is invalid.
        """
        if entityType.lower() not in ["road segment", "roadsegment"]:
            raise ValueError(f"Invalid entity type: {entityType}. Simulation requires edge IDs to generate a scenario.")

        root = ET.Element('data')
        interval = ET.SubElement(root, 'interval', begin='0', end='3600')
        scenarioFolder = self.scenarioGenerator.defineScenarioFolder(congestioned=congestioned)
        for _, row in collectedData.iterrows():
            edgeID = row.get('edgeid')
            trafficFlow = row.get('trafficflow')
            if edgeID is None:
                raise ValueError("Edge ID is missing for one of the rows in the collected data.")
            ET.SubElement(interval, 'edge', id=edgeID, entered=str(trafficFlow))


        tree = ET.ElementTree(root)
        ET.indent(tree, '  ')
        edgeFilePath = os.path.join(scenarioFolder, "edgefile.xml")
        tree.write(edgeFilePath, "UTF-8")
        routeFilePath = self.scenarioGenerator.generateRoutes(edgefile=edgeFilePath, folderPath=scenarioFolder, totalVehicles=totalVehicles,
                                                               minLoops=minLoops, congestioned=congestioned)
        self.scenarioGenerator.setScenario(routeFilePath=routeFilePath, manual=False, absolutePath=True)
        self.simulator.start(activeGui=activeGui)

        return scenarioFolder


"""   ## SI PUO' CANCELLARE
    def dbConnect(self, connectionString: str, host="localhost", port="5432", dbname="quantumleap", username="postgres",
                  password="postgres"):

        if connectionString is not None:
            connection = connectionString
        else:
            connection = "postgres://" + username + ":" + password + "@" + host + ":" + port + "/" + dbname
        with psycopg2.connect(connection) as conn:
            cursor = conn.cursor()
            return conn, cursor

"""
""" 
    #Function to create an edgefile with counting vehicles
    def recordFlow(self, timeslot: str, date: str, entityType: str, timecolumn = "datetime"):
      
        if (timeslot and date) is None:
            print("No ull datetime was given.")
            return
        if entityType is None:
            print("An Entity Type must be specified.")
            return
        root = ET.Element('data')
        interval = ET.SubElement(root, 'interval', begin='0', end='3600')
        if entityType == "roadsegment":
         
            PREVIOUS PART:            
            time1 = str(timeslot[0:5])
            time2 = str(timeslot[6:11])
            first = date + 'T' + time1 + ":00+00"
            second = date + 'T' + time2 + ":00+00"
            query = (('SELECT entity_id, trafficflow, ST_X(location) as lat, ST_Y(location),'
                     ' edgeid as lon FROM "mtopeniot"."ethttps://smartdatamodels.org/datamodel.transportation/roadsegm"')
                     + "  WHERE "+ timecolumn +" BETWEEN %s::timestamptz AND %s::timestamptz;")
            self.cursor.execute(query, (first, second))
            for row in self.cursor.fetchall():
                edge_id = row[4]
                if edge_id is not None:
                    edge = ET.SubElement(interval, 'edge', id=edge_id, entered=str(row[1]))
                    
         

        elif entityType == "device":
            query = "SELECT entity_id, trafficflow, ST_X(location) as lat, ST_Y(location) as lon FROM mtopeniot.etdevice WHERE "+ timecolumn + " LIKE %s and dateobserved LIKE %s"
            self.cursor.execute(query,  (timeslot, date))
            for row in self.cursor.fetchall():
                edge_id = self.getEdgeID(row[2], row[3])
                if edge_id is not None:
                    edge = ET.SubElement(interval, 'edge', id=edge_id, entered=str(row[1]))
                print(row)
        tree = ET.ElementTree(root)
        ET.indent(tree, '  ')
        tree.write("edgefile.xml", "UTF-8")
    """
""" THIS CAN BE DELETED.
    def getEdgeID(self, latitudine: float, longitudine: float):
        lat = general_utils.convert_format(str(latitudine))
        lon = general_utils.convert_format(str(longitudine))
        # Trimming because of the roundings
        lat = lat[:-1]
        lon = lon[:-1]
        df1 = pd.read_csv("../traffic_loop_dataset/day_flow.csv", sep=',')
        df1["longitudine"] = df1["longitudine"].apply(general_utils.convert_format)
        df1["latitudine"] = df1["latitudine"].apply(general_utils.convert_format)
        matches = df1[df1['longitudine'].str.startswith(lon) & df1['latitudine'].str.startswith(lat)]
        if matches.shape[0] > 1:
            print("Error, there are more roads at these coordinates")
            return None
        return matches.iloc[0]["edge_id"]
"""
