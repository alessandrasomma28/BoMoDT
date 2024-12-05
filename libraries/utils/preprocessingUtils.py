import pandas as pd
import csv
import xml.etree.ElementTree as ET
#import datetime
from datetime import datetime
from libraries.constants import *
import sumolib
import os

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
    df1.to_csv(PROCESSED_DATA_PATH + output_file, sep=';')
    print("Created Output file with Road IDs linked")

#This method is used to filter the file before using it inside the DT platform
def filterDay(input_file, output_file ='day_flow.csv', date ="01/02/2024"):
    df1 = pd.read_csv(input_file, sep=';')
    df1 = df1[df1['data'].str.contains(date)]
    df1.to_csv(PROCESSED_DATA_PATH + output_file, sep=';')


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
                lat, lon = starting_road_coord.split(',')
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
    df.to_csv(PROCESSED_DATA_PATH + "traffic_with_flow.csv", sep=';')
def generateFlow(inputFile, time_slot="07:00-08:00"):
    df = pd.read_csv(inputFile, sep=';')
    root = ET.Element('routes')
    for index, row in df.iterrows():
        start = row["starting_edge_id"]
        end = row["ending_edge_id"]
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
    tree.write(PROCESSED_DATA_PATH + "/flow.xml", "UTF-8")
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


########################################################
##### CORRECTED FROM HERE ....

def filterWithAccuracy(file_input: str, file_accuracy: str,date_column: str,sensor_id_column: str, output_file: str,  accepted_percentage: int):
    """
    Filter the traffic loop dataset using accuracy information.

    This function filters `file_input` (a traffic loop dataset) using `file_accuracy` (an accuracy dataset).
    Both files must contain columns for date and sensor ID to ensure proper filtering.
    Measurements with accuracy percentages below `accepted_percentage` are excluded.

    Args:
        file_input (str): Path to the input file (traffic loop dataset).
        file_accuracy (str): Path to the accuracy file.
        date_column (str): Name of the date column in both files.
        sensor_id_column (str): Name of the sensor ID column in both files.
        output_file (str): Path for the output filtered file.
        accepted_percentage (int): Minimum accepted percentage of accuracy for filtering.

    Returns:
        None: Saves the filtered data to `output_file`.
    """
    # Load the input data and accuracy data from the specified file paths
    df_input = pd.read_csv(file_input, sep=';', encoding="UTF-8")
    df_accuracy = pd.read_csv(file_accuracy, sep=';', encoding="UTF-8")

    # Clean and filter the accuracy data to only include measurements above `accepted_percentage`
    for ind, column in enumerate(df_accuracy.columns):
        if ind > 1:  # Ignore the first two columns, assumed to be `date_column` and `sensor_id_column`
            # Remove '%' and convert to integers
            df_accuracy[column] = df_accuracy[column].str.replace('%', '').astype(int)
            # Drop rows where the accuracy is below `accepted_percentage`
            df_accuracy = df_accuracy[df_accuracy[column] >= accepted_percentage]

    # Extract date and sensor ID columns as an identifier for filtering
    identifier = df_accuracy[[date_column, sensor_id_column]]
    keys = list(identifier.columns)

    # Create indices based on the date and sensor ID columns for both dataframes
    i1 = df_input.set_index(keys).index
    i2 = df_accuracy.set_index(keys).index

    # Filter `df_input` to include only rows that match the high-accuracy entries in `df_accuracy`
    filtered_df = df_input[i1.isin(i2)]

    # Ensure the output directory exists
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Directory '{output_dir}' created for the output file.")

    # Save the filtered data to the specified output file
    filtered_df.to_csv(output_file, sep=';', index=False)
    print(f"Output with filtered accuracy created at '{output_file}'.")
