import pandas as pd
import csv
import xml.etree.ElementTree as ET
import datetime
from libraries.constants import *
import sumolib
import os
from math import cos, asin, sqrt

def filterRoadsLegacy(input_file, road_file, output_file ='filtered_output.csv', input_column ='Nome via', filter_column ='nome_via'):
    """
    The function filters a traffic input file based on the road names. The input_column and filter_column must be
    specified to match the values of the road names between the input file and the road_file. The result will be written
    in the given output file. Unused roadnames inside the filter will be printed.
    """
    # Create a set of road names from the road file
    filter_roadnames = set()
    with open(road_file, 'r', newline='', encoding='utf-8') as csvfile_filter:
        reader_filter = csv.DictReader(csvfile_filter, delimiter=';')
        # Check if filter column exist inside the road_file
        if filter_column not in reader_filter.fieldnames:
            print("Error: column 'nome_via' not found inside the road file.")
            return
        for row in reader_filter:
            # Add column value to the filter set
            filter_roadnames.add(row[filter_column].lower())

    # Filter input file based on road names collected
    filtered_rows = []
    # List of road names in the input file
    input_roadnames = set()
    with open(input_file, 'r', newline='', encoding='utf-8') as csvfile_input:
        reader_input = csv.DictReader(csvfile_input, delimiter=';')
        headers = reader_input.fieldnames  # Ottieni gli header
        filtered_rows.append(headers)
        for row in reader_input:
            road_name = row[input_column].lower()
            input_roadnames.add(row[input_column].lower())
            # Add row if the road name is in the filter set
            if road_name in filter_roadnames:
                filtered_rows.append([row[col] for col in headers])

    # Write the result in the csv output file
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile_output:
        writer = csv.writer(csvfile_output, delimiter=';')
        writer.writerows(filtered_rows)
        print("Filtered output created. ")

    unmatched_roadnames = filter_roadnames - input_roadnames
    # Print unmatched roadnames
    print("Unused road names in the filter:")
    for voce in unmatched_roadnames:
        print(voce)
    print("The number of unmatched road names is: " + str(len(unmatched_roadnames)))


def filterWithAccuracy(file_input, file_accuracy, date_column='data', sensor_id_column='codice_spira', output_file='accurate_output.csv', accepted_percentage=90):
    """
    The function filters the traffic_loop_dataset using accuracy information. Both files must have the date and the ID of the sensor
    to be filtered properly. A threshold percentage can be provided to only accept the measurement above that value.
    """
    df1 = pd.read_csv(file_input, sep=';', encoding="UTF-8")
    df_acc = pd.read_csv(file_accuracy, sep=';', encoding="UTF-8")
    # Filtering the accuracy file to only have measurements above the accepted_percentage
    for ind, column in enumerate(df_acc.columns):
        if ind > 1:
            df_acc[column] = df_acc[column].str.replace('%', '')
            df_acc = df_acc.drop(df_acc[df_acc[column].astype(int) < accepted_percentage].index)
    # Filtering the file_input by matching it with the filtered accuracy file
    identifier = df_acc[[date_column, sensor_id_column]]
    keys = list(identifier.columns.values)
    i1 = df1.set_index(keys).index
    i2 = df_acc.set_index(keys).index
    df = df1[i1.isin(i2)]
    df.to_csv(output_file, sep=';')
    print("Output with filtered accuracy created. ")

def linkRoadsIDsLegacy(file_input, road_file_ids, output_file ='final.csv', input_roadname_column ='Nome via', direction_column ='direzione', filter_direction_column ='orientamento', roadname_column ='nome_via'):
    """
    The function adds the road IDs based on the road file given as a new column in the input file. The entries in the
    input file must have a direction (expressed using direction_column) in order to be linked with the right lane ID of
    the road.
    """
    df1 = pd.read_csv(file_input, sep=';')
    # Dropping entries without a direction
    df1 = df1.dropna(subset=[direction_column])
    df1["edge_id"] = "unknown"
    df2 = pd.read_csv(road_file_ids, sep=';')
    df2['nome_via'] = df2[roadname_column].str.lower()
    df1 = df1.reset_index()  # make sure indexes pair with number of rows
    for index, row in df1.iterrows():
        roadname = row[input_roadname_column].lower()
        direction = row[direction_column]
        # check if direction is multiple (e.g. SW for South-West)
        if len(direction) > 1:
            direction1 = direction[:1]
            direction2 = direction[1:]
            matched_row = df2[df2[roadname_column].str.contains(roadname) & (df2[filter_direction_column].str.contains(direction1) | df2[filter_direction_column].str.contains(direction2))]
        else:
            matched_row = df2[df2[roadname_column].str.contains(roadname) & df2[filter_direction_column].str.contains(direction)]
        df1.at[index, 'edge_id'] = matched_row['edge_id'].values
    df1.to_csv(simulationDataPath + output_file, sep=';')
    print("Created Output file with Road IDs linked")

