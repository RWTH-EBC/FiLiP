"""
Test the endpoint for subscription related task of NGSI-LD for ContextBrokerClient
"""
import json
import unittest

from pydantic import ValidationError
from filip.clients.ngsi_v2 import ContextBrokerClient
from filip.models.ngsi_v2.subscriptions import \
    Mqtt, \
    MqttCustom, \
    Subscription
# MQtt should be the same just the sub has to be changed to fit LD
from filip.models.base import FiwareHeader
from filip.utils.cleanup import clear_all, clean_test
from tests.config import settings

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
        self.fiware_header = FiwareHeader(
            service=settings.FIWARE_SERVICE,
            service_path=settings.FIWARE_SERVICEPATH)
        self.mqtt_url = "mqtt://test.de:1883"
        self.mqtt_topic = '/filip/testing'
        # self.notification =  {
        #     "attributes": ["filling", "controlledAsset"],
        #     "format": "keyValues",
        #     "endpoint": {
        #     "uri": "http://test:1234/subscription/low-stock-farm001-ngsild",
        #     "accept": "application/json"
        #     }
        # }
        self.sub_dict = {
            "description": "One subscription to rule them all",
            "type": "Subscription",
            "entities": [
                {
                    "type": "FillingLevelSensor",
                }
            ],
            "watchedAttributes": ["filling"],
            "q": "filling>0.6",
            "notification": {
                "attributes": ["filling", "controlledAsset"],
                "format": "keyValues",
                "endpoint": {
                "uri": "http://test:1234/subscription/low-stock-farm001-ngsild",
                "accept": "application/json"
                }
            },
            "@context": "http://context/ngsi-context.jsonld"
        }

    # def test_notification_models(self):
    #     """
    #     Test notification models
    #     """
    #     # Test url field sub field validation
    #     with self.assertRaises(ValidationError):
    #         Mqtt(url="brokenScheme://test.de:1883",
    #              topic='/testing')
    #     with self.assertRaises(ValidationError):
    #         Mqtt(url="mqtt://test.de:1883",
    #              topic='/,t')
    #     mqtt = Mqtt(url=self.mqtt_url,
    #                 topic=self.mqtt_topic)
    #     mqttCustom = MqttCustom(url=self.mqtt_url,
    #                             topic=self.mqtt_topic)

    #     # Test validator for conflicting fields
    #     notification = Notification.model_validate(self.notification)
    #     with self.assertRaises(ValidationError):
    #         notification.mqtt = mqtt
    #     with self.assertRaises(ValidationError):
    #         notification.mqtt = mqttCustom

    #     # test onlyChangedAttrs-field
    #     notification = Notification.model_validate(self.notification)
    #     notification.onlyChangedAttrs = True
    #     notification.onlyChangedAttrs = False
    #     with self.assertRaises(ValidationError):
    #         notification.onlyChangedAttrs = dict()


    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                cb_url=settings.CB_URL)
    
    def test_subscription_models(self) -> None:
        """
        Test subscription models
        Returns:
            None
        """
        sub = Subscription.model_validate(self.sub_dict)
        fiware_header = FiwareHeader(service=settings.FIWARE_SERVICE,
                                     service_path=settings.FIWARE_SERVICEPATH)
        with ContextBrokerClient(
                url=settings.CB_URL,
                fiware_header=fiware_header) as client:
            sub_id = client.post_subscription(subscription=sub)
            sub_res = client.get_subscription(subscription_id=sub_id)

            def compare_dicts(dict1: dict, dict2: dict):
                for key, value in dict1.items():
                    if isinstance(value, dict):
                        compare_dicts(value, dict2[key])
                    else:
                        self.assertEqual(str(value), str(dict2[key]))

            compare_dicts(sub.model_dump(exclude={'id'}),
                          sub_res.model_dump(exclude={'id'}))

        # test validation of throttling
        with self.assertRaises(ValidationError):
            sub.throttling = -1
        with self.assertRaises(ValidationError):
            sub.throttling = 0.1

    def test_query_string_serialization(self):
        sub = Subscription.model_validate(self.sub_dict)
        self.assertIsInstance(json.loads(sub.subject.condition.expression.model_dump_json())["q"],
                              str)
        self.assertIsInstance(json.loads(sub.subject.condition.model_dump_json())["expression"]["q"],
                              str)
        self.assertIsInstance(json.loads(sub.subject.model_dump_json())["condition"]["expression"]["q"],
                              str)
        self.assertIsInstance(json.loads(sub.model_dump_json())["subject"]["condition"]["expression"]["q"],
                              str)

    def test_model_dump_json(self):
        sub = Subscription.model_validate(self.sub_dict)

        # test exclude
        test_dict = json.loads(sub.model_dump_json(exclude={"id"}))
        with self.assertRaises(KeyError):
            _ = test_dict["id"]

        # test exclude_none
        test_dict = json.loads(sub.model_dump_json(exclude_none=True))
        with self.assertRaises(KeyError):
            _ = test_dict["throttling"]

        # test exclude_unset
        test_dict = json.loads(sub.model_dump_json(exclude_unset=True))
        with self.assertRaises(KeyError):
            _ = test_dict["status"]

        # test exclude_defaults
        test_dict = json.loads(sub.model_dump_json(exclude_defaults=True))
        with self.assertRaises(KeyError):
            _ = test_dict["status"]



