import os
from libraries.utils.preprocessingUtils import *
from libraries.constants import TRAFFIC_FLOW_OPENDATA_FILE_PATH, ACCURACY_TRAFFIC_LOOP_OPENDATA_FILE_PATH, SUMO_NET_PATH, SUMO_DETECTORS_ADD_FILE_PATH, PROCESSED_TRAFFIC_FLOW_EDGE_FILE_PATH

#csv file to be filtered
#inputFile = PROCESSED_DATA_PATH + 'traffic_flow_2024.csv'
#accuracyFile = PROCESSED_DATA_PATH + 'accuratezza-spire-anno-2024.csv'

accurateInputFile = PROCESSED_DATA_PATH + 'accurate_traffic_flow.csv'
netFile = SUMO_PATH + "static/joined_lanes.net.xml"

processedTrafficFlow = PROCESSED_DATA_PATH + ('processed_traff'
                                              'ic_flow.csv') ## CHI GENERA QUESTO FILE??

def run():

    #1. Filter the Open Data traffic flow dataset w.r.t. traffic loop accuracy.
    acceptedAccuracy = 95
    filterWithAccuracy(TRAFFIC_FLOW_OPENDATA_FILE_PATH, ACCURACY_TRAFFIC_LOOP_OPENDATA_FILE_PATH, date_column='data',sensor_id_column='codice_spira', output_file=TRAFFIC_FLOW_ACCURATE_FILE_PATH, accepted_percentage=acceptedAccuracy)


    #2. Filtering the dataset in a specific TIME WINDOW for testing purposes, and reordering the dataset in a chronological order.
    ##### Note: comment the following two code lines for working on the entire dataset.
    filteringDataset(TRAFFIC_FLOW_ACCURATE_FILE_PATH, "02/01/2024", "02/02/2024", TRAFFIC_FLOW_ACCURATE_FILE_PATH)
    reorderDataset(TRAFFIC_FLOW_ACCURATE_FILE_PATH, TRAFFIC_FLOW_ACCURATE_FILE_PATH)

    #3. Generate correspondence between roadName and edge ID in SUMO net file and creating the SUMO detectors additional file for modeling real induction loop positions in SUMO net.
    generateRoadNamesFile(inputFile=TRAFFIC_FLOW_ACCURATE_FILE_PATH, sumoNetFile=SUMO_NET_PATH,detectorFilePath=SUMO_DETECTORS_ADD_FILE_PATH, roadNamesFilePath=ROAD_NAMES_FILE_PATH)

    #4. Fill missing edge IDs in the road names file.
    fillMissingEdgeId(ROAD_NAMES_FILE_PATH)
    linkEdgeId(inputFile=TRAFFIC_FLOW_ACCURATE_FILE_PATH, roadnameFile=ROAD_NAMES_FILE_PATH, outputFile=PROCESSED_TRAFFIC_FLOW_EDGE_FILE_PATH)

    #5. Generate shadow types for creating road, traffic loop shadows within the DT.
    filterForShadowManager(PROCESSED_TRAFFIC_FLOW_EDGE_FILE_PATH)
    generateRealFlow(PROCESSED_TRAFFIC_FLOW_EDGE_FILE_PATH)

    #6. Generate example edgedata file to be used for route genaration
    generateEdgeDataFile(PROCESSED_TRAFFIC_FLOW_EDGE_FILE_PATH, date='01/02/2024', time_slot='07:00-08:00')
    #dailyFilter(PROCESSED_TRAFFIC_FLOW_EDGE_FILE_PATH, date='01/02/2024')

