"""
Tests clear functions in filip.utils.cleanup
"""
import random
import unittest
from datetime import datetime
from uuid import uuid4

from filip.clients.ngsi_v2 import ContextBrokerClient, IoTAClient, QuantumLeapClient
from filip.models.base import FiwareHeader
from filip.models.ngsi_v2.context import ContextEntity
from filip.models.ngsi_v2.iot import Device, ServiceGroup
from filip.models.ngsi_v2.subscriptions import Subscription
from filip.utils.cleanup import clear_context_broker, clear_iot_agent
from tests.config import settings


class TestClearFunctions(unittest.TestCase):

    def setUp(self) -> None:
        """
        Setup test data and clients

        Returns:
            None
        """
        self.fiware_header = FiwareHeader(
            service=settings.FIWARE_SERVICE,
            service_path=settings.FIWARE_SERVICEPATH)
        self.cb_url = settings.CB_URL
        self.cb_client = ContextBrokerClient(url=self.cb_url,
                                             fiware_header=self.fiware_header)
        self.iota_url = settings.IOTA_URL
        self.iota_client = IoTAClient(url=self.iota_url,
                                      fiware_header=self.fiware_header)

        self.ql_url = settings.QL_URL
        self.ql_client = QuantumLeapClient(url=self.ql_url, fiware_header=self.fiware_header)

    def test_clear_context_broker(self):
        """
        Test for clearing context broker using context broker client
        """
        entity = ContextEntity(id=str(random.randint(1, 50)),
                               type=f'filip:object:Type')
        self.cb_client.post_entity(entity=entity)
        subscription = Subscription.model_validate({
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
        self.cb_client.post_subscription(subscription=subscription)
        clear_context_broker(cb_client=self.cb_client)

        self.assertEqual(0, len(self.cb_client.get_entity_list()) or len(self.cb_client.get_subscription_list()))

    def test_clear_context_broker_with_url(self):
        """
        Test for clearing context broker using context broker url and fiware header as parameters
        """
        entity = ContextEntity(id=str(random.randint(1, 50)),
                               type=f'filip:object:Type')
        self.cb_client.post_entity(entity=entity)
        subscription = Subscription.model_validate({
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
        self.cb_client.post_subscription(subscription=subscription)
        clear_context_broker(url=self.cb_url, fiware_header=self.fiware_header)

        self.assertEqual(0, len(self.cb_client.get_entity_list()) or len(self.cb_client.get_entity_list()))

    def test_clear_iot_agent(self):
        """
        Test for clearing iota using iota client
        """
        service_group = ServiceGroup(entity_type='Thing',
                                     resource='/iot/json',
                                     apikey=str(uuid4()))
        device = {
            "device_id": "test_device",
            "service": self.fiware_header.service,
            "service_path": self.fiware_header.service_path,
            "entity_name": "test_entity",
        }

        self.iota_client.post_groups(service_group, update=False)
        self.iota_client.post_device(device=Device(**device), update=False)

        clear_iot_agent(iota_client=self.iota_client)

        self.assertEqual(0, len(self.iota_client.get_device_list()) or len(self.iota_client.get_group_list()))

    def test_clear_iot_agent_url(self):
        """
        Test for clearing iota using iota url and fiware header as parameters
        """
        service_group = ServiceGroup(entity_type='Thing',
                                     resource='/iot/json',
                                     apikey=str(uuid4()))
        device = {
            "device_id": "test_device",
            "service": self.fiware_header.service,
            "service_path": self.fiware_header.service_path,
            "entity_name": "test_entity",
        }

        self.iota_client.post_groups(service_group, update=False)
        self.iota_client.post_device(device=Device(**device), update=False)

        clear_iot_agent(url=self.iota_url, fiware_header=self.fiware_header)

        self.assertEqual(0, len(self.iota_client.get_device_list()) or len(self.iota_client.get_group_list()))

    def test_clear_quantumleap(self):
        # TODO
        pass

    def tearDown(self) -> None:
        """
        Cleanup test servers
        """
        self.cb_client.close()
        self.iota_client.close()
        self.ql_client.close()
