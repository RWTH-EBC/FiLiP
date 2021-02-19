import unittest
# Third-party imports...
import requests
from unittest.mock import Mock, patch
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
        self.client = IoTAClient()

    def test_device_model(self):
        device = models.Device(**self.device)
        self.assertEqual(device.dict(), self.device)

    def test_get_version(self):
        res = self.client.get_version()
        if res is not None:
            print(type(res.json()))

    def test_device_endpoints(self):
        self.client.post_devices()

    def test_get_device(self):
        res = requests.get('http://jsonplaceholder.typicode.com/todos')
        self.assertTrue(res.ok)