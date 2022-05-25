"""
Tests for filip.cb.client
"""
import copy
import unittest
import logging
import time
import random
import json

import paho.mqtt.client as mqtt
from datetime import datetime, timedelta
from urllib.parse import urlparse
from requests import RequestException
from filip.models.base import FiwareHeader
from filip.utils.simple_ql import QueryString
from filip.clients.ngsi_v2 import ContextBrokerClient
from filip.clients.ngsi_v2 import HttpClient, HttpClientConfig
from filip.config import settings
from filip.models.ngsi_v2.context import \
    ContextEntity, \
    ContextAttribute, \
    NamedContextAttribute, \
    NamedCommand, \
    Query, \
    ActionType

from filip.models.ngsi_v2.base import AttrsFormat, EntityPattern, Status, \
    NamedMetadata
from filip.models.ngsi_v2.subscriptions import Mqtt, Message, Subscription
from filip.models.ngsi_v2.iot import \
    Device, \
    DeviceCommand, \
    DeviceAttribute, \
    ServiceGroup, \
    StaticDeviceAttribute
from filip.utils.cleanup import clear_all, clean_test
from tests.config import settings


logger = logging.getLogger(__name__)


class TestContextBroker(unittest.TestCase):
    """
    Test class for ContextBrokerClient
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
        clear_all(fiware_header=self.fiware_header,
                  cb_url=settings.CB_URL,
                  iota_url=settings.IOTA_JSON_URL)
        self.resources = {
            "entities_url": "/v2/entities",
            "types_url": "/v2/types",
            "subscriptions_url": "/v2/subscriptions",
            "registrations_url": "/v2/registrations"
        }
        self.attr = {'temperature': {'value': 20.0,
                                     'type': 'Number'}}
        self.entity = ContextEntity(id='MyId', type='MyType', **self.attr)


        self.client = ContextBrokerClient(
            url=settings.CB_URL,
            fiware_header=self.fiware_header)
        self.subscription = Subscription.parse_obj({
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
            "expires": datetime.now(),
            "throttling": 0
        })

    def test_management_endpoints(self):
        """
        Test management functions of context broker client
        """
        with ContextBrokerClient(
                url=settings.CB_URL,
                fiware_header=self.fiware_header) as client:
            self.assertIsNotNone(client.get_version())
            self.assertEqual(client.get_resources(), self.resources)

    def test_statistics(self):
        """
        Test statistics of context broker client
        """
        with ContextBrokerClient(
                url=settings.CB_URL,
                fiware_header=self.fiware_header) as client:
            self.assertIsNotNone(client.get_statistics())

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                cb_url=settings.CB_URL,
                iota_url=settings.IOTA_JSON_URL)
    def test_pagination(self):
        """
        Test pagination of context broker client
        Test pagination. only works if enough entities are available
        """
        with ContextBrokerClient(
                url=settings.CB_URL,
                fiware_header=self.fiware_header) as client:
            entities_a = [ContextEntity(id=str(i),
                                        type=f'filip:object:TypeA') for i in
                          range(0, 1000)]
            client.update(action_type=ActionType.APPEND, entities=entities_a)
            entities_b = [ContextEntity(id=str(i),
                                        type=f'filip:object:TypeB') for i in
                          range(1000, 2001)]
            client.update(action_type=ActionType.APPEND, entities=entities_b)
            self.assertLessEqual(len(client.get_entity_list(limit=1)), 1)
            self.assertLessEqual(len(client.get_entity_list(limit=999)), 999)
            self.assertLessEqual(len(client.get_entity_list(limit=1001)), 1001)
            self.assertLessEqual(len(client.get_entity_list(limit=2001)), 2001)

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                cb_url=settings.CB_URL)
    def test_entity_filtering(self):
        """
        Test filter operations of context broker client
        """
        with ContextBrokerClient(
                url=settings.CB_URL,
                fiware_header=self.fiware_header) as client:
            # test patterns
            with self.assertRaises(ValueError):
                client.get_entity_list(id_pattern='(&()?')
            with self.assertRaises(ValueError):
                client.get_entity_list(type_pattern='(&()?')
            entities_a = [ContextEntity(id=str(i),
                                        type=f'filip:object:TypeA') for i in
                          range(0, 5)]

            client.update(action_type=ActionType.APPEND, entities=entities_a)
            entities_b = [ContextEntity(id=str(i),
                                        type=f'filip:object:TypeB') for i in
                          range(6, 10)]

            client.update(action_type=ActionType.APPEND, entities=entities_b)

            entities_all = client.get_entity_list()
            entities_by_id_pattern = client.get_entity_list(
                id_pattern='.*[1-5]')
            self.assertLess(len(entities_by_id_pattern), len(entities_all))

            entities_by_type_pattern = client.get_entity_list(
                type_pattern=".*TypeA$")
            self.assertLess(len(entities_by_type_pattern), len(entities_all))

            qs = QueryString(qs=[('presentValue', '>', 0)])
            entities_by_query = client.get_entity_list(q=qs)
            self.assertLess(len(entities_by_query), len(entities_all))

            # test options
            for opt in list(AttrsFormat):
                entities_by_option = client.get_entity_list(response_format=opt)
                self.assertEqual(len(entities_by_option), len(entities_all))
                self.assertEqual(client.get_entity(
                    entity_id='0',
                    response_format=opt),
                    entities_by_option[0])
            with self.assertRaises(ValueError):
                client.get_entity_list(response_format='not in AttrFormat')

            client.update(action_type=ActionType.DELETE, entities=entities_a)

            client.update(action_type=ActionType.DELETE, entities=entities_b)

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                cb_url=settings.CB_URL)
    def test_entity_operations(self):
        """
        Test entity operations of context broker client
        """
        with ContextBrokerClient(
                url=settings.CB_URL,
                fiware_header=self.fiware_header) as client:
            client.post_entity(entity=self.entity, update=True)
            res_entity = client.get_entity(entity_id=self.entity.id)
            client.get_entity(entity_id=self.entity.id, attrs=['temperature'])
            self.assertEqual(client.get_entity_attributes(
                entity_id=self.entity.id), res_entity.get_properties(
                response_format='dict'))
            res_entity.temperature.value = 25
            client.update_entity(entity=res_entity)
            self.assertEqual(client.get_entity(entity_id=self.entity.id),
                             res_entity)
            res_entity.add_attributes({'pressure': ContextAttribute(
                type='Number', value=1050)})
            client.update_entity(entity=res_entity)
            self.assertEqual(client.get_entity(entity_id=self.entity.id),
                             res_entity)

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                cb_url=settings.CB_URL)
    def test_attribute_operations(self):
        """
        Test attribute operations of context broker client
        """
        with ContextBrokerClient(
                url=settings.CB_URL,
                fiware_header=self.fiware_header) as client:
            entity = self.entity
            attr_txt = NamedContextAttribute(name='attr_txt',
                                             type='Text',
                                             value="Test")
            attr_bool = NamedContextAttribute(name='attr_bool',
                                              type='Boolean',
                                              value=True)
            attr_float = NamedContextAttribute(name='attr_float',
                                               type='Number',
                                               value=round(random.random(), 5))
            attr_list = NamedContextAttribute(name='attr_list',
                                              type='StructuredValue',
                                              value=[1, 2, 3])
            attr_dict = NamedContextAttribute(name='attr_dict',
                                              type='StructuredValue',
                                              value={'key': 'value'})
            entity.add_attributes([attr_txt,
                                   attr_bool,
                                   attr_float,
                                   attr_list,
                                   attr_dict])

            self.assertIsNotNone(client.post_entity(entity=entity,
                                                    update=True))
            res_entity = client.get_entity(entity_id=entity.id)

            for attr in entity.get_properties():
                self.assertIn(attr, res_entity.get_properties())
                res_attr = client.get_attribute(entity_id=entity.id,
                                                attr_name=attr.name)

                self.assertEqual(type(res_attr.value), type(attr.value))
                self.assertEqual(res_attr.value, attr.value)
                value = client.get_attribute_value(entity_id=entity.id,
                                                   attr_name=attr.name)
                # unfortunately FIWARE returns an int for 20.0 although float
                # is expected
                if isinstance(value, int) and not isinstance(value, bool):
                    value = float(value)
                self.assertEqual(type(value), type(attr.value))
                self.assertEqual(value, attr.value)

            for attr_name, attr in entity.get_properties(
                    response_format='dict').items():

                client.update_entity_attribute(entity_id=entity.id,
                                               attr_name=attr_name,
                                               attr=attr)
                value = client.get_attribute_value(entity_id=entity.id,
                                                   attr_name=attr_name)
                # unfortunately FIWARE returns an int for 20.0 although float
                # is expected
                if isinstance(value, int) and not isinstance(value, bool):
                    value = float(value)
                self.assertEqual(type(value), type(attr.value))
                self.assertEqual(value, attr.value)

            new_value = 1337.0
            client.update_attribute_value(entity_id=entity.id,
                                          attr_name='temperature',
                                          value=new_value)
            attr_value = client.get_attribute_value(entity_id=entity.id,
                                                    attr_name='temperature')
            self.assertEqual(attr_value, new_value)

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                cb_url=settings.CB_URL)
    def test_type_operations(self):
        """
        Test type operations of context broker client
        """
        with ContextBrokerClient(
                url=settings.CB_URL,
                fiware_header=self.fiware_header) as client:
            self.assertIsNotNone(client.post_entity(entity=self.entity,
                                                    update=True))
            client.get_entity_types()
            client.get_entity_types(options='count')
            client.get_entity_types(options='values')
            client.get_entity_type(entity_type='MyType')
            client.delete_entity(entity_id=self.entity.id,
                                 entity_type=self.entity.type)

    @unittest.skip('Does currently not work in CI')
    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                cb_url=settings.CB_URL)
    def test_subscriptions(self):
        """
        Test subscription operations of context broker client
        """
        with ContextBrokerClient(
                url=settings.CB_URL,
                fiware_header=self.fiware_header) as client:
            sub_id = client.post_subscription(subscription=self.subscription,
                                              skip_initial_notification=True)
            sub_res = client.get_subscription(subscription_id=sub_id)
            time.sleep(1)
            sub_update = sub_res.copy(
                update={'expires': datetime.now() + timedelta(days=1)})
            client.update_subscription(subscription=sub_update)
            sub_res_updated = client.get_subscription(subscription_id=sub_id)
            self.assertNotEqual(sub_res.expires, sub_res_updated.expires)
            self.assertEqual(sub_res.id, sub_res_updated.id)
            self.assertGreaterEqual(sub_res_updated.expires, sub_res.expires)

            # test duplicate prevention and update
            sub = self.subscription.copy()
            id1 = client.post_subscription(sub)
            sub_first_version = client.get_subscription(id1)
            sub.description = "This subscription shall not pass"

            id2 = client.post_subscription(sub, update=False)
            self.assertEqual(id1, id2)
            sub_second_version = client.get_subscription(id2)
            self.assertEqual(sub_first_version.description,
                             sub_second_version.description)

            id2 = client.post_subscription(sub, update=True)
            self.assertEqual(id1, id2)
            sub_second_version = client.get_subscription(id2)
            self.assertNotEqual(sub_first_version.description,
                                sub_second_version.description)

            # test that duplicate prevention does not prevent to much
            sub2 = self.subscription.copy()
            sub2.description = "Take this subscription to Fiware"
            sub2.subject.entities[0] = {
                "idPattern": ".*",
                "type": "Building"
            }
            id3 = client.post_subscription(sub2)
            self.assertNotEqual(id1, id3)

            # test get subscriptions by entity
            sub3 = client.get_subscription_by_entity("test", "Building")
            self.assertGreater(len(sub3), 0)

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                cb_url=settings.CB_URL,
                iota_url=settings.IOTA_JSON_URL)
    def test_subscription_set_status(self):
        """
        Test subscription operations of context broker client
        """
        sub = self.subscription.copy(
            update={'expires': datetime.now() + timedelta(days=1)})
        with ContextBrokerClient(
                url=settings.CB_URL,
                fiware_header=self.fiware_header) as client:
            sub_id = client.post_subscription(subscription=sub)
            sub_res = client.get_subscription(subscription_id=sub_id)
            self.assertEqual(sub_res.status, Status.ACTIVE)

            sub_inactive = sub_res.copy(update={'status': Status.INACTIVE})
            client.update_subscription(subscription=sub_inactive)
            sub_res_inactive = client.get_subscription(subscription_id=sub_id)
            self.assertEqual(sub_res_inactive.status, Status.INACTIVE)

            sub_active = sub_res_inactive.copy(update={'status': Status.ACTIVE})
            client.update_subscription(subscription=sub_active)
            sub_res_active = client.get_subscription(subscription_id=sub_id)
            self.assertEqual(sub_res_active.status, Status.ACTIVE)

            sub_expired = sub_res_active.copy(
                update={'expires': datetime.now() - timedelta(days=365)})
            client.update_subscription(subscription=sub_expired)
            sub_res_expired = client.get_subscription(subscription_id=sub_id)
            self.assertEqual(sub_res_expired.status, Status.EXPIRED)

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                cb_url=settings.CB_URL,
                iota_url=settings.IOTA_JSON_URL)
    def test_mqtt_subscriptions(self):
        mqtt_url = settings.MQTT_BROKER_URL
        mqtt_topic = ''.join([settings.FIWARE_SERVICE,
                              settings.FIWARE_SERVICEPATH])
        notification = self.subscription.notification.copy(
            update={'http': None, 'mqtt': Mqtt(url=mqtt_url,
                                               topic=mqtt_topic)})
        subscription = self.subscription.copy(
            update={'notification': notification,
                    'description': 'MQTT test subscription',
                    'expires': None})
        entity = ContextEntity(id='myID', type='Room', **self.attr)

        self.client.post_entity(entity=entity)
        sub_id = self.client.post_subscription(subscription)

        sub_message = None

        def on_connect(client, userdata, flags, reasonCode, properties=None):
            if reasonCode != 0:
                logger.error(f"Connection failed with error code: "
                             f"'{reasonCode}'")
                raise ConnectionError
            else:
                logger.info("Successfully, connected with result code " + str(
                    reasonCode))
            client.subscribe(mqtt_topic)

        def on_subscribe(client, userdata, mid, granted_qos, properties=None):
            logger.info("Successfully subscribed to with QoS: %s", granted_qos)

        def on_message(client, userdata, msg):
            logger.info(msg.topic + " " + str(msg.payload))
            nonlocal sub_message
            sub_message = Message.parse_raw(msg.payload)

        def on_disconnect(client, userdata, reasonCode, properties=None):
            logger.info("MQTT client disconnected with reasonCode "
                        + str(reasonCode))

        import paho.mqtt.client as mqtt
        mqtt_client = mqtt.Client(userdata=None,
                                  protocol=mqtt.MQTTv5,
                                  transport="tcp")
        # add our callbacks to the client
        mqtt_client.on_connect = on_connect
        mqtt_client.on_subscribe = on_subscribe
        mqtt_client.on_message = on_message
        mqtt_client.on_disconnect = on_disconnect

        # connect to the server
        mqtt_url = urlparse(mqtt_url)
        mqtt_client.connect(host=mqtt_url.hostname,
                            port=mqtt_url.port,
                            keepalive=60,
                            bind_address="",
                            bind_port=0,
                            clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY,
                            properties=None)

        # create a non-blocking thread for mqtt communication
        mqtt_client.loop_start()
        new_value = 50

        self.client.update_attribute_value(entity_id=entity.id,
                                           attr_name='temperature',
                                           value=new_value,
                                           entity_type=entity.type)
        time.sleep(5)

        # test if the subscriptions arrives and the content aligns with updates
        self.assertIsNotNone(sub_message)
        self.assertEqual(sub_id, sub_message.subscriptionId)
        self.assertEqual(new_value, sub_message.data[0].temperature.value)
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        time.sleep(1)

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                cb_url=settings.CB_URL)
    def test_batch_operations(self):
        """
        Test batch operations of context broker client
        """
        with ContextBrokerClient(
                url=settings.CB_URL,
                fiware_header=self.fiware_header) as client:
            entities = [ContextEntity(id=str(i),
                                      type=f'filip:object:TypeA') for i in
                        range(0, 1000)]
            client.update(entities=entities, action_type=ActionType.APPEND)
            entities = [ContextEntity(id=str(i),
                                      type=f'filip:object:TypeB') for i in
                        range(0, 1000)]
            client.update(entities=entities, action_type=ActionType.APPEND)
            entity = EntityPattern(idPattern=".*", typePattern=".*TypeA$")
            query = Query.parse_obj(
                {"entities": [entity.dict(exclude_unset=True)]})
            self.assertEqual(1000,
                             len(client.query(query=query,
                                              response_format='keyValues')))

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                cb_url=settings.CB_URL,
                iota_url=settings.IOTA_JSON_URL)
    def test_command_with_mqtt(self):
        """
        Test if a command can be send to a device in FIWARE

        To test this a virtual device is created and provisioned to FIWARE and
        a hosted MQTT Broker

        This test only works if the address of a running MQTT Broker is given in
        the environment ('MQTT_BROKER_URL')

        The main part of this test was taken out of the iot_mqtt_example, see
        there for a complete documentation
        """
        mqtt_broker_url = settings.MQTT_BROKER_URL

        device_attr1 = DeviceAttribute(name='temperature',
                                       object_id='t',
                                       type="Number",
                                       metadata={
                                           "unit":
                                               {"type": "Unit",
                                                "value": {
                                                    "name": {
                                                        "type": "Text",
                                                        "value": "degree "
                                                                 "Celsius"
                                                    }
                                                }}
                                       })

        # creating a static attribute that holds additional information
        static_device_attr = StaticDeviceAttribute(name='info',
                                                   type="Text",
                                                   value="Filip example for "
                                                         "virtual IoT device")
        # creating a command that the IoT device will liston to
        device_command = DeviceCommand(name='heater', type="Boolean")

        device = Device(device_id='MyDevice',
                        entity_name='MyDevice',
                        entity_type='Thing2',
                        protocol='IoTA-JSON',
                        transport='MQTT',
                        apikey=settings.FIWARE_SERVICEPATH.strip('/'),
                        attributes=[device_attr1],
                        static_attributes=[static_device_attr],
                        commands=[device_command])

        device_attr2 = DeviceAttribute(name='humidity',
                                       object_id='h',
                                       type="Number",
                                       metadata={
                                           "unitText":
                                               {"value": "percent",
                                                "type": "Text"}})

        device.add_attribute(attribute=device_attr2)

        # Send device configuration to FIWARE via the IoT-Agent. We use the
        # general ngsiv2 httpClient for this.
        service_group = ServiceGroup(
            service=self.fiware_header.service,
            subservice=self.fiware_header.service_path,
            apikey=settings.FIWARE_SERVICEPATH.strip('/'),
            resource='/iot/json')

        # create the Http client node that once sent the device cannot be posted
        # again and you need to use the update command
        config = HttpClientConfig(cb_url=settings.CB_URL,
                                  iota_url=settings.IOTA_JSON_URL)
        client = HttpClient(fiware_header=self.fiware_header, config=config)
        client.iota.post_group(service_group=service_group, update=True)
        client.iota.post_device(device=device, update=True)

        time.sleep(0.5)

        # check if the device is correctly configured. You will notice that
        # unfortunately the iot API does not return all the metadata. However,
        # it will still appear in the context-entity
        device = client.iota.get_device(device_id=device.device_id)

        # check if the data entity is created in the context broker
        entity = client.cb.get_entity(entity_id=device.device_id,
                                      entity_type=device.entity_type)

        # create a mqtt client that we use as representation of an IoT device
        # following the official documentation of Paho-MQTT.
        # https://www.eclipse.org/paho/index.php?page=clients/python/
        # docs/index.php

        # The callback for when the mqtt client receives a CONNACK response from
        # the server. All callbacks need to have this specific arguments,
        # Otherwise the client will not be able to execute them.
        def on_connect(client, userdata, flags, reasonCode, properties=None):
            client.subscribe(f"/{device.apikey}/{device.device_id}/cmd")

        # Callback when the command topic is succesfully subscribed
        def on_subscribe(client, userdata, mid, granted_qos, properties=None):
            pass

        # NOTE: We need to use the apikey of the service-group to send the
        # message to the platform
        def on_message(client, userdata, msg):
            data = json.loads(msg.payload)
            res = {k: v for k, v in data.items()}
            client.publish(topic=f"/json/{service_group.apikey}"
                                 f"/{device.device_id}/cmdexe",
                           payload=json.dumps(res))

        def on_disconnect(client, userdata, reasonCode, properties=None):
            pass

        mqtt_client = mqtt.Client(client_id="filip-test",
                                  userdata=None,
                                  protocol=mqtt.MQTTv5,
                                  transport="tcp")

        # add our callbacks to the client
        mqtt_client.on_connect = on_connect
        mqtt_client.on_subscribe = on_subscribe
        mqtt_client.on_message = on_message
        mqtt_client.on_disconnect = on_disconnect

        # extract the form the environment
        mqtt_broker_url = urlparse(mqtt_broker_url)

        mqtt_client.connect(host=mqtt_broker_url.hostname,
                            port=mqtt_broker_url.port,
                            keepalive=60,
                            bind_address="",
                            bind_port=0,
                            clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY,
                            properties=None)
        # create a non-blocking thread for mqtt communication
        mqtt_client.loop_start()

        for attr in device.attributes:
            mqtt_client.publish(
                topic=f"/json/{service_group.apikey}/{device.device_id}/attrs",
                payload=json.dumps({attr.object_id: random.randint(0, 9)}))

        time.sleep(5)
        entity = client.cb.get_entity(entity_id=device.device_id,
                                      entity_type=device.entity_type)

        # create and send a command via the context broker
        context_command = NamedCommand(name=device_command.name,
                                       value=False)
        client.cb.post_command(entity_id=entity.id,
                               entity_type=entity.type,
                               command=context_command)

        time.sleep(5)
        # check the entity the command attribute should now show OK
        entity = client.cb.get_entity(entity_id=device.device_id,
                                      entity_type=device.entity_type)

        # The main part of this test, for all this setup was done
        self.assertEqual("OK", entity.heater_status.value)

        # close the mqtt listening thread
        mqtt_client.loop_stop()
        # disconnect the mqtt device
        mqtt_client.disconnect()

    def test_patch_entity(self) -> None:
        """
        Test the methode: patch_entity
        Returns:
           None
        """

        # setup test-entity
        entity = ContextEntity(id="test_id1", type="test_type1")
        attr1 = NamedContextAttribute(name="attr1", value="1")
        attr1.metadata["m1"] = \
            NamedMetadata(name="meta1", type="metatype", value="2")
        attr2 = NamedContextAttribute(name="attr2", value="2")
        attr1.metadata["m2"] = \
            NamedMetadata(name="meta2", type="metatype", value="3")
        entity.add_attributes([attr1, attr2])

        # sub-Test1: Post new
        self.client.patch_entity(entity=entity)
        self.assertEqual(entity,
                         self.client.get_entity(entity_id=entity.id))
        self.tearDown()

        # sub-Test2: ID/type of old_entity changed
        self.client.post_entity(entity=entity)
        test_entity = ContextEntity(id="newID", type="newType")
        test_entity.add_attributes([attr1, attr2])
        self.client.patch_entity(test_entity, old_entity=entity)
        self.assertEqual(test_entity,
                         self.client.get_entity(entity_id=test_entity.id))
        self.assertRaises(RequestException, self.client.get_entity,
                          entity_id=entity.id)
        self.tearDown()

        # sub-Test3: a non valid old_entity is provided, entity exists
        self.client.post_entity(entity=entity)
        old_entity = ContextEntity(id="newID", type="newType")

        self.client.patch_entity(entity, old_entity=old_entity)
        self.assertEqual(entity, self.client.get_entity(entity_id=entity.id))
        self.tearDown()

        # sub-Test4: no old_entity provided, entity is new
        old_entity = ContextEntity(id="newID", type="newType")
        self.client.patch_entity(entity, old_entity=old_entity)
        self.assertEqual(entity, self.client.get_entity(entity_id=entity.id))
        self.tearDown()

        # sub-Test5: no old_entity provided, entity is new
        old_entity = ContextEntity(id="newID", type="newType")
        self.client.patch_entity(entity, old_entity=old_entity)
        self.assertEqual(entity, self.client.get_entity(entity_id=entity.id))
        self.tearDown()

        # sub-Test6: New attr, attr del, and attr changed. No Old_entity given
        self.client.post_entity(entity=entity)
        test_entity = ContextEntity(id="test_id1", type="test_type1")
        attr1_changed = NamedContextAttribute(name="attr1", value="2")
        attr1_changed.metadata["m4"] = \
            NamedMetadata(name="meta3", type="metatype5", value="4")
        attr3 = NamedContextAttribute(name="attr3", value="3")
        test_entity.add_attributes([attr1_changed, attr3])
        self.client.patch_entity(test_entity)

        self.assertEqual(test_entity,
                         self.client.get_entity(entity_id=entity.id))
        self.tearDown()

        # sub-Test7: Attr changes, concurrent changes in Fiware,
        #            old_entity given

        self.client.post_entity(entity=entity)

        concurrent_entity = ContextEntity(id="test_id1", type="test_type1")
        attr1_changed = copy.deepcopy(attr1)
        attr1_changed.metadata["m1"].value = "3"
        attr1_changed.value = "4"
        concurrent_entity.add_attributes([attr1_changed, attr2])
        self.client.patch_entity(concurrent_entity)

        user_entity = copy.deepcopy(entity)
        attr3 = NamedContextAttribute(name="attr3", value="3")
        user_entity.add_attributes([attr3])
        self.client.patch_entity(user_entity, old_entity=entity)

        result_entity = concurrent_entity
        result_entity.add_attributes([attr2, attr3])

        self.assertEqual(result_entity,
                         self.client.get_entity(entity_id=entity.id))
        self.tearDown()

    def tearDown(self) -> None:
        """
        Cleanup test server
        """
        self.client.close()
        clear_all(fiware_header=self.fiware_header,
                  cb_url=settings.CB_URL,
                  iota_url=settings.IOTA_JSON_URL)