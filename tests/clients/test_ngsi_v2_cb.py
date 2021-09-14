"""
Tests for filip.cb.client
"""
import unittest
import logging
import time
import random
from datetime import datetime
from requests import RequestException
from filip.models.base import FiwareHeader, DataType
from filip.utils.simple_ql import QueryString
from filip.clients.ngsi_v2 import ContextBrokerClient, IoTAClient
from filip.models.ngsi_v2.context import \
    AttrsFormat, \
    ContextEntity, \
    ContextAttribute, \
    NamedContextAttribute, \
    NamedCommand, \
    Subscription, \
    Query, \
    Entity, \
    ActionType


# Setting up logging
logging.basicConfig(
    level='ERROR',
    format='%(asctime)s %(name)s %(levelname)s: %(message)s')


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
        self.resources = {
            "entities_url": "/v2/entities",
            "types_url": "/v2/types",
            "subscriptions_url": "/v2/subscriptions",
            "registrations_url": "/v2/registrations"
        }
        self.attr = {'temperature': {'value': 20.0,
                                     'type': 'Number'}}
        self.entity = ContextEntity(id='MyId', type='MyType', **self.attr)
        self.fiware_header = FiwareHeader(service='filip',
                                          service_path='/testing')

        self.client = ContextBrokerClient(fiware_header=self.fiware_header)


    def test_management_endpoints(self):
        """
        Test management functions of context broker client
        """
        with ContextBrokerClient(fiware_header=self.fiware_header) as client:
            self.assertIsNotNone(client.get_version())
            self.assertEqual(client.get_resources(), self.resources)

    def test_statistics(self):
        """
        Test statistics of context broker client
        """
        with ContextBrokerClient(fiware_header=self.fiware_header) as client:
            self.assertIsNotNone(client.get_statistics())

    def test_pagination(self):
        """
        Test pagination of context broker client
        Test pagination. only works if enough entities are available
        """
        fiware_header = FiwareHeader(service='filip',
                                     service_path='/testing')
        with ContextBrokerClient(fiware_header=fiware_header) as client:
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

            client.update(action_type=ActionType.DELETE, entities=entities_a)
            client.update(action_type=ActionType.DELETE, entities=entities_b)

    def test_entity_filtering(self):
        """
        Test filter operations of context broker client
        """

        with ContextBrokerClient(fiware_header=self.fiware_header) as client:
            print(client.session.headers)
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

    def test_entity_operations(self):
        """
        Test entity operations of context broker client
        """
        with ContextBrokerClient(fiware_header=self.fiware_header) as client:
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
            res_entity.add_properties({'pressure': ContextAttribute(
                type='Number', value=1050)})
            client.update_entity(entity=res_entity)
            self.assertEqual(client.get_entity(entity_id=self.entity.id),
                             res_entity)

    def test_attribute_operations(self):
        """
        Test attribute operations of context broker client
        """
        with ContextBrokerClient(fiware_header=self.fiware_header) as client:
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
            entity.add_properties([attr_txt,
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

            client.delete_entity(entity_id=entity.id)

    def test_type_operations(self):
        """
        Test type operations of context broker client
        """
        with ContextBrokerClient(fiware_header=self.fiware_header) as client:
            self.assertIsNotNone(client.post_entity(entity=self.entity,
                                                    update=True))
            client.get_entity_types()
            client.get_entity_types(options='count')
            client.get_entity_types(options='values')
            client.get_entity_type(entity_type='MyType')
            client.delete_entity(entity_id=self.entity.id)

    def test_subscriptions(self):
        """
        Test subscription operations of context broker client
        """
        with ContextBrokerClient(fiware_header=self.fiware_header) as client:
            sub_example = {
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
            }
            sub = Subscription(**sub_example)
            sub_id = client.post_subscription(subscription=sub)
            sub_res = client.get_subscription(subscription_id=sub_id)
            time.sleep(1)
            sub_update = sub_res.copy(update={'expires': datetime.now()})
            client.update_subscription(subscription=sub_update)
            sub_res_updated = client.get_subscription(subscription_id=sub_id)
            self.assertNotEqual(sub_res.expires, sub_res_updated.expires)
            self.assertEqual(sub_res.id, sub_res_updated.id)
            self.assertGreaterEqual(sub_res_updated.expires, sub_res.expires)
            subs = client.get_subscription_list()
            for sub in subs:
                client.delete_subscription(subscription_id=sub.id)

    def test_batch_operations(self):
        """
        Test batch operations of context broker client
        """
        fiware_header = FiwareHeader(service='filip',
                                     service_path='/testing')
        with ContextBrokerClient(fiware_header=fiware_header) as client:
            entities = [ContextEntity(id=str(i),
                                      type=f'filip:object:TypeA') for i in
                        range(0, 1000)]
            client.update(entities=entities, action_type=ActionType.APPEND)
            entities = [ContextEntity(id=str(i),
                                      type=f'filip:object:TypeB') for i in
                        range(0, 1000)]
            client.update(entities=entities, action_type=ActionType.APPEND)
            e = Entity(idPattern=".*", typePattern=".*TypeA$")
            q = Query.parse_obj({"entities": [e.dict(exclude_unset=True)]})
            self.assertEqual(1000,
                             len(client.query(query=q,
                                              response_format='keyValues')))

    @unittest.skip("Test does currently not work in the CI. Valid reachable "
                   "endpoint needed")
    def test_command(self) -> None:
        """
        test sending commands
        Returns:
            None
        """

        iota_client = IoTAClient(fiware_header=self.fiware_header)
        test_device_id = 'test_device'
        entity_id = 'test_entity_id'
        entity_type = 'Tester'
        command_name = 'com'

        # make sure device does not exist
        try:
            iota_client.delete_device(device_id=test_device_id)
        except RequestException:
            pass

        # Create a device entry
        iota_client = IoTAClient(fiware_header=self.fiware_header)
        from filip.models.ngsi_v2.iot import Device, DeviceCommand

        # use a public accessible endpoint; it only needs to return
        # HTTP-CODE-200
        device = Device(device_id=test_device_id,
                        service=self.fiware_header.service,
                        service_path=self.fiware_header.service_path,
                        entity_name=entity_id,
                        entity_type=entity_type,
                        transport='HTTP',
                        endpoint="https://httpbin.org/",
                        )

        device.add_attribute(
            DeviceCommand(
                name=command_name,
                type=DataType.STRUCTUREDVALUE,

            )
        )

        iota_client.post_device(device=device, update=False)

        time.sleep(2)
        cmd = NamedCommand(name=command_name, value='3')
        self.client.post_command(entity_id=entity_id, entity_type=entity_type,
                                 command=cmd)
        time.sleep(2)
        entity_after = self.client.get_entity(entity_id=entity_id)

        self.assertEqual(entity_after.com_status.value, "PENDING")

        # clean up device
        iota_client.delete_device(device_id=test_device_id)
        iota_client.close()

    def tearDown(self) -> None:
        """
        Cleanup test server
        """
        try:
            entities = [ContextEntity(id=entity.id, type=entity.type) for
                        entity in self.client.get_entity_list()]
            self.client.update(entities=entities, action_type='delete')
        except RequestException:
            pass

        self.client.close()

    def test_command_with_mqtt(self):

        import json
        import logging
        import random
        import time
        import paho.mqtt.client as mqtt

        from urllib.parse import urlparse

        from filip.models import FiwareHeader
        from filip.models.ngsi_v2.iot import \
            Device, \
            DeviceCommand, \
            DeviceAttribute, \
            ServiceGroup, \
            StaticDeviceAttribute
        from filip.models.ngsi_v2.context import NamedCommand
        from filip.clients.ngsi_v2 import HttpClient, HttpClientConfig
        from filip.config import settings
        import os

        # Setting up logging
        logging.basicConfig(
            level='INFO',
            format='%(asctime)s %(name)s %(levelname)s: %(message)s')
        logger = logging.getLogger('filip-testing')

        # Before running the example you should set some global variables
        CB_URL = settings.CB_URL
        IOTA_URL = settings.IOTA_URL
        MQTT_BROKER_URL = os.environ.get('MQTT_BROKER_URL')
        DEVICE_APIKEY = 'filip-iot-test-device'
        SERVICE_GROUP_APIKEY = 'filip-iot-test-service-group'

        # Since we want to use the multi-tenancy concept of fiware we always
        # start
        # with create a fiware header
        fiware_header = FiwareHeader(
            service=self.fiware_header.service,
            service_path=self.fiware_header.service_path)

        # First we create our device configuration using the models provided for
        # filip.models.ngsi_v2.iot

        # creating an attribute for incoming measurements from e.g. a sensor we
        # do add the metadata for units here using the unit models. You will
        # later notice that the library automatically will augment the provided
        # information about units.
        device_attr1 = DeviceAttribute(name='temperature',
                                       object_id='t',
                                       type="Number",
                                       metadata={"unit":
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

        # NOTE: You need to know that if you define an apikey for a single
        # device it will be only used for outgoing traffic.
        # This is does not become very clear in the official documentation.
        # https://fiware-iotagent-json.readthedocs.io/en/latest/
        # usermanual/index.html
        device = Device(device_id='MyDevice',
                        entity_name='MyDevice',
                        entity_type='Thing2',
                        protocol='IoTA-JSON',
                        transport='MQTT',
                        apikey=DEVICE_APIKEY,
                        attributes=[device_attr1],
                        static_attributes=[static_device_attr],
                        commands=[device_command])

        # You can also add additional attributes via the Device API
        device_attr2 = DeviceAttribute(name='humidity',
                                       object_id='h',
                                       type="Number",
                                       metadata={"unitText":
                                                     {"value": "percent",
                                                      "type": "Text"}})

        device.add_attribute(attribute=device_attr2)

        # This will print our configuration that we will send
        logger.info(
            "This is our device configuration: \n" + device.json(indent=2))

        # Send device configuration to FIWARE via the IoT-Agent. We use the
        # general ngsiv2 httpClient for this.

        # NOTE: This is important in order to adjust the apikey for
        # incoming traffic.
        service_group = ServiceGroup(service=fiware_header.service,
                                     subservice=fiware_header.service_path,
                                     apikey=SERVICE_GROUP_APIKEY,
                                     resource='/iot/json')

        # create the Http client node that once sent the device cannot be posted
        # again and you need to use the update command
        config = HttpClientConfig(cb_url=CB_URL, iota_url=IOTA_URL)
        client = HttpClient(fiware_header=fiware_header, config=config)
        client.iota.post_group(service_group=service_group, update=True)
        client.iota.post_device(device=device, update=True)

        time.sleep(0.5)

        # check if the device is correctly configured. You will notice that
        # unfortunately the iot API does not return all the metadata. However,
        # it will still appear in the context-entity
        device = client.iota.get_device(device_id=device.device_id)
        logger.info(f"{device.json(indent=2)}")

        # check if the data entity is created in the context broker
        entity = client.cb.get_entity(entity_id=device.device_id,
                                      entity_type=device.entity_type)
        logger.info("This is our data entity belonging to our device: \n" +
                    entity.json(indent=2))

        # create a mqtt client that we use as representation of an IoT device
        # following the official documentation of Paho-MQTT.
        # https://www.eclipse.org/paho/index.php?page=clients/python/
        # docs/index.php

        # The callback for when the mqtt client receives a CONNACK response from
        # the server. All callbacks need to have this specific arguments,
        # Otherwise the client will not be able to execute them.
        def on_connect(client, userdata, flags, reasonCode, properties=None):
            if reasonCode != 0:
                logger.error(
                    f"Connection failed with error code: '{reasonCode}'")
            else:
                logger.info("Successfully, connected with result code " + str(
                    reasonCode))
            # Subscribing in on_connect() means that if we lose the connection
            # and reconnect then subscriptions will be renewed.
            # We do subscribe to the topic that the platfrom will publish our
            # commands on
            client.subscribe(f"/{device.apikey}/{device.device_id}/cmd")

        # Callback when the command topic is succesfully subscribed
        def on_subscribe(client, userdata, mid, granted_qos, properties=None):
            logger.info("Successfully subscribed to with QoS: %s", granted_qos)

        # The callback for when the device receives a PUBLISH  message like a command
        # from the server. Here, the received command will be printed and an
        # command-acknowledge will be sent to the platform.

        # NOTE: We need to use the apikey of the service-group to send the message to
        # the platform
        def on_message(client, userdata, msg):
            logger.info(msg.topic + " " + str(msg.payload))
            data = json.loads(msg.payload)
            res = {k: v for k, v in data.items()}
            client.publish(topic=f"/json/{service_group.apikey}"
                                 f"/{device.device_id}/cmdexe",
                           payload=json.dumps(res))

        def on_disconnect(client, userdata, reasonCode):
            logger.info("MQTT client disconnected" + str(reasonCode))

        mqtt_client = mqtt.Client(client_id="filip-iot-example",
                                  userdata=None,
                                  protocol=mqtt.MQTTv5,
                                  transport="tcp")
        # add our callbacks to the client
        mqtt_client.on_connect = on_connect
        mqtt_client.on_subscribe = on_subscribe
        mqtt_client.on_message = on_message
        mqtt_client.on_disconnect = on_disconnect
        # connect to the server
        print("------------------------------------------")
        print(MQTT_BROKER_URL)
        mqtt_url = urlparse(MQTT_BROKER_URL)
        print(mqtt_url)
        mqtt_client.connect(host=mqtt_url.hostname,
                            port=mqtt_url.port,
                            keepalive=60,
                            bind_address="",
                            bind_port=0,
                            clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY,
                            properties=None)
        # create a non-blocking thread for mqtt communication
        mqtt_client.loop_start()

        for attr in device.attributes:
            payload = json.dumps({attr.object_id: random.randint(0, 9)})
            logger.info("Send data to platform:" + payload)
            mqtt_client.publish(
                topic=f"/json/{service_group.apikey}/{device.device_id}/attrs",
                payload=json.dumps({attr.object_id: random.randint(0, 9)}))

        time.sleep(1)
        entity = client.cb.get_entity(entity_id=device.device_id,
                                      entity_type=device.entity_type)
        logger.info("This is updated entity status after measurements are "
                    "received: \n" + entity.json(indent=2))

        # create and send a command via the context broker
        context_command = NamedCommand(name=device_command.name,
                                       value=False)
        client.cb.post_command(entity_id=entity.id,
                               entity_type=entity.type,
                               command=context_command)

        time.sleep(1)
        # check the entity the command attribute should now show the PENDING
        entity = client.cb.get_entity(entity_id=device.device_id,
                                      entity_type=device.entity_type)

        self.assertEqual(entity.heater_status.value, "PENDING")


        # close the mqtt listening thread
        mqtt_client.loop_stop()
        # disconnect the mqtt device
        mqtt_client.disconnect()

        # cleanup the server and delete everything
        client.iota.delete_device(device_id=device.device_id)
        client.iota.delete_group(resource=service_group.resource,
                                 apikey=service_group.apikey)
        client.cb.delete_entity(entity_id=entity.id,
                                entity_type=entity.type)
