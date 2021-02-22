import unittest
import requests
from unittest.mock import Mock, patch
from uuid import uuid4
from core import FiwareHeader
from iota import IoTAClient, models

class TestClient(unittest.TestCase):
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
        self.fiware_header = FiwareHeader(service='filip', path='/testing')
        self.service = models.Service(service='filip',
                                      subservice='/testing',
                                      entity_type='Thing',
                                      resource='/iot/json',
                                      apikey=str(uuid4()))
        self.client = IoTAClient(fiware_header=self.fiware_header)

    def test_device_model(self):
        device = models.Device(**self.device)
        self.assertEqual(device.dict(), self.device)

    def test_get_version(self):
        res = self.client.get_version()
        if res:
            print(res)

    def test_service_endpoints(self):
        self.client.post_service(service=self.service)
        services = self.client.get_services()
        print(services)
        service = self.client.get_service(resource=self.service.resource,
                                          apikey=self.service.apikey)
        print(service.json(indent=2))
        self.client.delete_service(resource=service.resource,
                                   apikey=service.apikey)

    def test_device_endpoints(self):
        devices = self.client.get_devices()
        for device in devices:
            print(device.json(indent=2, exclude_defaults=True))

    def test_get_device(self):
        res = requests.get('http://jsonplaceholder.typicode.com/todos')
        self.assertTrue(res.ok)