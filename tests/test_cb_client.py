"""
Tests for filip.cb.client
"""
import unittest
import time
from datetime import datetime
from requests import RequestException
from filip.core.models import FiwareHeader
from filip.core.simple_query_language import QueryString
from filip.cb.client import ContextBrokerClient
from filip.cb.models import \
    AttrsFormat,\
    ContextEntity, \
    ContextAttribute, \
    NamedContextAttribute, \
    Subscription, \
    Query, \
    Entity, \
    ActionType


class TestContextBroker(unittest.TestCase):
    """
    Test class for ContextBrokerClient
    """
    def setUp(self) -> None:
        self.resources = {
            "entities_url": "/v2/entities",
            "types_url": "/v2/types",
            "subscriptions_url": "/v2/subscriptions",
            "registrations_url": "/v2/registrations"
        }
        self.attr = {'temperature': {'value': 20.0,
                                     'type': 'Number'}}
        self.entity = ContextEntity(id='MyId', type='MyType', **self.attr)
        self.fiware_header = FiwareHeader(service='filip',
                                          service_path='/testing')

        self.client = ContextBrokerClient(fiware_header=self.fiware_header)

    def test_management_endpoints(self):
        """
        Test management functions of context broker client
        """
        with ContextBrokerClient(fiware_header=self.fiware_header) as client:
            self.assertIsNotNone(client.get_version())
            self.assertEqual(client.get_resources(), self.resources)

    def test_statistics(self):
        """
        Test statistics of context broker client
        """
        with ContextBrokerClient(fiware_header=self.fiware_header) as client:
            self.assertIsNotNone(client.get_statistics())

    def test_pagination(self):
        """
        Test pagination of context broker client
        Test pagination. only works if enough entities are available
        """
        fiware_header = FiwareHeader(service='filip',
                                     service_path='/testing')
        with ContextBrokerClient(fiware_header=fiware_header) as client:
            entities_a = [ContextEntity(id=str(i),
                                        type=f'filip:object:TypeA') for i in
                          range(0, 1000)]
            client.update(action_type=ActionType.APPEND, entities=entities_a)
            entities_b = [ContextEntity(id=str(i),
                                        type=f'filip:object:TypeB') for i in
                          range(1000, 2001)]
            client.update(action_type=ActionType.APPEND, entities=entities_b)
            self.assertLessEqual(len(client.get_entity_list(limit=1)), 1)
            self.assertLessEqual(len(client.get_entity_list(limit=999)), 999)
            self.assertLessEqual(len(client.get_entity_list(limit=1001)), 1001)
            self.assertLessEqual(len(client.get_entity_list(limit=2001)), 2001)

            client.update(action_type=ActionType.DELETE, entities=entities_a)
            client.update(action_type=ActionType.DELETE, entities=entities_b)

    def test_entity_filtering(self):
        """
        Test filter operations of context broker client
        """
        fiware_header = FiwareHeader(service='filip',
                                     service_path='/testing')
        with ContextBrokerClient(fiware_header=fiware_header) as client:
            # test patterns
            with self.assertRaises(ValueError):
                client.get_entity_list(id_pattern='(&()?')
            with self.assertRaises(ValueError):
                client.get_entity_list(type_pattern='(&()?')
            entities_a = [ContextEntity(id=str(i),
                                        type=f'filip:object:TypeA') for i in
                          range(0, 5)]

            client.update(action_type=ActionType.APPEND, entities=entities_a)
            entities_b = [ContextEntity(id=str(i),
                                        type=f'filip:object:TypeB') for i in
                          range(6, 10)]

            client.update(action_type=ActionType.APPEND, entities=entities_b)

            entities_all = client.get_entity_list()
            entities_by_id_pattern = client.get_entity_list(
                id_pattern='.*[1-5]')
            self.assertLess(len(entities_by_id_pattern), len(entities_all))

            entities_by_type_pattern = client.get_entity_list(
                type_pattern=".*TypeA$")
            self.assertLess(len(entities_by_type_pattern), len(entities_all))

            qs = QueryString(qs=[('presentValue', '>', 0)])
            entities_by_query = client.get_entity_list(q=qs)
            self.assertLess(len(entities_by_query), len(entities_all))

            # test options
            for opt in list(AttrsFormat):
                entities_by_option = client.get_entity_list(response_format=opt)
                self.assertEqual(len(entities_by_option), len(entities_all))
                self.assertEqual(client.get_entity(
                    entity_id='0',
                    response_format=opt),
                    entities_by_option[0])
            with self.assertRaises(ValueError):
                client.get_entity_list(response_format='not in AttrFormat')

            client.update(action_type=ActionType.DELETE, entities=entities_a)

            client.update(action_type=ActionType.DELETE, entities=entities_b)

    def test_entity_operations(self):
        """
        Test entity operations of context broker client
        """
        with ContextBrokerClient(fiware_header=self.fiware_header) as client:
            client.post_entity(entity=self.entity, update=True)
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
        """
        Test attribute operations of context broker client
        """
        with ContextBrokerClient(fiware_header=self.fiware_header) as client:
            entity = self.entity
            attr_txt = NamedContextAttribute(name='attr_txt',
                                             type='Text',
                                             value="Test")
            attr_txt = NamedContextAttribute(name='attr_txt',
                                             type='Boolean',
                                             value=True)
            attr_list = NamedContextAttribute(name='attr_list',
                                              type='StructuredValue',
                                              value=[1, 2, 3])
            attr_dict = NamedContextAttribute(name='attr_dict',
                                              type='StructuredValue',
                                              value={'key': 'value'})
            entity.add_properties([attr_txt, attr_list, attr_dict])

            self.assertIsNotNone(client.post_entity(entity=entity,
                                                    update=True))
            res_entity = client.get_entity(entity_id=entity.id)

            for attr in entity.get_properties():
                self.assertIn(attr, res_entity.get_properties())
                res_attr = client.get_attribute(entity_id=entity.id,
                                                attr_name=attr.name)

                self.assertEqual(type(res_attr.value), type(attr.value))
                self.assertEqual(res_attr.value, attr.value)
                value = client.get_attribute_value(entity_id=entity.id,
                                                   attr_name=attr.name)
                # unfortunately FIWARE returns an int for 20.0 although float
                # is expected
                if isinstance(value, int) and not isinstance(value, bool):
                    value=float(value)
                self.assertEqual(type(value), type(attr.value))
                self.assertEqual(value, attr.value)

            new_value = 1337.0
            client.update_attribute_value(entity_id=entity.id,
                                          attr_name='temperature',
                                          value=new_value)
            attr_value = client.get_attribute_value(entity_id=entity.id,
                                                    attr_name='temperature')
            self.assertEqual(attr_value, new_value)

            client.delete_entity(entity_id=entity.id)

    def test_type_operations(self):
        """
        Test type operations of context broker client
        """
        with ContextBrokerClient(fiware_header=self.fiware_header) as client:
            self.assertIsNotNone(client.post_entity(entity=self.entity,
                                                    update=True))
            client.get_entity_types()
            client.get_entity_types(options='count')
            client.get_entity_types(options='values')
            client.get_entity_type(entity_type='MyType')
            client.delete_entity(entity_id=self.entity.id)

    def test_subscriptions(self):
        """
        Test subscription operations of context broker client
        """
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
            self.assertEqual(sub_res.id, sub_res_updated.id)
            self.assertGreaterEqual( sub_res_updated.expires, sub_res.expires)
            subs = client.get_subscription_list()
            for sub in subs:
                client.delete_subscription(subscription_id=sub.id)

    def test_batch_operations(self):
        """
        Test batch operations of context broker client
        """
        fiware_header = FiwareHeader(service='filip',
                                     service_path='/testing')
        with ContextBrokerClient(fiware_header=fiware_header) as client:
            entities = [ContextEntity(id=str(i),
                                      type=f'filip:object:TypeA') for i in
                        range(0, 1000)]
            client.update(entities=entities, action_type=ActionType.APPEND)
            entities = [ContextEntity(id=str(i),
                                      type=f'filip:object:TypeB') for i in
                        range(0, 1000)]
            client.update(entities=entities, action_type=ActionType.APPEND)
            e = Entity(idPattern=".*", typePattern=".*TypeA$")
            q = Query.parse_obj({"entities": [e.dict(exclude_unset=True)]})
            self.assertEqual(1000,
                             len(client.query(query=q, format='keyValues')))

    def tearDown(self) -> None:
        # Cleanup test server
        try:
            entities = [ContextEntity(id=entity.id, type=entity.type) for
                        entity in self.client.get_entity_list()]
            self.client.update(entities=entities, action_type='delete')
        except RequestException:
            pass
        self.client.close()
