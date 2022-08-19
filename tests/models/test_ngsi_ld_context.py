"""
Test module for context broker models
"""

import unittest

from filip.models.ngsi_ld.context import \
    ContextLDEntity, ContextProperty


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
        self.attr = {'temperature': {'value': 20, 'type': 'Property'}}
        self.relation = {'relation': {'object': 'OtherEntity', 'type': 'Relationship'}}
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
        attr = ContextProperty(**{'value': "20"})
        self.assertIsInstance(attr.value, int)
        attr = ContextProperty(**{'value': 20})
        self.assertIsInstance(attr.value, str)



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



