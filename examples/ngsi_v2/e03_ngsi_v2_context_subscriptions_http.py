"""
# Examples for subscriptions

# create new subscriptions following the API Walkthrough example:
# https://fiware-orion.readthedocs.io/en/master/user/walkthrough_apiv2.html#subscriptions
"""
# ## Import packages
import logging
import datetime
import time
from filip.config import settings
from filip.models.ngsi_v2.subscriptions import Subscription
from filip.clients.ngsi_v2.cb import ContextBrokerClient
from filip.models.base import FiwareHeader

# ## Parameters
#
# To run this example you need a working Fiware v2 setup with a context-broker
# You can set the address:
#
# Host address of Context Broker
CB_URL = settings.CB_URL

# You can also change the used Fiware service
# FIWARE-Service
SERVICE = 'filip'
# FIWARE-Servicepath
SERVICE_PATH = '/example'

# Web server URL for receiving notifications
SERVER_URL = "http://<my_url>/notify/"
# Replace <my_url> with the URL of the web server, where you'd like to receive notifications
# e.g. "http://host.docker.internal:8080/notify/", or if you're not sure how to set up the 
# server, create a dummy version via 
# https://fiware-orion.rtfd.io/en/master/user/walkthrough_apiv2.html#starting-accumulator-server

# Setting up logging
logging.basicConfig(
    level='INFO',
    format='%(asctime)s %(name)s %(levelname)s: %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S')
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    # # 1 Client setup
    #
    # Create the context broker client, for more details view the example: e01_http_clients.py
    fiware_header = FiwareHeader(service=SERVICE,
                                 service_path=SERVICE_PATH)
    cb_client = ContextBrokerClient(url=CB_URL,
                                    fiware_header=fiware_header)
    entities = cb_client.get_entity_list()
    logger.info(entities)

    # # 2 Subscription setup
    #
    # The system is notified every time the "temperature" attribute of the entity (subject)
    # with the id "urn:ngsi-ld:Room:001" changes. The payload of the notification includes
    # only "temperature" attribute. Payload is completely modifiable.
    # The subscription expires after 15 minutes.
    interesting_entity_id = "urn:ngsi-ld:Room:001"
    sub_example = {
        "description": "Subscription to receive HTTP-Notifications about "
                       + interesting_entity_id,
        "subject": {
            "entities": [
                {
                    "id": "urn:ngsi-ld:Room:001",
                    "type": "Room"
                }
            ],
            "condition": {
                "attrs": [
                    "temperature"
                ]
            }
        },
        "notification": {
            "http": {
                "url": SERVER_URL + interesting_entity_id
            },
            "attrs": [
                "temperature"
            ]
        },
        "expires": datetime.datetime.now() + datetime.timedelta(minutes=15),
        "throttling": 0
    }
    sub = Subscription(**sub_example)
    # Posting an example subscription for Room1
    sub_id = cb_client.post_subscription(subscription=sub)

    # # 3 Filter subscriptions
    retrieve_sub = cb_client.get_subscription(sub_id)
    logger.info(retrieve_sub)

    time.sleep(1)

    # # 4 Update subscription
    #
    sub_to_update = cb_client.get_subscription(sub_id)
    # Update expiration time of the example subscription
    sub_to_update = sub_to_update.model_copy(
        update={'expires': datetime.datetime.now() +
                           datetime.timedelta(minutes=15)})
    cb_client.update_subscription(sub_to_update)
    updated_subscription = cb_client.get_subscription(sub_id)
    logger.info(updated_subscription)

    # # 5 Deleting the example subscription
    #
    cb_client.delete_subscription(sub_id)

    # # 6 Clean up (Optional)
    #
    # Close client
    cb_client.close()
