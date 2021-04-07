import unittest
import re
import time
from datetime import datetime
from filip.core.models import FiwareHeader
from filip.core.simple_query_language import QueryString
from filip.cb.client import ContextBrokerClient
from filip.cb.models import \
    ContextEntity, \
    ContextAttribute, \
    Subscription, \
    Update, \
    Query, \
    Entity, \
    ActionType


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
        fiware_header = FiwareHeader(service='filip',
                                     service_path='/testing')
        with ContextBrokerClient(fiware_header=fiware_header) as client:
            entitiesA = [ContextEntity(id=str(i),
                                      type=f'filip:object:TypeA') for i in
                        range(0, 1000)]
            update = Update(actionType=ActionType.APPEND, entities=entitiesA)
            client.update(update=update)
            entitiesB = [ContextEntity(id=str(i),
                                       type=f'filip:object:TypeB') for i in
                        range(1000, 2001)]
            update = Update(actionType=ActionType.APPEND, entities=entitiesB)
            client.update(update=update)
            self.assertLessEqual(len(client.get_entity_list(limit=1)), 1)
            self.assertLessEqual(len(client.get_entity_list(limit=999)), 999)
            self.assertLessEqual(len(client.get_entity_list(limit=1001)), 1001)
            self.assertLessEqual(len(client.get_entity_list(limit=2001)), 2001)

            update = Update(actionType=ActionType.DELETE,
                            entities=entitiesA)
            client.update(update=update)
            update = Update(actionType=ActionType.DELETE,
                            entities=entitiesB)
            client.update(update=update)


    def test_entity_filtering(self):
        fiware_header = FiwareHeader(service='filip',
                                     service_path='/testing')
        with ContextBrokerClient(fiware_header=fiware_header) as client:
            # test patterns
            with self.assertRaises(re.error):
                client.get_entity_list(id_pattern='(&()?')
            with self.assertRaises(re.error):
                client.get_entity_list(type_pattern='(&()?')
            entitiesA = [ContextEntity(id=str(i),
                                      type=f'filip:object:TypeA') for i in
                        range(0, 5)]
            update = Update(actionType=ActionType.APPEND, entities=entitiesA)
            client.update(update=update)
            entitiesB = [ContextEntity(id=str(i),
                                       type=f'filip:object:TypeB') for i in
                        range(6, 10)]
            update = Update(actionType=ActionType.APPEND, entities=entitiesB)
            client.update(update=update)

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
            entities_by_key_values = client.get_entity_list(
                options=['keyValues'])
            self.assertEqual(len(entities_by_key_values), len(entities_all))

            update = Update(actionType=ActionType.DELETE,
                            entities=entitiesA)
            client.update(update=update)
            update = Update(actionType=ActionType.DELETE,
                            entities=entitiesB)
            client.update(update=update)

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
            client.get_entity_types()
            client.get_entity_types(options='count')
            client.get_entity_types(options='values')
            client.get_entity_type(entity_type='MyType')
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

    def test_batch_operations(self):
        fiware_header = FiwareHeader(service='filip',
                                     service_path='/testing')
        with ContextBrokerClient(fiware_header=fiware_header) as client:
            entities = [ContextEntity(id=str(i),
                                      type=f'filip:object:TypeA') for i in
                        range(0, 1000)]
            update = Update(actionType=ActionType.APPEND, entities=entities)
            client.update(update=update)
            entities = [ContextEntity(id=str(i),
                                      type=f'filip:object:TypeB') for i in
                        range(0, 1000)]
            update = Update(actionType=ActionType.APPEND, entities=entities)
            client.update(update=update)
            e = Entity(idPattern=".*", typePattern=".*TypeA$")
            q = Query.parse_obj({"entities":[e.dict(exclude_unset=True)]})
            self.assertEqual(1000,
                             len(client.query(query=q, options='keyValues')))

    def tearDown(self) -> None:
        # Cleanup test server
        try:
            entities = self.client.get_entity_list()
            update = Update(actionType=ActionType.DELETE,
                            entities=entities)
            self.client.update(update=update)
        except:
            pass
        self.client.close()
