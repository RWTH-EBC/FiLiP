"""
# Example for working with the QuantumLeapClient
"""

# ## Import packages
import logging
import time
import datetime
import random
from filip.config import settings
from filip.models.ngsi_ld.subscriptions import SubscriptionLD
from filip.models.ngsi_ld.context import ContextLDEntity, ContextProperty, MessageLD
from filip.models.base import FiwareLDHeader
from filip.clients.ngsi_v2 import QuantumLeapClient
from filip.clients.ngsi_ld.cb import ContextBrokerLDClient
from filip.utils.cleanup import clear_quantumleap, clear_context_broker_ld

# ## Parameters
#
# To run this example you need a working Fiware v2 setup with a
# Context Broker and QuantumLeap. Here you can set the addresses:
#
# Host address of Context Broker
LD_CB_URL = settings.LD_CB_URL
# Host address of QuantumLeap
QL_URL = settings.QL_URL

# Here you can also change FIWARE service and service path.
# NGSI-LD Tenant
NGSILD_TENANT = "filip"

# Setting up logging
logging.basicConfig(
    level="INFO",
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # ## 1 Setup
    #
    # QuantumLeapClient and ContextBrokerClient are created to access
    # FIWARE in the space given by the FiwareHeader.
    #
    # For more information see: e01_http_clients.py

    fiware_header = FiwareLDHeader()

    ql_client = QuantumLeapClient(url=QL_URL, fiware_header=fiware_header)
    clear_quantumleap(ql_client=ql_client)
    print(
        f"Quantum Leap Client version: {ql_client.get_version()['version']}"
        f" located at url: {ql_client.base_url}"
    )

    cb_ld_client = ContextBrokerLDClient(url=LD_CB_URL, fiware_header=fiware_header)
    clear_context_broker_ld(cb_ld_client=cb_ld_client)

    print(
        f"Context Broker version: {cb_ld_client.get_version()}"
        f" located at url: {cb_ld_client.base_url}"
    )

    # ## 2 Interact with QL
    #
    # ### 2.1 Create a ContextEntity to work with
    #
    # For more information see: e01_ngsi_v2_context_basics.py
    hall = {
        "id": "urn:ngsi-ld:Hall1",
        "type": "Room",
        "temperature": {"value": random.randint(0, 100), "type": "Property"},
    }

    hall_entity = ContextLDEntity(**hall)
    cb_ld_client.post_entity(hall_entity)

    # ### 2.2 Manage subscriptions
    #
    # Create a subscription
    # Note: The IPs must be the ones that Orion and quantumleap can access,
    # e.g. service name or static IP, localhost will not work here.

    subscription: SubscriptionLD = SubscriptionLD.model_validate(
        {
            "description": "Subscription to receive HTTP-Notifications about "
            + hall_entity.id,
            "entities": [{"type": "Room"}],
            "watchedAttributes": ["temperature"],
            "q": "temperature<101",
            "notification": {
                "attributes": [],
                "format": "normalized",
                "endpoint": {
                    "uri": "http://localhost:8668/v2/notify",
                    "Accept": "application/json",
                },
            },
            "expires": datetime.datetime.now() + datetime.timedelta(minutes=15),
            "throttling": 0,
            "id": "urg:ngsi-ld:Sub:001",
            "type": "Subscription",
        }
    )
    subscription_id = cb_ld_client.post_subscription(subscription=subscription)

    # get all subscriptions
    subscription_list = cb_ld_client.get_subscription_list()

    # notify QL manually
    for sub in subscription_list:
        print(sub.model_dump())
        for entity in sub.entities:
            if entity.type == hall_entity.type:
                try:
                    ql_client.post_notification(
                        notification=MessageLD(
                            data=[hall_entity], subscriptionId=sub.id
                        )
                    )
                    subscription_id = sub.id
                except Exception as e:
                    print(e)

    # notify QL via Orion
    for i in range(5, 10):
        cb_ld_client.update_entity_attribute(
            entity_id=hall_entity.id,
            attr=ContextProperty(value=i),
            attr_name="temperature",
        )

    time.sleep(1)
    # get historical data as object and you can directly convert them to pandas dataframes
    try:
        print(
            f"get_entity_by_id method converted to pandas:\n"
            f"{ql_client.get_entity_by_id(hall_entity.id).to_pandas()}\n"
        )

        print(
            f"get_entity_values_by_id method:\n"
            f"{ql_client.get_entity_values_by_id(hall_entity.id)}\n"
        )

        print(
            f"get_entity_attr_by_id method:\n"
            f"{ql_client.get_entity_attr_by_id(hall_entity.id, 'temperature')}\n"
        )

        print(
            f"get_entity_attr_values_by_id method:\n"
            f"{ql_client.get_entity_attr_values_by_id(hall_entity.id, attr_name='temperature')}\n"
        )

        print(
            f"get_entity_attr_by_type method:\n"
            f"{ql_client.get_entity_attr_by_type(hall_entity.type, attr_name='temperature')}\n"
        )

        print(
            f"get_entity_attr_values_by_type method:\n"
            f"{ql_client.get_entity_attr_values_by_type(hall_entity.type, 'temperature')}"
        )
    except:
        logger.info("There might be no historical data for some calls.")

    # ## 2.3 Delete
    #
    # Delete entity in QL
    try:
        ql_client.delete_entity(entity_id=hall_entity.id, entity_type=hall_entity.type)
    except:
        logger.error("Can not delete data from QL")

    # delete entity in CV
    try:
        cb_ld_client.delete_entity(
            entity_id=hall_entity.id, entity_type=hall_entity.type
        )
    except:
        logger.error("Can not delete entity from context broker")

    # delete the subscription
    try:
        cb_ld_client.delete_subscription(subscription_id)
    except:
        logger.error("Can not delete subscription from context broker.")

    # # 3 Clean up (Optional)
    #
    # Close clients
    ql_client.close()
    cb_ld_client.close()
