"""
Test the endpoint for subscription related task of NGSI-LD for ContextBrokerClient
"""
import json
import unittest

from pydantic import ValidationError

from filip.clients.ngsi_ld.cb import ContextBrokerLDClient
from filip.models.base import FiwareLDHeader
from filip.models.ngsi_ld.context import \
    ContextProperty, \
    NamedContextProperty
from filip.models.ngsi_ld.subscriptions import \
    Endpoint, \
    NotificationParams, \
    Subscription
from filip.utils.cleanup import clear_all, clean_test
from tests.config import settings
from random import randint


class TestSubscriptions(unittest.TestCase):
    """
    Test class for context broker models
    """

    def cleanup(self):
        """
        Cleanup test subscriptions
        """
        sub_list = self.cb_client.get_subscription_list()
        for sub in sub_list:
            if sub.id.startswith('urn:ngsi-ld:Subscription:test_sub'):
                self.cb_client.delete_subscription(sub.id)

    def setUp(self) -> None:
        """
        Setup test data
        Returns:
            None
        """
        FIWARE_SERVICE = "service"
        FIWARE_SERVICEPATH = "/"
        self.fiware_header = FiwareLDHeader(
            service=FIWARE_SERVICE,
            service_path=FIWARE_SERVICEPATH)
        # self.mqtt_url = "mqtt://test.de:1883"
        # self.mqtt_topic = '/filip/testing'
        # self.notification =  {
        #     "attributes": ["filling", "controlledAsset"],
        #     "format": "keyValues",
        #     "endpoint": {
        #     "uri": "http://test:1234/subscription/low-stock-farm001-ngsild",
        #     "accept": "application/json"
        #     }
        # }
        #self.mqtt_url = TestSettings.MQTT_BROKER_URL
        self.mqtt_topic = ''.join([FIWARE_SERVICE, FIWARE_SERVICEPATH])
        self.MQTT_BROKER_URL_INTERNAL = "mqtt://mosquitto:1883"
        self.MQTT_BROKER_URL_EXPOSED = "mqtt://localhost:1883"
        self.endpoint_mqtt = Endpoint(**{
            "uri": "mqtt://my.host.org:1883/my/test/topic",
            "accept": "application/json",  # TODO check whether it works
        })
        self.cb_client = ContextBrokerLDClient(url=settings.LD_CB_URL, fiware_header=self.fiware_header)
        self.endpoint_http = Endpoint(**{
            "uri": "http://137.226.248.246:1027/ngsi-ld/v1/subscriptions",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
     )
        self.cleanup()

    def tearDown(self) -> None:
        self.cleanup()


    def test_post_subscription_http(self):
        """
        Create a new HTTP subscription.
        Args:
            - Request body: required
        Returns:
            - (201) successfully created subscription
        Tests:
            - Create a HTTP subscription and post it
        """
        attr_id = "attr"
        id = "urn:ngsi-ld:Subscription:" + "test_sub0"
        notification_param = NotificationParams(attributes=[attr_id], endpoint=self.endpoint_http)
        sub = Subscription(id=id, notification=notification_param, entities=[{"type": "Room"}])
        self.cb_client.post_subscription(sub)


    def test_post_subscription_http_check_broker(self):
        """
        Create a new HTTP subscription and check whether messages are received.
        Args:
            - Request body: required
        Returns:
            - (201) successfully created subscription 
        Tests:
            - Create a subscription and post something from this subscription 
                to see if the subscribed broker gets the message.
            - Create a subscription twice to one message and see if the message is 
                received twice or just once.
        """
        pass

    def test_get_subscription(self):
        """
        Returns the subscription if it exists.
        Args:
            - subscriptionId(string): required
        Returns: 
            - (200) subscription or empty list if successful 
            - Error Code
        Tests:
            - Get Subscription and check if the subscription is the same as the one posted
        """
        attr_id = "attr"
        id = "urn:ngsi-ld:Subscription:" + "test_sub0"
        notification_param = NotificationParams(attributes=[attr_id], endpoint=self.endpoint_http)
        sub = Subscription(id=id, notification=notification_param, entities=[{"type": "Room"}])
        self.cb_client.post_subscription(sub)
        sub_get = self.cb_client.get_subscription(subscription_id=id)
        self.assertEqual(sub.entities, sub_get.entities)
        self.assertEqual(sub.notification.attributes, sub_get.notification.attributes)
        self.assertEqual(sub.notification.endpoint.uri, sub_get.notification.endpoint.uri)


    def test_get_subscription_check_broker(self):
        """
        Returns the subscription if it exists.
        Args:
            - subscriptionId(string): required
        Returns:
            - (200) subscription or empty list if successful
            - Error Code
        Tests:
            - Subscribe to a message and see if it appears when the message is subscribed to
            - Choose a non-existent ID and see if the return is an empty array
        """
        pass

    def test_post_subscription_mqtt(self):
#            uri_string =  "mqtt://my.host.org:1883/topic/" + str(i)
#            endpoint_mqtt = Endpoint(**{
#                "uri": uri_string,
#                "accept": "application/json",
#                "notifierInfo": [
#                    {
#                        "key": "MQTT-Version",
#                        "value": "mqtt5.0"
#                    }
#                ]
#            })
#            notification_param = NotificationParams(attributes=[attr_id], endpoint=endpoint_mqtt)

#        sub_example = {
#        "description": "Subscription to receive MQTT-Notifications about "
#                       "urn:ngsi-ld:Room:001",
#        "subject": {
#            "entities": [
#                {
#                    "id": "urn:ngsi-ld:Room:001",
#                    "type": "Room"
#                }
#            ],
#            "condition": {
#                "attrs": [
#                    "temperature"
#                ]
#            }
#        },
#        "notification": {
#            "mqtt": {
#                "url": self.MQTT_BROKER_URL_INTERNAL,
#                "topic": self.mqtt_topic
#            },
#            "attrs": [
#                "temperature"
#            ]
#        },
#        "throttling": 0
#    }
#        endpoint_mqtt = Endpoint(**{
#            "uri": uri_string,
#            "accept": "application/json",
#            "notifierInfo": [
#                {
#                    "key": "MQTT-Version",
#                    "value": "mqtt5.0"
#                }
#            ]
#        })
#        self.cb_client.post_subscription(sub_example)
#        notification_param = NotificationParams(attributes=[attr_id], endpoint=endpoint_mqtt)
#        sub = Subscription(id=id, notification=notification_param)
#        #self.cb_client.post_subscription(sub)
        pass


    def test_get_subscription_list(self):
        """
        Get a list of all current subscriptions the broker has subscribed to.
        Args:
            - limit(number($double)): Limits the number of subscriptions retrieved
        Returns:
            - (200) list of subscriptions
        Tests for get subscription list:
            - Create list of subscriptions and get the list of subscriptions -> compare the lists
            - Set a limit for the subscription number and compare the count of subscriptions
        """
        sub_post_list = list()
        for i in range(10):
            attr_id = "attr" + str(i)
            id = "urn:ngsi-ld:Subscription:" + "test_sub" + str(i)
            notification_param = NotificationParams(attributes=[attr_id], endpoint=self.endpoint_http)
            sub = Subscription(id=id, notification=notification_param, entities=[{"type": "Room"}])
            sub_post_list.append(sub)
            self.cb_client.post_subscription(sub)

        sub_list = self.cb_client.get_subscription_list()
        sub_id_list = [sub.id for sub in sub_list]

        for sub in sub_post_list:
            self.assertIn(sub.id, sub_id_list)

        sub_limit = 5
        sub_list2 = self.cb_client.get_subscription_list(limit=sub_limit)
        self.assertEqual(len(sub_list2), sub_limit)


    def test_delete_subscription(self):
        """
        Cancels subscription. 
        Args: 
            - subscriptionID(string): required
        Returns:
            - Successful: 204, no content 
        Tests:
            - Post and delete subscription then get all subscriptions and check whether deleted subscription is still there.
        """
        for i in range(10): 
            attr_id = "attr" + str(i)
            notification_param = NotificationParams(attributes=[attr_id], endpoint=self.endpoint_http)
            id = "urn:ngsi-ld:Subscription:" + "test_sub" + str(i)
            sub = Subscription(id=id, notification=notification_param, entities=[{"type": "Room"}])

            if i == 0: 
                del_sub = sub
                del_id = id
            self.cb_client.post_subscription(sub)
        
        sub_list = self.cb_client.get_subscription_list(limit=10)
        sub_id_list = [sub.id for sub in sub_list]
        self.assertIn(del_sub.id, sub_id_list)

        self.cb_client.delete_subscription(subscription_id=del_id)
        sub_list = self.cb_client.get_subscription_list(limit=10)
        sub_id_list = [sub.id for sub in sub_list]
        self.assertNotIn(del_sub.id, sub_id_list)

        for sub in sub_list:
            self.cb_client.delete_subscription(subscription_id=sub.id)


    def test_delete_subscription_check_broker(self):
        """
        Cancels subscription and checks on subscribed values.
        Args:
            - subscriptionID(string): required
        Returns:
            - Successful: 204, no content
        Tests:
            - Post and delete subscription then see if the broker still gets subscribed values.
        """
        pass

            
    def test_update_subscription(self):
        """
        Update a subscription.
        Only the fields included in the request are updated in the subscription.
        Args:
            - subscriptionID(string): required
            - body(body): required
        Returns:
            - Successful: 204, no content
        Tests: 
            - Patch existing subscription and read out if the subscription got patched.
            - Try to patch non-existent subscriptions.
            - Try to patch more than one subscription at once.
        """
        attr_id = "attr"
        id = "urn:ngsi-ld:Subscription:" + "test_sub77"
        notification_param = NotificationParams(attributes=[attr_id], endpoint=self.endpoint_http)
        sub = Subscription(id=id, notification=notification_param, entities=[{"type": "Room"}])
        self.cb_client.post_subscription(sub)
        sub_list = self.cb_client.get_subscription_list()
        self.assertEqual(len(sub_list), 1)

        sub_changed = Subscription(id=id, notification=notification_param, entities=[{"type": "House"}])

        self.cb_client.update_subscription(sub_changed)

        # Try to patch non-existent subscriptions.
        # TODO
        #Try to patch more than one subscription at once.
        # TODO


    def test_update_subscription_check_broker(self):
        """
        Update a subscription and check changes in received messages.
        Args:
            - subscriptionID(string): required
            - body(body): required
        Returns:
            - Successful: 204, no content
        Tests:
            - Patch existing subscription and read out if the subscription got patched.
        """
        pass