def generateEdgedataFile(input_file, output_file ='edgedata.xml', date ="01/02/2024", time_slot ="00:00-01:00", duration ='3600'):
    """
    The function generate the XML edgedata file useful for the route sampler in Eclipse SUMO. Each row in the input file
    must have an edge id, a date and a time_slot in which the number of vehicles are reported.
    """
    root = ET.Element('data')
    interval = ET.SubElement(root, 'interval', begin='0', end=duration)
    df1 = pd.read_csv(input_file, sep=';')
    df1 = df1[df1['data'].str.contains(date)]
    for index, row in df1.iterrows():
        edge_id = str(row['edge_id'])
        first = int(time_slot[0:2])
        last = int(time_slot[6:8])
        # check if time window is longer than one hour
        if last - first > 1:
            time_slots = []
            for hour in range(first, last):
                time_slot1 = f"{hour:02d}:00-{(hour + 1) % 24:02d}:00"
                time_slots.append(time_slot1)
            total_count = 0
            for time_slot1 in time_slots:
                total_count += row[time_slot1]
            count = str(total_count)
        else:
            count = str(row[time_slot])
        edge = ET.SubElement(interval,'edge', id=edge_id, entered=count)
    tree = ET.ElementTree(root)
    ET.indent(tree, '  ')
    tree.write(simulationDataPath + output_file, "UTF-8")

#This method is used to filter the file before using it inside the DT platform
def filterDay(input_file, output_file ='day_flow.csv', date ="01/02/2024"):
    df1 = pd.read_csv(input_file, sep=';')
    df1 = df1[df1['data'].str.contains(date)]
    df1.to_csv(simulationDataPath + output_file, sep=';')


# Function to map the existing traffic loop and generate an additional SUMO file containing the traffic detectors at
# corresponding positions
def generateDetectorFileLegacy(realDataFile: str, outputPath: str):
    df = pd.read_csv(realDataFile, sep=';')
    trafficLoopRoads = df["edge_id"].unique()
    print(len(trafficLoopRoads.shape))
    root = ET.Element('additional')
    for index, road in enumerate(trafficLoopRoads):
        # road = road.replace(" ", "")
        if str(road) != "nan":
            ET.SubElement(root, 'inductionLoop', id = str(index)+'_0', lane=str(road)+'_0', pos="50", freq="1800", file="e1_real_output.xml")
        # ET.SubElement(root, 'inductionLoop', id = str(index)+'_1', lane = road+'_1', pos = "5", freq = "1800", file = "e1_real_output.xml")
    tree = ET.ElementTree(root)
    ET.indent(tree, '  ')
    tree.write(outputPath+"detectors.add.xml", "UTF-8")

