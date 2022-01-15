"""
# Examples for subscriptions

# create new subscription following the API Walkthrough example:
# https://fiware-orion.readthedocs.io/en/master/user/walkthrough_apiv2/index.html
"""

import logging
from datetime import datetime
import time

from filip.models.ngsi_v2.subscriptions import Subscription
from filip.clients.ngsi_v2.cb import ContextBrokerClient
from filip.models.base import FiwareHeader

AUTH = ('user', 'pass')

"""
To run this example you need a working Fiware v2 setup with a context-broker 
and an iota-broker. You can here set the addresses:
"""
cb_url = "http://localhost:1026"
iota_url = "http://localhost:4041"

"""
You can here also change the used Fiware service
"""
service = 'filip'
service_path = '/example_iot'


# Setting up logging
logging.basicConfig(
    level='INFO',
    format='%(asctime)s %(name)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


if __name__ == "__main__":

    # # 1 Setting up a client
    #
    cb_client = ContextBrokerClient(
        url=cb_url,
        fiware_header=FiwareHeader(service=service, service_path=service_path))

    # # 2 Setup a subscription
    #
    sub_example = {
        "description": "A subscription to get info about Room1",
        "subject": {
            "entities": [
                {
                    "id": "Room1",
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
                "url": "http://localhost:1028/accumulate"
            },
            "attrs": [
                "temperature"
            ]
        },
        "expires": datetime.now(),
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
    sub_to_update = sub_to_update.copy(update={'expires': datetime.now()})
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