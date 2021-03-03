import unittest
import re
from unittest.mock import Mock, patch
from core.models import FiwareHeader
from core.simple_query_language import SimpleQuery, Statement
from cb.models import ContextEntity, ContextAttribute
from cb.client import ContextBrokerClient


class TestContextBroker(unittest.TestCase):
    def setUp(self) -> None:
        self.resources = {
            "entities_url": "/v2/entities",
            "types_url": "/v2/types",
            "subscriptions_url": "/v2/subscriptions",
            "registrations_url": "/v2/registrations"
        }
        self.attr = {'temperature': {'value': 20,
                                     'type': 'Number'}}
        self.entity=ContextEntity(id='MyId', type='MyType', **self.attr)
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

    def test_entity_filtering(self):
        fiware_header = FiwareHeader(service='n5geh',
                                     service_path='/eonerc_main_building')
        with ContextBrokerClient(fiware_header=fiware_header) as client:
            # test patterns
            with self.assertRaises(re.error):
                client.get_entities(id_pattern='(&()?')
            with self.assertRaises(re.error):
                client.get_entities(type_pattern='(&()?')

            entities = client.get_entities()
            entities_by_id_pattern = client.get_entities(
                id_pattern='bacnet501.*')
            self.assertLess(len(entities_by_id_pattern), len(entities))

            entities_by_type_pattern = client.get_entities(
                type_pattern='humidity$')
            self.assertLess(len(entities_by_type_pattern), len(entities))

            query = SimpleQuery(statements=[('presentValue', '>', 0)])
            entities_by_query = client.get_entities(q=query)
            self.assertLess(len(entities_by_query), len(entities))

            # test options
            entities_by_key_values = client.get_entities(options=['keyValues'])
            self.assertEqual(len(entities_by_key_values), len(entities))

    def test_entity_operations(self):
        with ContextBrokerClient(fiware_header=self.fiware_header) as client:
            self.assertIsNotNone(client.post_entity(entity=self.entity,
                                                    update=True))
            res_entity = client.get_entity(entity_id=self.entity.id)
            client.get_entity(entity_id=self.entity.id, attrs=['temperature'])
            self.assertEqual(client.get_entity_attributes(
                entity_id=self.entity.id), res_entity.get_properties(
                format='dict'))
            res_entity.temperature.value = 25
            client.update_entity(entity=res_entity)
            self.assertEqual(client.get_entity(entity_id=self.entity.id),
                             res_entity)
            res_entity.add_properties({'pressure': ContextAttribute(
                type='Number', value=1050)})
            client.update_entity(entity=res_entity)
            self.assertEqual(client.get_entity(entity_id=self.entity.id),
                             res_entity)

    def test_attribute_operations(self):
        with ContextBrokerClient(fiware_header=self.fiware_header) as client:
            self.assertIsNotNone(client.post_entity(entity=self.entity,
                                                    update=True))
            attr = client.get_attribute(entity_id=self.entity.id,
                                        attr_name='temperature')
            attr_value = client.get_attribute_value(entity_id=self.entity.id,
                                                    attr_name='temperature')
            self.assertEqual(attr_value, attr.value)
            new_value = 1337
            client.update_attribute_value(entity_id=self.entity.id,
                                          attr_name='temperature',
                                          value=new_value)
            attr_value = client.get_attribute_value(entity_id=self.entity.id,
                                                    attr_name='temperature')
            self.assertEqual(attr_value, new_value)
            client.delete_entity(entity_id=self.entity.id)

    def test_type_operations(self):
        with ContextBrokerClient(fiware_header=self.fiware_header) as client:
            self.assertIsNotNone(client.post_entity(entity=self.entity,
                                                    update=True))
            print(client.get_entity_types())
            print(client.get_entity_types(options='count'))
            print(client.get_entity_types(options='values'))
            print(client.get_entity_type(entity_type='MyType'))
            client.delete_entity(entity_id=self.entity.id)

    def tearDown(self) -> None:
        # Cleanup test server
        try:
            self.client.delete_entity(entity_id=self.entity.id)
        except:
            pass
        self.client.close()