#NEW PRE-PROCESSING FUNCTIONS
def generateRoadnamesFile(inputFile, sumoNetFile, outputFile ='new_roadnames.csv'):
    """
    Using the geopoint coordinates available in the input file, a roadnames file with edge_id linked to each
    road is created. The edge_ids are found using a sumolib function to get edges near to the given coordinates.
    :param inputFile: the file including every possible road to be mapped to an edge_id
    :param sumoNet: a SUMO network instance including the same roads present in the input file
    :param outputFile: the file name of the new roadnames generated
    :return:
    """
    # path = os.path.abspath('./SUMO/bologna/full.net.xml')
    net = sumolib.net.readNet(sumoNetFile)
    input_df = pd.read_csv(inputFile, sep=';')
    df_unique = input_df[['Nome via', 'geopoint']].drop_duplicates()
    # df_unique = input_df[['Nome via']].drop_duplicates()
    root = ET.Element('additional')
    for index, row in df_unique.iterrows():
        coord = row['geopoint']
        lat, lon = coord.split(',')
        lat = float(lat)
        lon = float(lon)
        x, y = net.convertLonLat2XY(lon, lat)
        print(f"SUMO reference coordinates (x,y): {x, y}")

        candiates_edges = net.getNeighboringEdges(x, y, r=25)
        # Sorting neighbors by distance
        edges_and_dist = sorted(candiates_edges, key=lambda x: x[1])

        if len(edges_and_dist) != 0:
            closest_edge = edges_and_dist[0][0]
            i = 0
            name = (closest_edge.getName()).lower()
            roadname = row["Nome via"].lower()
            while name != roadname:
                i += 1
                if i == edges_and_dist.__len__():
                    i=0
                    closest_edge = edges_and_dist[i][0]
                    while closest_edge.getType in ["highway.pedestrian","highway.track", "highway.footway", "highway.path",
                                                   "highway.cycleway", "highway.steps"]:
                        i += 1
                        closest_edge = edges_and_dist[i][0]
                    break

                closest_edge = edges_and_dist[i][0]
                name = (closest_edge.getName()).lower()

        else:
            # dropping the loops outside the network
            df_unique.drop(index, inplace=True)
            continue
        print(f"Name: {closest_edge.getName()}")
        print(f"Edge ID: {closest_edge.getID()}")
        df_unique.at[index, 'edge_id'] = closest_edge.getID()
        ET.SubElement(root, 'inductionLoop', id=str(index) + '_0', lane=str(closest_edge.getID()) + '_0', pos="-5", freq="1800",
                      file="e1_real_output.xml")
    tree = ET.ElementTree(root)
    ET.indent(tree, '  ')
    tree.write(simulationPath + "static/detectors.add.xml", "UTF-8")
    df_unique.to_csv(simulationDataPath + outputFile, sep=';')

def fillMissingEdgeId(roadnameFile):
    """
    Finds all entries without edge_id and adds the first edge_id it finds with the same road name
    :param roadnameFile:
    :return:
    """
    df = pd.read_csv(roadnameFile, sep=';')
    empty = 0
    for index, row in df.iterrows():
        if pd.isnull(row['edge_id']):
            same_street = df[(df['Nome via'] == row['Nome via']) & (df['edge_id'].notna())]
            if not same_street.empty:
                df.at[index, 'edge_id'] = same_street['edge_id'].values[0]
            else:
                empty += 1
    print("Road without edge id: " + str(empty))
    df.to_csv(roadnameFile, sep=';')

def linkEdgeId(inputFile, roadnameFile, outputFile: str):
    """
    Using a roadnameFile with edge_ids (created with generate_roadname_files) edge_id is added for each entry in
    the :param inputFile
    :param inputFile:
    :param roadnameFile:
    :return:
    """
    df = pd.read_csv(inputFile, sep=';')
    df_roadnames = pd.read_csv(roadnameFile, sep=';')

    for index, row in df.iterrows():
        edge = df_roadnames.loc[(df_roadnames['Nome via'] == row['Nome via']) & (df_roadnames['geopoint'] == row['geopoint']), 'edge_id']
        if len(edge) == 0:
            df.drop(index, inplace=True)
            continue
        df.at[index, 'edge_id'] = edge.values
    df.to_csv(outputFile, sep=';')


