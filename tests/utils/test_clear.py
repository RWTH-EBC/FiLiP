"""
Tests clear functions in filip.utils.cleanup
"""
import random
import time
import unittest
import urllib.parse
from datetime import datetime
from typing import List
from uuid import uuid4
from requests import RequestException
from filip.clients.ngsi_ld.cb import ContextBrokerLDClient
from filip.clients.ngsi_v2 import ContextBrokerClient, IoTAClient, QuantumLeapClient
from filip.models.base import FiwareHeader, FiwareLDHeader
from filip.models.ngsi_ld.context import ContextLDEntity, ActionTypeLD
from filip.models.ngsi_ld.subscriptions import SubscriptionLD, NotificationParams, \
    Endpoint
from filip.models.ngsi_v2.context import ContextEntity
from filip.models.ngsi_v2.iot import Device, ServiceGroup
from filip.models.ngsi_v2.subscriptions import Subscription, Message
from filip.utils.cleanup import clear_context_broker, clear_iot_agent, clear_quantumleap, \
    clear_context_broker_ld
from tests.config import settings


class TestClearFunctions(unittest.TestCase):

    def setUp(self) -> None:
        """
        Setup test data and clients

        Returns:
            None
        """
        # use specific service for testing clear functions
        self.fiware_header = FiwareHeader(
            service="filip_clear_test",
            service_path=settings.FIWARE_SERVICEPATH)
        self.cb_url = settings.CB_URL
        self.cb_client = ContextBrokerClient(url=self.cb_url,
                                             fiware_header=self.fiware_header)
        self.cb_client_ld = ContextBrokerLDClient(
            fiware_header=FiwareLDHeader(ngsild_tenant=settings.FIWARE_SERVICE),
            url=settings.LD_CB_URL)

        self.iota_url = settings.IOTA_URL
        self.iota_client = IoTAClient(url=self.iota_url,
                                      fiware_header=self.fiware_header)

        self.ql_url = settings.QL_URL
        self.ql_client = QuantumLeapClient(url=self.ql_url,
                                           fiware_header=self.fiware_header)
        self.sub_dict = {
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

    def test_clear_context_broker(self):
        """
        Test for clearing context broker using context broker client
        """
        entity = ContextEntity(id=str(random.randint(1, 50)),
                               type=f'filip:object:Type')
        self.cb_client.post_entity(entity=entity)
        subscription = Subscription.model_validate(self.sub_dict)
        self.cb_client.post_subscription(subscription=subscription)
        clear_context_broker(cb_client=self.cb_client)

        self.assertEqual(0, len(self.cb_client.get_entity_list()) or len(self.cb_client.get_subscription_list()))

    def test_clear_context_broker_ld(self):
        """
        Test for clearing context broker LD using context broker client
        """
        random_list = [random.randint(0, 100) for _ in range(10)]
        entities = [ContextLDEntity(id=f"urn:ngsi-ld:clear_test:{str(i)}",
                                    type='clear_test') for i in random_list]
        self.cb_client_ld.entity_batch_operation(action_type=ActionTypeLD.CREATE,
                                                 entities=entities)
        notification_param = NotificationParams(attributes=["attr"],
                                                endpoint=Endpoint(**{
                                                    "uri": urllib.parse.urljoin(
                                                        str(settings.LD_CB_URL),
                                                        "/ngsi-ld/v1/subscriptions"),
                                                    "accept": "application/json"
                                                }))
        sub = SubscriptionLD(id=f"urn:ngsi-ld:Subscription:clear_test:{random.randint(0, 100)}",
                             notification=notification_param,
                             entities=[{"type": "clear_test"}])
        self.cb_client_ld.post_subscription(subscription=sub)
        clear_context_broker_ld(cb_ld_client=self.cb_client_ld)
        self.assertEqual(0, len(self.cb_client_ld.get_entity_list()))
        self.assertEqual(0, len(self.cb_client_ld.get_subscription_list()))

    def test_clear_context_broker_with_url(self):
        """
        Test for clearing context broker using context broker url and fiware header as parameters
        """
        entity = ContextEntity(id=str(random.randint(1, 50)),
                               type=f'filip:object:Type')
        self.cb_client.post_entity(entity=entity)
        subscription = Subscription.model_validate(self.sub_dict)
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
            "entity_type": "test_type",
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
            "entity_type": "test_type",
        }

        self.iota_client.post_groups(service_group, update=False)
        self.iota_client.post_device(device=Device(**device), update=False)

        clear_iot_agent(url=self.iota_url, fiware_header=self.fiware_header)

        self.assertEqual(0, len(self.iota_client.get_device_list()) or len(self.iota_client.get_group_list()))

    def test_clear_quantumleap(self):
        from random import random

        clear_quantumleap(ql_client=self.ql_client)
        rec_numbs = 3
        def create_data_points():
            def create_entities(_id) -> List[ContextEntity]:
                def create_attr():
                    return {'temperature': {'value': random(),
                                            'type': 'Number'},
                            'humidity': {'value': random(),
                                         'type': 'Number'},
                            'co2': {'value': random(),
                                    'type': 'Number'}}

                return [ContextEntity(id=f'Room:{_id}', type='Room', **create_attr())]

            fiware_header = self.fiware_header

            with QuantumLeapClient(url=settings.QL_URL, fiware_header=fiware_header) \
                    as client:
                for i in range(rec_numbs):
                    notification_message = Message(data=create_entities(i),
                                                   subscriptionId="test")
                    client.post_notification(notification_message)

        create_data_points()
        time.sleep(2)
        self.assertEqual(len(self.ql_client.get_entities()), rec_numbs)
        clear_quantumleap(url=self.ql_url,
                          fiware_header=self.fiware_header)
        with self.assertRaises(RequestException):
            self.ql_client.get_entities()

        create_data_points()
        time.sleep(2)
        self.assertEqual(len(self.ql_client.get_entities()), rec_numbs)
        clear_quantumleap(ql_client=self.ql_client)
        with self.assertRaises(RequestException):
            self.ql_client.get_entities()

    def tearDown(self) -> None:
        """
        Cleanup test servers
        """
        self.cb_client.close()
        self.iota_client.close()
        self.ql_client.close()