def generateRoadNamesFile(inputFile: str, sumoNetFile: str, detectorFilePath: str, roadNamesFilePath: str):
    """
    Generate a road names file with edge IDs linked to each road based on geopoint coordinates.

    This function uses the coordinates provided in the input file to find the closest `edge_id` in the SUMO network.
    The `edge_id` is associated with each road name based on the provided coordinates. This information is saved in
    a CSV file and an XML file containing induction loop definitions for SUMO simulations.

    Args:
        inputFile (str): Path to the CSV file containing roads to map to an edge ID. This file should include
                         at least the columns 'Nome via' (road name) and 'geopoint' (latitude,longitude coordinates).
        sumoNetFile (str): Path to the SUMO network file (e.g., `net.xml`) that includes the road network.
        detectorFilePath (str): Path for the output XML file containing induction loop definitions.
        roadNamesFilePath (str): Path for the output CSV file where the mapped road names and edge IDs will be saved.

    Returns:
        None: The function saves two files:
              - A CSV file (`roadNamesFilePath`) with the road name and its corresponding edge ID.
              - An XML file (`detectorFilePath`) with induction loop definitions for SUMO.
    """
    # Load the SUMO network using sumolib
    net = sumolib.net.readNet(sumoNetFile)

    # Load input data and filter unique road names and geopoints
    input_df = pd.read_csv(inputFile, sep=';')
    df_unique = input_df[['Nome via', 'geopoint']].drop_duplicates()

    # Create the root element for the XML file
    root = ET.Element('additional')

    for index, row in df_unique.iterrows():
        # Extract latitude and longitude from the geopoint
        coord = row['geopoint']
        lat, lon = map(float, coord.split(','))

        # Convert geographic coordinates to SUMO's (x, y) coordinates
        x, y = net.convertLonLat2XY(lon, lat)
        print(f"SUMO reference coordinates (x, y): ({x}, {y})")

        # Find neighboring edges within a 25m radius, sorted by distance
        candidate_edges = net.getNeighboringEdges(x, y, r=25)
        edges_and_dist = sorted(candidate_edges, key=lambda edge: edge[1])

        # Attempt to find the closest edge that matches the road name or is suitable
        closest_edge = None
        if edges_and_dist:
            for edge, dist in edges_and_dist:
                edge_name = edge.getName().lower()
                road_name = row["Nome via"].lower()

                # Check if the edge name matches the road name, or find a suitable edge type
                if edge_name == road_name or edge.getType() not in ["highway.pedestrian", "highway.track",
                                                                    "highway.footway", "highway.path",
                                                                    "highway.cycleway", "highway.steps"]:
                    closest_edge = edge
                    break
            else:
                # If no matching edge is found, set closest_edge to the first suitable edge
                closest_edge = next((edge for edge, dist in edges_and_dist if
                                     edge.getType() not in ["highway.pedestrian", "highway.track", "highway.footway",
                                                            "highway.path", "highway.cycleway", "highway.steps"]), None)

        if closest_edge:
            print(f"Name: {closest_edge.getName()}")
            print(f"Edge ID: {closest_edge.getID()}")

            # Assign the closest edge ID to the row in df_unique
            df_unique.at[index, 'edge_id'] = closest_edge.getID()

            # Add an induction loop element to the XML structure
            ET.SubElement(root, 'inductionLoop', id=f"{index}_0", lane=f"{closest_edge.getID()}_0", pos="-5",
                          freq="1800", file="e1_real_output.xml")
        else:
            # Drop rows where no suitable edge is found within the network
            print(f"No suitable edge found for road '{row['Nome via']}' at coordinates ({lat}, {lon}).")
            df_unique.drop(index, inplace=True)

    # Ensure the directory for the XML output file exists
    os.makedirs(os.path.dirname(detectorFilePath), exist_ok=True)

    # Save the XML tree with pretty formatting
    tree = ET.ElementTree(root)
    ET.indent(tree, '  ')
    tree.write(detectorFilePath, encoding="UTF-8", xml_declaration=True)
    print(f"XML file saved at '{detectorFilePath}'")

    # Ensure the directory for the CSV output file exists
    os.makedirs(os.path.dirname(roadNamesFilePath), exist_ok=True)

    # Save the updated DataFrame with edge IDs to the specified CSV file path
    df_unique.to_csv(roadNamesFilePath, sep=';', index=False)
    print(f"CSV file with road names and edge IDs saved at '{roadNamesFilePath}'")
