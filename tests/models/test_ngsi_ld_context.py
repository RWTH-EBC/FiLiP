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
        # TODO to remove
        # self.attr = {'temperature': {'value': 20, 'type': 'Property'}}
        # self.relation = {
        #     'relation': {'object': 'OtherEntity', 'type': 'Relationship'}}
        # self.entity_data = {'id': 'urn:ngsi-ld:MyType:MyId',
        #                     'type': 'MyType'}
        # self.entity_data.update(self.attr)
        # self.entity_data.update(self.relation)
        self.entity1_dict = {
            "id": "urn:ngsi-ld:OffStreetParking:Downtown1",
            "type": "OffStreetParking",
            "name": {
                "type": "Property",
                "value": "Downtown One"
            },
            "availableSpotNumber": {
                "type": "Property",
                "value": 121,
                "observedAt": "2017-07-29T12:05:02Z",
                "reliability": {
                    "type": "Property",
                    "value": 0.7
                },
                "providedBy": {
                    "type": "Relationship",
                    "object": "urn:ngsi-ld:Camera:C1"
                }
            },
            "totalSpotNumber": {
                "type": "Property",
                "value": 200
            },
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [-8.5, 41.2]
                }
            },
            "@context": [
                "http://example.org/ngsi-ld/latest/parking.jsonld",
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context-v1.3.jsonld"
            ]
        }
        self.entity2_dict = {
            "id": "urn:ngsi-ld:Vehicle:A4567",
            "type": "Vehicle",
            "@context": [
                "http://example.org/ngsi-ld/latest/commonTerms.jsonld",
                "http://example.org/ngsi-ld/latest/vehicle.jsonld",
                "http://example.org/ngsi-ld/latest/parking.jsonld",
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context-v1.3.jsonld"
            ]
        }
        self.entity2_props_dict = {
            "brandName": {
                "type": "Property",
                "value": "Mercedes"
            }
        }
        self.entity2_rel_dict = {
            "isParked": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:OffStreetParking:Downtown1",
                "observedAt": "2017-07-29T12:00:04Z",
                "providedBy": {
                    "type": "Relationship",
                    "object": "urn:ngsi-ld:Person:Bob"
                }
            }
        }
        self.entity2_dict.update(self.entity2_props_dict)
        self.entity2_dict.update(self.entity2_rel_dict)

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
        entity1 = ContextLDEntity(**self.entity1_dict)
        entity2 = ContextLDEntity(**self.entity2_dict)

        self.assertEqual(self.entity1_dict,
                         entity1.model_dump(exclude_unset=True))
        entity1 = ContextLDEntity.model_validate(self.entity1_dict)

        self.assertEqual(self.entity2_dict,
                         entity2.model_dump(exclude_unset=True))
        entity2 = ContextLDEntity.model_validate(self.entity2_dict)

        # check all properties can be returned by get_properties
        properties = entity2.get_properties(response_format='list')
        for prop in properties:
            self.assertEqual(self.entity2_props_dict[prop.name],
                             prop.model_dump(
                                 exclude={'name'},
                                 exclude_unset=True))  # TODO may not work

        # check all relationships can be returned by get_relationships
        relationships = entity2.get_relationships(response_format='list')
        for relationship in relationships:
            self.assertEqual(self.entity2_rel_dict[relationship.name],
                             relationship.model_dump(
                                 exclude={'name'},
                                 exclude_unset=True))  # TODO may not work

        # test add entity
        new_prop = {'new_prop': ContextProperty(type='Number', value=25)}
        entity2.add_properties(new_prop)

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
