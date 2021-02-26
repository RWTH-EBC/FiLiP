import unittest
from unittest.mock import Mock, patch
from core.models import FiwareHeader
from cb.client import ContextBrokerClient

class TestContextBroker(unittest.TestCase):
    def setUp(self) -> None:
        self.resources = {
            "entities_url": "/v2/entities",
            "types_url": "/v2/types",
            "subscriptions_url": "/v2/subscriptions",
            "registrations_url": "/v2/registrations"
        }


        self.fiware_header = FiwareHeader(service='filip',
                                          service_path='/testing')

        self.client = ContextBrokerClient(fiware_header=self.fiware_header)

    def test_management_endpoints(self):
        with ContextBrokerClient(fiware_header=self.fiware_header) as client:
            self.assertIsNotNone(client.get_version())
            self.assertEqual(client.get_resources(), self.resources)

    def test_statistics(self):
        with ContextBrokerClient(fiware_header=self.fiware_header) as client:
            self.assertIsNotNone(client.get_statistics())



    def tearDown(self) -> None:
        self.client.close()
