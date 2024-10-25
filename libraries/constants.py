# environment variables file for the containers and their port
containerEnvPath = "./docker-files/fiware-dt-platform/.env"

# folder where processed traffic loops measures are stored (typically in a one-day length)
# TODO: this tlpath should be corrected to collect all the daily datasets
#  that are in the folder. For now, we are taking only the real flow to check if it's working.
tlPath = "./traffic_loop_dataset/real_dataset"
# folder where registered devices are stored
outputPath = "./registered_devices/"

shadowFilePath = "./digital_shadows/coordinates_roads_edge.csv"
shadowPath = "./digital_shadows/"


### SMART DATA MODELS RELATED CONSTANTS
transportationCTX="https://raw.githubusercontent.com/smart-data-models/dataModel.Transportation/4df15072b13da6c7bd7e86915df91fb28921aa7f/context.jsonld"
deviceCTX="https://raw.githubusercontent.com/smart-data-models/dataModel.Device/master/context.jsonld"
roadSegmentType="https://smartdatamodels.org/dataModel.Transportation/RoadSegment"
roadType="https://smartdatamodels.org/dataModel.Transportation/Road"
trafficFlowObservedType = "https://smartdatamodels.org/dataModel.Transportation/TrafficFlowObserved"
deviceType = "https://uri.etsi.org/ngsi-ld/default-context/TrafficLoopDevices"

### SUMO-RELATED CONSTANTS
# path where the data used for simulation are stored
citySimulationDataPath = "./SUMO/bologna/data/"
simulationDataPath = "./SUMO/joined/data/"
citySimulationPath = "SUMO/bologna/"
simulationPath = "SUMO/joined/"
sumoToolsPath = r"C:\Program Files (x86)\Eclipse\Sumo\tools"

# Path where data for simulating different SUMO scenario are collected.
scenarioCollectionPath = "SUMO/joined/scenarioCollection"

