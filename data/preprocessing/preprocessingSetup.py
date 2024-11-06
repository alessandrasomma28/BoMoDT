import os
from libraries.utils.preprocessingUtils import *

#csv file to be filtered
inputFile = (simulationDataPath + 'traffic_flow_2024.csv')
accuracyFile = simulationDataPath + 'accuratezza-spire-anno-2024.csv'
accurateInputFile = simulationDataPath + 'accurate_traffic_flow.csv'
netFile = simulationPath + "static/joined_lanes.net.xml"
processedTrafficFlow = simulationDataPath + 'processed_traffic_flow.csv'

def run():
    filterForShadowManager(processedTrafficFlow)
    generateRealFlow(processedTrafficFlow)
    filterWithAccuracy(inputFile, accuracyFile, date_column='data', sensor_id_column='codice_spira', output_file=accurateInputFile, accepted_percentage=95)
    generateRoadnamesFile(inputFile=accurateInputFile, sumoNetFile=netFile, outputFile='roadnames.csv')
    roadnamesFile = os.path.abspath(simulationDataPath + 'roadnames.csv')
    fillMissingEdgeId(roadnamesFile)
    linkEdgeId(inputFile=accurateInputFile, roadnameFile=roadnamesFile, outputFile=processedTrafficFlow)

    generateEdgedataFile(processedTrafficFlow, 'edgedata.xml', '01/02/2024', '07:00-08:00')
    filterDay(processedTrafficFlow, date='01/02/2024')
