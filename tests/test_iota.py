import unittest

import requests
from uuid import uuid4

from filip.core.models import FiwareHeader
from filip.iota.client import IoTAClient
from filip.iota.models import ServiceGroup, \
    Device, \
    DeviceAttribute, \
    DeviceCommand, \
    LazyDeviceAttribute, \
    StaticDeviceAttribute
from filip.cb.client import ContextBrokerClient
from filip.cb.models import ContextEntity


class TestAgent(unittest.TestCase):
    def setUp(self) -> None:
        self.device = {
            "device_id": "test_device",
            "service": None,
            "service_path": "/",
            "entity_name": "test_entity",
            "entity_type": "test_entity_type",
            "timezone": 'Europe/Berlin',
            "timestamp": None,
            "apikey": "1234",
            "endpoint": None,
            "transport": 'HTTP',
            "internal_attributes": None,
            "expressionLanguage": None
        }
        self.fiware_header = FiwareHeader(service='filip',
                                          service_path='/testing')
        self.service_group1 = ServiceGroup(entity_type='Thing',
                                           resource='/iot/json',
                                           apikey=str(uuid4()))
        self.service_group2 = ServiceGroup(entity_type='OtherThing',
                                           resource='/iot/json',
                                           apikey=str(uuid4()))
        self.client = IoTAClient(fiware_header=self.fiware_header)

    def test_get_version(self):
        with IoTAClient(fiware_header=self.fiware_header) as client:
            self.assertIsNotNone(client.get_version())

    def test_service_group_model(self):
        pass

    def test_service_group_endpoints(self):
        self.client.post_groups(service_groups=[self.service_group1,
                                                self.service_group2])
        groups = self.client.get_group_list()
        with self.assertRaises(requests.RequestException):
            self.client.post_groups(groups, update=False)

        self.client.get_group(resource=self.service_group1.resource,
                              apikey=self.service_group1.apikey)
        for gr in groups:
            self.client.delete_group(resource=gr.resource,
                                     apikey=gr.apikey)

    def test_device_model(self):
        device = Device(**self.device)
        self.assertEqual(self.device,
                         device.dict(exclude_unset=True))

    def test_device_endpoints(self):
        """
        Test device creation
        """
        fiware_header = FiwareHeader(service='filip',
                                     service_path='/testing')
        with IoTAClient(fiware_header=fiware_header) as client:
            client.get_device_list()
            device = Device(**self.device)

            attr = DeviceAttribute(name='temperature',
                                   object_id='t',
                                   type='Number',
                                   entity_name='test')
            attr_command = DeviceCommand(name='open')
            attr_lazy = LazyDeviceAttribute(name='pressure',
                                            object_id='p',
                                            type='Text',
                                            entity_name='pressure')
            attr_static = StaticDeviceAttribute(name='hasRoom',
                                                type='Relationship',
                                                value='my_partner_id')
            device.add_attribute(attr)
            device.add_attribute(attr_command)
            device.add_attribute(attr_lazy)
            device.add_attribute(attr_static)

            client.post_device(device=device)
            device_res = client.get_device(device_id=device.device_id)
            self.assertEqual(device.dict(exclude={'service',
                                                  'service_path',
                                                  'timezone'}),
                             device_res.dict(exclude={'service',
                                                      'service_path',
                                                      'timezone'}))
            self.assertEqual(self.fiware_header.service, device_res.service)
            self.assertEqual(self.fiware_header.service_path,
                             device_res.service_path)

    def test_metadata(self):
        """
        Test for metadata works but the api of iot agent-json seems not
        working correctly
        Returns:
            None
        """
        metadata = {"accuracy": {"type": "Text",
                                 "value": "+-5%"}}
        attr = DeviceAttribute(name="temperature",
                               object_id="temperature",
                               type="Number",
                               metadata=metadata)
        device = Device(**self.device)
        device.device_id = "device_with_meta"
        device.add_attribute(attribute=attr)
        print(device.json(indent=2))
        fiware_header = FiwareHeader(service='filip',
                                     service_path='/testing')

        with IoTAClient(fiware_header=fiware_header) as client:
            client.post_device(device=device)
            print(client.get_device(device_id=device.device_id).json(
                indent=2, exclude_unset=True))

        with ContextBrokerClient(fiware_header=fiware_header) as client:
            print(client.get_entity(entity_id=device.entity_name).json(
                indent=2))


    def tearDown(self) -> None:
        """
        Cleanup test server
        """
        try:
            devices = self.client.get_device_list()
            for device in devices:
                self.client.delete_device(device_id=device.device_id)
            with ContextBrokerClient(fiware_header=self.fiware_header) as \
                    client:

                entities = [ContextEntity(id=entity.id, type=entity.type) for
                            entity in client.get_entity_list()]
                client.update(entities=entities, action_type='delete')

        except requests.RequestException:
            pass
        self.client.close()
