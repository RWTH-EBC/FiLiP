import logging
from datetime import datetime
import time

from filip.cb.models import Subscription
from filip.cb import ContextBrokerClient
from filip.core.models import FiwareHeader

AUTH = ('user', 'pass')

# create new subscription following the API Walkthrough example:
# https://fiware-orion.readthedocs.io/en/master/user/walkthrough_apiv2/index.html
# #subscriptions

logger = logging.getLogger(__name__)


def setup():
    logger.info("------Setting up client------")
    with ContextBrokerClient(fiware_header=FiwareHeader(service='filip',
                                                        service_path='/testing')) as \
            cb_client:
        for key, value in cb_client.get_version().items():
            print("Context broker version" + value["version"] + "at url " +
                  cb_client.base_url)


def create_subscription():
    with ContextBrokerClient(fiware_header=FiwareHeader(service='filip',
                                                        service_path='/testing')) as \
            cb_client:
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
        logger.info("------Posting an example subscription for Room1------")
        returned_sub_id = cb_client.post_subscription(subscription=sub)
    return returned_sub_id


def filter_subscription(sub_id_filter):
    with ContextBrokerClient(fiware_header=FiwareHeader(service='filip',
                                                        service_path='/testing')) as \
            cb_client:
        logger.info("------Get the entered subscription------")
        retrieve_sub = cb_client.get_subscription(sub_id_filter)
        logger.info(retrieve_sub)


def update_subscription(sub_id_to_update):
    with ContextBrokerClient(fiware_header=FiwareHeader(service='filip',
                                                        service_path='/testing')) as \
            cb_client:
        sub_to_update = cb_client.get_subscription(sub_id_to_update)
        sub_to_update = sub_to_update.copy(update={'expires': datetime.now()})
        logger.info("------Updated expiration time of the example subscription------")
        cb_client.update_subscription(sub_to_update)
        updated_subscription = cb_client.get_subscription(sub_id_to_update)
        logger.info(updated_subscription)


def delete_subscription(sub_id_to_delete):
    with ContextBrokerClient(fiware_header=FiwareHeader(service='filip',
                                                        service_path='/testing')) as \
            cb_client:
        logger.info("------Deleting the example subscription------")
        cb_client.delete_subscription(sub_id_to_delete)


if __name__ == "__main__":
    logger.info("------EXAMPLE SUBSCRIPTION------")
    sub_id = create_subscription()
    filter_subscription(sub_id)
    time.sleep(1)
    update_subscription(sub_id)
    delete_subscription(sub_id)
