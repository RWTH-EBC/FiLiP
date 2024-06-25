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

    def setUp(self) -> None:
        """
        Setup test data
        Returns:
            None
        """
        self.fiware_header = FiwareLDHeader(ngsild_tenant=settings.FIWARE_SERVICE)
        self.cb_client = ContextBrokerLDClient(fiware_header=self.fiware_header,
                                               url=settings.LD_CB_URL)
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
        self.cb_client = ContextBrokerLDClient()
        self.endpoint_http = Endpoint(**{
            "uri": "http://my.endpoint.org/notify",
            "accept": "application/json"
        })

    def test_get_subscription_list(self):
        """
        Get a list of all current subscriptions the broker has subscribed to.
        Args: 
            - limit(number($double)): Limits the number of subscriptions retrieved
            - offset(number($double)): Skip a number of subscriptions
            - options(string): Options dictionary("count")
        Returns:
            - (200) list of subscriptions
        Tests for get subscription list:
            - Get the list of subscriptions and get the count of the subsciptions -> compare the count
            - Go through the list and have a look at duplicate subscriptions
            - Set a limit for the subscription number and compare the count of subscriptions sent with the limit
            - Set offset for the subscription to retrive and check if the offset was procceded correctly.
            - Save beforehand all posted subscriptions and see if all the subscriptions exist in the list -> added to Test 1
        """
        
        """Test 1"""
        sub_post_list = list()
        for i in range(10): 
            attr_id = "attr" + str(i)
            attr = {attr_id: ContextProperty(value=randint(0,50))}
            id = "test_sub" + str(i)
            uri_string =  "mqtt://my.host.org:1883/topic/" + str(i)

            endpoint_mqtt = Endpoint(**{
                "uri": uri_string,
                "accept": "application/json",
                "notifierInfo": [
                    {
                        "key": "MQTT-Version",
                        "value": "mqtt5.0"
                    }
                ]
            })
            notification_param = NotificationParams(attributes=[attr_id], endpoint=endpoint_mqtt)
            sub = Subscription(id=id, notification=notification_param)
            self.cb_client.post_subscription(sub)
        # attr_id = "attr" + str(1)
        # attr = {attr_id: ContextProperty(value=randint(0,50))}
        # id = "test_sub" + str(1)
        # uri_string =  "mqtt://my.host.org:1883/topic/" + str(1)
        sub_example = {
        "description": "Subscription to receive MQTT-Notifications about "
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
            "mqtt": {
                "url": self.MQTT_BROKER_URL_INTERNAL,
                "topic": self.mqtt_topic
            },
            "attrs": [
                "temperature"
            ]
        },
        "throttling": 0
    }
        endpoint_mqtt = Endpoint(**{
            "uri": uri_string,
            "accept": "application/json",
            "notifierInfo": [
                {
                    "key": "MQTT-Version",
                    "value": "mqtt5.0"
                }
            ]
        })
        self.cb_client.post_subscription(sub_example)

        notification_param = NotificationParams(attributes=[attr_id], endpoint=endpoint_mqtt)
        sub = Subscription(id=id, notification=notification_param)
        #self.cb_client.post_subscription(sub)
        sub_list = self.cb_client.get_subscription_list()
        self.assertEqual(10, len(sub_list))
        
        for sub in sub_post_list:
            self.assertIn(sub in sub_list)
            
        for sub in sub_list:
            self.cb_client.delete_subscription(id=sub.id)
            
     
        """Test 2"""
        for i in range(2): 
            attr_id = "attr"
            attr = {attr_id: ContextProperty(value=20)}
            notification_param = NotificationParams(attributes=[attr_id], endpoint=self.endpoint_http)       
            id = "test_sub" 
            sub = Subscription(id=id, notification=notification_param)
            self.cb_client.post_subscription(sub)
        sub_list = self.cb_client.get_subscription_list()
        self.assertNotEqual(sub_list[0], sub_list[1])
        for sub in sub_list:
            self.cb_client.delete_subscription(id=sub.id)
            
            
        """Test 3"""
        for i in range(10): 
            attr_id = "attr" + str(i)
            attr = {attr_id: ContextProperty(value=randint(0,50))}
            notification_param = NotificationParams(attributes=[attr_id], endpoint=self.endpoint_http)       
            id = "test_sub" + str(i)
            sub = Subscription(id=id, notification=notification_param)
            self.cb_client.post_subscription(sub)
        sub_list = self.cb_client.get_subscription_list(limit=5)
        self.assertEqual(5, len(sub_list))
        for sub in sub_list:
            self.cb_client.delete_subscription(id=sub.id)
            
    def test_post_subscription(self):
        """
        Create a new subscription.
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
 

    def test_get_subscription(self):
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


    def test_delete_subscription(self):
        """
        Cancels subscription. 
        Args: 
            - subscriptionID(string): required
        Returns:
            - Successful: 204, no content 
        Tests:
            - Post and delete subscription then do get subscriptions and see if it returns the subscription still.
            - Post and delete subscription then see if the broker still gets subscribed values.
        """
        """Test 1"""
        for i in range(10): 
            attr_id = "attr" + str(i)
            attr = {attr_id: ContextProperty(value=randint(0,50))}
            notification_param = NotificationParams(attributes=[attr_id], endpoint=self.endpoint_http)       
            id = "test_sub_" + str(i)
            sub = Subscription(id=id, notification=notification_param)
            if i == 0: 
                subscription = sub
            self.cb_client.post_subscription(sub)
        
        self.cb_client.delete_subscription(id="test_sub_0")
        sub_list = self.cb_client.get_subscription_list(limit=10)
        self.assertNotIn(subscription, sub_list)
        for sub in sub_list:
            self.cb_client.delete_subscription(id=sub.id)
            
    def test_update_subscription(self):
        """
        Only the fileds included in the request are updated in the subscription. 
        Args:
            - subscriptionID(string): required
            - body(body): required
        Returns:
            - Successful: 204, no content
        Tests: 
            - Patch existing subscription and read out if the subscription got patched.
            - Try to patch non-existent subscriüptions.
            - Try to patch more than one subscription at once.
        """ 

    def tearDown(self) -> None:
        """
        Cleanup test server
        """
        clear_all(fiware_header=self.fiware_header,
                cb_url=settings.CB_URL)