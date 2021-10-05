"""
Test module for context broker models
"""
import time
import unittest
from typing import List

from pydantic import ValidationError
from filip.clients.ngsi_v2 import ContextBrokerClient
from filip.models.ngsi_v2.context import \
    ActionType, \
    Command, \
    ContextMetadata, \
    ContextAttribute, \
    ContextEntity, \
    create_context_entity_model, \
    NamedContextMetadata, \
    Subscription, \
    Update, NamedContextAttribute, ContextEntityKeyValues, NamedCommand
from filip.models.base import FiwareHeader


class TestContextModels(unittest.TestCase):
    """
    Test class for context broker models
    """
    def setUp(self) -> None:
        """
        Setup test data
        Returns:
            None
        """
        self.attr = {'temperature': {'value': 20,
                                     'type': 'Number'}}
        self.relation = {'relation': {'value': 'OtherEntity',
                                      'type': 'RelationField'}}
        self.entity_data = {'id': 'MyId',
                            'type': 'MyType'}
        self.entity_data.update(self.attr)
        self.entity_data.update(self.relation)

    def test_cb_attribute(self) -> None:
        """
        Test context attribute models
        Returns:
            None
        """
        attr = ContextAttribute(**{'value': 20, 'type': 'Text'})
        self.assertIsInstance(attr.value, str)
        attr = ContextAttribute(**{'value': 20, 'type': 'Number'})
        self.assertIsInstance(attr.value, float)
        attr = ContextAttribute(**{'value': [20, 20], 'type': 'Float'})
        self.assertIsInstance(attr.value, list)
        attr = ContextAttribute(**{'value': [20.0, 20.0], 'type': 'Integer'})
        self.assertIsInstance(attr.value, list)
        attr = ContextAttribute(**{'value': [20, 20], 'type': 'Array'})
        self.assertIsInstance(attr.value, list)

    def test_cb_metadata(self) -> None:
        """
        Test context metadata model
        Returns:
            None
        """
        md1 = ContextMetadata(type='Text', value='test')
        md2 = NamedContextMetadata(name='info', type='Text', value='test')
        md3 = [NamedContextMetadata(name='info', type='Text', value='test')]
        attr1 = ContextAttribute(value=20,
                                 type='Integer',
                                 metadata={'info': md1})
        attr2 = ContextAttribute(**attr1.dict(exclude={'metadata'}),
                                 metadata=md2)
        attr3 = ContextAttribute(**attr1.dict(exclude={'metadata'}),
                                 metadata=md3)
        self.assertEqual(attr1, attr2)
        self.assertEqual(attr1, attr3)

    def test_cb_entity(self) -> None:
        """
        Test context entity models
        Returns:
            None
        """
        entity = ContextEntity(**self.entity_data)
        self.assertEqual(self.entity_data, entity.dict(exclude_unset=True))
        entity = ContextEntity.parse_obj(self.entity_data)
        self.assertEqual(self.entity_data, entity.dict(exclude_unset=True))

        properties = entity.get_properties(response_format='list')
        self.assertEqual(self.attr, {properties[0].name: properties[0].dict(
            exclude={'name', 'metadata'}, exclude_unset=True)})
        properties = entity.get_properties(response_format='dict')
        self.assertEqual(self.attr['temperature'],
                         properties['temperature'].dict(exclude={'metadata'},
                                                        exclude_unset=True))

        relations = entity.get_relationships()
        self.assertEqual(self.relation, {relations[0].name: relations[0].dict(
            exclude={'name', 'metadata'}, exclude_unset=True)})

        new_attr = {'new_attr': ContextAttribute(type='Number', value=25)}
        entity.add_attributes(new_attr)

        generated_model = create_context_entity_model(data=self.entity_data)
        entity = generated_model(**self.entity_data)
        self.assertEqual(self.entity_data, entity.dict(exclude_unset=True))
        entity = generated_model.parse_obj(self.entity_data)
        self.assertEqual(self.entity_data, entity.dict(exclude_unset=True))

    def test_cb_subscriptions(self) -> None:
        """
        Test subscription models
        Returns:
            None
        """
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

    def test_command(self):
        """
        Test command model
        Returns:

        """
        cmd_data = {"type": "command",
                    "value": [5]}
        Command(**cmd_data)
        Command(value=[0])
        with self.assertRaises(ValidationError):
            class NotSerializableObject:
                test: "test"
            Command(value=NotSerializableObject())
            Command(type="cmd", value=5)

    def test_update_model(self):
        """
        Test model for bulk updates
        Returns:
            None
        """
        entities = [ContextEntity(id='1', type='myType')]
        action_type = ActionType.APPEND
        Update(actionType=action_type, entities=entities)
        with self.assertRaises(ValueError):
            Update(actionType='test', entities=entities)

    def test_fiware_safe_fields(self):
        """
        Tests all fields of models/ngsi_v2/context.py that have a regex to
        be FIWARE safe
        Returns:
            None
        """

        from pydantic.error_wrappers import ValidationError

        valid_strings: List[str] = ["name", "test123", "3_:strange-Name!"]
        invalid_strings: List[str] = ["my name", "Test?", "#False", "/notvalid"]

        special_strings: List[str] = ["id", "type", "geo:location"]

        # Test if all needed fields, detect all invalid strings
        for string in invalid_strings:
            self.assertRaises(ValidationError,
                              ContextMetadata, type=string)
            self.assertRaises(ValidationError,
                              NamedContextMetadata, name=string)
            self.assertRaises(ValidationError,
                              ContextAttribute, type=string)
            self.assertRaises(ValidationError,
                              NamedContextAttribute, name=string)
            self.assertRaises(ValidationError,
                              ContextEntityKeyValues, id=string, type="name")
            self.assertRaises(ValidationError,
                              ContextEntityKeyValues, id="name", type=string)
            self.assertRaises(ValidationError,
                              NamedCommand, name=string)

        # Test if all needed fields, do not trow wrong errors
        for string in valid_strings:
            ContextMetadata(type=string)
            NamedContextMetadata(name=string)
            ContextAttribute(type=string)
            NamedContextAttribute(name=string)
            ContextEntityKeyValues(id=string, type=string)
            NamedCommand(id=string, name=string)

        # Test for the special-string protected field if all strings are blocked
        for string in special_strings:
            self.assertRaises(ValidationError,
                              NamedContextAttribute, name=string)
            self.assertRaises(ValidationError,
                              NamedCommand, name=string)
        # Test for the normal protected field if all strings are allowed
        for string in special_strings:
            ContextMetadata(type=string)
            NamedContextMetadata(name=string)
            ContextAttribute(type=string)
            ContextEntityKeyValues(id=string, type=string)