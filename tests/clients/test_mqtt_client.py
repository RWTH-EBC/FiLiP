import logging
import time
import unittest
from random import randrange
from paho.mqtt.client import MQTT_CLEAN_START_FIRST_ONLY
from filip.custom_types import AnyMqttUrl
from filip.models import FiwareHeader
from filip.models.ngsi_v2.context import NamedCommand
from filip.models.ngsi_v2.iot import \
    Device, \
    DeviceAttribute, \
    DeviceCommand, \
    ServiceGroup, PayloadProtocol
from filip.clients.mqtt import IoTAMQTTClient
from filip.utils.cleanup import clean_test, clear_all
from tests.config import settings


logger = logging.getLogger(__name__)


class TestMQTTClient(unittest.TestCase):
    """
    Test case for IoTAMQTTClient
    """

    def setUp(self) -> None:
        self.fiware_header = FiwareHeader(
            service=settings.FIWARE_SERVICE,
            service_path=settings.FIWARE_SERVICEPATH)
        self.service_group_json=ServiceGroup(
            apikey=settings.FIWARE_SERVICEPATH.strip('/'),
            resource="/iot/json")
        self.service_group_ul=ServiceGroup(
            apikey=settings.FIWARE_SERVICEPATH.strip('/'),
            resource="/iot/d")

        # create a device configuration
        device_attr = DeviceAttribute(name='temperature',
                                      object_id='t',
                                      type="Number")
        device_command = DeviceCommand(name='heater', type="Boolean")

        self.device_json = Device(device_id='my_json_device',
                                  entity_name='my_json_device',
                                  entity_type='Thing',
                                  protocol='IoTA-JSON',
                                  transport='MQTT',
                                  apikey=self.service_group_json.apikey,
                                  attributes=[device_attr],
                                  commands=[device_command])

        self.device_ul = Device(device_id='my_ul_device',
                                entity_name='my_ul_device',
                                entity_type='Thing',
                                protocol='PDI-IoTA-UltraLight',
                                transport='MQTT',
                                apikey=self.service_group_ul.apikey,
                                attributes=[device_attr],
                                commands=[device_command])

        self.mqttc = IoTAMQTTClient()

        def on_connect(mqttc, obj, flags, rc):
            mqttc.logger.info("rc: " + str(rc))

        def on_connect_fail(mqttc, obj):
            mqttc.logger.info("Connect failed")

        def on_publish(mqttc, obj, mid):
            mqttc.logger.info("mid: " + str(mid))

        def on_subscribe(mqttc, obj, mid, granted_qos):
            mqttc.logger.info("Subscribed: " + str(mid)
                              + " " + str(granted_qos))

        def on_log(mqttc, obj, level, string):
            mqttc.logger.info(string)

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
        mqtt_broker_url = settings.MQTT_BROKER_URL

        self.mqttc.connect(host=mqtt_broker_url.host,
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

    def test_init(self):
        devices = [self.device_json, self.device_ul]
        mqttc = IoTAMQTTClient(devices=devices,
                               service_groups=[self.service_group_json])
        self.assertListEqual(mqttc.devices, devices)

    def test_service_groups(self):
        self.mqttc.add_service_group(service_group=self.service_group_json)
        with self.assertRaises(AssertionError):
            self.mqttc.add_service_group(service_group="SomethingRandom")
        with self.assertRaises(ValueError):
            self.mqttc.add_service_group(
                service_group=self.service_group_json.model_dump())

        self.assertEqual(
            self.service_group_json,
            self.mqttc.get_service_group(self.service_group_json.apikey))

        self.mqttc.update_service_group(service_group=self.service_group_json)

        with self.assertRaises(KeyError):
            self.mqttc.update_service_group(
                service_group=self.service_group_json.model_copy(
                    update={'apikey': 'someOther'}))

        with self.assertRaises(KeyError):
            self.mqttc.delete_service_group(apikey="SomethingRandom")

        self.mqttc.delete_service_group(apikey=self.service_group_json.apikey)

    def test_devices(self):
        with self.assertRaises(ValueError):
            self.mqttc.devices = [self.device_ul, self.device_ul]

        self.mqttc.add_device(device=self.device_json)
        with self.assertRaises(ValueError):
            self.mqttc.add_device(device=self.device_json)
        self.mqttc.get_device(self.device_json.device_id)

        self.mqttc.update_device(device=self.device_json)
        with self.assertRaises(KeyError):
            self.mqttc.update_device(
                device=self.device_json.model_copy(
                    update={'device_id': "somethingRandom"}))

        self.mqttc.delete_device(device_id=self.device_json.device_id)

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                cb_url=settings.CB_URL,
                iota_url=settings.IOTA_JSON_URL)
    def test_add_command_callback_json(self):
        """
        Test for receiving commands for a specific device
        Returns:
            None
        """
        for group in self.mqttc.service_groups:
            self.mqttc.delete_service_group(group.apikey)

        for device in self.mqttc.devices:
            self.mqttc.delete_device(device.device_id)

        def on_command(client, obj, msg):
            apikey, device_id, payload = \
                client.get_encoder(PayloadProtocol.IOTA_JSON).decode_message(
                    msg=msg)

            # acknowledge a command. Here command are usually single
            # messages. The first key is equal to the commands name.
            client.publish(device_id=device_id,
                           command_name=next(iter(payload)),
                           payload=payload)

        self.mqttc.add_service_group(self.service_group_json)
        self.mqttc.add_device(self.device_json)
        self.mqttc.add_command_callback(device_id=self.device_json.device_id,
                                        callback=on_command)

        from filip.clients.ngsi_v2 import HttpClient, HttpClientConfig
        httpc_config = HttpClientConfig(cb_url=settings.CB_URL,
                                        iota_url=settings.IOTA_JSON_URL)
        httpc = HttpClient(fiware_header=self.fiware_header,
                           config=httpc_config)
        httpc.iota.post_group(service_group=self.service_group_json, update=True)
        httpc.iota.post_device(device=self.device_json, update=True)

        mqtt_broker_url: AnyMqttUrl = settings.MQTT_BROKER_URL

        self.mqttc.connect(host=mqtt_broker_url.host,
                           port=mqtt_broker_url.port,
                           keepalive=60,
                           bind_address="",
                           bind_port=0,
                           clean_start=MQTT_CLEAN_START_FIRST_ONLY,
                           properties=None)
        self.mqttc.subscribe()

        entity = httpc.cb.get_entity(entity_id=self.device_json.device_id,
                                     entity_type=self.device_json.entity_type)
        context_command = NamedCommand(name=self.device_json.commands[0].name,
                                       value=False)
        self.mqttc.loop_start()

        httpc.cb.post_command(entity_id=entity.id,
                              entity_type=entity.type,
                              command=context_command)

        time.sleep(2)
        # close the mqtt listening thread
        self.mqttc.loop_stop()
        # disconnect the mqtt device
        self.mqttc.disconnect()

        entity = httpc.cb.get_entity(entity_id=self.device_json.device_id,
                                     entity_type=self.device_json.entity_type)

        # The main part of this test, for all this setup was done
        self.assertEqual("OK", entity.heater_status.value)

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                cb_url=settings.CB_URL,
                iota_url=settings.IOTA_JSON_URL)
    def test_publish_json(self):
        """
        Test for receiving commands for a specific device
        Returns:
            None
        """
        for group in self.mqttc.service_groups:
            self.mqttc.delete_service_group(group.apikey)

        for device in self.mqttc.devices:
            self.mqttc.delete_device(device.device_id)

        self.mqttc.add_service_group(self.service_group_json)
        self.mqttc.add_device(self.device_json)

        from filip.clients.ngsi_v2 import HttpClient, HttpClientConfig
        httpc_config = HttpClientConfig(cb_url=settings.CB_URL,
                                        iota_url=settings.IOTA_JSON_URL)
        httpc = HttpClient(fiware_header=self.fiware_header,
                           config=httpc_config)
        httpc.iota.post_group(service_group=self.service_group_json, update=True)
        httpc.iota.post_device(device=self.device_json, update=True)

        mqtt_broker_url = settings.MQTT_BROKER_URL

        self.mqttc.connect(host=mqtt_broker_url.host,
                           port=mqtt_broker_url.port,
                           keepalive=60,
                           bind_address="",
                           bind_port=0,
                           clean_start=MQTT_CLEAN_START_FIRST_ONLY,
                           properties=None)
        self.mqttc.loop_start()

        payload = randrange(0, 100, 1)/1000
        self.mqttc.publish(device_id=self.device_json.device_id,
                           payload={self.device_json.attributes[0].object_id:
                                        payload})
        time.sleep(1)
        entity = httpc.cb.get_entity(entity_id=self.device_json.device_id,
                                     entity_type=self.device_json.entity_type)
        self.assertEqual(payload, entity.temperature.value)

        payload = randrange(0, 100, 1) / 1000
        self.mqttc.publish(device_id=self.device_json.device_id,
                           attribute_name="temperature",
                           payload=payload)
        time.sleep(1)
        entity = httpc.cb.get_entity(entity_id=self.device_json.device_id,
                                     entity_type=self.device_json.entity_type)
        self.assertEqual(payload, entity.temperature.value)


        # These test do currently not workt due to time stamp parsing
        # self.mqttc.publish(device_id=self.device_json.device_id,
        #                    payload={self.device_json.attributes[
        #                   0].object_id: 50},
        #                    timestamp=True)
        # time.sleep(1)
        # entity = httpc.cb.get_entity(entity_id=self.device_json.device_id,
        #                              entity_type=self.device_json.entity_type)
        # self.assertEqual(50, entity.temperature.value)
