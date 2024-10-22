"""
Tests for filip.cb.client
"""
import unittest
import logging
import time
import random
import json
import paho.mqtt.client as mqtt
from datetime import datetime
from requests import RequestException

from filip.clients.ngsi_ld.cb import ContextBrokerLDClient
from filip.models.base import  DataType, FiwareLDHeader
from filip.models.ngsi_ld.context import ActionTypeLD, ContextLDEntity, ContextProperty, NamedContextProperty
from filip.utils.simple_ql import QueryString

from filip.models.ngsi_v2.base import AttrsFormat
from filip.models.ngsi_v2.subscriptions import Subscription
from tests.config import settings
from filip.models.ngsi_v2.context import \
    NamedCommand, \
    Query, \
    ContextEntity


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
            "entities_url": "/ngsi-ld/v1/entities",
            "types_url": "/ngsi-ld/v1/types"
        }
        self.attr = {
            'testtemperature': {
                'type': 'Property',
                'value': 20.0}
        }
        self.entity = ContextLDEntity(id='urn:ngsi-ld:my:id4', type='MyType', **self.attr)
        self.fiware_header = FiwareLDHeader()
        self.client = ContextBrokerLDClient(fiware_header=self.fiware_header,
                                            url=settings.LD_CB_URL)
        # todo replace with clean up function for ld
        try:
            # todo implement with pagination, the default limit is 20
            #  and max limit is 1000 for orion-ld
            for i in range(0, 10):
                entity_list = self.client.get_entity_list(limit=1000)
                for entity in entity_list:
                    self.client.delete_entity_by_id(entity_id=entity.id)
        except RequestException:
            pass

    def tearDown(self) -> None:
        """
        Cleanup test server
        """
        # todo replace with clean up function for ld
        try:
            for i in range(0, 10):
                entity_list = self.client.get_entity_list(limit=1000)
                for entity in entity_list:
                    self.client.delete_entity_by_id(entity_id=entity.id)
        except RequestException:
            pass
        self.client.close()

    def test_management_endpoints(self):
        """
        Test management functions of context broker client
        """
        self.assertIsNotNone(self.client.get_version())
        # TODO: check whether there are other "management" endpoints

    def test_statistics(self):
        """
        Test statistics of context broker client
        """
        self.assertIsNotNone(self.client.get_statistics())

    def test_pagination(self):
        """
        Test pagination of context broker client
        Test pagination. only works if enough entities are available
        self.assertLessEqual(len(self.client.get_entity_list(limit=1)), 1)
        self.assertLessEqual(len(self.client.get_entity_list(limit=50)), 50)
        self.assertLessEqual(len(self.client.get_entity_list(limit=100)), 100)
        self.client.entity_batch_operation(action_type=ActionTypeLD.DELETE, entities=entities_a)
        """
        
        #for some reason, batch delete fails if batch size is above 800 ???
        entities_a = [ContextLDEntity(id=f"urn:ngsi-ld:test:{str(i)}",
                                    type=f'filip:object:TypeA') for i in
                        range(0, 800)]
        
        self.client.entity_batch_operation(action_type=ActionTypeLD.CREATE, entities=entities_a)
        
        entity_list = self.client.get_entity_list(limit=1)
        self.assertEqual(len(entity_list),1)
        
        entity_list = self.client.get_entity_list(limit=400)
        self.assertEqual(len(entity_list),400)
        
        entity_list = self.client.get_entity_list(limit=800)
        self.assertEqual(len(entity_list),800)
        
        entity_list = self.client.get_entity_list(limit=1000)
        self.assertEqual(len(entity_list),800)
        
        self.client.entity_batch_operation(action_type=ActionTypeLD.DELETE, entities=entities_a)
