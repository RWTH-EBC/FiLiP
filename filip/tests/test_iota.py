import unittest
from unittest.mock import Mock, patch
from uuid import uuid4
from core.models import FiwareHeader
from iota.client import IoTAClient
from iota.models import ServiceGroup, Device


class TestAgent(unittest.TestCase):
    def setUp(self) -> None:
        self.device = {
            "device_id": "saf",
            "service_group": None,
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
        groups = self.client.get_groups()
        self.assertEqual(self.client.post_groups(groups, update=False), None)

        group = self.client.get_group(resource=self.service_group1.resource,
                                        apikey=self.service_group1.apikey)
        for gr in groups:
            self.client.delete_group(resource=gr.resource,
                                     apikey=gr.apikey)

    def test_device_model(self):
        device = Device(**self.device)
        self.assertEqual(device.dict(), self.device)

    def test_device_endpoints(self):
        devices = self.client.get_devices()
        for device in devices:
            print(device.json(indent=2, exclude_defaults=True))

    def tearDown(self) -> None:
        self.client.close()

