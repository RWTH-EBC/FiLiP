import unittest
import requests
from uuid import uuid4
from filip.core.models import FiwareHeader
from filip.iota.client import IoTAClient
from filip.iota.models import ServiceGroup, Device


class TestAgent(unittest.TestCase):
    def setUp(self) -> None:
        self.device = {
            "device_id": "saf",
            "service": None,
            "service_path": "/",
            "entity_name": "saf",
            "entity_type": "all",
            "timezone": 'Europe/Berlin',
            "timestamp": None,
            "apikey": "1234",
            "endpoint": None,
            "protocol": None,
            "transport": None,
            "lazy": None,
            "commands": None,
            "attributes": None,
            "static_attributes": None,
            "internal_attributes": None,
            "expressionLanguage": None,
            "explicitAttrs": None,
            "ngsiVersion": None
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
        device = Device(**self.device)
        self.assertEqual(device.dict(), self.device)

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
        self.assertEqual(device.dict(), self.device)

    def test_device_endpoints(self):
        fiware_header = FiwareHeader(service='filip',
                                     service_path='/testing')
        with IoTAClient(fiware_header=fiware_header) as client:
            # Todo: Add device creation in scope
            client.get_device_list()

    def tearDown(self) -> None:
        self.client.close()

