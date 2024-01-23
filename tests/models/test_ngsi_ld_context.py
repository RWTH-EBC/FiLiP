"""
Test module for context broker models
"""

import unittest

from pydantic import ValidationError

from filip.models.ngsi_ld.context import \
    ContextLDEntity, ContextProperty


class TestLDContextModels(unittest.TestCase):
    """
    Test class for context broker models
    """
    def setUp(self) -> None:
        """
        Setup test data
        Returns:
            None
        """
        self.attr = {'temperature': {'value': 20, 'type': 'Property'}}
        self.relation = {'relation': {'object': 'OtherEntity', 'type': 'Relationship'}}
        self.entity_data = {'id': 'urn:ngsi-ld:MyType:MyId',
                            'type': 'MyType'}
        self.entity_data.update(self.attr)
        self.entity_data.update(self.relation)

    def test_cb_attribute(self) -> None:
        """
        Test context attribute models
        Returns:
            None
        """
        attr = ContextProperty(**{'value': "20"})
        self.assertIsInstance(attr.value, float)
        attr = ContextProperty(**{'value': 20})
        self.assertIsInstance(attr.value, float)

    def test_entity_id(self) -> None:
        with self.assertRaises(ValidationError):
            ContextLDEntity(**{'id': 'MyId', 'type': 'MyType'})

    def test_cb_entity(self) -> None:
        """
        Test context entity models
        Returns:
            None
        """
        entity = ContextLDEntity(**self.entity_data)
        self.assertEqual(self.entity_data, entity.dict(exclude_unset=True))
        entity = ContextLDEntity.parse_obj(self.entity_data)
        self.assertEqual(self.entity_data, entity.dict(exclude_unset=True))

        properties = entity.get_properties(response_format='list')
        self.assertEqual(self.attr, {properties[0].name: properties[0].dict(exclude={'name'},
            exclude_unset=True)})
        properties = entity.get_properties(response_format='dict')
        self.assertEqual(self.attr['temperature'],
                         properties['temperature'].dict(exclude_unset=True))

        relations = entity.get_relationships()
        self.assertEqual(self.relation, {relations[0].name: relations[0].dict(exclude={'name'},
             exclude_unset=True)})

        new_attr = {'new_attr': ContextProperty(type='Number', value=25)}
        entity.add_properties(new_attr)

    def test_get_attributes(self):
        """
        Test the get_attributes method
        """
        pass
        # entity = ContextEntity(id="test", type="Tester")
        # attributes = [
        #     NamedContextAttribute(name="attr1", type="Number"),
        #     NamedContextAttribute(name="attr2", type="string"),
        # ]
        # entity.add_attributes(attributes)
        # self.assertEqual(entity.get_attributes(strict_data_type=False), attributes)
        # self.assertNotEqual(entity.get_attributes(strict_data_type=True), attributes)
        # self.assertNotEqual(entity.get_attributes(), attributes)

    def test_entity_delete_attributes(self):
        """
        Test the delete_attributes methode
        also tests the get_attribute_name method
        """
        pass
        # attr = ContextAttribute(**{'value': 20, 'type': 'Text'})
        # named_attr = NamedContextAttribute(**{'name': 'test2', 'value': 20,
        #                                       'type': 'Text'})
        # attr3 = ContextAttribute(**{'value': 20, 'type': 'Text'})
        #
        # entity = ContextEntity(id="12", type="Test")
        #
        # entity.add_attributes({"test1": attr, "test3": attr3})
        # entity.add_attributes([named_attr])
        #
        # entity.delete_attributes({"test1": attr})
        # self.assertEqual(entity.get_attribute_names(), {"test2", "test3"})
        #
        # entity.delete_attributes([named_attr])
        # self.assertEqual(entity.get_attribute_names(), {"test3"})
        #
        # entity.delete_attributes(["test3"])
        # self.assertEqual(entity.get_attribute_names(), set())

    def test_entity_add_attributes(self):
        """
        Test the add_attributes methode
        Differentiate between property and relationship
        """
        pass