"""
Test module for context broker models
"""

import unittest

from geojson_pydantic import Point, MultiPoint, LineString, Polygon, GeometryCollection
from pydantic import ValidationError

from filip.models.ngsi_ld.context import (
    ContextLDEntity,
    ContextProperty,
    NamedContextProperty,
    ContextGeoPropertyValue,
    ContextGeoProperty,
    NamedContextGeoProperty,
    NamedContextRelationship,
)


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
            "name": {"type": "Property", "value": "Downtown One"},
            "availableSpotNumber": {
                "type": "Property",
                "value": 121,
                "observedAt": "2017-07-29T12:05:02Z",
                "reliability": {"type": "Property", "value": 0.7},
                "providedBy": {
                    "type": "Relationship",
                    "object": "urn:ngsi-ld:Camera:C1",
                },
            },
            "totalSpotNumber": {"type": "Property", "value": 200},
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": (-8.5, 41.2),  # coordinates are normally a tuple
                },
            },
            "@context": [
                "http://example.org/ngsi-ld/latest/parking.jsonld",
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context-v1.3.jsonld",
            ],
        }
        self.entity1_props_dict = {
            "location": {
                "type": "GeoProperty",
                "value": {"type": "Point", "coordinates": (-8.5, 41.2)},
            },
            "totalSpotNumber": {"type": "Property", "value": 200},
            "availableSpotNumber": {
                "type": "Property",
                "value": 121,
                "observedAt": "2017-07-29T12:05:02Z",
                "reliability": {"type": "Property", "value": 0.7},
                "providedBy": {
                    "type": "Relationship",
                    "object": "urn:ngsi-ld:Camera:C1",
                },
            },
            "name": {"type": "Property", "value": "Downtown One"},
        }
        self.entity1_context = [
            "http://example.org/ngsi-ld/latest/parking.jsonld",
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context-v1.3.jsonld",
        ]
        self.entity2_dict = {
            "id": "urn:ngsi-ld:Vehicle:A4567",
            "type": "Vehicle",
            "@context": [
                "http://example.org/ngsi-ld/latest/commonTerms.jsonld",
                "http://example.org/ngsi-ld/latest/vehicle.jsonld",
                "http://example.org/ngsi-ld/latest/parking.jsonld",
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context-v1.3.jsonld",
            ],
        }
        self.entity2_props_dict = {
            "brandName": {"type": "Property", "value": "Mercedes"}
        }
        self.entity2_rel_dict = {
            "isParked": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:OffStreetParking:Downtown1",
                "observedAt": "2017-07-29T12:00:04Z",
                "providedBy": {
                    "type": "Relationship",
                    "object": "urn:ngsi-ld:Person:Bob",
                },
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
                    "object": "urn:ngsi-ld:Person:Bob",
                },
            },
        }
        # # The entity for testing the nested structure of properties
        # self.entity_sub_props_dict_wrong = {
        #     "id": "urn:ngsi-ld:OffStreetParking:Downtown1",
        #     "type": "OffStreetParking",
        #     "name": {
        #         "type": "Property",
        #         "value": "Downtown One"
        #     },
        #     "totalSpotNumber": {
        #         "type": "Property",
        #         "value": 200
        #     },
        #     "location": {
        #         "type": "GeoProperty",
        #         "value": {
        #             "type": "Point",
        #             "coordinates": [-8.5, 41.2]
        #         }
        #     },
        #     "@context": [
        #         "http://example.org/ngsi-ld/latest/parking.jsonld",
        #         "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context-v1.3.jsonld"
        #     ]
        # }
        self.testpoint_value = {"type": "Point", "coordinates": (-8.5, 41.2)}
        self.testmultipoint_value = {
            "type": "MultiPoint",
            "coordinates": (
                (-3.80356167695194, 43.46296641666926),
                (-3.804056, 43.464638),
            ),
        }
        self.testlinestring_value = {
            "type": "LineString",
            "coordinates": (
                (-3.80356167695194, 43.46296641666926),
                (-3.804056, 43.464638),
            ),
        }
        self.testpolygon_value = {
            "type": "Polygon",
            "coordinates": [
                [
                    (-3.80356167695194, 43.46296641666926),
                    (-3.804056, 43.464638),
                    (-3.805056, 43.463638),
                    (-3.80356167695194, 43.46296641666926),
                ]
            ],
        }
        self.testgeometrycollection_value = {
            "type": "GeometryCollection",
            "geometries": [
                {
                    "type": "Point",
                    "coordinates": (-3.80356167695194, 43.46296641666926),
                },
                {
                    "type": "LineString",
                    "coordinates": ((-3.804056, 43.464638), (-3.805056, 43.463638)),
                },
            ],
        }
        self.entity_geo_dict = {
            "id": "urn:ngsi-ld:Geometry:001",
            "type": "MyGeometry",
            "testpoint": {"type": "GeoProperty", "value": self.testpoint_value},
            "testmultipoint": {
                "type": "GeoProperty",
                "value": self.testmultipoint_value,
                "observedAt": "2023-09-12T12:35:00Z",
            },
            "testlinestring": {
                "type": "GeoProperty",
                "value": self.testlinestring_value,
                "observedAt": "2023-09-12T12:35:30Z",
            },
            "testpolygon": {
                "type": "GeoProperty",
                "value": self.testpolygon_value,
                "observedAt": "2023-09-12T12:36:00Z",
            },
        }

    def test_cb_property(self) -> None:
        """
        Test context property models
        Returns:
            None
        """
        prop = ContextProperty(**{"value": "20"})
        self.assertIsInstance(prop.value, str)
        prop = ContextProperty(**{"value": 20.53})
        self.assertIsInstance(prop.value, float)
        prop = ContextProperty(**{"value": 20})
        self.assertIsInstance(prop.value, int)

    def test_geo_property(self) -> None:
        """
        Test ContextGeoPropertyValue models
        Returns:
            None
        """
        geo_entity = ContextLDEntity(**self.entity_geo_dict)
        new_entity = ContextLDEntity(id="urn:ngsi-ld:Geometry:002", type="MyGeometry")
        test_point = NamedContextGeoProperty(
            name="testpoint", type="GeoProperty", value=Point(**self.testpoint_value)
        )
        test_MultiPoint = NamedContextGeoProperty(
            name="testmultipoint",
            type="GeoProperty",
            value=MultiPoint(**self.testmultipoint_value),
        )
        test_LineString = NamedContextGeoProperty(
            name="testlinestring",
            type="GeoProperty",
            value=LineString(**self.testlinestring_value),
        )
        test_Polygon = NamedContextGeoProperty(
            name="testpolygon",
            type="GeoProperty",
            value=Polygon(**self.testpolygon_value),
        )
        with self.assertRaises(ValueError):
            test_GeometryCollection = NamedContextGeoProperty(
                name="testgeometrycollection",
                type="GeoProperty",
                value=GeometryCollection(**self.testgeometrycollection_value),
            )
        new_entity.add_geo_properties(
            [test_point, test_MultiPoint, test_LineString, test_Polygon]
        )

    def test_cb_entity(self) -> None:
        """
        Test context entity models
        Returns:
            None
        """
        test = ContextLDEntity.get_model_fields_set()
        entity1 = ContextLDEntity(**self.entity1_dict)
        entity2 = ContextLDEntity(**self.entity2_dict)

        self.assertEqual(self.entity1_dict, entity1.model_dump(exclude_unset=True))
        entity1 = ContextLDEntity.model_validate(self.entity1_dict)

        self.assertEqual(self.entity2_dict, entity2.model_dump(exclude_unset=True))
        entity2 = ContextLDEntity.model_validate(self.entity2_dict)

        # check all properties can be returned by get_properties
        properties_1 = entity1.get_properties(response_format="list")
        for prop in properties_1:
            self.assertEqual(
                self.entity1_props_dict[prop.name],
                prop.model_dump(exclude={"name"}, exclude_unset=True),
            )

        properties_2 = entity2.get_properties(response_format="list")
        for prop in properties_2:
            self.assertEqual(
                self.entity2_props_dict[prop.name],
                prop.model_dump(exclude={"name"}, exclude_unset=True),
            )

        # check all relationships can be returned by get_relationships
        relationships = entity2.get_relationships(response_format="list")
        for relationship in relationships:
            self.assertEqual(
                self.entity2_rel_dict[relationship.name],
                relationship.model_dump(exclude={"name"}, exclude_unset=True),
            )

        # test add properties
        new_prop = {"new_prop": ContextProperty(value=25)}
        entity2.add_properties(new_prop)
        properties = entity2.get_properties(response_format="list")
        self.assertIn("new_prop", [prop.name for prop in properties])

    def test_validate_subproperties_dict(self) -> None:
        """
        Test the validation of multi-level properties in entities
        Returns:
            None
        """
        entity4 = ContextLDEntity(**self.entity1_dict)

    def test_validate_subproperties_dict_wrong(self) -> None:
        """
        Test the validation of multi-level properties in entities
        Returns:
            None
        """
        entity_sub_props_dict_wrong_1 = self.entity1_dict.copy()
        entity_sub_props_dict_wrong_1["availableSpotNumber"]["reliability"][
            "type"
        ] = "NotProperty"
        with self.assertRaises(ValueError):
            entity5 = ContextLDEntity(**entity_sub_props_dict_wrong_1)
        entity_sub_props_dict_wrong_2 = self.entity1_dict.copy()
        entity_sub_props_dict_wrong_2["availableSpotNumber"]["providedBy"][
            "type"
        ] = "NotRelationship"
        with self.assertRaises(ValueError):
            entity5 = ContextLDEntity(**entity_sub_props_dict_wrong_2)

    def test_get_properties(self):
        """
        Test the get_properties method
        """
        entity = ContextLDEntity(
            id="urn:ngsi-ld:test",
            type="Tester",
            hasLocation={"type": "Relationship", "object": "urn:ngsi-ld:test2"},
        )

        properties = [
            NamedContextProperty(name="prop1"),
            NamedContextProperty(name="prop2"),
        ]
        entity.add_properties(properties)
        entity.get_properties(response_format="list")
        self.assertEqual(entity.get_properties(response_format="list"), properties)

    def test_entity_delete_properties(self):
        """
        Test the delete_properties method
        """
        prop = ContextProperty(**{"value": 20, "type": "Property"})
        named_prop = NamedContextProperty(
            **{"name": "test2", "value": 20, "type": "Property"}
        )
        prop3 = ContextProperty(**{"value": 20, "type": "Property"})

        entity = ContextLDEntity(id="urn:ngsi-ld:12", type="Test")

        entity.add_properties({"test1": prop, "test3": prop3})
        entity.add_properties([named_prop])

        entity.delete_properties({"test1": prop})
        self.assertEqual(
            set([_prop.name for _prop in entity.get_properties()]), {"test2", "test3"}
        )

        entity.delete_properties([named_prop])
        self.assertEqual(
            set([_prop.name for _prop in entity.get_properties()]), {"test3"}
        )

        entity.delete_properties(["test3"])
        self.assertEqual(set([_prop.name for _prop in entity.get_properties()]), set())

    def test_entity_relationships(self):
        entity = ContextLDEntity(**self.entity3_dict)

        # test get relationships
        relationships_list = entity.get_relationships(response_format="list")
        self.assertEqual(len(relationships_list), 1)
        relationships_dict = entity.get_relationships(response_format="dict")
        self.assertIn("isParked", relationships_dict)

        # test add relationships
        new_rel_dict = {
            "name": "new_rel",
            "type": "Relationship",
            "obejct": "urn:ngsi-ld:test",
        }
        new_rel = NamedContextRelationship(**new_rel_dict)
        entity.add_relationships([new_rel])
        relationships_list = entity.get_relationships(response_format="list")
        self.assertEqual(len(relationships_list), 2)

        # test delete relationships
        entity.delete_relationships(["isParked"])
        relationships_list = entity.get_relationships(response_format="list")
        self.assertEqual(len(relationships_list), 1)
        relationships_dict = entity.get_relationships(response_format="dict")
        self.assertNotIn("isParked", relationships_dict)

    def test_get_context(self):
        entity1 = ContextLDEntity(**self.entity1_dict)
        context_entity1 = entity1.get_context()

        self.assertEqual(self.entity1_context, context_entity1)

        # test here if entity without context can be validated and get_context
        # works accordingly:
        entity3 = ContextLDEntity(**self.entity3_dict)
        context_entity3 = entity3.get_context()

        self.assertEqual(None, context_entity3)
