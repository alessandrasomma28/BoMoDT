import os.path
from pathlib import Path

##### PROJECT ABSOLUTE PATH #####
path = Path((os.path.abspath(__file__)))
projectPath = str(path.parent.parent.absolute())


# FIWARE ENVIRONMENT AND SMART DATA MODELS CONSTANTS
CONTAINER_ENV_FILE_PATH = projectPath + "/fiwareenv/.env"
TRANSPORTATION_DATA_MODEL_CTX= "https://raw.githubusercontent.com/smart-data-models/dataModel.Transportation/4df15072b13da6c7bd7e86915df91fb28921aa7f/context.jsonld"
DEVICE_DATA_MODEL_CTX= "https://raw.githubusercontent.com/smart-data-models/dataModel.Device/master/context.jsonld"
ROAD_SEGMENT_DATA_MODEL_TYPE= "https://smartdatamodels.org/dataModel.Transportation/RoadSegment"
ROAD_DATA_MODEL_TYPE= "https://smartdatamodels.org/dataModel.Transportation/Road"
TRAFFIC_FLOW_OBSERVED_DATA_MODEL_TYPE = "https://smartdatamodels.org/dataModel.Transportation/TrafficFlowObserved"


# DATA RELATED CONSTANTS
SHADOW_TYPE_FILE_PATH = projectPath + "/data/digitalshadow/digital_shadow_types.csv"
SHADOW_TYPE_PATH = projectPath + "/data/digitalshadow/"
SHADOWS_PATH = projectPath + "/data/digitalshadow/"



REAL_WORLD_DATA_PATH = projectPath + "/data/realworlddata"
REAL_TRAFFIC_FLOW_DATA_MVENV_PATH = REAL_WORLD_DATA_PATH + "/mvenvdata"
REAL_TRAFFIC_FLOW_DATA_MVENV_FILE_PATH = REAL_WORLD_DATA_PATH + "/mvenvdata/real_traffic_flow.csv"
# folder where registered devices are stored
REGISTERED_DEVICES_PATH = projectPath + "/registereddevices/"

TRAFFIC_FLOW_OPENDATA_FILE_PATH = REAL_WORLD_DATA_PATH + "/opendata/traffic_flow_2024.csv"
ACCURACY_TRAFFIC_LOOP_OPENDATA_FILE_PATH = REAL_WORLD_DATA_PATH + "/opendata/accuracy_loops_2024.csv"

PROCESSED_DATA_PATH = projectPath + "/data/preprocessing/"
TRAFFIC_FLOW_ACCURATE_FILE_PATH = PROCESSED_DATA_PATH + "/accurate_traffic_flow.csv"
PROCESSED_TRAFFIC_FLOW_EDGE_FILE_PATH = PROCESSED_DATA_PATH +"/processed_traffic_flow.csv"
ROAD_NAMES_FILE_PATH = PROCESSED_DATA_PATH + "/road_names.csv"
EDGE_DATA_FILE_PATH = PROCESSED_DATA_PATH + "/edgedata.xml"
DAILY_TRAFFIC_FLOW_FILE_PATH = PROCESSED_DATA_PATH + "/daily_flow.csv"

## SUMO ENVIRONMENT RELATED CONSTANTS
SUMO_PATH = projectPath + "/sumoenv"
SUMO_NET_PATH = SUMO_PATH + "/static/joined_lanes.net.xml"
SUMO_DETECTORS_ADD_FILE_PATH = SUMO_PATH + "/static/detectors.add.xml"
SUMO_LOG_PATH = SUMO_PATH + "/sumolog/commandlog.txt"


SUMO_TOOLS_PATH = r"C:\Program Files (x86)\Eclipse\Sumo\tools"

# Path where data for simulating different sumoenv scenario are collected.
SCENARIO_COLLECTION_PATH = "sumoenv/scenarioCollection"

