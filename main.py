from libraries.utils.generalUtils import *
from libraries.utils.preprocessingUtils import *
from libraries.classes.DataManager import *
from libraries.classes.Planner import Planner
from libraries.classes.DigitalTwinManager import DigitalTwinManager
from libraries.classes.Agent import *
from libraries.classes.SumoSimulator import Simulator
from libraries.classes.SubscriptionManager import QuantumLeapManager
from libraries.classes.Broker import Broker
from data.preprocessing import preprocessingSetup
from libraries.utils.multiThreadingUtils import runPhysicalSystem, runSimulation
import threading

if __name__ == "__main__":


    preprocessingSetup.run()

    # 1. Instantiate Orion CB, IoT Agent and create three types of subscriptions.
    envVar = loadEnvVar(CONTAINER_ENV_FILE_PATH)
    iotanorth = envVar.get("IOTA_NORTH_PORT")
    iotasouth = envVar.get("IOTA_SOUTH_PORT")
    cbport = envVar.get("ORIONLD_PORT")
    timescalePort = envVar.get("TIMESCALE_DB_PORT")
    quantumleapPort = envVar.get("QUANTUMLEAP_PORT")
    contextBroker = Broker(pn=cbport, pnt=None, host="localhost", fiwareservice="openiot")
    cbConnection = contextBroker.createConnection()
    IoTAgent = Agent(aid="01", hostname="localhost", cb_port=cbport, south_port=iotasouth, northport=iotanorth, fw_service="openiot", fw_path="/")
    quantumLeapManager = QuantumLeapManager(containerName="fiware-quantumleap", cbPort=cbport, quantumleapPort=quantumleapPort)

    quantumLeapManager.createQuantumLeapSubscription(cbConnection=cbConnection, entityType="Road Segment", attribute="trafficFlow", description="Notify me of Traffic Flow")
    quantumLeapManager.createQuantumLeapSubscription(cbConnection=cbConnection, entityType="trafficflowobserved", attribute="trafficFlow", description="Notify me of Traffic Flow")
    quantumLeapManager.createQuantumLeapSubscription(cbConnection=cbConnection, entityType="Device", attribute="trafficFlow", description="Notify me of traffic Flow")


    #### Comment/decomment these two code lines to run the physical system.
    # TODO: thread-multiprocessing
    #roads, files = setupPhysicalSystem(IoTAgent)
    #startPhysicalSystem(roads)

    physicalSystemThread = threading.Thread(target=runPhysicalSystem, args=(IoTAgent,))
    physicalSystemThread.daemon = True  # Stops thread when main program exits
    physicalSystemThread.start()

    timescaleManager = TimescaleManager(host="localhost", port=timescalePort, dbname="quantumleap", username="postgres", password="postgres")
    dataManager = DataManager("TwinDataManager")
    dataManager.addDBManager(timescaleManager)

    logFile="./command_log.txt"
    sumoSimulator = Simulator(configurationPath=SUMO_PATH, logFile=logFile)
    twinPlanner = Planner(simulator=sumoSimulator)
    twinManager = DigitalTwinManager(dataManager, SUMO_PATH, logFile)

    firstTimeslotEvent.wait()

    simulationParams = {
        "timeslot": "00:00-01:00",
        "date": "2024/02/01",
        "entityType": "Road Segment",
        "totalVehicles": 100,
        "minLoops": 3,
        "congestioned": False,
        "activeGui": True,
        "timecolumn": "timeslot"
    }

    # Run the simulation with the given parameters
    runSimulation(twinManager, **simulationParams)

    # Running another simulation with different parameters
    anotherSimulationParams = {
        "timeslot": "01:00-02:00",
        "date": "2024/02/02",
        "entityType": "TrafficLight",
        "totalVehicles": 150,
        "minLoops": 5,
        "congestioned": False,
        "activeGui": True,
        "timecolumn": "timeSlotColumn"
    }
    runSimulation(twinManager, **anotherSimulationParams)



    # 2. The DigitalTwinManager needs i) a DataManager for accessing data; ii) a SumoSimulator for running simulations
    #    iii) a Planner including a ScenarioGenerator for generating sumoenv scenarios.
   # timescaleManager = TimescaleManager(
    #    host="localhost",
      #  port=timescalePort,
     #   dbname="quantumleap",
     #   username="postgres",
     #   password="postgres"
   # )
   # dataManager = DataManager("TwinDataManager")
    #dataManager.addDBManager(timescaleManager)

    #configurationPath = SUMO_PATH
    #logFile = "./command_log.txt"
    #sumoSimulator = Simulator(configurationPath=configurationPath, logFile=logFile)
    #twinPlanner = Planner(simulator=sumoSimulator)
    #twinManager = DigitalTwinManager(dataManager, configurationPath, logFile)

    # 3. Simulation of one hour slot scenario. The function will open sumo gui. The play button must be pressed to run the simulation. When simulation ends, the function returns the folder path in which sumoenv files have been generated.
    #scenarioFolder = twinManager.simulateBasicScenarioForOneHourSlot(timeslot="00:00-01:00", date="2024/02/01", entityType='Road Segment', totalVehicles=100, minLoops=3, congestioned=False, activeGui=True, timecolumn="timeslot")
    #print(scenarioFolder)
    #twinManager.generateGraphs(scenarioFolder)
    #twinManager.showGraphs(scenarioFolder, saveSummary=False)



