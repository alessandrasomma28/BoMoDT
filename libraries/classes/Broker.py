# ****************************************************
# Broker Module for Context Management:
#   This module provides functionality to interact with a FIWARE Context Broker for traffic entities management. It handles
#   updating context entities based on Road, RoadSegment, and TrafficFlowObservation smart data models. The entities' state
#   is update when data are received from IoT devices. Exceptions are raised and handled to indicate specific errors during entity creation, update,
# or retrieval processes.
#   Classes:
#       - Broker: Handles context updates, entity creation, and relations management.
#       - ContextUpdateError: Custom base exception for context update errors.
#       - RoadEntityError, RoadSegmentEntityError, TrafficFlowObservedError: Specific exceptions for errors related
#           to road, road segment, and traffic flow observed entities.
# ****************************************************


from ngsildclient import Client, Entity, Rel
from typing import Optional, List, Tuple
from libraries.classes.DigitalShadowManager import DigitalShadowManager
from libraries.constants import transportationCTX, roadSegmentType, roadType
from libraries.utils.generalUtils import convertDate


class ContextUpdateError(Exception):
    """
    Base class for all context update errors.
    """
    def __init__(self, message: str, entityType: List[str], additionalInfo: str = ""):
        super().__init__(message)
        self.entityType = entityType
        self.additionalInfo = additionalInfo

    def __str__(self):
        types = ', '.join(self.entityType)
        return f"Error updating entities ({types}): {self.args[0]}. {self.additionalInfo}"


class RoadEntityError(ContextUpdateError):
    """
    Raise when there is an issue with the Road entity.
    """
    def __init__(self, message: str, coordinates: List[float], laneDirection: str):
        super().__init__(message, ["Road"], f"Coordinates: {coordinates}, Lane Direction: {laneDirection}")


class RoadSegmentEntityError(ContextUpdateError):
    """
    Raise when there is an issue with the RoadSegment entity.
    """
    def __init__(self, message: str, entityID: str):
        super().__init__(message, ["RoadSegment"], f"Entity ID: {entityID}")


class TrafficFlowObservedError(ContextUpdateError):
    """
    Raise when there is an issue with the TrafficFlowObserved entity.
    """
    def __init__(self, message: str, supposedID: str):
        super().__init__(message, ["TrafficFlowObserved"], f"Supposed ID: {supposedID}")

