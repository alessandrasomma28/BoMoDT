import os

from libraries.constants import *
from libraries.preprocessing_utils import *

### PREPROCESSING PHASE
#csv file to be filtered
inputFile = (citySimulationDataPath + 'traffic_flow_2024.csv')  # File CSV contenente l'insieme dei nomi di vie
outputFile = simulationDataPath + 'output.csv'  # File CSV dove salvare il risultato filtrato
accuracyFile = citySimulationDataPath + 'accuratezza-spire-anno-2024.csv'  # File che rappresenta in percentuale l'accuratezza delle spire
accurateInputFile = citySimulationDataPath + 'accurate_traffic_flow.csv'
filterFile = simulationPath + 'roadnames.csv'


filter_with_accuracy(inputFile, accuracyFile, date_column='data', sensor_id_column='codice_spira', output_file=accurateInputFile, accepted_percentage=95)
netFile = citySimulationPath + 'static/full.net.xml'

##FUNCTION TO BE TESTD
# generate_detector_csv(accurateInputFile)
# add_start_end(inputFile=citySimulationDataPath + "day_flow.csv", roadnameFile=newroadnamesFile,
#               arcFile= citySimulationDataPath + "arcstra.csv", nodeFile=citySimulationDataPath + "nodi.csv", sumoNetFile=netFile)
# generate_flow(citySimulationDataPath + "traffic_with_flow.csv")


#NEW FUNCTIONS RUN
# generate_roadnames_file(inputFile=accurateInputFile, sumoNetFile=netFile, outputFile='roadnames.csv')
newroadnamesFile = os.path.abspath(citySimulationDataPath + 'roadnames.csv')
# fill_missing_edge_id(newroadnamesFile)
fileWithEdges = link_edge_id(accurateInputFile, newroadnamesFile)


# # call this function to filter road according to the filter file
# filter_roads_legacy(accuracyOutputFile, filterFile, outputFile)
# # this function add a new column in the data, pointing which edge_id is linked with the referring roads
# link_roads_IDs_legacy(outputFile, filterFile)

# linked_roads = simulationDataPath + 'final.csv'
# generate_edgedata_file(linked_roads, 'edgedata.xml', '01/02/2024', '07:00-10:00')
generate_edgedata_file(fileWithEdges, 'edgedata.xml', '01/02/2024', '07:00-08:00')

filter_day(fileWithEdges, date='01/02/2024')

# generate_detector_file("./traffic_loop_dataset/day_flow.csv", "./SUMO/joined/data/")