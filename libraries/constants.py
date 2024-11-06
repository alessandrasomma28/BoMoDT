#Project Path
import os.path
from pathlib import Path
path = Path((os.path.abspath(__file__)))
projectPath = str(path.parent.parent.absolute())


# environment variables file for the containers and their port
containerEnvPath = "./fiwareenv/.env"

# folder where processed traffic loops measures are stored (typically in a one-day length)
# TODO: this tlpath should be corrected to collect all the daily datasets
#  that are in the folder. For now, we are taking only the real flow to check if it's working.
tlPath = "./data/realworlddata/mvenvdata"
# folder where registered devices are stored
outputPath = "./registereddevices/"

shadowFilePath = "./digitalshadows/coordinates_roads_edge.csv"
shadowPath = "./digitalshadows/"


### SMART DATA MODELS RELATED CONSTANTS
transportationCTX="https://raw.githubusercontent.com/smart-data-models/dataModel.Transportation/4df15072b13da6c7bd7e86915df91fb28921aa7f/context.jsonld"
deviceCTX="https://raw.githubusercontent.com/smart-data-models/dataModel.Device/master/context.jsonld"
roadSegmentType="https://smartdatamodels.org/dataModel.Transportation/RoadSegment"
roadType="https://smartdatamodels.org/dataModel.Transportation/Road"
trafficFlowObservedType = "https://smartdatamodels.org/dataModel.Transportation/TrafficFlowObserved"


### sumoenv-RELATED CONSTANTS
# path where the data used for simulation are stored
simulationDataPath = projectPath + "./data/preprocessing/data/"
simulationPath = projectPath + "/sumoenv/joined/"
sumoToolsPath = r"C:\Program Files (x86)\Eclipse\Sumo\tools"

# Path where data for simulating different sumoenv scenario are collected.
scenarioCollectionPath = "sumoenv/joined/scenarioCollection"

