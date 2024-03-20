"""
Test module for context subscriptions and notifications
"""
import json
import unittest

from pydantic import ValidationError
# from filip.clients.ngsi_v2 import ContextBrokerClient
from filip.models.ngsi_ld.subscriptions import \
    Subscription, \
    Endpoint
from filip.models.base import FiwareHeader
from filip.utils.cleanup import clear_all, clean_test
from tests.config import settings


class TestLDSubscriptions(unittest.TestCase):
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
                "attributes": ["speed"],
                "format": "keyValues",
                "endpoint": {
                    "uri": "http://my.endpoint.org/notify",
                    "accept": "application/json"
                }
            }
        self.sub_dict = {
            "id": "urn:ngsi-ld:Subscription:mySubscription",
            "type": "Subscription",
            "entities": [
                {
                    "type": "Vehicle"
                }
            ],
            "watchedAttributes": ["speed"],
            "q": "speed>50",
            "geoQ": {
                "georel": "near;maxDistance==2000",
                "geometry": "Point",
                "coordinates": [-1, 100]
                },
            "notification": {
                "attributes": ["speed"],
                "format": "keyValues",
                "endpoint": {
                    "uri": "http://my.endpoint.org/notify",
                    "accept": "application/json"
                }
            },
            "@context": [
                "http://example.org/ngsi-ld/latest/vehicle.jsonld",
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context-v1.3.jsonld"
            ]
            }

    def test_endpoint_models(self):
        """
        According to NGSI-LD Spec section 5.2.15
        Returns:

        """
        endpoint_http = Endpoint(**{
            "uri": "http://my.endpoint.org/notify",
            "accept": "application/json"
        })
        endpoint_mqtt = Endpoint(**{
            "uri": "mqtt://my.host.org:1883/my/test/topic",
            "accept": "application/json",  # TODO check whether it works
            "notifierInfo": [
                {
                    "key": "MQTT-Version",
                    "value": "mqtt5.0"
                }
            ]
        })
        with self.assertRaises(ValidationError):
            endpoint_https = Endpoint(**{
                "uri": "https://my.endpoint.org/notify",
                "accept": "application/json"
            })
        with self.assertRaises(ValidationError):
            endpoint_amqx = Endpoint(**{
                "uri": "amqx://my.endpoint.org/notify",
                "accept": "application/json"
            })

    def test_notification_models(self):
        """
        Test notification models
        According to NGSI-LD Spec section 5.2.14
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
        notification = Notification.model_validate(self.notification)
        with self.assertRaises(ValidationError):
            notification.mqtt = httpCustom
        with self.assertRaises(ValidationError):
            notification.mqtt = mqtt
        with self.assertRaises(ValidationError):
            notification.mqtt = mqttCustom

        # test onlyChangedAttrs-field
        notification = Notification.model_validate(self.notification)
        notification.onlyChangedAttrs = True
        notification.onlyChangedAttrs = False
        with self.assertRaises(ValidationError):
            notification.onlyChangedAttrs = dict()

    def test_entity_selector_models(self):
        """
        According to NGSI-LD Spec section 5.2.33
        Returns:

        """
        pass

    def test_temporal_query_models(self):
        """
        According to NGSI-LD Spec section 5.2.21
        Returns:

        """
        pass

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                cb_url=settings.CB_URL)
    def test_subscription_models(self) -> None:
        """
        Test subscription models
        According to NGSI-LD Spec section 5.2.12
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

    def tearDown(self) -> None:
        """
        Cleanup test server
        """
        clear_all(fiware_header=self.fiware_header,
                  cb_url=settings.CB_URL)