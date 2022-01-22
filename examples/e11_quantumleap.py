"""
# Example for working with the QuantumLeapClient
"""
# ## Import packages
import logging
import time
import random

from filip.models.ngsi_v2.subscriptions import Message
from filip.models.ngsi_v2.context import ContextEntity
from filip.models.base import FiwareHeader
from filip.clients.ngsi_v2 import ContextBrokerClient, QuantumLeapClient
from filip.utils.cleanup import clear_all
# ## Parameters
#
# To run this example you need a working Fiware v2 setup with a
# context-broker and QuantumLeap. You can here set the addresses:
#
# Host address of Context Broker
CB_URL = "http://localhost:1026"
# Host address of QuantumLeap
QL_URL = "http://localhost:8668"

# You can here also change the used Fiware service
# FIWARE-Service
SERVICE = 'filip'
# FIWARE-Servicepath
SERVICE_PATH = '/example'


# Setting up logging
logging.basicConfig(
    level='INFO',
    format='%(asctime)s %(name)s %(levelname)s: %(message)s')

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    # ## 1 Setup
    #
    # A QuantumLeapClient and a ContextBrokerClient are created to access
    # FIWARE in the space given by the FiwareHeader. For more information see:
    # e1_http_clients.py
    
    fiware_header = FiwareHeader(service=SERVICE, service_path=SERVICE_PATH)

    # clear all existing data
    clear_all(fiware_header=fiware_header, cb_url=CB_URL, ql_url=QL_URL)

    ql_client = QuantumLeapClient(url=QL_URL, fiware_header=fiware_header)
    print("Quantum Leap " + ql_client.get_version()["version"] + " at url " +
          ql_client.base_url)

    cb_client = ContextBrokerClient(url=CB_URL, fiware_header=fiware_header)

    print("Context broker version "
          + cb_client.get_version()["orion"]["version"]
          + " at url " + cb_client.base_url)

    # ## 2 Interact with QL
    #
    # ### 2.1 Create a ContextEntity to work with
    #
    # for more details see: e2_context_basics.py
    hall = {"id": "Hall_1",
            "type": "Room",
            "temperature": {"value": random.randint(0, 100),
                            "type": "Integer"},
            }

    hall_entity = ContextEntity(**hall)
    cb_client.post_entity(hall_entity)
    
    # ### 2.2 Manage subscriptions
    #
    # create a subscription
    # Note: that the IP must be the ones that orion and quantumleap can access,
    # e.g. service name or static IP, localhost will not work here.
    ql_client.post_subscription(entity_id=hall_entity.id,
                                cb_url="http://orion:1026",
                                ql_url="http://quantumleap:8668",
                                throttling=0)

    # Get all subscriptions
    subscription_list = cb_client.get_subscription_list()
    
    # Notify QL manually
    subscription_id = ""
    for sub in subscription_list:
        for entity in sub.subject.entities:
            if entity.id == hall_entity.id:
                try:
                    ql_client.post_notification(
                        notification=Message(
                            data=[hall_entity],
                            subscriptionId=sub.id))
                    subscription_id = sub.id
                except:
                    logger.error("Can not notify QL")

    # Notify QL via Orion
    for i in range(5, 10):
        cb_client.update_attribute_value(entity_id=hall_entity.id,
                                         entity_type=hall_entity.type,
                                         attr_name="temperature",
                                         value=i)

    time.sleep(1)
    # Get historical data as object you may directly convert them to pandas
    # dataframes
    try:
        print(ql_client.get_entity_by_id(hall_entity.id).to_pandas())
        print(ql_client.get_entity_values_by_id(hall_entity.id))
        print(ql_client.get_entity_attr_by_id(hall_entity.id,
                                              "temperature"))
        print(ql_client.get_entity_attr_values_by_id(hall_entity.id,
                                                     attr_name="temperature"))
        print(ql_client.get_entity_attr_by_type(hall_entity.type,
                                                attr_name="temperature"))
        print(ql_client.get_entity_attr_values_by_type(hall_entity.type,
                                                       "temperature"))
    except:
        logger.info("There might be no historical data for some calls.")

    # ## 2.3 Delete
    #
    # delete entity in QL
    try:
        ql_client.delete_entity(entity_id=hall_entity.id,
                                entity_type=hall_entity.type)
    except:
        logger.error("Can not delete data from QL")

    # delete entity in  CV
    try:
        cb_client.delete_entity(entity_id=hall_entity.id,
                                entity_type=hall_entity.type)
    except:
        logger.error("Can not delete entity from context broker")

    # delete subscription
    try:
        cb_client.delete_subscription(subscription_id)
    except:
        logger.error("Can not delete subscription from context broker.")
    
    # # 3 Clean up (Optional)
    #
    # Close clients
    ql_client.close()
    cb_client.close()