def addStartEnd(inputFile, roadnameFile, arcFile, nodeFile, sumoNetFile):
    df = pd.read_csv(inputFile, sep=';')
    df_roadnames = pd.read_csv(roadnameFile, sep=';')
    df_arch = pd.read_csv(arcFile, sep=';')
    df_nodes = pd.read_csv(nodeFile, sep=';')
    net = sumolib.net.readNet(sumoNetFile)
    for index, row in df.iterrows():
        codvia = row['codice via']
        codarco = row['codice arco']
        matched = df_arch.loc[(df_arch['CODVIA'] == codvia) & (df_arch['CODARCO'] == codarco)]
        if matched.shape[0] > 0:
            if type(matched['Da'].values[0]) == float:
                starting_roadname = "None"
            else:
                starting_roadname = matched['Da'].values[0].lower()
            if type(matched['A'].values[0]) == float:
                ending_roadname = "None"
            else:
                ending_roadname = matched['A'].values[0].lower()

            starting_node = matched["COD_NODO1"].values[0]
            ending_node = matched["COD_NODO2"].values[0]

            starting_road_coord = df_nodes.loc[df_nodes['CODICE'] == starting_node]['Geo Point'].values[0]
            ending_road_coord = df_nodes.loc[df_nodes['CODICE'] == ending_node]['Geo Point'].values[0]
            coords = [starting_road_coord, ending_road_coord]
            for ind, coord in enumerate(coords):
                lat, lon = coord.split(',')
                lat = float(lat)
                lon = float(lon)
                x, y = net.convertLonLat2XY(lon, lat)
                print(f"SUMO reference coordinates (x,y): {x, y}")
                candiates_edges = net.getNeighboringEdges(x, y, r=25)
                # Sorting neighbors by distance
                edges_and_dist = sorted(candiates_edges, key=lambda x: x[1])
                if len(edges_and_dist) != 0:
                    closest_edge = edges_and_dist[0][0]
                    i = 0
                    print(closest_edge.getType())
                    name = (closest_edge.getName()).lower()
                    if ind == 0:
                        if type(matched['Da'].values[0]) == float:
                            matchname = "None"
                        else:
                            matchname = matched["Da"].values[0].lower()
                    else:
                        if type(matched['A'].values[0]) == float:
                            matchname = "None"
                        else:
                            matchname = matched["A"].values[0].lower()
                    while name != matchname:
                        i += 1
                        if i == edges_and_dist.__len__():
                            i = 0
                            closest_edge = edges_and_dist[i][0]
                            while closest_edge.getType in ["highway.pedestrian", "highway.track", "highway.footway",
                                                           "highway.path",
                                                           "highway.cycleway", "highway.steps"]:
                                i += 1
                                closest_edge = edges_and_dist[i][0]
                            break

                        closest_edge = edges_and_dist[i][0]
                        name = (closest_edge.getName()).lower()
                else:
                    continue
                print(f"Name: {closest_edge.getName()}")
                print(f"Edge ID: {closest_edge.getID()}")
                if ind == 0:
                    df.at[index, 'starting_edge_id'] = closest_edge.getID()
                else:
                    df.at[index, 'ending_edge_id'] = closest_edge.getID()

        else:
            print("Error, road not found!")
    df.to_csv(simulationDataPath+ "traffic_with_flow.csv", sep=';')

def generateFlow(inputFile, time_slot="07:00-08:00", date="01/02/2024"):
    df = pd.read_csv(inputFile, sep=';')
    root = ET.Element('routes')
    df = df[df['data'].str.contains(date)]
    for index, row in df.iterrows():
        start = row["starting_edge_id"]
        end = row["ending_edge_id"]
        via = row["edge_id"]
        first = int(time_slot[0:2])
        last = int(time_slot[6:8])
        # check if time window is longer than one hour
        if last - first > 1:
            time_slots = []
            for hour in range(first, last):
                time_slot1 = f"{hour:02d}:00-{(hour + 1) % 24:02d}:00"
                time_slots.append(time_slot1)
            total_count = 0
            for time_slot1 in time_slots:
                total_count += row[time_slot1]
            count = str(total_count)
        else:
            count = str(row[time_slot])
        ET.SubElement(root, "flow", id=str(index), frm=str(start), to=str(end), begin="0", end="3600", number=count)
    tree = ET.ElementTree(root)
    ET.indent(tree, '  ')
    tree.write(simulationDataPath + "/flow.xml", "UTF-8")

