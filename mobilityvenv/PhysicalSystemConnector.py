# ****************************************************
# Module Purpose:
#   This library defines three main classes: Device, Sensor, and PhysicalSystemConnector for modeling and
#   managing physical systems.
#
#   - The Device class represents a generic device and includes attributes for device identification and API key.
#   - The Sensor class inherits from Device and adds attributes specific to sensors, such as name and sensor type.
#     It also includes methods for setting a data callback and sending data.
#   - The PhysicalSystemConnector class represents a connector within a physical system. It allows for the addition
#     of sensors and provides methods for managing them, such as retrieving the number of connected devices and saving
#     device information to a CSV file.
#
# ****************************************************

from libraries.utils.generalUtils import *
import inspect


class Device:
    """
    Class representing a generic device.
    Class Attributes:
    - devicePartialID (str): Unique identifier of the device.
    - deviceType (str): String to classify the device type.
    - apiKey : API alphanumeric key associated with the device.

    Class Methods:
        - __init__ : Constructor to initialize a new instance of the class.
    """

    devicePartialID = str
    deviceType = str
    apiKey = str

    def __init__(self, partial_id: str, devicetype: str, key: str):
        """
        Inizialize a new Device instance.

        :param partial_id: Unique identifier of the device. It should be structured as
                               DEVICE_CATEGORY:PROGRESSIVE_NUMBER, e.g., two GPS sensors should have
                               device IDs as GPS:001 and GPS:002.
        :param devicetype: Type of the device.
        :param key: API key associated with the device.
        """
        self.devicePartialID = partial_id
        self.deviceType = devicetype
        self.apiKey = key


class Sensor(Device):
    """
    Represents a sensor device, inheriting from the Device class.

    Class Attributes:
    - name (str): Name of the sensor.
    - sensorType (str): Category of sensor, e.g., all sensors measuring location/position
                         have sensorType set as GPS.

    Class Methods:
        - __init__: Constructor to initialize a new instance of the class.
        - help: Method for printing docstrings of class methods.
        - setDataCallback: Method to set a callback function to handle sensor data.
        - sendData: Method to send data using the defined callback function.
    """
    name: str
    sensorType: str

    def __init__(self, device_partialid: str, devicekey: str, name: str, sensortype: str):
        """
        Initialize a new Sensor instance.

        :param device_partialid: Unique identifier of the sensor device.
        :param devicekey: API key associated with the sensor device.
        :param name: Name of the sensor.
        :param sensortype: Type of the sensor.
        """
        super().__init__(partial_id=device_partialid, devicetype="Sensor", key=devicekey)
        self.name = name
        self.sensorType = sensortype
        self.dataCallback = None

    def help(self, method_names=None):
        """
        Prints the docstring of specified methods in the parameter list or all methods in this class.

        :param method_names: List of method names to print docstrings for (optional)
        """
        if method_names is None:
            methods = inspect.getmembers(self, predicate=inspect.ismethod)
            for name, method in methods:
                if name != '__init__':  # excluding the constructor
                    print(f"{name}:\n{method.__doc__}\n")
        else:
            for name in method_names:
                if name != "__init__":
                    method = getattr(self, name, None)
                    if method is not None and inspect.ismethod(method):
                        print(f"{name}:\n{method.__doc__}\n")

    def setDataCallback(self, callback) -> None:
        """
        Set a callback function to handle sensor data.

        :param callback: The callback function to be set.
        """
        self.dataCallback = callback

    def sendData(self, *data, device_id: str, device_key: str):
        """
        Send data using the defined callback function.

        :param data: Variable number of data to be sent.
        :param device_id: Unique identifier of the sensor device.
        :param device_key: API key associated with the sensor device.
        :raises RuntimeError: If no callback function is defined.
        """
        if self.dataCallback:
            self.dataCallback(data, device_id=device_id, device_key=device_key)
        else:
            raise RuntimeError("No callback for sending data defined.")


