"""
Test module for context subscriptions and notifications
"""
import json
import unittest

from pydantic import ValidationError
from filip.clients.ngsi_v2 import ContextBrokerClient
from filip.models.ngsi_v2.subscriptions import \
    Http, \
    HttpCustom, \
    Mqtt, \
    MqttCustom, \
    Notification, \
    Subscription, \
    NgsiPayload, \
    NgsiPayloadAttr, Condition
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
        self.sub_dict = {
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
        with self.assertRaises(ValidationError):
            HttpCustom(url="https://working-url.de:80", json={}, ngsi={})
        with self.assertRaises(ValidationError):
            HttpCustom(url="https://working-url.de:80", payload="", json={})
        httpCustom = HttpCustom(url=self.http_url)
        mqtt = Mqtt(url=self.mqtt_url,
                    topic=self.mqtt_topic)
        mqttCustom = MqttCustom(url=self.mqtt_url,
                                topic=self.mqtt_topic)

        # Test validator for conflicting fields
        notification = Notification.model_validate(self.notification)
        with self.assertRaises(ValidationError):
            notification.mqtt = httpCustom
        notification = Notification.model_validate(self.notification)
        with self.assertRaises(ValidationError):
            notification.mqtt = mqtt
        notification = Notification.model_validate(self.notification)
        with self.assertRaises(ValidationError):
            notification.mqtt = mqttCustom
        with self.assertRaises(ValidationError):
            HttpCustom(url=self.http_url, json={}, payload="")
        with self.assertRaises(ValidationError):
            MqttCustom(url=self.mqtt_url,
                       topic=self.mqtt_topic, ngsi=NgsiPayload(), payload="")
        with self.assertRaises(ValidationError):
            HttpCustom(url=self.http_url, ngsi=NgsiPayload(), json="")

        #Test validator for ngsi payload type
        with self.assertRaises(ValidationError):
            attr_dict = {
                "metadata": {}
            }
            NgsiPayloadAttr(**attr_dict)
        with self.assertRaises(ValidationError):
            attr_dict = {
                "id": "entityId",
                "type": "entityType",
                "k": "v"
            }
            NgsiPayload(NgsiPayloadAttr(**attr_dict),id="someId",type="someType")

        # test onlyChangedAttrs-field
        notification = Notification.model_validate(self.notification)
        notification.onlyChangedAttrs = True
        notification.onlyChangedAttrs = False
        with self.assertRaises(ValidationError):
            notification.onlyChangedAttrs = dict()

    def test_substitution_models(self):
        """
        Test substibution in notification models
        Check: https://fiware-orion.readthedocs.io/en/3.8.1/orion-api.html#custom-notifications
        """
        # Substitution in payloads
        payload = "t=${temperature}"
        _json = {
            "t1": "${temperature}"
        }
        ngsi_payload = {  # NGSI payload (templatized)
            "id": "some_prefix:${id}",
            "type": "NewType",
            "t2": "${temperature}"
        }

        # In case of httpCustom:
        notification_httpCustom_data = {
            "httpCustom":
            {
                "url": "http://localhost:1234"
            },
            "attrs": [
                "temperature",
                "humidity"
            ]
        }
        notification_httpCustom = Notification.model_validate(
            notification_httpCustom_data)
        notification_httpCustom.httpCustom.url = "http://${hostName}.com"
        # Headers (both header name and value can be templatized)
        notification_httpCustom.httpCustom.headers = {
            "Fiware-Service": "${Service}",
            "Fiware-ServicePath": "${ServicePath}",
            "x-auth-token": "${authToken}"
        }
        notification_httpCustom.httpCustom.qs = {
            "type": "${type}",
        }
        notification_httpCustom.httpCustom.method = "${method}"
        notification_httpCustom.httpCustom.payload = payload
        notification_httpCustom.httpCustom.payload = None
        notification_httpCustom.httpCustom.json = _json
        notification_httpCustom.httpCustom.json = None
        notification_httpCustom.httpCustom.ngsi = ngsi_payload

        # In case of mqttCustom:
        notification_mqttCustom_data = {
            "mqttCustom":
            {
                "url": "mqtt://localhost:1883",
                "topic": "/some/topic/${id}"
            },
            "attrs": [
                "temperature",
                "humidity"
            ]
        }
        notification_mqttCustom = Notification.model_validate(
            notification_mqttCustom_data)
        notification_mqttCustom.mqttCustom.payload = payload
        notification_mqttCustom.mqttCustom.payload = None
        notification_mqttCustom.mqttCustom.json = _json
        notification_mqttCustom.mqttCustom.json = None
        notification_mqttCustom.mqttCustom.ngsi = ngsi_payload

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                cb_url=settings.CB_URL)
    def test_subscription_models(self) -> None:
        """
        Test subscription models
        Returns:
            None
        """
        tmp_dict=self.sub_dict.copy()
        sub = Subscription.model_validate(tmp_dict)
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

            tmp_dict.update({"notification":{
                "httpCustom": {
                    "url": "http://localhost:1234",
                    "ngsi":{
                        "patchattr":{
                            "value":"${temperature/2}",
                            "type":"Calculated"
                        }
                    },
                    "method":"POST"
                },
                "attrs": [
                    "temperature",
                    "humidity"
                ]
            }})
            sub = Subscription.model_validate(tmp_dict)
            sub_id = client.post_subscription(subscription=sub)
            sub_res = client.get_subscription(subscription_id=sub_id)
            compare_dicts(sub.model_dump(exclude={'id'}),
                          sub_res.model_dump(exclude={'id'}))

            tmp_dict.update({"notification":{
                "httpCustom": {
                    "url": "http://localhost:1234",
                    "json":{
                        "t":"${temperate}",
                        "h":"${humidity}"
                    },
                    "method":"POST"
                },
                "attrs": [
                    "temperature",
                    "humidity"
                ]
            }})
            sub = Subscription.model_validate(tmp_dict)
            sub_id = client.post_subscription(subscription=sub)
            sub_res = client.get_subscription(subscription_id=sub_id)
            compare_dicts(sub.model_dump(exclude={'id'}),
                          sub_res.model_dump(exclude={'id'}))

            tmp_dict.update({"notification":{
                "httpCustom": {
                    "url": "http://localhost:1234",
                    "payload":"Temperature is ${temperature} and humidity ${humidity}",
                    "method":"POST"
                },
                "attrs": [
                    "temperature",
                    "humidity"
                ]
            }})
            sub = Subscription.model_validate(tmp_dict)
            sub_id = client.post_subscription(subscription=sub)
            sub_res = client.get_subscription(subscription_id=sub_id)
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

    def test_alteration_types_model(self):
        c = Condition(alterationTypes=["entityCreate", "entityDelete"])
        # entity override is not a valid alteration type
        with self.assertRaises(ValueError):
            c = Condition(alterationTypes=["entityOverride", "entityDelete"])
        # test alteration types with different input types
        # list success
        c = Condition(alterationTypes=["entityCreate", "entityDelete"])
        # tuple success
        c = Condition(alterationTypes=("entityChange", "entityDelete"))
        # set success
        c = Condition(alterationTypes={"entityUpdate", "entityDelete"})
        # str fail
        with self.assertRaises(ValueError):
            c = Condition(alterationTypes="entityCreate")

    def tearDown(self) -> None:
        """
        Cleanup test server
        """
        clear_all(fiware_header=self.fiware_header,
                  cb_url=settings.CB_URL)