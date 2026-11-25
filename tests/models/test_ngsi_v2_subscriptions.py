"""
Test module for context subscriptions and notifications
"""

import json
import unittest

from pydantic import ValidationError
from filip.clients.ngsi_v2 import ContextBrokerClient
from filip.models.ngsi_v2.subscriptions import (
    Http,
    HttpCustom,
    Mqtt,
    MqttCustom,
    Kafka,
    KafkaCustom,
    Notification,
    Subscription,
    NgsiPayload,
    NgsiPayloadAttr,
    Condition,
)
from filip.models.base import FiwareHeader
from filip.utils.validators import KafkaSaslMechanism, KafkaSecurityProtocol
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
            service=settings.FIWARE_SERVICE, service_path=settings.FIWARE_SERVICEPATH
        )
        self.http_url = "https://test.de:80"
        self.mqtt_url = "mqtt://test.de:1883"
        self.mqtt_topic = "/filip/testing"
        self.kafka_url = "kafka://test.de:9092"
        self.kafka_topic = "filip.testing"
        self.notification = {
            "http": {"url": "http://localhost:1234"},
            "attrs": ["temperature", "humidity"],
        }
        self.sub_dict = {
            "description": "One subscription to rule them all",
            "subject": {
                "entities": [{"idPattern": ".*", "type": "Room"}],
                "condition": {
                    "attrs": ["temperature"],
                    "expression": {"q": "temperature>40"},
                },
            },
            "notification": {
                "http": {"url": "http://localhost:1234"},
                "attrs": ["temperature", "humidity"],
            },
            "expires": "2030-04-05T14:00:00Z",
        }

    def test_notification_models(self):
        """
        Test notification models
        """
        # Test url field sub field validation
        with self.assertRaises(ValueError):
            Http(url="brokenScheme://test.de:80")
        with self.assertRaises(ValueError):
            HttpCustom(url="brokenScheme://test.de:80")
        with self.assertRaises(ValueError):
            Mqtt(url="brokenScheme://test.de:1883", topic="/testing")
        with self.assertRaises(ValueError):
            Mqtt(url="mqtt://test.de:1883", topic="/,t")
        with self.assertRaises(ValueError):
            HttpCustom(url="https://working-url.de:80", json={}, ngsi={})
        with self.assertRaises(ValueError):
            HttpCustom(url="https://working-url.de:80", payload="", json={})
        httpCustom = HttpCustom(url=self.http_url)
        mqtt = Mqtt(url=self.mqtt_url, topic=self.mqtt_topic)
        mqttCustom = MqttCustom(url=self.mqtt_url, topic=self.mqtt_topic)

        # Test validator for conflicting fields
        notification = Notification.model_validate(self.notification)
        with self.assertRaises(ValueError):
            notification.mqtt = httpCustom
        notification = Notification.model_validate(self.notification)
        with self.assertRaises(ValueError):
            notification.mqtt = mqtt
        notification = Notification.model_validate(self.notification)
        with self.assertRaises(ValueError):
            notification.mqtt = mqttCustom
        with self.assertRaises(ValueError):
            HttpCustom(url=self.http_url, json={}, payload="")
        with self.assertRaises(ValueError):
            MqttCustom(
                url=self.mqtt_url, topic=self.mqtt_topic, ngsi=NgsiPayload(), payload=""
            )
        with self.assertRaises(ValueError):
            HttpCustom(url=self.http_url, ngsi=NgsiPayload(), json="")

        # Test validator for ngsi payload type
        with self.assertRaises(ValueError):
            attr_dict = {"metadata": {}}
            NgsiPayloadAttr(**attr_dict)
        with self.assertRaises(ValueError):
            attr_dict = {"id": "entityId", "type": "entityType", "k": "v"}
            NgsiPayload(NgsiPayloadAttr(**attr_dict), id="someId", type="someType")

        # test onlyChangedAttrs-field
        notification = Notification.model_validate(self.notification)
        notification.onlyChangedAttrs = True
        notification.onlyChangedAttrs = False
        with self.assertRaises(ValueError):
            notification.onlyChangedAttrs = dict()

        # test covered
        notification = Notification.model_validate(self.notification)
        notification.covered = True
        with self.assertRaises(ValueError):
            notification.attrs = []

    def test_kafka_notification_models(self):
        """
        Test kafka notification models
        Check: https://fiware-orion.readthedocs.io/en/master/user/kafka_notifications.html
        """
        # Test url field sub field validation
        with self.assertRaises(ValueError):
            Kafka(url="brokenScheme://test.de:9092", topic=self.kafka_topic)
        with self.assertRaises(ValueError):
            Kafka(url="mqtt://test.de:1883", topic=self.kafka_topic)
        # A whole cluster is addressed by a comma separated list of brokers,
        # where only the leading one carries the scheme
        self.assertEqual(
            "kafka://broker1:9092,broker2:9092",
            Kafka(url="kafka://broker1:9092,broker2:9092", topic=self.kafka_topic).url,
        )
        with self.assertRaises(ValueError):
            Kafka(url="kafka://broker1:9092,broker2:brokenPort", topic=self.kafka_topic)

        # Test topic field validation. Kafka restricts topic names to the
        # characters a-z, A-Z, 0-9, '.', '_' and '-'
        # Raises error for reserved names (., ..)
        with self.assertRaises(ValueError):
            Kafka(url=self.kafka_url, topic="filip/testing")
        with self.assertRaises(ValueError):
            Kafka(url=self.kafka_url, topic=".")
        with self.assertRaises(ValueError):
            Kafka(url=self.kafka_url, topic="..")
        with self.assertRaises(ValueError):
            Kafka(url=self.kafka_url, topic="")
        with self.assertRaises(ValueError):
            Kafka(url=self.kafka_url, topic="a" * 250)
        # Macro replacement of the topic is only performed in custom
        # notifications, hence macros are not accepted in plain kafka ones
        with self.assertRaises(ValueError):
            Kafka(url=self.kafka_url, topic="filip.${id}")
        self.assertEqual(
            "filip.${id}",
            KafkaCustom(url=self.kafka_url, topic="filip.${id}").topic,
        )
        with self.assertRaises(ValueError):
            KafkaCustom(url=self.kafka_url, topic="filip/${id}")

        # Test validation of the SASL authentication fields. user and passwd
        # must be used together and require a saslMechanism
        with self.assertRaises(ValueError):
            Kafka(url=self.kafka_url, topic=self.kafka_topic, user="filip")
        with self.assertRaises(ValueError):
            Kafka(url=self.kafka_url, topic=self.kafka_topic, passwd="filip")
        with self.assertRaises(ValueError):
            Kafka(
                url=self.kafka_url,
                topic=self.kafka_topic,
                user="filip",
                passwd="filip",
            )
        with self.assertRaises(ValueError):
            Kafka(
                url=self.kafka_url,
                topic=self.kafka_topic,
                user="filip",
                passwd="filip",
                saslMechanism="brokenMechanism",
            )
        with self.assertRaises(ValueError):
            Kafka(
                url=self.kafka_url,
                topic=self.kafka_topic,
                user="filip",
                passwd="filip",
                saslMechanism=KafkaSaslMechanism.PLAIN,
                securityProtocol="brokenProtocol",
            )
        kafka = Kafka(
            url=self.kafka_url,
            topic=self.kafka_topic,
            key="${id}",
            user="filip",
            passwd="filip",
            saslMechanism=KafkaSaslMechanism.SCRAM_SHA_512,
            securityProtocol=KafkaSecurityProtocol.SASL_SSL,
        )
        self.assertEqual("SCRAM-SHA-512", kafka.saslMechanism.value)
        self.assertEqual("SASL_SSL", kafka.securityProtocol.value)

        # Test validator for conflicting payload fields
        with self.assertRaises(ValueError):
            KafkaCustom(url=self.kafka_url, topic=self.kafka_topic, json={}, ngsi={})
        with self.assertRaises(ValueError):
            KafkaCustom(url=self.kafka_url, topic=self.kafka_topic, payload="", json={})
        with self.assertRaises(ValueError):
            KafkaCustom(
                url=self.kafka_url,
                topic=self.kafka_topic,
                ngsi=NgsiPayload(),
                payload="",
            )
        kafkaCustom = KafkaCustom(url=self.kafka_url, topic=self.kafka_topic)

        # Test validator for conflicting endpoints
        notification = Notification.model_validate(self.notification)
        with self.assertRaises(ValueError):
            notification.kafka = kafka
        notification = Notification.model_validate(self.notification)
        with self.assertRaises(ValueError):
            notification.kafkaCustom = kafkaCustom
        notification = Notification(kafka=kafka)
        with self.assertRaises(ValueError):
            notification.kafkaCustom = kafkaCustom
        notification = Notification(kafka=kafka)
        with self.assertRaises(ValueError):
            notification.mqtt = Mqtt(url=self.mqtt_url, topic=self.mqtt_topic)

    def test_substitution_models(self):
        """
        Test substibution in notification models
        Check: https://fiware-orion.readthedocs.io/en/3.8.1/orion-api.html#custom-notifications
        """
        # Substitution in payloads
        payload = "t=${temperature}"
        _json = {"t1": "${temperature}"}
        ngsi_payload = {  # NGSI payload (templatized)
            "id": "some_prefix:${id}",
            "type": "NewType",
            "t2": "${temperature}",
        }

        # In case of httpCustom:
        notification_httpCustom_data = {
            "httpCustom": {"url": "http://localhost:1234"},
            "attrs": ["temperature", "humidity"],
        }
        notification_httpCustom = Notification.model_validate(
            notification_httpCustom_data
        )
        notification_httpCustom.httpCustom.url = "http://${hostName}.com"
        # Headers (both header name and value can be templatized)
        notification_httpCustom.httpCustom.headers = {
            "Fiware-Service": "${Service}",
            "Fiware-ServicePath": "${ServicePath}",
            "x-auth-token": "${authToken}",
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
            "mqttCustom": {
                "url": "mqtt://localhost:1883",
                "topic": "/some/topic/${id}",
            },
            "attrs": ["temperature", "humidity"],
        }
        notification_mqttCustom = Notification.model_validate(
            notification_mqttCustom_data
        )
        notification_mqttCustom.mqttCustom.payload = payload
        notification_mqttCustom.mqttCustom.payload = None
        notification_mqttCustom.mqttCustom.json = _json
        notification_mqttCustom.mqttCustom.json = None
        notification_mqttCustom.mqttCustom.ngsi = ngsi_payload

        # In case of kafkaCustom. Note that macro replacement is performed in
        # topic, key, headers, payload, json and ngsi, but not in url
        notification_kafkaCustom_data = {
            "kafkaCustom": {
                "url": "kafka://localhost:9092",
                "topic": "some.topic.${id}",
                "key": "${id}",
            },
            "attrs": ["temperature", "humidity"],
        }
        notification_kafkaCustom = Notification.model_validate(
            notification_kafkaCustom_data
        )
        # Headers (both header name and value can be templatized)
        notification_kafkaCustom.kafkaCustom.headers = {
            "Fiware-Service": "${Service}",
            "Fiware-ServicePath": "${ServicePath}",
        }
        notification_kafkaCustom.kafkaCustom.payload = payload
        notification_kafkaCustom.kafkaCustom.payload = None
        notification_kafkaCustom.kafkaCustom.json = _json
        notification_kafkaCustom.kafkaCustom.json = None
        notification_kafkaCustom.kafkaCustom.ngsi = ngsi_payload

    @clean_test(
        fiware_service=settings.FIWARE_SERVICE,
        fiware_servicepath=settings.FIWARE_SERVICEPATH,
        cb_url=settings.CB_URL,
    )
    def test_subscription_models(self) -> None:
        """
        Test subscription models
        Returns:
            None
        """
        tmp_dict = self.sub_dict.copy()
        sub = Subscription.model_validate(tmp_dict)
        fiware_header = FiwareHeader(
            service=settings.FIWARE_SERVICE, service_path=settings.FIWARE_SERVICEPATH
        )
        with ContextBrokerClient(
            url=settings.CB_URL, fiware_header=fiware_header
        ) as client:
            sub_id = client.post_subscription(subscription=sub)
            sub_res = client.get_subscription(subscription_id=sub_id)

            def compare_dicts(dict1: dict, dict2: dict):
                for key, value in dict1.items():
                    if isinstance(value, dict):
                        compare_dicts(value, dict2[key])
                    else:
                        self.assertEqual(str(value), str(dict2[key]))

            compare_dicts(
                sub.model_dump(exclude={"id"}), sub_res.model_dump(exclude={"id"})
            )

            tmp_dict.update(
                {
                    "notification": {
                        "httpCustom": {
                            "url": "http://localhost:1234",
                            "ngsi": {
                                "patchattr": {
                                    "value": "${temperature/2}",
                                    "type": "Calculated",
                                }
                            },
                            "method": "POST",
                        },
                        "attrs": ["temperature", "humidity"],
                    }
                }
            )
            sub = Subscription.model_validate(tmp_dict)
            sub_id = client.post_subscription(subscription=sub)
            sub_res = client.get_subscription(subscription_id=sub_id)
            compare_dicts(
                sub.model_dump(exclude={"id"}), sub_res.model_dump(exclude={"id"})
            )

            tmp_dict.update(
                {
                    "notification": {
                        "httpCustom": {
                            "url": "http://localhost:1234",
                            "json": {"t": "${temperate}", "h": "${humidity}"},
                            "method": "POST",
                        },
                        "attrs": ["temperature", "humidity"],
                    }
                }
            )
            sub = Subscription.model_validate(tmp_dict)
            sub_id = client.post_subscription(subscription=sub)
            sub_res = client.get_subscription(subscription_id=sub_id)
            compare_dicts(
                sub.model_dump(exclude={"id"}), sub_res.model_dump(exclude={"id"})
            )

            tmp_dict.update(
                {
                    "notification": {
                        "httpCustom": {
                            "url": "http://localhost:1234",
                            "payload": "Temperature is ${temperature} and humidity ${humidity}",
                            "method": "POST",
                        },
                        "attrs": ["temperature", "humidity"],
                    }
                }
            )
            sub = Subscription.model_validate(tmp_dict)
            sub_id = client.post_subscription(subscription=sub)
            sub_res = client.get_subscription(subscription_id=sub_id)
            compare_dicts(
                sub.model_dump(exclude={"id"}), sub_res.model_dump(exclude={"id"})
            )

        # test validation of throttling
        with self.assertRaises(ValueError):
            sub.throttling = -1
        with self.assertRaises(ValueError):
            sub.throttling = 0.1

    def test_query_string_serialization(self):
        sub = Subscription.model_validate(self.sub_dict)
        self.assertIsInstance(
            json.loads(sub.subject.condition.expression.model_dump_json())["q"], str
        )
        self.assertIsInstance(
            json.loads(sub.subject.condition.model_dump_json())["expression"]["q"], str
        )
        self.assertIsInstance(
            json.loads(sub.subject.model_dump_json())["condition"]["expression"]["q"],
            str,
        )
        self.assertIsInstance(
            json.loads(sub.model_dump_json())["subject"]["condition"]["expression"][
                "q"
            ],
            str,
        )

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
        clear_all(fiware_header=self.fiware_header, cb_url=settings.CB_URL)
