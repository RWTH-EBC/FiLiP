import unittest
import re
import time
from unittest.mock import Mock, patch
from datetime import datetime
from core.models import FiwareHeader
from core.simple_query_language import SimpleQuery, Statement
from cb.models import ContextEntity, ContextAttribute, Subscription
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

    def test_pagination(self):
        # test pagination. only works if enough entities are available
        fiware_header = FiwareHeader(service='n5geh',
                                     service_path='/eonerc_main_building')
        with ContextBrokerClient(fiware_header=fiware_header) as client:
            self.assertLessEqual(len(client.get_entity_list(limit=1)), 1)
            self.assertLessEqual(len(client.get_entity_list(limit=999)), 999)
            self.assertLessEqual(len(client.get_entity_list(limit=1001)), 1001)
            self.assertLessEqual(len(client.get_entity_list(limit=2001)), 2001)

    def test_entity_filtering(self):
        fiware_header = FiwareHeader(service='n5geh',
                                     service_path='/eonerc_main_building')
        with ContextBrokerClient(fiware_header=fiware_header) as client:
            # test patterns
            with self.assertRaises(re.error):
                client.get_entity_list(id_pattern='(&()?')
            with self.assertRaises(re.error):
                client.get_entity_list(type_pattern='(&()?')

            entities_all = client.get_entity_list()
            entities_by_id_pattern = client.get_entity_list(
                id_pattern='bacnet501.*')
            self.assertLess(len(entities_by_id_pattern), len(entities_all))

            entities_by_type_pattern = client.get_entity_list(
                type_pattern='humidity$')
            self.assertLess(len(entities_by_type_pattern), len(entities_all))

            query = SimpleQuery(statements=[('presentValue', '>', 0)])
            entities_by_query = client.get_entity_list(q=query)
            self.assertLess(len(entities_by_query), len(entities_all))

            # test options
            entities_by_key_values = client.get_entity_list(
                options=['keyValues'])
            self.assertEqual(len(entities_by_key_values), len(entities_all))

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

    def test_subscriptions(self):
        with ContextBrokerClient(fiware_header=self.fiware_header) as client:
            sub_example = {
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
            sub = Subscription(**sub_example)
            sub_id = client.post_subscription(subscription=sub)
            sub_res = client.get_subscription(subscription_id=sub_id)
            time.sleep(1)
            sub_update = sub_res.copy(update={'expires': datetime.now()})
            client.update_subscription(subscription=sub_update)
            sub_res_updated = client.get_subscription(subscription_id=sub_id)
            self.assertNotEqual(sub_res.expires, sub_res_updated.expires)
            subs = client.get_subscription_list()
            self.assertIn(sub_res_updated, subs)
            for sub in subs:
                client.delete_subscription(subscription_id=sub.id)

    def tearDown(self) -> None:
        # Cleanup test server
        try:
            entities = self.client.get_entity_list()
            for entity in entities:
                self.client.delete_entity(entity_id=entity.id)
        except:
            pass
        self.client.close()
