import os
from libraries.constants import *
from libraries.preprocessing_utils import *

#csv file to be filtered
inputFile = (citySimulationDataPath + 'traffic_flow_2024.csv')
accuracyFile = citySimulationDataPath + 'accuratezza-spire-anno-2024.csv'  # File che rappresenta in percentuale l'accuratezza delle spire
accurateInputFile = citySimulationDataPath + 'accurate_traffic_flow.csv'
netFile = citySimulationPath + 'static/full.net.xml'

filter_with_accuracy(inputFile, accuracyFile, date_column='data', sensor_id_column='codice_spira', output_file=accurateInputFile, accepted_percentage=95)

##FUNCTION TO BE TESTED
# generate_detector_csv(accurateInputFile)
# add_start_end(inputFile=citySimulationDataPath + "day_flow.csv", roadnameFile=newroadnamesFile,
#               arcFile= citySimulationDataPath + "arcstra.csv", nodeFile=citySimulationDataPath + "nodi.csv", sumoNetFile=netFile)
# generate_flow(citySimulationDataPath + "traffic_with_flow.csv")

# generate_roadnames_file(inputFile=accurateInputFile, sumoNetFile=netFile, outputFile='roadnames.csv')
newroadnamesFile = os.path.abspath(citySimulationDataPath + 'roadnames.csv')
# fill_missing_edge_id(newroadnamesFile)
processedTrafficFlow = link_edge_id(accurateInputFile, newroadnamesFile)

generate_edgedata_file(processedTrafficFlow, 'edgedata.xml', '01/02/2024', '07:00-08:00')
filter_day(processedTrafficFlow, date='01/02/2024')
