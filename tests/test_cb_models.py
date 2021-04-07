import unittest
from filip.core.models import FiwareHeader
from filip.cb.client import ContextBrokerClient
from filip.cb.models import \
    ContextAttribute,\
    ContextEntity, \
    create_context_entity_model, \
    Expression, \
    Condition, \
    Subscription


class TestModels(unittest.TestCase):
    def setUp(self) -> None:
        self.attr = {'temperature': {'value': 20,
                                     'type': 'Number'}}

        self.entity_data = {'id': 'MyId',
                            'type': 'MyType'}
        self.entity_data.update(self.attr)

    def test_cb_attribute(self):
        pass

    def test_cb_metadata(self):
        pass

    def test_cb_entity(self):
        entity = ContextEntity(**self.entity_data)
        self.assertEqual(self.entity_data, entity.dict(exclude_unset=True))
        entity = ContextEntity.parse_obj(self.entity_data)
        self.assertEqual(self.entity_data, entity.dict(exclude_unset=True))
        properties = entity.get_properties()
        self.assertEqual(self.attr, {properties[0].name: properties[0].dict(
            exclude={'name', 'metadata'}, exclude_unset=True)})
        new_attr = {'new_attr': ContextAttribute(type='Number', value=25)}
        entity.add_properties(new_attr)

        GeneratedModel = create_context_entity_model(data=self.entity_data)
        entity = GeneratedModel(**self.entity_data)
        self.assertEqual(self.entity_data, entity.dict(exclude_unset=True))
        entity = GeneratedModel.parse_obj(self.entity_data)
        self.assertEqual(self.entity_data, entity.dict(exclude_unset=True))

    def test_cb_subscriptions(self):
        exp = Expression(q='temperature>40')
        print(exp.json(indent=2))
        con = Condition(attrs=['temperature'], expression=exp)
        print(con.json(indent=2))

        sub_dict = {
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
                "expires": "2016-04-05T14:00:00Z",
                "throttling": 5
            }

        sub = Subscription.parse_obj(sub_dict)
        fiware_header = FiwareHeader(service='filip',
                                     service_path='/testing')
        with ContextBrokerClient(fiware_header=fiware_header) as client:
            sub_id = client.post_subscription(subscription=sub)
            sub_res = client.get_subscription(subscription_id=sub_id)
            self.assertEqual(sub.json(exclude={'id', 'status', 'expires'},
                                      exclude_none=True),
                             sub_res.json(exclude={'id', 'status', 'expires'},
                                          exclude_none=True))
            sub_ids = [sub.id for sub in client.get_subscription_list()]
            for sub_id in sub_ids:
                client.delete_subscription(subscription_id=sub_id)
