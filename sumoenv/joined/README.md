# Urban Simulation with SUMO 

This section summarises the activities carried out with the SUMO simulator, which consisted of running realistic traffic simulations in two districts of the city of Bologna. The activity involved an initial obtaining of data, subsequent pre-processing of these to make them usable by the simulator, and the execution of several simulations for the various time slots.

### Data Sourcing  
In order to construct a plausible simulation scenario, it was necessary to obtain data for the construction of the road network in SUMO (consisting of roads, junctions, traffic lights, etc.) and the traffic data itself. 

As for road networks, configurations available in the [SUMO scenario repository](https://github.com/DLR-TS/sumo-scenarios/tree/main) were used. The repository provides two neighbourhoods of the city of Bologna, identified by the name of their main street, namely Costa and Pasubio. These two areas are also proposed in joint form in the folder named *joined*. The folder consists of the network file (with the *net.xml* extension) and several additional files that enrich and complete the simulation environment:
- **run.sumocfg**: simulations on SUMO are usually defined via the .sumocfg file, which specifies what the inputs and outputs of the simulation are. In addition, there are parameters that modify the execution of the simulation itself (e.g. microscopic or mesoscopic execution).
- **joined_lanes.net.xml**: a SUMO network file that describes the traffic-related part of a map, the roads and intersections the simulated vehicles run along or across. The SUMO network contains every street (as a collection of lanes) including position, shape and speed limit of every lane, all the junctions and connections between lanes and junctions. 
- **routesampled.rou.xml**: this file represents the set of vehicles and routes they will take within the simulation. This data is the result of a series of pre-processing operations which, starting from the traffic loop readings obtained from Open Data, generated vehicle routes that would comply with the data detected. Details on how these routes are generated are explained in the pre-processing section.
- **joined_tls.add.xml** : the file includes the set of traffic lights and defines their operating logic.
- **joined_vtypes_add.xml** : The file includes the set of vehicle types passing through the simulation. Each vehicle is characterised by its size, the shape it takes in the simulation, acceleration and braking values.
- **tripinfos.xml**: output file showing the data collected from each vehicle, including departure and arrival times and speeds, the length of the route travelled and the time waiting in traffic.

All files presented are used within the simulation thanks to the configuration file *.sumocfg*. Once the simulation has started, the user must wait for it to complete in order to collect the output data.

The traffic data were taken from the [Open Data database of the municipality of Bologna ](https://opendata.comune.bologna.it/pages/home/). Among the various data made available by the database, those relating to the detection of the flow of vehicles through loops for the year 2024 and the accuracy of the loop measurement were taken. Since this data is constantly being updated, the tests performed only considered data from the 1st of January to the 30th of April 2024.
- [**traffic_flow_2024.csv**](https://opendata.comune.bologna.it/explore/dataset/rilevazione-flusso-veicoli-tramite-spire-anno-2024/information/?disjunctive.codice_spira&disjunctive.tipologia&disjunctive.nome_via&disjunctive.stato&sort=data): this file contains readings of the traffic flow through the loops. The file shows the readings in separate time slots per column, as well as the geographic location of the loop, in the form of geopoint coordinates. In order to associate the accuracy of the loops contained in the other file, it is necessary to refer to the loop code, here present with the name "*codice_spira*". There are two other entries in addition to the coordinates to provide more detail on the location of the loop: the street name (named "*Nome via*") and the direction (named "*direzione*") of the lane on which the traffic was detected, placed in the form of a cardinal point (in Italian NSOE stands for NSWE).
- [**accuratezza_spire_anno_2024.csv**](https://opendata.comune.bologna.it/explore/dataset/accuratezza-spire-anno-2024/information/?disjunctive.codice_spira_2): this file shows the percentage of accuracy of the traffic data detected by the loops. This dataset is to be cross-referenced with the first one by comparing the loop codes. The accuracy is reported for each time slot with a percentage value, where 100% indicates a correct detection of the data, 0% means that the loop did not detect the data, and intermediate values indicate partial detections within the reference time slot.

Finally, there is one last file, manually constructed by comparing the road names in the *traffic_flow_2024.csv* file with the *joined_lanes.net.xml* road network. This file, called **roadnames.csv** closely links these two data, reporting the edge ids associated with each road in the network used.
### Data pre-processing 

<figure align="center">
  <img
  src="https://github.com/user-attachments/assets/0be33d1e-c6f2-4fa9-bde1-a200f2984561"
  alt="Pre-processing-flow">
</figure>


The data obtained from Open Data is clearly presented in a raw format, which is hardly usable by SUMO. In order to make use of the data, it is necessary to extrapolate the car count information for a given lane and associate it with the lane identifier in the road network file described above. All files processed in the pre-processing phase are saved in the data folder.

Firstly, the data collected concerns the entire city of Bologna. It is therefore necessary to filter the data, taking into consideration only those relating to the districts identified by *via Costa* and *via Pasubio*. 
For this type of operation, the *filter_roads* function in the platform's preprocessing utils allows filtering precisely by the name of the streets under examination. In order to match the roads in the measurement with the roads in the network, however, it is necessary to map the names of the roads with the edge ids of the network. This operation, carried out manually, resulted in the file *roadnames.csv*. The result of the *filter_roads* operation (saved in the *output.csv* file) selected around three thousand rows of the approximately one hundred thousand in the total dataset. 

Subsequently, thanks to the accuracy data provided by Open Data, the data were further filtered, selecting only those with a certain accuracy value. This operation was carried out through the use of the function *filter_with_accuracy* which, based on the percentage value to be accepted (set by default at 90%), selects only those entries with a value strictly greater than the set value. The result is saved in the file *accurate_output.csv*. 

Starting from the constructed data roadnames.csv, through the function *link_roads_IDs*, the edge_id entries were added considering the direction of the road in a new file, named *final.csv*.

The final step is to reshape the data according to the structure required to generate a traffic file that can be used by SUMO. For this purpose, the function *generate_edgedata_file* allows the creation of a file needed to construct the route file to be used for the simulation. The generated file (**edgedata.xml**) shows, for each edge id, the number of vehicles that passed through a given time slot. This file will then be used for the simulation of one hour of traffic.

### Route File Generation

The generation of a route from traffic measurements obtained from Open Data is done through the use of a python script provided by the SUMO library, called [*routeSampler*](https://sumo.dlr.de/docs/Tools/Turns.html#routesamplerpy). This script generates traffic from an initial route file and a traffic count file of roads (called edgeData).

Instead, the generation of the initial route file is implemented through the use of another SUMO script, called [*randomTrips*](https://sumo.dlr.de/docs/Tools/Trip.html), which in turn accepts the network file (net.xml) as input and, defining appropriate parameters, generates a routing file (rou.xml) for that network. Among the various parameters that can be used for generation, *--fringe-factor* has been used for starting vehicle's trips at the fringe of the network, while *--random-routing-factor* has been configured to obtain different routes even for identical trips. The following is an example of a configuration of the randomTrips generation command:
```
python randomTrips.py -n .\joined_lanes.net.xml -r sampleRoutes.rou.xml --fringe-factor 10 –random-routing-factor 2
```
Afterwards, the output generated by the randomTrips command (*sampleRoutes.rou.xml*) is used together with the edgeData file generated by the previous preprocessing step to obtain a new route file respecting the crossing constraints.
```
python routeSampler.py -r .\sampleRoutes.rou.xml --edgedata-files .\edgedata.xml -o generatedRoutes.rou.xml --total-count 3000 --optimize full
```
the combined use of *--total-count* and *--optimize full* parameters allows the generation of routes that respect the counts detected by the loops but do not generate a vehicle for each count, resulting in higher (and unrealistic) traffic. Note that the commands used and shown as an example were used for traffic generation in the 8:00pm - 9:00pm time slot.