class Broker:
    """
    Class to manage the creation and update of context entities in the Context Broker.

    Class Attributes:
    - portNumber (int): Port number for the Context Broker connection.
    - portTemporal (Optional[int]): Optional port for Context Broker connection if temporal operations are enabled.
    - hostname (str): Hostname of the Context Broker.
    - fiwareService (str): FIWARE service name (tenant) for managing context entities.
    - entitiesList (List[Tuple[str, int]]): List of entity types and their progressive numbers.
    - shadowManagerReference (DigitalShadowManager):

    Class Methods:
    -


    """
    portNumber: int
    portTemporal: Optional[int]
    fiwareService: str
    hostname: str
    entitiesList: List[Tuple[str, int]]
    shadowManagerReference: Optional['DigitalShadowManager']

    def __init__(self, pn: int, pnt: Optional[int], host: str, fiwareservice: str):
        """
        Initializes the Broker class with connection details.

        Args:
        :param pn: Port number for the Context Broker.
        :param pnt: Temporal port number for the Context Broker.
        :param host: Hostname of the Context Broker.
        :param fiwareservice: FIWARE service/tenant name.
        """
        self.portNumber = pn
        self.portTemporal = pnt
        self.hostname = host
        self.fiwareService = fiwareservice
        self.entitiesList = []
        self.shadowManagerReference = None

    def createConnection(self) -> Client:
        """
        Establish a connection to the Context Broker.

        :returns Client: A client object to interact with the Context Broker.
        :raises ConnectionError: If the connection to the Context Broker fails.
        """
        try:
            if self.portTemporal is None:
                cb = Client(hostname=self.hostname, port=self.portNumber, tenant=self.fiwareService, overwrite=True)
            else:
                cb = Client(hostname=self.hostname, port=self.portNumber, port_temporal=self.portTemporal,
                            tenant=self.fiwareService, overwrite=True)
            return cb
        except Exception as e:
            raise ConnectionError(f"Impossible to connect: {str(e)}")

        # Method to add a new entity type and its progressive number to the list

    def addEntitiesList(self, entityType: str, progressiveNumber: int):
        """
        Add or update an entity type and its progressive number in the entity list.

        :param entityType: The type of entity (e.g., "Road", "RoadSegment").
        :param progressiveNumber: The progressive number for the entity.

        """
        entityFound = False
        for i, (etype, pnum) in enumerate(self.entitiesList):
            if etype == entityType:
                self.entitiesList[i] = (entityType, progressiveNumber)
                entityFound = True
                break
        if not entityFound:
            self.entitiesList.append((entityType, progressiveNumber))


    def getEntitiesList(self) -> List[Tuple[str, int]]:
        """
        Retrieve the list of entities and their progressive numbers.

        :returns: List[Tuple]: List of tuples with entity type and progressive number.
        """
        return self.entitiesList

    def displayEntities(self):
        """
        Display all entities and their progressive numbers. If no entities exist, inform the user.

        """
        if not self.entitiesList:
            print("No entities available.")
        for entity in self.entitiesList:
            print(f"Entity Type: {entity[0]}, Progressive Number: {entity[1]}")

    def getProgressiveNumber(self, entityType: str) -> int:
        """
        Retrieve the progressive number for a given entity type.

        :param: entityType: The type of entity (e.g., "Road", "RoadSegment").
        :returns Optional[int]: The progressive number if found, otherwise 0.
        """
        for etype, pnum in self.entitiesList:
            if etype == entityType:
                return pnum  # Return the progressive number if the entity type is found
        return 0  # Return 0

    def updateProgressiveNumber(self, entityType: str, newNumber: int):
        """
        Update the progressive number for a given entity type.

        :param entityType: The type of entity (e.g., "Road", "RoadSegment").
        :param newNumber: The new progressive number to set.
        :raises ValueError: If the entity type does not exist in the list.
        """
        entityFound = False
        for i, (etype, pnum) in enumerate(self.entitiesList):
            if etype == entityType:
                self.entitiesList[i] = (entityType, newNumber)
                entityFound = True
                break
        if not entityFound:
            self.entitiesList.append((entityType, newNumber))

    def updateContext(self, deviceID:str, date: str, timeSlot: str, trafficFlow: int, coordinates: List[float], laneDirection: str,
                      cbConnection: Optional[Client]) -> bool:
        """
        Update the existing Context entities based on data received from physical devices through the IoT Agent.

        :param deviceID: Identifier for the physical device.
        :param date: Date of the traffic flow observation.
        :param timeSlot: Time slot of the traffic flow observation.
        :param trafficFlow: Traffic flow measured.
        :param coordinates: GPS coordinates (longitude, latitude) of the traffic loop installed on the road segment.
        :param laneDirection: Direction of the road segment lane.
        :param cbConnection: Optional Client object of an already existing Context Broker connection.


        :returns bool: True if the update was successful, False otherwise.
        :raise RoadEntityError: When there is an issue with creating/updating a Road entity.
        :raise RoadSegmentEntityError: When there is an issue with creating/updating a Road Segment entity.
        :raise TrafficFlowObservedError: When there is an issue with creating/updating a Traffic Flow Observed entity.

        """
        try:
            if self.shadowManagerReference is None:
                self.shadowManagerReference = DigitalShadowManager()
            roadShadow = self.shadowManagerReference.searchShadow(shadowType="road", timeSlot=timeSlot, trafficFlow=trafficFlow,
                                                          coordinates=coordinates, laneDirection=laneDirection, deviceID=deviceID)
            if not roadShadow:
                raise RoadEntityError(f"No Road Shadow found for coordinates {coordinates} and direction {laneDirection}", coordinates=coordinates, laneDirection=laneDirection)
            roadName = roadShadow.name
            edgeID = roadShadow.get('edgeID')
            startPoint = roadShadow.get('startPoint')
            endPoint = roadShadow.get('endPoint')
            completeDate = convertDate(date=date, timeslot=timeSlot)
            deviceURN = "urn:ngsi-ld:Device:{}".format(deviceID)

            if cbConnection is None:
                cbConnection=self.createConnection()
            entityRoad = self.searchEntity(cbConnection=cbConnection, dataSearch=roadName, eType="Road")
            if entityRoad is not None:
                entityRoadSegment = self.searchEntity(cbConnection=cbConnection, dataSearch=edgeID, eType="RoadSegment")
                if entityRoadSegment is not None:
                    if self.updateFlow(cbConnection=cbConnection, newFlow=trafficFlow, date=completeDate,
                                       cEntity=entityRoadSegment, eType="RoadSegment", timeslot=timeSlot):
                        trafficFlowObsID = entityRoadSegment['refTrafficFlowObs'].value
                        trafficFlowObs = cbConnection.get(trafficFlowObsID)
                        if trafficFlowObs is not None:
                            if self.updateFlow(cbConnection=cbConnection, newFlow=trafficFlow,
                                                   date=completeDate, cEntity=trafficFlowObs,
                                                   eType="TrafficFlowObserved", timeslot=timeSlot):
                                return True
                            else:
                                raise TrafficFlowObservedError(f"Unable to update flow of Traffic Flow Observed entity for the retrieved ID: {trafficFlowObsID}",
                                    supposedID=trafficFlowObsID)
                        else:
                            raise TrafficFlowObservedError(f"Traffic Flow Observed entity not found for the retrieved ID: {trafficFlowObsID}",
                                                           supposedID=trafficFlowObsID)
                    else:
                        raise RoadSegmentEntityError("Unable to update Traffic Flow attribute in RoadSegment entity with ID:", entityID=entityRoadSegment.id)
                else:
                    rsNumber=self.getProgressiveNumber("RoadSegment") + 1
                    tfoNumber=self.getProgressiveNumber("TrafficFlowObserved") + 1
                    entityRoadSegment=self.createRoadSegmentEntity(progressiveNumber=rsNumber,startPoint=startPoint, endPoint=endPoint,coordinates=coordinates,
                                                                   direction=laneDirection, edgeID=edgeID, trafficFlow=trafficFlow,
                                                                   date=completeDate,trafficLoopID=deviceURN, timeslot=timeSlot)
                    entityTrafficFlowObs=self.createTrafficFlowObsEntity(progressiveNumber=tfoNumber, direction=laneDirection,
                                                                         date=completeDate, trafficFlow=trafficFlow,
                                                                         trafficLoopID=deviceURN, roadSegmentID=entityRoadSegment.id, timeslot=timeSlot)
                    entityRoadSegment=self.updateRoadSegmentRelation(rsEntity=entityRoadSegment, roadID=entityRoad.id,
                                                   traffiFlowObsID=entityTrafficFlowObs.id)
                    entityRoad=self.updateRoadRelation(rEntity=entityRoad, roadSegmentID=entityRoadSegment.id)
                    created = cbConnection.create([entityRoadSegment, entityTrafficFlowObs])
                    updated = cbConnection.update(entityRoad)

                    if created and updated:
                        self.updateProgressiveNumber("RoadSegment", rsNumber)
                        self.updateProgressiveNumber("TrafficFlowObserved", tfoNumber)
                        print(self.getProgressiveNumber("RoadSegment"))
                        return True
                    else:
                        raise ContextUpdateError("Failed to create or update context entities.",
                                                 entityType=["RoadSegment", "TrafficFlowObserved"])
            else:
                rNumber = self.getProgressiveNumber("Road") + 1
                rsNumber = self.getProgressiveNumber("RoadSegment") + 1
                tfoNumber = self.getProgressiveNumber("TrafficFlowObserved") + 1
                entityRoad=self.createRoadEntity(progressiveNumber=rNumber, roadName=roadName)
                entityRoadSegment = self.createRoadSegmentEntity(progressiveNumber=rsNumber, startPoint=startPoint,
                                                                 endPoint=endPoint, coordinates=coordinates,
                                                                 direction=laneDirection, edgeID=edgeID,
                                                                 trafficFlow=trafficFlow,
                                                                 date=completeDate, trafficLoopID=deviceURN, timeslot=timeSlot)
                entityTrafficFlowObs = self.createTrafficFlowObsEntity(progressiveNumber=tfoNumber,
                                                                       direction=laneDirection,
                                                                       date=completeDate, trafficFlow=trafficFlow,
                                                                       trafficLoopID=deviceURN,
                                                                       roadSegmentID=entityRoadSegment.id, timeslot=timeSlot)
                entityRoadSegment = self.updateRoadSegmentRelation(rsEntity=entityRoadSegment, roadID=entityRoad.id,
                                                                   traffiFlowObsID=entityTrafficFlowObs.id)
                entityRoad = self.updateRoadRelation(rEntity=entityRoad, roadSegmentID=entityRoadSegment.id)
                cbConnection.create([entityRoad, entityRoadSegment, entityTrafficFlowObs])
                self.updateProgressiveNumber("Road", rNumber)
                self.updateProgressiveNumber("RoadSegment", rsNumber)
                # print(self.getProgressiveNumber("RoadSegment"))
                self.updateProgressiveNumber("TrafficFlowObserved", tfoNumber)
                return True
        except Exception as e:
            print(f"Error during context update: {str(e)}")
            return False

    def createRoadSegmentEntity(self, progressiveNumber: int, startPoint: int, endPoint: int, coordinates: List[float], direction: str,
                                edgeID: str, trafficFlow: int, date: str, trafficLoopID: str, timeslot: str) -> Entity:

        roadSegmentID = 'RS{:03d}'.format(progressiveNumber)
        roadSegment = Entity("RoadSegment", roadSegmentID, ctx=transportationCTX)
        roadSegment.prop('startPoint', int(startPoint))
        roadSegment.prop('endPoint', int(endPoint))
        if len(coordinates) == 2:
            #longitude = int(coordinates[0]) - latitude = int(coordinates[1])
            longitude = coordinates[0]
            latitude = coordinates[1]
            roadSegment.gprop('location', (longitude,latitude))
        else:
            raise ValueError("Coordinates must contain exactly two values: latitude and longitude.")

        roadSegment.prop('direction', direction)
        roadSegment.prop('edgeID', edgeID)
        roadSegment.prop('trafficFlow', trafficFlow).rel(Rel.OBSERVED_BY, trafficLoopID, nested=True)
        roadSegment.tprop('DateTime', date)
        roadSegment.prop('timeslot', timeslot)
        return roadSegment

    def updateRoadSegmentRelation(self, rsEntity: Entity, roadID: str, traffiFlowObsID: str) -> Entity:
        rsEntity.prop('refTrafficFlowObs', traffiFlowObsID)
        rsEntity.rel(Rel.IS_CONTAINED_IN, roadID)
        return rsEntity

    def createTrafficFlowObsEntity(self, progressiveNumber: int, direction: str, trafficFlow: int, date: str,
                                   trafficLoopID: str, roadSegmentID: str, timeslot: str) -> Entity:
        trafficFlowID = 'TFO{:03d}'.format(progressiveNumber)
        trafficFlowObs = Entity("TrafficFlowObserved", trafficFlowID, ctx=transportationCTX)
        trafficFlowObs.prop('laneDirection', direction)
        trafficFlowObs.rel('refRoadSegment', roadSegmentID)
        trafficFlowObs.prop('trafficFlow', trafficFlow).rel(Rel.OBSERVED_BY, roadSegmentID, nested=True)
        trafficFlowObs.tprop('DateTime', date)
        trafficFlowObs.prop('timeslot', timeslot)
        return trafficFlowObs


    def createRoadEntity(self,progressiveNumber: int, roadName: str) -> Entity:
        roadID = 'R{:03d}'.format(progressiveNumber)
        road = Entity("Road", roadID, ctx=transportationCTX)
        road.prop('BolognaRoadName', roadName)
        return road

    def updateRoadRelation(self, rEntity: Entity, roadSegmentID: str) -> Entity:
        rEntity.rel(Rel.HAS_PART, roadSegmentID)
        return rEntity

    def searchEntity(self, cbConnection: Client, dataSearch: str, eType: str) -> Entity:
        # dataSearch = {roadName: str, edgeID: str}
        if eType == "RoadSegment":
            generator = cbConnection.query_generator(type=roadSegmentType)
            e: Entity | None = next((e for e in generator if e["edgeID"].value == dataSearch), None)
            return e
        elif eType == "Road":
            generator = cbConnection.query_generator(type=roadType)
            e: Entity | None = next((e for e in generator if e["BolognaRoadName"].value == dataSearch), None)
            return e

    def updateFlow(self, cbConnection: Client, newFlow: int, date: str, cEntity: Entity, eType: str, timeslot: str) -> bool:
        if eType == "RoadSegment":
            cEntity["trafficFlow"].value = newFlow
            cEntity.tprop("DateTime",date)
            cEntity.prop('timeslot', timeslot)
            response = cbConnection.update(cEntity, overwrite=True)
            return response
        elif eType=="TrafficFlowObserved":
            cEntity["trafficFlow"].value = newFlow
            cEntity.tprop('DateTime',date)
            cEntity.prop('timeslot', timeslot)
            response = cbConnection.update(cEntity, overwrite=True)
            return response
        else:
            return False


