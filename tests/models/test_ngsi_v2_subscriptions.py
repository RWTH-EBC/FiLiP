"""
Test module for context subscriptions and notifications
"""
import unittest

from pydantic import ValidationError
from filip.clients.ngsi_v2 import ContextBrokerClient
from filip.models.ngsi_v2.subscriptions import \
    Http, \
    HttpCustom, \
    Mqtt, \
    MqttCustom, \
    Notification, \
    Subscription
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
        self.http_url = "https://test.de:80"
        self.mqtt_url = "mqtt://test.de:1883"
        self.mqtt_topic = '/filip/testing'
        self.notification = {
            "http":
            {
                "url": "http://localhost:1234"
            },
            "attrs": [
                "temperature",
                "humidity"
            ]
        }

    def test_notification_models(self):
        """
        Test notification models
        """
        # Test url field sub field validation
        with self.assertRaises(ValidationError):
            Http(url="brokenScheme://test.de:80")
        with self.assertRaises(ValidationError):
            HttpCustom(url="brokenScheme://test.de:80")
        with self.assertRaises(ValidationError):
            Mqtt(url="brokenScheme://test.de:1883",
                 topic='/testing')
        with self.assertRaises(ValidationError):
            Mqtt(url="mqtt://test.de:1883",
                 topic='/,t')
        httpCustom = HttpCustom(url=self.http_url)
        mqtt = Mqtt(url=self.mqtt_url,
                    topic=self.mqtt_topic)
        mqttCustom = MqttCustom(url=self.mqtt_url,
                                topic=self.mqtt_topic)

        # Test validator for conflicting fields
        notification = Notification.parse_obj(self.notification)
        with self.assertRaises(ValidationError):
            notification.mqtt = httpCustom
        with self.assertRaises(ValidationError):
            notification.mqtt = mqtt
        with self.assertRaises(ValidationError):
            notification.mqtt = mqttCustom

        # test onlyChangedAttrs-field
        notification.onlyChangedAttrs = True
        notification.onlyChangedAttrs = False
        with self.assertRaises(ValidationError):
            notification.onlyChangedAttrs = dict()


    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                cb_url=settings.CB_URL)
    def test_subscription_models(self) -> None:
        """
        Test subscription models
        Returns:
            None
        """
        sub_dict = {
            "description": "One subscription to rule them all",
            "subject": {
                "entities": [
                    {
                        "idPattern": ".*",
                        "type": "Room"
                    }
                ],
                "condition": {
                    "attrs": [
                        "temperature"
                    ],
                    "expression": {
                        "q": "temperature>40"
                    }
                }
            },
            "notification": {
                "http": {
                    "url": "http://localhost:1234"
                },
                "attrs": [
                    "temperature",
                    "humidity"
                ]
            },
            "expires": "2030-04-05T14:00:00Z",
        }

        sub = Subscription.parse_obj(sub_dict)
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

            compare_dicts(sub.dict(exclude={'id'}),
                          sub_res.dict(exclude={'id'}))

        # test validation of throttling
        with self.assertRaises(ValidationError):
            sub.throttling = -1
        with self.assertRaises(ValidationError):
            sub.throttling = 0.1

    def tearDown(self) -> None:
        """
        Cleanup test server
        """
        clear_all(fiware_header=self.fiware_header,
                  cb_url=settings.CB_URL)