def fillMissingEdgeId(roadnameFile: str):
    """
    Fill in missing edge IDs in the road names file.

    This function finds all entries in the specified road names file that lack an `edge_id`. For each entry with a missing
    `edge_id`, it attempts to find another entry in the same file with the same road name (`Nome via`) that has a valid
    `edge_id`. If such an entry is found, the missing `edge_id` is filled in with this value. The function also reports
    the number of entries that couldn't be assigned an `edge_id` because no matching road name with an `edge_id` was found.

    Args:
        roadnameFile (str): Path to the CSV file containing road names and edge IDs.

    Returns:
        None: The function updates the CSV file in place.

    :param roadnameFile: The path to the CSV file where road names and edge IDs are stored. The file is expected to
                         contain at least two columns:
                         - 'Nome via': The name of the road.
                         - 'edge_id': The unique identifier for each edge in the SUMO network.

    Side Effects:
        - Updates the input CSV file by filling in missing `edge_id` values where possible.
        - Prints the number of rows without an `edge_id` after attempting to fill them in.
    """
    # Load the road names data from the specified file
    df = pd.read_csv(roadnameFile, sep=';')
    empty = 0

    # Iterate over each row to check for missing edge IDs
    for index, row in df.iterrows():
        if pd.isnull(row['edge_id']):
            # Find other rows with the same road name ('Nome via') that have a valid edge ID
            sameStreet = df[(df['Nome via'] == row['Nome via']) & (df['edge_id'].notna())]
            if not sameStreet.empty:
                # Fill in the missing edge_id with the first matching edge_id found
                df.at[index, 'edge_id'] = sameStreet['edge_id'].values[0]
            else:
                # Increment count if no matching edge ID is found
                empty += 1

    # Report the number of roads without an edge ID
    print("Roads without edge ID: " + str(empty))
    # Save the updated DataFrame back to the CSV file
    df.to_csv(roadnameFile, sep=';', index=False)
def linkEdgeId(inputFile: str, roadnameFile: str, outputFile: str):
    """
    Link edge IDs from the road names file to each entry in the input file.

    This function matches entries from `inputFile` to entries in `roadnameFile` based on the road name (`Nome via`)
    and geographic point (`geopoint`). If a match is found, it assigns the corresponding `edge_id` to the entry in
    `inputFile`. Entries without a match are removed. The resulting data is saved to `outputFile`.

    Args:
        inputFile (str): Path to the input CSV file containing entries to which edge IDs will be linked.
                         This file should contain columns 'Nome via' and 'geopoint' for matching.
        roadnameFile (str): Path to the CSV file containing road names and edge IDs. This file should also
                            include 'Nome via', 'geopoint', and 'edge_id' columns.
        outputFile (str): Path for the output CSV file where the modified data with linked edge IDs will be saved.

    Returns:
        None: The function saves the updated data with edge IDs to `outputFile`.

    :param inputFile: The input CSV file containing data entries that need edge IDs.
    :param roadnameFile: The CSV file containing road names and associated edge IDs.
    :param outputFile: The path for the output CSV file where the updated data will be saved.

    Side Effects:
        - Saves the updated input data, with edge IDs linked where possible, to the specified `outputFile`.
    """
    # Load input and road names data
    df = pd.read_csv(inputFile, sep=';')
    dfRoadnames = pd.read_csv(roadnameFile, sep=';')

    # Iterate over each row in the input DataFrame to find and link edge IDs
    for index, row in df.iterrows():
        # Find matching edge_id in the road names file based on road name and geopoint
        edge = dfRoadnames.loc[
            (dfRoadnames['Nome via'] == row['Nome via']) &
            (dfRoadnames['geopoint'] == row['geopoint']),
            'edge_id'
        ]

        # If no matching edge_id is found, remove the row; otherwise, link the edge_id
        if len(edge) == 0:
            df.drop(index, inplace=True)
            continue
        df.at[index, 'edge_id'] = edge.values[0]  # Assign the first match

    # Save the modified DataFrame to the output file
    df.to_csv(outputFile, sep=';', index=False)
    print(f"Updated file with linked edge IDs saved at '{outputFile}'")
def filterForShadowManager(inputFile: str):
    """
    Filter and format data for the Shadow Manager.

    This function processes the input CSV file to extract and rename specific columns relevant to the Shadow Manager.
    It selects unique traffic loop entries based on the combination of road name (`RoadName`) and traffic loop ID (`TrafficLoopID`).
    The filtered and renamed data is then saved to a CSV file named `digital_shadow_types.csv` in the `SHADOW_TYPE_PATH` directory.

    Args:
        inputFile (str): Path to the CSV file containing raw traffic loop data with various columns.

    Returns:
        None: The function saves the processed data to `digital_shadow_types.csv` in the `SHADOW_TYPE_PATH` directory (resulting in the SHADOW_TYPE_FILE_PATH)

    :param inputFile: The path to the input CSV file.
    Side Effects:
        - Saves the processed and filtered data to a CSV file named `digital_shadow_types.csv` in the `SHADOW_TYPE_PATH` directory.
        - Creates the `SHADOW_TYPE_PATH` directory if it does not already exist.
    """
    # Load the input CSV file
    df = pd.read_csv(inputFile, sep=';')

    # Select and rename relevant columns for the Shadow Manager
    df = df[['Nodo da', 'Nodo a', 'Nome via', 'direzione', 'longitudine', 'latitudine', 'geopoint',
             'ID_univoco_stazione_spira', 'edge_id', 'codice_spira', 'Livello']]
    df.columns = ['StartingPoint', 'EndPoint', 'RoadName', 'Direction', 'Longitude', 'Latitude', 'Geopoint',
                  'TrafficLoopID', 'EdgeID', 'TrafficLoopCode', 'TrafficLoopLevel']

    # Remove duplicate entries based on the combination of RoadName and TrafficLoopID
    df = df.drop_duplicates(['RoadName', 'TrafficLoopID'])

    # Ensure the output directory exists
    if not os.path.isdir(SHADOW_TYPE_PATH):
        os.mkdir(SHADOW_TYPE_PATH)

    # Save the filtered DataFrame to a CSV file in the specified directory
    df.to_csv(os.path.join(SHADOW_TYPE_FILE_PATH), sep=';', index=False)