def test_get_subscription_list(self,
                               subscriptions):
    """
    Get a list of all current subscription the broke has subscribed to.
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
        - Save beforehand all posted subscriptions and see if all the subscriptions exist in the list
    """

  

def test_post_subscription(self, 
                           ):
    """
    Create a new subscription.
    Args:
        - Content-Type(string): required
        - body: required
    Returns:
        - (201) successfully created subscription 
    Tests:
        - Create a subscription and post something from this subscription 
            to see if the subscribed broker gets the message.
        - Create a subscription twice to one message and see if the message is 
            received twice or just once.
    """
    sub = Subscription.model_validate(self.sub_dict)
    fiware_header = FiwareHeader(service=settings.FIWARE_SERVICE,
                                    service_path=settings.FIWARE_SERVICEPATH)
    with ContextBrokerClient(
            url=settings.CB_URL,
            fiware_header=fiware_header) as client:
        sub_id = client.post_subscription(subscription=sub)
        sub_res = client.get_subscription(subscription_id=sub_id)

        def compare_dicts(dict1: dict, dict2: dict):
            for key, value in dict1.items():
                if isinstance(value, dict):
                    compare_dicts(value, dict2[key])
                else:
                    self.assertEqual(str(value), str(dict2[key]))

        compare_dicts(sub.model_dump(exclude={'id'}),
                        sub_res.model_dump(exclude={'id'}))

    # test validation of throttling
    with self.assertRaises(ValidationError):
        sub.throttling = -1
    with self.assertRaises(ValidationError):
        sub.throttling = 0.1


def test_get_subscription():
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
    sub = Subscription.model_validate(self.sub_dict)
    fiware_header = FiwareHeader(service=settings.FIWARE_SERVICE,
                                    service_path=settings.FIWARE_SERVICEPATH)
    with ContextBrokerClient(
            url=settings.CB_URL,
            fiware_header=fiware_header) as client:
        sub_id = client.post_subscription(subscription=sub)
        sub_res = client.get_subscription(subscription_id=sub_id)



def test_delete_subscrption():
    """
    Cancels subscription. 
    Args: 
        - subscriptionID(string): required
    Returns:
        - Successful: 204, no content 
    Tests:
        - Post and delete subscription then do get subscription and see if it returns the subscription still.
        - Post and delete subscriüption then see if the broker still gets subscribed values.
    """


def test_update_subscription():
    """
    Only the fileds included in the request are updated in the subscription. 
    Args:
        - subscriptionID(string): required
        - Content-Type(string): required
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