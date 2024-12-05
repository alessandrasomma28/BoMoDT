from mobilityvenv.MobilityVirtualEnvironment import setupPhysicalSystem, startPhysicalSystem
import time

# Function to run the physical system
def runPhysicalSystem(iotAgent):
    """
    Function to continuously run the physical system in a separate thread.
    Args:
        iotAgent: The IoT Agent used for the physical system setup.
    """
    roads, files = setupPhysicalSystem(iotAgent)
    try:
        while True:
            startPhysicalSystem(roads)
            time.sleep(1)  # Adjust the sleep interval as needed
    except KeyboardInterrupt:
        print("Stopping Physical System...")
        # Add cleanup logic here if necessary



def runSimulation(twinManager, timeslot, date, entityType, totalVehicles, minLoops, congestioned, activeGui, timecolumn):
    """
    Function to run simulations using the twin manager.
    Args:
        twinManager: The digital twin manager object used for running simulations.
        timeslot (str): The time range for the simulation (e.g., "00:00-01:00").
        date (str): The date for the simulation (e.g., "2024/02/01").
        entityType (str): The type of entity being simulated (e.g., "Road Segment").
        totalVehicles (int): The total number of vehicles in the simulation.
        minLoops (int): The minimum number of loops in the simulation.
        congestioned (bool): Whether the scenario is congestioned or not.
        activeGui (bool): Whether the SUMO GUI is active during the simulation.
        timecolumn (str): The column used for timeslot management.
    """
    try:
        scenarioFolder = twinManager.simulateBasicScenarioForOneHourSlot(
            timeslot=timeslot,
            date=date,
            entityType=entityType,
            totalVehicles=totalVehicles,
            minLoops=minLoops,
            congestioned=congestioned,
            activeGui=activeGui,
            timecolumn=timecolumn
        )
        print(f"Simulation results stored in: {scenarioFolder}")
        twinManager.generateGraphs(scenarioFolder)
        twinManager.showGraphs(scenarioFolder, saveSummary=False)
    except Exception as e:
        print(f"An error occurred during the simulation: {e}")