def generateRealFlow(inputFile: str):
    """
    Generate a real traffic flow file with selected columns.

    This function reads a CSV file containing traffic flow data, selects specific columns, and saves the filtered data
    to a new CSV file named `real_traffic_flow.csv` in the `REAL_TRAFFIC_FLOW_DATA_MVENV_PATH` directory.

    :param inputFile: The path to the input CSV file containing traffic data.

    Returns:
        None: The function saves the filtered data to `real_traffic_flow.csv` in the specified directory.
    """
    # Load the input CSV file
    df = pd.read_csv(inputFile, sep=';')

    # Select the relevant columns for real traffic flow data
    columns_to_keep = [
        'data', 'codice_spira', '00:00-01:00', '01:00-02:00', '02:00-03:00', '03:00-04:00', '04:00-05:00',
        '05:00-06:00', '06:00-07:00', '07:00-08:00', '08:00-09:00', '09:00-10:00', '10:00-11:00', '11:00-12:00',
        '12:00-13:00', '13:00-14:00', '14:00-15:00', '15:00-16:00', '16:00-17:00', '17:00-18:00', '18:00-19:00',
        '19:00-20:00', '20:00-21:00', '21:00-22:00', '22:00-23:00', '23:00-24:00', 'Nome via', 'direzione',
        'longitudine', 'latitudine', 'geopoint', 'ID_univoco_stazione_spira'
    ]
    df = df[columns_to_keep]

    # Ensure the output directory exists
    os.makedirs(REAL_TRAFFIC_FLOW_DATA_MVENV_PATH, exist_ok=True)

    # Save the filtered DataFrame to the output CSV file with index label 'index'
    output_file = os.path.join(REAL_TRAFFIC_FLOW_DATA_MVENV_PATH, "real_traffic_flow.csv")
    df.to_csv(output_file, sep=';', index_label='index')
    print(f"Filtered real traffic flow data saved at '{output_file}'")


def generateEdgeDataFile(input_file: str, date: str = "01/02/2024", time_slot: str = "00:00-01:00", duration: str = '3600'):
    """
    Generate an XML `edgedata` file for the route sampler in Eclipse SUMO.

    This function creates an XML file that includes edge traffic data for the specified date and time slot, based on the
    vehicle count data in `input_file`. The output XML file is saved to `EDGE_DATA_FILE_PATH`.

    :param input_file: Path to the CSV file containing traffic data. The file should contain:
                       - 'edge_id': ID of the road edge.
                       - 'data': Date of traffic measurement.
                       - Hourly time slot columns with vehicle counts (e.g., '00:00-01:00', '01:00-02:00').
    :param date: Date for which traffic data is extracted, formatted as 'dd/mm/yyyy'.
    :param time_slot: Time slot for traffic data extraction (e.g., '00:00-01:00').
    :param duration: Duration in seconds for the interval in the XML file. Default is '3600' (one hour).
    """
    # Create the root element for the XML structure
    root = ET.Element('data')
    interval = ET.SubElement(root, 'interval', begin='0', end=duration)

    # Load and filter data based on the specified date
    df = pd.read_csv(input_file, sep=';')
    df = df[df['data'].str.contains(date)]

    for index, row in df.iterrows():
        edge_id = str(row['edge_id'])
        first = int(time_slot[:2])
        last = int(time_slot[6:8])

        # Calculate the vehicle count for the specified time slot
        if last - first > 1:  # If the time slot spans multiple hours
            total_count = sum(row[f"{hour:02d}:00-{(hour + 1) % 24:02d}:00"] for hour in range(first, last))
            count = str(total_count)
        else:
            count = str(row[time_slot])

        # Add the edge element to the XML with the calculated count
        ET.SubElement(interval, 'edge', id=edge_id, entered=count)

    # Ensure the directory for the output file exists
    os.makedirs(os.path.dirname(EDGE_DATA_FILE_PATH), exist_ok=True)

    # Save the XML tree with indentation
    tree = ET.ElementTree(root)
    ET.indent(tree, '  ')
    tree.write(EDGE_DATA_FILE_PATH, encoding="UTF-8", xml_declaration=True)
    print(f"Edge data XML saved at '{EDGE_DATA_FILE_PATH}'")


