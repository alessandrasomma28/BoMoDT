import os

from libraries.constants import *
from libraries.preprocessing_utils import *

### PREPROCESSING PHASE
#csv file to be filtered
inputFile = simulationDataPath + 'traffic_flow_2024.csv'  # File CSV contenente l'insieme dei nomi di vie
outputFile = simulationDataPath + 'output.csv'  # File CSV dove salvare il risultato filtrato
accuracyFile = citySimulationDataPath + 'accuratezza-spire-anno-2024.csv'  # File che rappresenta in percentuale l'accuratezza delle spire
accuracyOutputFile = citySimulationDataPath + 'accurate_output.csv'
filterFile = simulationPath + 'roadnames.csv'

# # First the entries are filtered based on the accuracy value of measurement
filter_with_accuracy(inputFile, accuracyFile, date_column='data', sensor_id_column='codice_spira', output_file=accuracyOutputFile, accepted_percentage=95)

#NEW FUNCTIONS RUN
inputCityFile = citySimulationDataPath + 'traffic_flow_2024.csv'
netFile = citySimulationPath + 'static/full.net.xml'
# generate_roadnames_file(inputFile=accuracyOutputFile, sumoNetFile=netFile, outputFile='new_roadnames.csv')
newroadnamesFile = os.path.abspath(citySimulationDataPath + 'new_roadnames.csv')
fill_missing_edge_id(newroadnamesFile)
fileWithEdges = link_edge_id(accuracyOutputFile, newroadnamesFile)


# # call this function to filter road according to the filter file
# filter_roads_legacy(accuracyOutputFile, filterFile, outputFile)
# # this function add a new column in the data, pointing which edge_id is linked with the referring roads
# link_roads_IDs_legacy(outputFile, filterFile)

linked_roads = simulationDataPath + 'final.csv'
# generate_edgedata_file(linked_roads, 'edgedata.xml', '01/02/2024', '07:00-10:00')
generate_edgedata_file(fileWithEdges, 'edgedata.xml', '01/02/2024', '07:00-08:00')

filter_day(fileWithEdges, date='01/02/2024')

# generate_detector_file("./traffic_loop_dataset/day_flow.csv", "./SUMO/joined/data/")