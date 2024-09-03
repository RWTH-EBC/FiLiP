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
        self.entity1_props_dict = {
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [-8.5, 41.2]
                }
            },
            "totalSpotNumber": {
                "type": "Property",
                "value": 200
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
            "name": {
                "type": "Property",
                "value": "Downtown One"
            },
        }
        self.entity1_context = [
                "http://example.org/ngsi-ld/latest/parking.jsonld",
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context-v1.3.jsonld"
            ]
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
        self.entity3_dict = {
            "id": "urn:ngsi-ld:Vehicle:test1243",
            "type": "Vehicle",
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
        # The entity for testing the nested structure of properties
        self.entity_sub_props_dict = {
            "id": "urn:ngsi-ld:Vehicle:test1243",
            "type": "Vehicle",
            "Make": {
                "type": "Property",
                "value": "Tesla",
                "Model": {
                    "type": "Property",
                    "value": "Model 3",
                    "Year": {
                        "type": "Property",
                        "value": 2024
                    }
                },
                "Warranty": [
                    {
                        "Coverage": {
                            "value": "Premium",
                            "type": "Property"
                        }
                    },
                    {
                        "Duration": {
                            "value": 5,
                            "type": "Property"
                        }
                    }
                ],
            }
        }
        self.entity_list_property = {
            "id": "urn:ngsi-ld:Vehicle:A4567",
            "type": "Vehicle",
            "speed": [
                {
                    "type": "Property",
                    "value": 55,
                    "source": {
                        "type": "Property",
                        "value": "Speedometer"
                    },
                    "datasetId": "urn:ngsi-ld:Property:speedometerA4567-speed"
                },
                {
                    "type": "Property",
                    "value": 54.5,
                    "source": {
                        "type": "Property",
                        "value": "GPS"
                    },
                    "datasetId": "urn:ngsi-ld:Property:gpsBxyz123-speed"
                }
            ],
            "@context": [
                {
                    "Vehicle": "http://example.org/Vehicle",
                    "speed": "http://example.org/speed",
                    "source": "http://example.org/hasSource"
                },
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context-v1.3.jsonld"
            ]
        }

    def test_cb_property(self) -> None:
        """
        Test context property models
        Returns:
            None
        """
        prop = ContextProperty(**{'value': "20"})
        self.assertIsInstance(prop.value, str)
        prop = ContextProperty(**{'value': 20.53})
        self.assertIsInstance(prop.value, float)
        prop = ContextProperty(**{'value': 20})
        self.assertIsInstance(prop.value, int)

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
        properties_1 = entity1.get_properties(response_format='list')
        for prop in properties_1:
            self.assertEqual(self.entity1_props_dict[prop.name],
                             prop.model_dump(
                                 exclude={'name'},
                                 exclude_unset=True))

        properties_2 = entity2.get_properties(response_format='list')
        for prop in properties_2:
            self.assertEqual(self.entity2_props_dict[prop.name],
                             prop.model_dump(
                                 exclude={'name'},
                                 exclude_unset=True))

        # check all relationships can be returned by get_relationships
        relationships = entity2.get_relationships(response_format='list')
        for relationship in relationships:
            self.assertEqual(self.entity2_rel_dict[relationship.name],
                             relationship.model_dump(
                                 exclude={'name'},
                                 exclude_unset=True))

        # test add properties
        new_prop = {'new_prop': ContextProperty(value=25)}
        entity2.add_properties(new_prop)
        properties = entity2.get_properties(response_format='list')
        self.assertIn("new_prop", [prop.name for prop in properties])

    def test_validate_subproperties_dict(self) -> None:
        """
        Test the validation of multi-level properties in entities
        Returns:
            None
        """
        entity4 = ContextLDEntity(**self.entity_sub_props_dict)
        entity4._validate_properties()

    def test_validate_subproperties_list(self) -> None:
        """
        Test the validation of multi-level properties in entities
        Returns:
            None
        """
        entity4 = ContextLDEntity(**self.entity_list_property)
        entity4._validate_properties()

    def test_get_properties(self):
        """
        Test the get_properties method
        """
        pass
        entity = ContextLDEntity(id="urn:ngsi-ld:test", type="Tester")

        properties = [
            NamedContextProperty(name="prop1"),
            NamedContextProperty(name="prop2"),
        ]
        entity.add_properties(properties)
        self.assertEqual(entity.get_properties(response_format="list"),
                         properties)

    def test_entity_delete_properties(self):
        """
        Test the delete_properties method
        """
        prop = ContextProperty(**{'value': 20, 'type': 'Text'})
        named_prop = NamedContextProperty(**{'name': 'test2',
                                             'value': 20,
                                             'type': 'Text'})
        prop3 = ContextProperty(**{'value': 20, 'type': 'Text'})

        entity = ContextLDEntity(id="urn:ngsi-ld:12", type="Test")

        entity.add_properties({"test1": prop, "test3": prop3})
        entity.add_properties([named_prop])

        entity.delete_properties({"test1": prop})
        self.assertEqual(set([_prop.name for _prop in entity.get_properties()]),
                         {"test2", "test3"})

        entity.delete_properties([named_prop])
        self.assertEqual(set([_prop.name for _prop in entity.get_properties()]),
                         {"test3"})

        entity.delete_properties(["test3"])
        self.assertEqual(set([_prop.name for _prop in entity.get_properties()]),
                         set())

    def test_entity_relationships(self):
        pass
        # TODO relationships CRUD

    def test_get_context(self):
        entity1 = ContextLDEntity(**self.entity1_dict)
        context_entity1 = entity1.get_context()

        self.assertEqual(self.entity1_context,
                         context_entity1)

        # test here if entity without context can be validated and get_context works accordingly:
        entity3 = ContextLDEntity(**self.entity3_dict)
        context_entity3 = entity3.get_context()

        self.assertEqual(None,
                         context_entity3)