def generateDetectorFile(inputFile):
    df = pd.read_csv(inputFile, sep=';')
    df_unique = df[['Nome via', 'geopoint']].drop_duplicates()
    # Creazione del file CSV
    with open('output.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['id', 'lat', 'lon'])  # Scrive l'intestazione
        for index, row in df_unique.iterrows():
            id = 'det' + str(index)
            coord = row['geopoint']
            lat, lon = coord.split(',')
            lat = str(lat)
            lon = str(lon)
            writer.writerow([id,lat,lon])

def filterForShadowManager(inputFile):
    df = pd.read_csv(inputFile, sep=';')
    df = df[['Nodo da', 'Nodo a', 'Nome via', 'direzione', 'longitudine', 'latitudine', 'geopoint',
             'ID_univoco_stazione_spira', 'edge_id', 'codice_spira', 'Livello']]
    df.columns = ['StartingPoint', 'EndPoint', 'RoadName', 'Direction', 'Longitude', 'Latitude', 'Geopoint',
                  'TrafficLoopID', 'EdgeID', 'TrafficLoopCode', 'TrafficLoopLevel']

    df = df.drop_duplicates(['RoadName', 'TrafficLoopID', 'Geopoint'])
    if not os.path.isdir(projectPath + '/data/digitalshadow/'):
        os.mkdir(projectPath + '/data/digitalshadow/')
    df.to_csv(projectPath + "/data/digitalshadow/filtered_traffic_flow.csv", sep=';')

def generateRealFlow(inputFile):
    df = pd.read_csv(inputFile, sep=';')
    df = df[['data','codice_spira','00:00-01:00','01:00-02:00','02:00-03:00','03:00-04:00','04:00-05:00',
        '05:00-06:00','06:00-07:00','07:00-08:00','08:00-09:00','09:00-10:00','10:00-11:00','11:00-12:00','12:00-13:00',
        '13:00-14:00','14:00-15:00','15:00-16:00','16:00-17:00','17:00-18:00','18:00-19:00','19:00-20:00','20:00-21:00',
        '21:00-22:00','22:00-23:00','23:00-24:00','Nome via','direzione','longitudine','latitudine','geopoint',
             'ID_univoco_stazione_spira']]
    if not os.path.isdir(projectPath + '/data/realworlddata/mvenvdata'):
        os.mkdir(projectPath + '/data/realworlddata/mvenvdata')
    df.to_csv(projectPath + "/data/realworlddata/mvenvdata/real_traffic_flow.csv", sep=';', index_label='index')



def generateTurnData(inputFile):
    df = pd.read_csv(inputFile, sep=';')
    root = ET.Element('data')
    interval = ET.SubElement(root, 'interval', id='generated', begin='0', end='3600')
    for index, row in df.iterrows():
        start = row['starting_edge_id']
        end = row['ending_edge_id']
        count = row['07:00-08:00']
        edgeId = row['edge_id']
        edgerelation = ET.SubElement(interval, 'edgeRelation', id=str(edgeId), frm=str(start), to=str(end), count=str(count))
    tree = ET.ElementTree(root)
    ET.indent(tree, '  ')
    tree.write(simulationDataPath + "turn.xml", "UTF-8")

# def distance(lat1, lon1, lat2, lon2):
#     p = 0.017453292519943295
#     hav = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * (1-cos((lon2-lon1)*p)) / 2
#     return 12742 * asin(sqrt(hav))
#
# def closest(data, v):
#     return min(data, key=lambda p: distance(v['lat'],v['lon'],p['lat'],p['lon']))

# def altAddStartEnd(inputFile, roadnameFile, arcFile, nodeFile, sumoNetFile):
#     df = pd.read_csv(inputFile, sep=';')
#     df_roadnames = pd.read_csv(roadnameFile, sep=';')
#     df_arch = pd.read_csv(arcFile, sep=';')
#     df_nodes = pd.read_csv(nodeFile, sep=';')
#     net = sumolib.net.readNet(sumoNetFile)
#     for index, row in df.iterrows():
#         codvia = row['codice via']
#         codarco = row['codice arco']
#         matched = df_arch.loc[(df_arch['CODVIA'] == codvia) & (df_arch['CODARCO'] == codarco)]
#         if matched.shape[0] > 0:
#             if type(matched['Da'].values[0]) == float:
#                 starting_roadname = "None"
#             else:
#                 starting_roadname = matched['Da'].values[0].lower()
#             if type(matched['A'].values[0]) == float:
#                 ending_roadname = "None"
#             else:
#                 ending_roadname = matched['A'].values[0].lower()
#
#             starting_node = matched["COD_NODO1"].values[0]
#             ending_node = matched["COD_NODO2"].values[0]
#
#             starting_road_coord = df_nodes.loc[df_nodes['CODICE'] == starting_node]['Geo Point'].values[0]
#             ending_road_coord = df_nodes.loc[df_nodes['CODICE'] == ending_node]['Geo Point'].values[0]
#             coords = [starting_road_coord, ending_road_coord]
#             for index, coord in enumerate(coords):
#                 lat, lon = starting_road_coord.split(',')
#                 # v  = {'lat':}
#                 print("prova")