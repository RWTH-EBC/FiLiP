import unittest
import requests
from unittest.mock import Mock, patch
from uuid import uuid4
from core import FiwareHeader
from iota import Agent, models

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
        self.service_group = models.ServiceGroup(entity_type='Thing',
                                                 resource='/iot/json',
                                                 apikey=str(uuid4()))
        self.service_group = models.ServiceGroup(entity_type='OtherThing',
                                                 resource='/iot/json',
                                                 apikey=str(uuid4()))
        self.client = Agent(fiware_header=self.fiware_header)

    def test_device_model(self):
        device = models.Device(**self.device)
        self.assertEqual(device.dict(), self.device)

    def test_get_version(self):
        self.assertIsNotNone(self.client.get_version())

    def test_service_group_endpoints(self):
        self.client.post_group(service_group=self.service_group)
        groups = self.client.get_groups()
        group = self.client.get_group(resource=self.service_group.resource,
                                        apikey=self.service_group.apikey)
        self.client.delete_group(resource=group.resource,
                                   apikey=group.apikey)

    def test_device_endpoints(self):
        devices = self.client.get_devices()
        for device in devices:
            print(device.json(indent=2, exclude_defaults=True))

