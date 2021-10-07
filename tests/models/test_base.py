"""
Tests for filip.core.models
"""
import unittest
import json
from pydantic import ValidationError
from requests import RequestException
from filip.models.base import FiwareHeader
from filip.clients.ngsi_v2 import ContextBrokerClient
from filip.models.ngsi_v2.context import ContextEntity


class TestModels(unittest.TestCase):
    """
    Test class for core.models
    """
    def setUp(self) -> None:
        self.service_paths = ['/testing', '/testing2']
        self.fiware_header = {'fiware-service': 'filip',
                              'fiware-servicepath': self.service_paths[0]}

    def test_fiware_header(self):
        """
        Test for fiware header
        """
        header = FiwareHeader.parse_obj(self.fiware_header)
        self.assertEqual(header.dict(by_alias=True),
                         self.fiware_header)
        self.assertEqual(header.json(by_alias=True),
                         json.dumps(self.fiware_header))
        self.assertRaises(ValidationError, FiwareHeader,
                          service='jkgsadh ', service_path='/testing')
        self.assertRaises(ValidationError, FiwareHeader,
                          service='%', service_path='/testing')
        self.assertRaises(ValidationError, FiwareHeader,
                          service='filip', service_path='testing/')
        self.assertRaises(ValidationError, FiwareHeader,
                          service='filip', service_path='/$testing')
        self.assertRaises(ValidationError, FiwareHeader,
                          service='filip', service_path='/testing ')
        self.assertRaises(ValidationError, FiwareHeader,
                          service='filip', service_path='#')
        headers = FiwareHeader.parse_obj(self.fiware_header)
        with ContextBrokerClient(fiware_header=headers) as client:
            entity = ContextEntity(id='myId', type='MyType')
            for path in self.service_paths:
                client.fiware_service_path = path
                client.post_entity(entity=entity)
                client.get_entity(entity_id=entity.id)
            client.fiware_service_path = '/#'
            self.assertEqual(len(client.get_entity_list()),
                             len(self.service_paths))
            for path in self.service_paths:
                client.fiware_service_path = path
                client.delete_entity(entity_id=entity.id)

    def tearDown(self) -> None:
        # Cleanup test server
        with ContextBrokerClient() as client:
            client.fiware_service = 'filip'

            for path in self.service_paths:
                try:
                    client.fiware_service_path = path
                    entities = client.get_entity_list()
                    client.update(entities=entities, action_type='delete')
                except RequestException:
                    pass
            client.close()
