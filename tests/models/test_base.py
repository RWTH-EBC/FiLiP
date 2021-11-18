"""
Tests for filip.core.models
"""
import json
import unittest
from pydantic import ValidationError
from filip.models.base import FiwareHeader
from filip.clients.ngsi_v2 import ContextBrokerClient
from filip.models.ngsi_v2.context import ContextEntity
from filip.utils.cleanup import clear_all, clean_test
from tests.config import settings, generate_servicepath


class TestModels(unittest.TestCase):
    """
    Test class for core.models
    """

    def setUp(self) -> None:
        # create variables for test
        self.service_paths = [generate_servicepath(), generate_servicepath()]
        self.fiware_header = {'fiware-service': settings.FIWARE_SERVICE,
                              'fiware-servicepath': settings.FIWARE_SERVICEPATH}

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                cb_url=settings.CB_URL)
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
        with ContextBrokerClient(url=settings.CB_URL,
                                 fiware_header=headers) as client:
            entity = ContextEntity(id='myId', type='MyType')
            for path in self.service_paths:
                client.fiware_service_path = path
                client.post_entity(entity=entity)
                client.get_entity(entity_id=entity.id)
            client.fiware_service_path = '/#'
            self.assertGreaterEqual(len(client.get_entity_list()),
                                    len(self.service_paths))
            for path in self.service_paths:
                client.fiware_service_path = path
                client.delete_entity(entity_id=entity.id,
                                     entity_type=entity.type)

    def tearDown(self) -> None:
        # Cleanup test server
        with ContextBrokerClient(url=settings.CB_URL) as client:
            client.fiware_service = settings.FIWARE_SERVICE

            for path in self.service_paths:
                header = FiwareHeader(
                    service=settings.FIWARE_SERVICE,
                    service_path=path)
                clear_all(fiware_header=header, cb_url=settings.CB_URL)
            client.close()