def dailyFilter(inputFilePath: str, date: str):
    """
    Filter data by a specific date and save to a predefined daily traffic flow file.

    This function reads an input CSV file, filters rows based on the specified date, and saves the filtered data to `DAILY_TRAFFIC_FLOW_FILE_PATH'. The output file can be used
    within the Digital Twin environment for testing.

    :param inputFilePath: Path to the input CSV file containing raw traffic data. Expected columns include:
    :param date: Date to filter the data by, formatted as 'dd/mm/yyyy'.
    """
    # Load the input CSV file
    df = pd.read_csv(inputFilePath, sep=';')

    # Filter data by the specified date
    df_filtered = df[df['data'].str.contains(date)]

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(DAILY_TRAFFIC_FLOW_FILE_PATH), exist_ok=True)

    # Save the filtered data to the daily traffic flow file path
    df_filtered.to_csv(DAILY_TRAFFIC_FLOW_FILE_PATH, sep=';', index=False)
    print(f"Filtered data for date '{date}' saved at '{DAILY_TRAFFIC_FLOW_FILE_PATH}'")

def reorderDataset(inputFilePath: str, outputFilePath: str):
    """
    Reorder the dataset in chronological order based on the 'data' column.

    :param inputFilePath: Path to the input CSV file containing the dataset.
    :param outputFilePath: Path to the output file where the reordered dataset will be saved.
    """
    # Load the dataset
    df = pd.read_csv(inputFilePath, sep=';')

    # Ensure `data` column is in datetime format
    df['data'] = pd.to_datetime(df['data'], format='%Y-%m-%d')

    # Sort the dataset by date
    df_sorted = df.sort_values(by='data')

    # Save the reordered dataset
    df_sorted.to_csv(outputFilePath, sep=';', index=False)
    print(f"Dataset reordered by date and saved at '{outputFilePath}'")

def filteringDataset(inputFilePath: str, start_date: str, end_date: str, outputFilePath: str):
    """
    Filter the dataset for a specific date range and save it to a specified file.

    :param inputFilePath: Path to the input CSV file containing the dataset.
    :param start_date: Start date for filtering, formatted as 'mm/dd/yyyy'.
    :param end_date: End date for filtering, formatted as 'mm/dd/yyyy'.
    :param outputFilePath: Path where the filtered dataset will be saved.

    :side effect: Saves the filtered dataset to `outputFilePath`.
    """
    # Load the dataset
    df = pd.read_csv(inputFilePath, sep=';')

    # Convert `start_date` and `end_date` from 'mm/dd/yyyy' to 'yyyy-mm-dd' format for consistent comparison
    start_date = datetime.strptime(start_date, '%m/%d/%Y').strftime('%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%m/%d/%Y').strftime('%Y-%m-%d')

    # Ensure `data` column is parsed as datetime in 'dd/mm/yyyy' format
    df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')

    # Filter the dataset for the specified date range
    mask = (df['data'] >= start_date) & (df['data'] <= end_date)
    filtered_df = df.loc[mask]

    # Save the filtered dataset
    filtered_df.to_csv(outputFilePath, sep=';', index=False)
    print(f"Filtered data from {start_date} to {end_date} saved at '{outputFilePath}'")

def fillMissingDirections(inputFilePath: str, directionColumn="direzione", defaultDirection='N'):
    """
    Fill missing direction in a traffic file. If a default direction is not set, North will be used.
    Args:
        inputFilePath: Path to the input CSV file.
        directionColumn: column name where directions are defined.
        defaultDirection: direction to use when a road w.o. direction is met.

    Returns:
        The function updates the CSV file in place.
    """
    # Load the dataset
    df = pd.read_csv(inputFilePath, sep=';')

    # Replace empty or NaN values in the direction column with the defaultDirection
    df[directionColumn] = df[directionColumn].fillna(defaultDirection)

    # Save the modified dataset back to the same file
    df.to_csv(inputFilePath, index=False, sep=';')

    print(f"Missing values in '{directionColumn}' filled with default direction '{defaultDirection}'. File updated: {inputFilePath}")


