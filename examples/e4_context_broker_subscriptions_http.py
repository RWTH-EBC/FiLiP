"""
# Examples for subscriptions

# create new subscription following the API Walkthrough example:
# https://fiware-orion.readthedocs.io/en/master/user/walkthrough_apiv2/index.html
"""
# ## Import packages
import logging
import datetime
import time

from filip.models.ngsi_v2.subscriptions import Subscription
from filip.clients.ngsi_v2.cb import ContextBrokerClient
from filip.models.base import FiwareHeader

# ## Parameters
#
# To run this example you need a working Fiware v2 setup with a context-broker
# You can here set the address:
#
# Host address of Context Broker
CB_URL = "http://localhost:1026"

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
    # # 1 Setup Client
    #
    # create the client, for more details view the example: e1_http_clients.py
    fiware_header = FiwareHeader(service=SERVICE,
                                 service_path=SERVICE_PATH)
    cb_client = ContextBrokerClient(url=CB_URL,
                                    fiware_header=fiware_header)
    ents = cb_client.get_entity_list()
    logger.info(ents)

    # # 2 Setup a subscription
    #
    sub_example = {
        "description": "Subscription to receive HTTP-Notifications about "
                       "urn:ngsi-ld:Room:001",
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
                "url": "http://<my_url>/notify"
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
    sub_to_update = sub_to_update.copy(
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
