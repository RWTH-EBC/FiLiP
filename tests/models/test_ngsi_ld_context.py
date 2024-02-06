"""
Test module for context broker models
"""

import unittest

from pydantic import ValidationError

from filip.models.ngsi_ld.context import \
    ContextLDEntity, ContextProperty, NamedContextProperty


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

        # test add properties
        new_prop = {'new_prop': ContextProperty(value=25)}
        entity2.add_properties(new_prop)
        entity2.get_properties(response_format='list')
        self.assertIn("new_prop", [prop.name for prop in properties])

    def test_get_attributes(self):
        """
        Test the get_attributes method
        """
        pass
        entity = ContextLDEntity(id="test", type="Tester")
        properties = [
            NamedContextProperty(name="attr1"),
            NamedContextProperty(name="attr2"),
        ]
        entity.add_properties(properties)
        self.assertEqual(entity.get_properties(response_format="list"),
                         properties)
        # TODO why it should be different?
        self.assertNotEqual(entity.get_properties(),
                            properties)

    def test_entity_delete_attributes(self):
        """
        Test the delete_attributes methode
        """
        attr = ContextProperty(**{'value': 20, 'type': 'Text'})
        named_attr = NamedContextProperty(**{'name': 'test2',
                                             'value': 20,
                                             'type': 'Text'})
        attr3 = ContextProperty(**{'value': 20, 'type': 'Text'})

        entity = ContextLDEntity(id="12", type="Test")

        entity.add_properties({"test1": attr, "test3": attr3})
        entity.add_properties([named_attr])

        entity.delete_properties({"test1": attr})
        self.assertEqual(set([_prop.name for _prop in entity.get_properties()]),
                         {"test2", "test3"})

        entity.delete_properties([named_attr])
        self.assertEqual(set([_prop.name for _prop in entity.get_properties()]),
                         {"test3"})

        entity.delete_properties(["test3"])
        self.assertEqual(set([_prop.name for _prop in entity.get_properties()]),
                         set())

    def test_entity_add_attributes(self):
        """
        Test the add_attributes methode
        Differentiate between property and relationship
        """
        pass
