"""
Test module for context broker models
"""
import unittest
from typing import List
from pydantic import ValidationError

from filip.models.base import DataType
from filip.clients.ngsi_v2 import IoTAClient, ContextBrokerClient
from filip.models.ngsi_v2.iot import Device, TransportProtocol, DeviceCommand
from filip.models import FiwareHeader
from filip.utils.cleanup import clear_all
from tests.config import settings

from filip.models.ngsi_v2.base import Metadata, NamedMetadata
from filip.models.ngsi_v2.context import \
    ActionType, \
    Command, \
    ContextAttribute, \
    ContextEntity, \
    create_context_entity_model, \
    Update, \
    NamedContextAttribute, \
    ContextEntityKeyValues, \
    NamedCommand


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
                                      'type': 'Relationship'}}
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
        md1 = Metadata(type='Text', value='test')
        md2 = NamedMetadata(name='info', type='Text', value='test')
        md3 = [NamedMetadata(name='info', type='Text', value='test')]
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
                              Metadata, type=string)
            self.assertRaises(ValidationError,
                              NamedMetadata, name=string)
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
            Metadata(type=string)
            NamedMetadata(name=string)
            ContextAttribute(type=string)
            NamedContextAttribute(name=string)
            ContextEntityKeyValues(id=string, type=string)
            NamedCommand(name=string, value=string)

        # Test for the special-string protected field if all strings are blocked
        for string in special_strings:
            self.assertRaises(ValidationError, ContextAttribute, type=string)
            self.assertRaises(ValidationError,
                              NamedContextAttribute, name=string)
            self.assertRaises(ValidationError,
                              NamedCommand, name=string)
        # Test for the normal protected field if all strings are allowed
        for string in special_strings:
            Metadata(type=string)
            NamedMetadata(name=string)
            ContextEntityKeyValues(id=string, type=string)

    def test_entity_delete_attributes(self):
        """
        Test the delete_attributes methode
        also tests the get_attribute_name method
        """
        attr = ContextAttribute(**{'value': 20, 'type': 'Text'})
        named_attr = NamedContextAttribute(**{'name': 'test2', 'value': 20,
                                              'type': 'Text'})
        attr3 = ContextAttribute(**{'value': 20, 'type': 'Text'})

        entity = ContextEntity(id="12", type="Test")

        entity.add_attributes({"test1": attr, "test3": attr3})
        entity.add_attributes([named_attr])

        entity.delete_attributes({"test1": attr})
        self.assertEqual(entity.get_attribute_names(), {"test2", "test3"})

        entity.delete_attributes([named_attr])
        self.assertEqual(entity.get_attribute_names(), {"test3"})

        entity.delete_attributes(["test3"])
        self.assertEqual(entity.get_attribute_names(), set())

    def test_entity_get_command_methods(self):
        """
        Tests the two methods:
            get_commands and get_command_triple
        """

        # test the manual creation of an entity with Command
        entity = ContextEntity(id="test", type="Tester")

        entity.add_attributes([NamedCommand(name="myCommand", value=".")])

        self.assertEqual(entity.get_commands()[0].name, "myCommand")
        with self.assertRaises(AttributeError):
            entity.get_command_triple("myCommand")
        with self.assertRaises(KeyError):
            entity.get_command_triple("--")

        # test the automated command creation via Fiware and DeviceModel
        device = Device(device_id="id",
                        service=settings.FIWARE_SERVICE,
                        service_path=settings.FIWARE_SERVICEPATH,
                        entity_name="name",
                        entity_type="type",
                        transport=TransportProtocol.HTTP,
                        endpoint="http://localhost:1234")

        device.add_command(DeviceCommand(name="myCommand"))

        with IoTAClient(
                url=settings.IOTA_JSON_URL,
                fiware_header=FiwareHeader(
                    service=settings.FIWARE_SERVICE,
                    service_path=settings.FIWARE_SERVICEPATH)) as client:
            client.post_device(device=device)

        with ContextBrokerClient(
                url=settings.CB_URL,
                fiware_header=FiwareHeader(
                    service=settings.FIWARE_SERVICE,
                    service_path=settings.FIWARE_SERVICEPATH)) as client:

            entity = client.get_entity(entity_id="name", entity_type="type")
            self.assertEqual(entity.get_commands()[0].name, "myCommand")

            (command, c_status, c_info) = entity.get_command_triple("myCommand")

            self.assertEqual(command.type, DataType.COMMAND)
            self.assertEqual(c_status.type, DataType.COMMAND_STATUS)
            self.assertEqual(c_info.type, DataType.COMMAND_RESULT)

    def tearDown(self) -> None:
        """
        Cleanup test server
        """
        clear_all(fiware_header=FiwareHeader(
            service=settings.FIWARE_SERVICE,
            service_path=settings.FIWARE_SERVICEPATH),
            cb_url=settings.CB_URL,
            iota_url=settings.IOTA_JSON_URL)
