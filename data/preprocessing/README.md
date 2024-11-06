# Data Files
This section describes the input and output files used within the preprocessing phase. Files that are processing results but are used as inputs for other functions are given in the Input/Output Files section
## Input Files
- **traffic_flow_2024.csv**: this file contains the traffic loop measurement data from January to April 2024. This data was taken from the [Bologna Open Data Repository - Traffic FLow](https://opendata.comune.bologna.it/explore/dataset/rilevazione-flusso-veicoli-tramite-spire-anno-2024). Used in:
	- *filter_with_accuracy*: using this file with *accuratezza-spire-anno-2024.csv*, the function filters the file, keeping the entries that have at least an certain amount of accuracy in percentage (above 95% by default). The output file is *accurate_traffic_flow.csv*.
	
- **accuratezza-spire-anno-2024.csv**: this file reports the accuracy value, in percentage related to the measurement taken. This data was taken from the [Bologna Open Data Repository - Traffic Flow Accuracy](https://opendata.comune.bologna.it/explore/dataset/accuratezza-spire-anno-2024). Used in:
	- *filter_with_accuracy*.

## Output Files
- **processed_traffic_flow.csv**: this file contains the accurate traffic loop measurement augmented with the road edge IDs coupled with the SUMO net. This is the outcome of an accuracy filtering and a linking function for edge_IDs.

## Input/Output Files 
- **accurate_traffic_flow.csv**: this file is the outcome of the *filter_with_accuracy* function. It contains the traffic loop measurement from January to April 2024 that have a certain value of accuracy (above 95% by default). Used in:
	- *(LEGACY) generate_detector_csv*: (INCLUDED into generate_roadname_file) function that creates a *detector.add.xml* file useful for simulate traffic loops inside the SUMO net.
	- *generate_roadname_file*: the function generate a *roadnames.csv*, a file that links each road to the SUMO net. It also generate a *detectors.add.xml*, an additional file for SUMO that simulate the traffic loops inside the SUMO net.
	- *link_edge_id*: using this file and the *roadnames.csv* file created previously, this function add the edge id columns inside the file, creating *linked_traffic_flow.csv*, file that can be used for generating counting/flow data for SUMO simulation.
- **roadnames.csv**: this file is the outcome of the *generate_roadname_file* function. It contains the name, the geopoint and the edge id for each road, linking the roads to the edges in the SUMO net. Used in:
	- *fill_missing_edge_id*: the function finds entries that didn't find any match in the *generate_roadname_file* and add the first edge id found with the same road name.
	- *link_edge_id*. 
