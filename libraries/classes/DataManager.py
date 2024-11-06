import pandas as pd
import typing
from typing import Optional
import psycopg2
from psycopg2.extensions import connection as PsycopgConnection, cursor as PsycopgCursor
from pymongo import MongoClient
from pymongo.database import Database
from datetime import datetime


#TODO: this class is responsible for managing all data. this means that has to be enriched
# with management of sumoenv results data, FIWARE data etc
class DataManager:
    """
    The DataManager class manages database connections and interaction with multiple database managers
    across the Digital Twin platform. It allows for adding and retrieving various database managers, and
    fetching connections to work with the database.

    Class Attributes:
    - name (str): The name of the data management system.
    - dbManagersByTypes (Dict[str, List[Any]]): A dictionary to store database managers by type.

    Class Methods:
    - addDBManager: Adds database managers to the system.
    - getDBManagerByType: Retrieves the database manager for the requested database type.
    - getDBConnectionByType: Retrieves the database connection and related attributes for the requested type.
    """

    name: str
    dbManagersByTypes: typing.Dict[str, typing.List[typing.Any]]

    def __init__(self, name: str):
        """
        Initializes the DataManager with a default name for the data management system.

        :param name: The name of the data management system.
        """
        self.name = name
        self.dbManagersByTypes = {}

    def addDBManager(self, dbManager: typing.Any):
        """
        Adds a new database manager to the dictionary of managers by type.

        :param dbManager: The database manager instance (e.g., TimescaleManager, MongoDBManager).
        """
        dbType = dbManager.name.replace("Manager", "")
        if dbType not in self.dbManagersByTypes:
            self.dbManagersByTypes[dbType] = []
        self.dbManagersByTypes[dbType].append(dbManager)
        print(f"Added {dbType} database manager reference.")

    def getDBManagerByType(self, dbType: str) -> typing.Any:
        """
        Retrieves a specific database manager for the given database type.

        :param dbType: The type of the database (e.g., "TimescaleDB", "MongoDB").
        :return: The database manager for the specified type.
        :raises ValueError: If the specified database type is not found.
        """
        dbType = dbType.replace("Manager", "")
        if dbType in self.dbManagersByTypes:
            return self.dbManagersByTypes[dbType][0]  # Return the first manager of that type
        else:
            raise ValueError(f"No database connections found for type: {dbType}")


    def getDBConnectionByType(self, dbType: str):
        """
        Retrieves the connection and related attributes for a specific database type.

        :param dbType: The type of the database (e.g., "TimescaleDBManager", "MongoDBManager").
        :return: The connection and cursor for TimescaleDBManager or client and db for MongoDBManager.
        :raises ValueError: If the specified database type is not found or not supported.
        """
        if dbType not in self.dbManagersByTypes:
            raise ValueError(f"No database managers found for type: {dbType}")

        manager = self.dbManagersByTypes[dbType]#[0]

        if dbType == "TimescaleDB" or dbType == "Timescale":
            # Ensure the manager has the required attributes
            if hasattr(manager, 'connection') and hasattr(manager, 'cursor'):
                return manager.connection, manager.cursor
            else:
                raise AttributeError(
                    f"The manager for {dbType} does not have the required attributes (connection, cursor).")

        elif dbType == "MongoDB" or dbType == "Mongo":
            if hasattr(manager, 'client') and hasattr(manager, 'db'):
                return manager.client, manager.db
            else:
                raise AttributeError(f"The manager for {dbType} does not have the required attributes (client, db).")

        else:
            raise ValueError(f"Unsupported database type: {dbType}")


class DBManager:
    """
    The base class for specific database managers, such as TimescaleDB and MongoDB.

    Class Attributes:
    - name (str): The name of the database manager.
    """

    def __init__(self, name: str):
        """
        Initializes the DBManager with a default name.

        :param name: The name of the database manager.
        """
        self.name = name