#
        # from datetime import datetime, timedelta
        # timestamp = datetime.now() + timedelta(days=1)
        # timestamp = timestamp.astimezone().isoformat()
        # self.mqttc.publish(device_id=self.device_json.device_id,
        #                    payload={self.device_json.attributes[
        #                   0].object_id: 60,
        #                             'timeInstant': timestamp})
        # time.sleep(1)
        # entity = httpc.cb.get_entity(entity_id=self.device_json.device_id,
        #                              entity_type=self.device_json.entity_type)
        # self.assertEqual(60, entity.temperature.value)
        # self.assertEqual(timestamp, entity.TimeInstant.value)
#
        # print(entity.json(indent=2))

        # close the mqtt listening thread
        self.mqttc.loop_stop()
        # disconnect the mqtt device
        self.mqttc.disconnect()

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                cb_url=settings.CB_URL,
                iota_url=settings.IOTA_UL_URL)
    def test_add_command_callback_ultralight(self):
        """
        Test for receiving commands for a specific device
        Returns:
            None
        """
        for group in self.mqttc.service_groups:
            self.mqttc.delete_service_group(group.apikey)

        for device in self.mqttc.devices:
            self.mqttc.delete_device(device.device_id)

        def on_command(client, obj, msg):
            apikey, device_id, payload = \
                client.get_encoder(PayloadProtocol.IOTA_UL).decode_message(
                    msg=msg)

            # acknowledge a command. Here command are usually single
            # messages. The first key is equal to the commands name.
            client.publish(device_id=device_id,
                           command_name=next(iter(payload)),
                           payload={'heater': True})

        self.mqttc.add_service_group(self.service_group_ul)
        self.mqttc.add_device(self.device_ul)
        self.mqttc.add_command_callback(device_id=self.device_ul.device_id,
                                        callback=on_command)

        from filip.clients.ngsi_v2 import HttpClient, HttpClientConfig
        httpc_config = HttpClientConfig(cb_url=settings.CB_URL,
                                        iota_url=settings.IOTA_UL_URL)
        httpc = HttpClient(fiware_header=self.fiware_header,
                           config=httpc_config)
        httpc.iota.post_group(service_group=self.service_group_ul)
        httpc.iota.post_device(device=self.device_ul, update=True)

        mqtt_broker_url = settings.MQTT_BROKER_URL

        self.mqttc.connect(host=mqtt_broker_url.host,
                           port=mqtt_broker_url.port,
                           keepalive=60,
                           bind_address="",
                           bind_port=0,
                           clean_start=MQTT_CLEAN_START_FIRST_ONLY,
                           properties=None)
        self.mqttc.subscribe()

        entity = httpc.cb.get_entity(entity_id=self.device_ul.device_id,
                                     entity_type=self.device_ul.entity_type)
        context_command = NamedCommand(name=self.device_ul.commands[0].name,
                                       value=False)
        self.mqttc.loop_start()

        httpc.cb.post_command(entity_id=entity.id,
                              entity_type=entity.type,
                              command=context_command)

        time.sleep(5)
        # close the mqtt listening thread
        self.mqttc.loop_stop()
        # disconnect the mqtt device
        self.mqttc.disconnect()

        entity = httpc.cb.get_entity(entity_id=self.device_ul.device_id,
                                     entity_type=self.device_ul.entity_type)

        # The main part of this test, for all this setup was done
        self.assertEqual("OK", entity.heater_status.value)

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                cb_url=settings.CB_URL,
                iota_url=settings.IOTA_UL_URL)
    def test_publish_ultralight(self):
        """
        Test for receiving commands for a specific device
        Returns:
            None
        """
        for group in self.mqttc.service_groups:
            self.mqttc.delete_service_group(group.apikey)

        for device in self.mqttc.devices:
            self.mqttc.delete_device(device.device_id)

        self.mqttc.add_service_group(self.service_group_ul)
        self.mqttc.add_device(self.device_ul)

        from filip.clients.ngsi_v2 import HttpClient, HttpClientConfig
        httpc_config = HttpClientConfig(cb_url=settings.CB_URL,
                                        iota_url=settings.IOTA_UL_URL)
        httpc = HttpClient(fiware_header=self.fiware_header,
                           config=httpc_config)
        httpc.iota.post_group(service_group=self.service_group_ul,
                              update=True)
        httpc.iota.post_device(device=self.device_ul, update=True)

        time.sleep(0.5)

        mqtt_broker_url = settings.MQTT_BROKER_URL

        self.mqttc.connect(host=mqtt_broker_url.host,
                           port=mqtt_broker_url.port,
                           keepalive=60,
                           bind_address="",
                           bind_port=0,
                           clean_start=MQTT_CLEAN_START_FIRST_ONLY,
                           properties=None)
        self.mqttc.loop_start()

        payload = randrange(0, 100, 1)/1000
        self.mqttc.publish(
            device_id=self.device_ul.device_id,
            payload={self.device_ul.attributes[0].object_id: payload})
        time.sleep(1)
        entity = httpc.cb.get_entity(entity_id=self.device_ul.device_id,
                                     entity_type=self.device_ul.entity_type)
        self.assertEqual(payload, entity.temperature.value)

        payload = randrange(0, 100, 1)/1000
        self.mqttc.publish(device_id=self.device_ul.device_id,
                           attribute_name="temperature",
                           payload=payload)
        time.sleep(1)
        entity = httpc.cb.get_entity(entity_id=self.device_ul.device_id,
                                     entity_type=self.device_ul.entity_type)
        self.assertEqual(payload, entity.temperature.value)

        # These test do currently not workt due to time stamp parsing
        # self.mqttc.publish(device_id=self.device_ul.device_id,
        #                    payload={self.device_ul.attributes[0].object_id:
        #                   50},
        #                    timestamp=True)
        # time.sleep(1)
        # entity = httpc.cb.get_entity(entity_id=self.device_ul.device_id,
        #                              entity_type=self.device_ul.entity_type)
        # self.assertEqual(50, entity.temperature.value)
#
        # from datetime import datetime, timedelta
        # timestamp = datetime.now() + timedelta(days=1)
        # timestamp = timestamp.astimezone().isoformat()
        # self.mqttc.publish(device_id=self.device_ul.device_id,
        #                    payload={self.device_ul.attributes[0].object_id:
        #                    60,
        #                             'timeInstant': timestamp})
        # time.sleep(1)
        # entity = httpc.cb.get_entity(entity_id=self.device_ul.device_id,
        #                              entity_type=self.device_ul.entity_type)
        # self.assertEqual(60, entity.temperature.value)
        # self.assertEqual(timestamp, entity.TimeInstant.value)
        #
        # print(entity.json(indent=2))

        # close the mqtt listening thread
        self.mqttc.loop_stop()
        # disconnect the mqtt device
        self.mqttc.disconnect()

    def tearDown(self) -> None:
        """
        Cleanup test server
        """
        clear_all(fiware_header=self.fiware_header,
                  cb_url=settings.CB_URL,
                  iota_url=[settings.IOTA_JSON_URL, settings.IOTA_UL_URL])
