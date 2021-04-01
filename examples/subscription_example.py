import logging
from datetime import datetime
import time

from cb.models import Subscription
from cb import ContextBrokerClient
from core.models import FiwareHeader

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


#
# def Step_By_Step_reducing_scope_with_expression():
#     description = "Notify me of low stock in Store 001"
#     subject_entity = sub.Subject_Entity(".*", "InventoryItem")
#     subject_expression = sub.Subject_Expression()
#     subject_expression.q = "shelfCount<10;refStore==urn:ngsi-ld:Store:002"
#     subject_condition = sub.Subject_Condition(["shelfCount"], subject_expression)
#     subject = sub.Subject([subject_entity], subject_condition)
#     expression = sub.Subject_Expression()
#     http_params = sub.HTTP_Params(
#     "http://tutorial:3000/subscription/low-stock-store002")
#     notification = sub.Notification(http_params)
#     notification.attrsFormat = "keyValues"
#
#     subscription = sub.Subscription(subject, notification, description)
#     return subscription.get_json()
#
# def http_custom_subscription():
#     description = "A subscription to get info about Room3"
#
#     subject_entity = sub.Subject_Entity("Room3", "Room")
#     subject_condition = sub.Subject_Condition(["temperature", "pressure"])
#     subject = sub.Subject([subject_entity], subject_condition)
#
#     http_params = sub.HTTP_Params("http://localhost:1028/accumulate")
#     http_params.headers =  {"Content-Type": "text/plain", "X-Auth-Token":
#     "n5u43SunZCGX0AbnD9e8R537eDslLM"}
#     http_params.method = "PUT"
#     http_params.qs = {"type": "${type}", "id": "${id}"}
#     http_params.payload = "The temperature is ${temperature} degrees"
#     notification = sub.Notification(http_params)
#
#     subscription = sub.Subscription(subject, notification, description)
#     return subscription.get_json()
#
# def check_duplicate_subscription():
#
#     description = "A second subscription for Room3"
#     subject_entity = sub.Subject_Entity("Room3", "Room")
#     subject_condition = sub.Subject_Condition(["pressure"])
#     subject = sub.Subject([subject_entity], subject_condition)
#
#     http_params = sub.HTTP_Params("http://localhost:1028/accumulate")
#     http_params.headers =  {"Content-Type": "text/plain", "X-Auth-Token":
#     "n5u43SunZCGX0AbnD9e8R537eDslLM"}
#     http_params.method = "PUT"
#     http_params.qs = {"type": "${type}", "id": "${id}"}
#     http_params.payload = "The temperature is ${temperature} degrees"
#     notification = sub.Notification(http_params)
#
#     subscription = sub.Subscription(subject, notification, description)
#     return subscription.get_json()
#
#
# def check_existing_type_subscription():
#     """
#     Function checks whether a subscription allready exists.
#     :return:
#     """
#     description = "Notify me of low stock in Store 001"
#     subject_entity = sub.Subject_Entity(".*", "")
#     subject_expression = sub.Subject_Expression()
#     subject_expression.q = "shelfCount<10;refStore==urn:ngsi-ld:Store:002"
#     subject_condition = sub.Subject_Condition(["shelfCount"], subject_expression)
#     subject = sub.Subject([subject_entity], subject_condition)
#     expression = sub.Subject_Expression()
#     http_params = sub.HTTP_Params(
#     "http://tutorial:3000/subscription/low-stock-store002")
#     notification = sub.Notification(http_params)
#     notification.attrsFormat = "keyValues"
#
#     subscription = sub.Subscription(subject, notification, description)
#     return subscription.get_json()
#
#
# def check_existing_id_pattern_subscription():
#     """
#     Function checks whether a subscription already exists for an id type.
#     :return:
#     """
#     description = "A subscription to get info about Room1"
#
#     subject_entity = sub.Subject_Entity("Roo*", "Room")
#     subject_condition = sub.Subject_Condition(["pressure"])
#     subject = sub.Subject([subject_entity], subject_condition)
#
#     http_params = sub.HTTP_Params("http://localhost:1028/accumulate")
#     notification_attributes = sub.Notification_Attributes("attrs", ["temperature"])
#     notification = sub.Notification(http_params, notification_attributes)
#
#     expires = datetime.datetime(2040, 1, 1, 14).isoformat()
#     print (expires)
#     throttling = 5
#
#     subscription = sub.Subscription(subject, notification, description, expires,
#     throttling)
#     return subscription.get_json()


if __name__ == "__main__":
    logger.info("------EXAMPLE SUBSCRIPTION------")
    sub_id = create_subscription()
    filter_subscription(sub_id)
    time.sleep(1)
    update_subscription(sub_id)
    delete_subscription(sub_id)
    #
    # print("---------------------")
    # body = Step_By_Step_reducing_scope_with_expression()
    # print(body)
    # sub_id2 = ORION_CB.create_subscription(body)
    # print("subscription id = " + str(sub_id2))
    #
    # print("---------------------")
    # body = http_custom_subscription()
    # print(body)
    # sub_id3 = ORION_CB.create_subscription(body)
    # print("subscription id = " + str(sub_id3))
    # print("---------------------")
    #
    # # checking for duplicate sbuscription
    # duplicate_body = check_duplicate_subscription()
    # exists = ORION_CB.check_duplicate_subscription(subscription_body=duplicate_body)
    # print("The subscription allready exists:", exists)
    #
    # duplicate_type_body = check_existing_type_subscription()
    # exists_type = ORION_CB.check_duplicate_subscription(
    # subscription_body=duplicate_type_body)
    # print("The subscription allready exists:", exists_type)
    #
    # id_match_body = check_existing_id_pattern_subscription()
    # exists_id_pattern = ORION_CB.check_duplicate_subscription(id_match_body)
    # print("The subscription allready exists:", exists_id_pattern)
    #
    # print("deleting subscriptions..")
    # time.sleep(1)
    # sub_id = sub_id1
    # ORION_CB.delete_subscription(sub_id)
    # print("deleted subscription " + sub_id)
    # time.sleep(1)
    # sub_id = sub_id2
    # ORION_CB.delete_subscription(sub_id)
    # print("deleted subscription " + sub_id)
    # time.sleep(1)
    # sub_id = sub_id3
    # ORION_CB.delete_subscription(sub_id)
    # print("deleted subscription " + sub_id)
    #
    # ORION_CB.delete_all_subscriptions()
    #