class TimescaleManager(DBManager):
    """
    The TimescaleManager class manages the connection to a TimescaleDB database and provides methods
    for storing and retrieving simulation data.

    Class Attributes:
    - connectionString (str): The connection string for connecting to the database.
    - connection (psycopg2.connection): The connection object for interacting with the TimescaleDB.
    - cursor (psycopg2.cursor): The cursor object for executing SQL queries.

    Class Methods:
    - dbConnect: Establishes a connection to the TimescaleDB.
    - storeSimulationData: Stores simulation data in the TimescaleDB.
    - retrieveHistoricalData: Retrieves historical data from the TimescaleDB.
    """

    connectionString: str
    connection: Optional[PsycopgConnection]
    cursor: Optional[PsycopgCursor]

    def __init__(self, host="localhost", port="5432", dbname="quantumleap", username="postgres",
                 password="postgres", managerName: Optional[str] = "TimescaleDBManager"):
        """
        Initializes the TimescaleManager with a connection to a TimescaleDB.

        :param host: The database host (default is localhost).
        :param port: The database port (default is 5432).
        :param dbname: The name of the database (default is 'quantumleap').
        :param username: The username for the database (default is 'postgres').
        :param password: The password for the database (default is 'postgres').
        :param managerName: Optional name to identify this manager. If not provided, defaults to 'TimescaleDBManager'.
        """
        super().__init__(name=managerName)
        self.connection, self.cursor = self.dbConnect(host=host, port=port, dbname=dbname, username=username, password=password)

    def dbConnect(self, host="localhost", port="5432", dbname="quantumleap", username="postgres",
                  password="postgres") -> typing.Tuple[PsycopgConnection, PsycopgCursor]:
        """
        Establishes a connection to a TimescaleDB database using psycopg2.

        :param host: The database host (default is localhost).
        :param port: The database port (default is 5432).
        :param dbname: The name of the database (default is 'quantumleap').
        :param username: The username for the database (default is 'postgres').
        :param password: The password for the database (default is 'postgres').
        :return: A tuple containing the connection and cursor objects.
        """
        self.connectionString = f"postgres://{username}:{password}@{host}:{port}/{dbname}"
        connection = psycopg2.connect(self.connectionString)
        cursor = connection.cursor()
        return connection, cursor


    def retrieveHistoricalDataForTimeslot(self, timeslot: str, date: str, entityType: str, timecolumn: str) -> pd.DataFrame:
        """
        Retrieves historical data from the TimescaleDB based on the provided parameters.

        :param timeslot: The time slot for which data is retrieved (e.g., "00:00-01:00").
        :param date: The date for which data is retrieved (e.g., "2024-02-01").
        :param entityType: The type of entity (e.g., "roadsegment", "device", "trafficflowobserved").
        :param timecolumn: The name of the time column in the database (default is 'timeslot').
        :return: A pandas DataFrame containing the retrieved historical data.
        """

        if not timeslot or not date or not entityType or not timecolumn:
            raise ValueError("All parameters (timeslot, date, entityType, timecolumn) must be provided.")

        if entityType.lower() in ["road segment", "roadsegment"]:
            tableName = "ethttps://smartdatamodels.org/datamodel.transportation/roadsegm"
            query = (
                f'SELECT entity_id, trafficflow, ST_X(location) as lat, ST_Y(location) as lon, edgeid as edgeID '
                f'FROM "mtopeniot"."ethttps://smartdatamodels.org/datamodel.transportation/roadsegm" '
                f'WHERE {timecolumn} = %s AND DATE(datetime) = %s'
            )
            self.cursor.execute(query, (timeslot, date))

        elif entityType.lower() == "device":
            try:
                queryDate = datetime.strptime(date, "%Y/%m/%d").strftime("%d/%m/%Y")
            except ValueError as e:
                print(f"Error converting date: {e}")
                return None
            query = (
                f'SELECT entity_id, trafficflow, ST_X(location) as lat, ST_Y(location) as lon '
                f'FROM mtopeniot.etdevice '
                f'WHERE {timecolumn} LIKE %s AND dateobserved LIKE %s'
            )
            self.cursor.execute(query, (timeslot, queryDate))

        elif entityType.lower() in ["trafficflowobserved", "traffic flow observed"]:
            query = (
                f'SELECT entity_id, trafficflow '
                f'FROM "mtopeniot"."ethttps://smartdatamodels.org/datamodel.transportation/trafficf" '
                f'WHERE {timecolumn} = %s AND DATE(datetime) = %s'
            )
            self.cursor.execute(query, (timeslot, date))

        records = self.cursor.fetchall()
        columns = [desc[0] for desc in self.cursor.description]
        return pd.DataFrame(records, columns=columns)

    def createView(self, tableName: str, viewName: str, schema="mtopeniot"):
        """
        Create a view from a specific table inside TimescaleDB. The view can be used to access tables with complex names
        (like NGSI-LD types). The created view will be available in the public schema
        :param tableName: name of the table from which to create the view
        :param viewName: name of the view
        :param schema: name of the schema in which the table is stored. By default, it's mtopeniot
        :return:
        """
        query = f"""
            CREATE VIEW {viewName} AS SELECT * FROM {schema}."{tableName}";
            """
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print(f"View '{viewName}' successfully created from table '{tableName}'!")
        except psycopg2.Error as e:
            print(f"Error during view creation: {e}")

class MongoDBManager(DBManager):
    """
    The MongoDBManager class manages the connection to a MongoDB database and provides methods for storing and retrieving data.

    Class Attributes:
    - client (MongoClient): The MongoDB client instance for interacting with the MongoDB server.
    - db (Database): The MongoDB database object.

    Class Methods:
    - storeSimulationData: Stores simulation data in the MongoDB database.
    - retrieveHistoricalData: Retrieves historical data from the MongoDB database.
    """

    client: MongoClient
    db: Database

    def __init__(self, connectionString: str, dbName: str):
        """
        Initializes the MongoDBManager with a connection string and database name.

        :param connectionString: The connection string to use for connecting to the MongoDB server.
        :param dbName: The name of the MongoDB database to use.
        """
        super().__init__(name="MongoDBManager")
        self.client = MongoClient(connectionString)
        self.db = self.client[dbName]


