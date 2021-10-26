import logging
import json
from paho.mqtt.client import MQTT_CLEAN_START_FIRST_ONLY
from unittest import TestCase
from urllib.parse import urlparse
from filip.clients.mqtt import MQTTClient
from tests.config import settings


logger = logging.getLogger(__name__)


class TestMQTTClient(TestCase):
    def setUp(self) -> None:
        self.mqttc = MQTTClient()

        def on_connect(mqttc, obj, flags, rc):
            print("rc: " + str(rc))

        def on_connect_fail(mqttc, obj):
            print("Connect failed")

        def on_publish(mqttc, obj, mid):
            print("mid: " + str(mid))

        def on_subscribe(mqttc, obj, mid, granted_qos):
            print("Subscribed: " + str(mid) + " " + str(granted_qos))

        def on_log(mqttc, obj, level, string):
            print(string)

        self.mqttc.on_connect = on_connect
        self.mqttc.on_connect_fail = on_connect_fail
        self.mqttc.on_publish = on_publish
        self.mqttc.on_subscribe = on_subscribe
        self.mqttc.on_log = on_log

    def test_original_functionality(self):
        """
        demonstrate normal client behavior
        For additional examples on how to use the client please check:
        https://github.com/eclipse/paho.mqtt.python/tree/master/examples
        define callbacks methods"""
        first_topic = f"/filip/{settings.FIWARE_SERVICEPATH.strip('/')}/first"
        second_topic = f"/filip/{settings.FIWARE_SERVICEPATH.strip('/')}/second"
        first_payload = "filip_test_1"
        second_payload = "filip_test_2"
        def on_message_first(mqttc, obj, msg, properties=None):
            self.assertEqual(msg.payload.decode('utf-8'), first_payload)

        def on_message_second(mqttc, obj, msg, properties=None):
            self.assertEqual(msg.payload.decode('utf-8'), second_payload)

        self.mqttc.message_callback_add(sub=first_topic,
                                        callback=on_message_first)
        self.mqttc.message_callback_add(sub=second_topic,
                                        callback=on_message_second)
        mqtt_broker_url = urlparse(settings.MQTT_BROKER_URL)

        self.mqttc.connect(host=mqtt_broker_url.hostname,
                           port=mqtt_broker_url.port,
                           keepalive=60,
                           bind_address="",
                           bind_port=0,
                           clean_start=MQTT_CLEAN_START_FIRST_ONLY,
                           properties=None)
        self.mqttc.subscribe(topic=first_topic)

        # create a non blocking loop
        self.mqttc.loop_start()
        self.mqttc.publish(topic=first_topic, payload="filip_test")

        # add additional subscription to connection
        self.mqttc.subscribe(topic=second_topic)
        self.mqttc.publish(topic=second_topic, payload="filip_test")

        # remove subscriptions and callbacks
        self.mqttc.message_callback_remove(first_topic)
        self.mqttc.message_callback_remove(second_topic)
        self.mqttc.unsubscribe(first_topic)
        self.mqttc.unsubscribe(second_topic)

        # stop network loop and disconnect cleanly
        self.mqttc.loop_stop()
        self.mqttc.disconnect()

    def test_get_service_group(self):
        self.fail()

    def test_add_service_group(self):
        self.fail()

    def test_delete_service_group(self):
        self.fail()

    def test_update_service_group(self):
        self.fail()

    def test_get_device(self):
        self.fail()

    def test_add_device(self):
        self.fail()

    def test_delete_device(self):
        self.fail()

    def test_update_device(self):
        self.fail()

    def test_add_command_callback(self):
        self.fail()

    def test_publish(self):
        self.fail()

    def test_subscribe(self):
        self.fail()