class PhysicalSystemConnector:
    """
    Class representing a Physical System Connector.

    Class Attributes:
    - partialIdentifier (str): Specifies part of entity full identifier, e.g., B01.
    - name (str): Indicates the specific name of the physical system, e.g., bus name.

    Class Methods:
    - __init__: Constructor to initialize a new instance of the class.
    - help: Method for printing docstrings of class methods.
    - sensors: Property to get or set the list of sensors connected to the connector.
    - __getitem__: Method to get a sensor from the list by index.
    - addSensors: Method to add one or more sensors to the connector.
    - sensorExist: Method to check the existence of a sensor with a provided ID.
    - getSensor: Method to retrieve a sensor from the attached sensor list.
    - numberConnectedDevice: Method to get the number of connected devices.
    - saveConnectedDevice: Method to save information about connected devices to a CSV file.
    """
    partialIdentifier: str
    name: str

    def __init__(self, psc_partial_id: str, psc_name_id: str):
        """
        Initialize a new instance of the PhysicalSystemConnector class.

        :param psc_partial_id: A string representing part of entity's full identifier.
        :param psc_name_id: A string representing the entity's name.
        """
        self.partialIdentifier = psc_partial_id
        self.name = psc_name_id
        self._sensors = []

    def help(self, method_names=None):
        """
        Print the docstring of specified methods in the parameter list or all methods in this class.

        :param method_names: List of method names to print docstrings for (optional)
        """
        if method_names is None:
            methods = inspect.getmembers(self, predicate=inspect.ismethod)
            for name, method in methods:
                if name != '__init__':  # excluding the constructor
                    print(f"{name}:\n{method.__doc__}\n")
        else:
            for name in method_names:
                if name != "__init__":
                    method = getattr(self, name, None)
                    if method is not None and inspect.ismethod(method):
                        print(f"{name}:\n{method.__doc__}\n")

    @property
    def sensors(self) -> list:
        """
        Return a list of sensors.

        This method retrieves and returns a list of sensors from the instance variable '_sensors'.
        If the list is empty, it raises a ValueError to indicate that no sensors have been added.

        :return: A list containing the sensors.
        :raises ValueError: if no sensors are added to the connector.
        """
        if not self._sensors:
            raise ValueError(f"No sensors added to {self.name} connector")
        return list(self._sensors)

    @sensors.setter
    def sensors(self, sensor) -> None:
        """
        Set the sensors. This method expects a single sensor object.

        :param sensor: Single sensor object to be added.
        :raises TypeError: If the input is not a Sensor object
        """
        if isinstance(sensor, Sensor):
            self._sensors = sensor
        else:
            raise TypeError("Input must be a Sensor object.")

    def __getitem__(self, index):
        """
        Get a sensor from the list by index.

        :param index: Index of the sensor to retrieve.
        :return: The Sensor object at the specified index.
        :raises AssertionError: If the index is not an integer.
        """
        assert isinstance(index, int)
        return self._sensors[index]

    def addSensor(self, *sensors):
        """
        Add one or more Sensor objects to the existing list of sensors.

        :param sensors: Variable length Sensor object arguments.
        :raises TypeError: If any of the arguments is not a Sensor object.
        """

        for sensor in sensors:
            if isinstance(sensor, Sensor):
                self._sensors.append(sensor)
            else:
                raise TypeError("Only Sensor objects can be added.")

    def sensorExist(self, device_partial_id: str) -> bool:
        """
        Check if a sensor with the given device_partial_id exists in the Physical System.

        :param device_partial_id: The sensor ID to check for.
        :return: True if the ID is found in the sensor list, False otherwise.
        """
        return any(sensor.devicePartialID == device_partial_id for sensor in self._sensors)

    def getSensor(self, device_partial_id: str) -> Sensor:
        """
        Retrieve a sensor by its device_partial_id.

        :param device_partial_id: The ID of the sensor to retrieve.
        :return: The Sensor object with the given ID.
        :raises ValueError: If no sensor with the given ID is found.
        """
        for sensor in self._sensors:
            if sensor.devicePartialID == device_partial_id:
                return sensor
        raise ValueError(f"No sensor with ID {device_partial_id} found in {self.name} connector.")

    # TODO: this function must be available for each device type, for now it is working only for sensors, but a proper
    #  PhysicalSystemConnector should have at least sensors and actuators.
    def numberConnectedDevice(self) -> int:
        """
        Get the number of connected devices.

        :return: Number of connected devices
        """
        if isinstance(self._sensors, list):
            return len(self._sensors)
        else:
            return 0  # if sensors is not a list -> no sensors are connected.

    def saveConnectedDevice(self, folder):
        """
        Save information about connected devices to a.csv file in the specified folder.

        :param folder: Path to the folder where the .csv file will be saved.
        """

        os.makedirs(folder, exist_ok=True)
        csv_filename = os.path.join(folder, f"{self.name}.csv")
        field_names = ["pcs_id", "num_connected_devices", "device_id", "device_key"] # num_connected_devices is not so useful in this case, could remove it later
        num_connected_devices = self.numberConnectedDevice()
        # if the file already exists --> check the data
        if os.path.exists(csv_filename):
            # For now this if is deactivated with this return, not sure if will be useful to change file content
            # if the file already exist
            return

            existing_data = pd.read_csv(csv_filename, dtype={0: str})
            existing_data.columns = field_names

            # Create a list of device IDs that are present in the sensors list of the physical system connector
            valid_device_ids = [device.devicePartialID for device in self._sensors]

            # Drop the rows from existing_data where the device IDs are not present in the valid_device_ids list.
            #existing_data = existing_data[existing_data[field_names[2]].isin(valid_device_ids)] REMOVED IN ORDER TO HAVE ONE SERVICE GROUP

            # Check if the num_connected devices is updated
            if (existing_data[field_names[1]] != num_connected_devices).any():
                existing_data[field_names[1]] = num_connected_devices

            # Check device IDs and their keys
            for device in self._sensors:
                found_device = False
                for index, row in existing_data.iterrows():
                    if device.devicePartialID == row[field_names[2]]:
                        found_device = True
                        if isinstance(device.apiKey, str):
                            existing_data.at[index, field_names[3]] = device.apiKey
                        else:
                            # Convert device.api_key to string if necessary
                            existing_data.at[index, field_names[3]] = str(device.apiKey)
                if not found_device:
                    new_row = {field_names[0]: self.name_identifier, field_names[1]: num_connected_devices,
                               field_names[2]: device.devicePartialID, field_names[3]: device.apiKey}
                    existing_data = pd.concat([existing_data, pd.DataFrame([new_row])], ignore_index=True)
            existing_data.to_csv(csv_filename, index=False)
        else:
            data = [{
                field_names[0]: self.name,
                field_names[1]: num_connected_devices,
                field_names[2]: device.devicePartialID,
                field_names[3]: device.apiKey
            } for device in self._sensors]
            df = pd.DataFrame(data, columns=field_names)
            df.to_csv(csv_filename, index=False)
