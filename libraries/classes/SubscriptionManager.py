from ngsildclient import Client, SubscriptionBuilder
import typing
from libraries.constants import roadSegmentType, trafficFlowObservedType


class QuantumLeapManager:
    """
    A class to manage NGSI-LD subscriptions for monitoring and interacting with the context broker.

    Attributes:
        containerName (str): The name of the container running the context broker.
        cbPort (int): The port number for the context broker.
        quantumleapPort (int): The port number for QuantumLeap.
        activeSubscriptions (Dict[str, List[Any]]): A dictionary to store active subscriptions.
    """
    containerName: str
    cbPort: int
    quantumleapPort: int
    activeSubscriptions: typing.Dict[str, typing.List[typing.Any]]

    def __init__(self, containerName: str, cbPort: int, quantumleapPort: int):
        """
        Initializes the SubscriptionManager with container name, context broker port, and QuantumLeap port.

        :param containername: The name of the container where context broker is running.
        :param cbPort: The port number for the context broker.
        :param quantumleapPort: The port number for QuantumLeap.
        """
        self.containerName = containerName
        self.cbPort = cbPort
        self.quantumleapPort = quantumleapPort
        self.activeSubscriptions = {}

    def createQuantumLeapSubscription(self, cbConnection: Client, entityType: str, attribute: str, description: str):
        """
        Creates a subscription in the context broker for a specific entity type and attribute.

        :param cbConnection: An instance of the NGSI-LD Client for interacting with the context broker.
        :param entityType: The entity type to subscribe to.
        :param attribute: The attribute of the entity to watch for changes.
        :param description: A description for the subscription.
        :raises ValueError: If the subscription creation fails.
        """
        subscriptionPayload = dict()
        try:
            notificationurl = f"http://{self.containerName}:{self.quantumleapPort}/v2/notify"

            if entityType.lower() in ["road segment", "roadsegment"]:
                entityType = roadSegmentType
            elif entityType.lower() in ["trafficflowobserved", "traffic flow observed"]:
                entityType = trafficFlowObservedType
            elif entityType.lower() == "device":
                entityType = "Device"

            subscriptionPayload = (
                SubscriptionBuilder(notificationurl)
                .description(description)
                .select_type(entityType)
                .watch([attribute])
                .build()
            )
            newSubscription = cbConnection.subscriptions.create(subscriptionPayload)
            self.activeSubscriptions[entityType] = self.activeSubscriptions.get(entityType, []) + [newSubscription]
            print(f"Subscription created: {subscriptionPayload}")

        except Exception as e:
            raise ValueError(f"Failed to create subscription for {entityType}: {e}")
