import unittest
import json
from pydantic import ValidationError
from cb.models import \
    BaseContextAttribute,\
    ContextEntity, \
    create_context_entity_model


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

        GeneratedModel = create_context_entity_model(data=self.entity_data)
        entity = GeneratedModel(**self.entity_data)
        self.assertEqual(self.entity_data, entity.dict(exclude_unset=True))
        entity = GeneratedModel.parse_obj(self.entity_data)
        self.assertEqual(self.entity_data, entity.dict(exclude_unset=True))
