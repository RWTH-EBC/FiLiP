"""
Test module for context broker models
"""

import unittest
from typing import List
from pydantic_core import PydanticCustomError
from geojson_pydantic import (
    Point,
    MultiPoint,
    LineString,
    MultiLineString,
    Polygon,
    MultiPolygon,
    Feature,
    FeatureCollection,
)

from filip.models.base import DataType
from filip.clients.ngsi_v2 import IoTAClient, ContextBrokerClient
from filip.models.ngsi_v2.iot import Device, TransportProtocol, DeviceCommand
from filip.models import FiwareHeader
from filip.utils.cleanup import clear_all
from tests.config import settings

from filip.models.ngsi_v2.base import Metadata, NamedMetadata
from filip.models.ngsi_v2.context import (
    ActionType,
    Command,
    ContextAttribute,
    ContextEntity,
    Update,
    NamedContextAttribute,
    ContextEntityKeyValues,
    NamedCommand,
    PropertyFormat,
)
from filip.utils.model_generation import create_context_entity_model


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
        self.attr = {"temperature": {"value": 20, "type": "Number"}}
        self.relation = {"relation": {"value": "OtherEntity", "type": "Relationship"}}
        self.entity_data = {"id": "MyId", "type": "MyType"}
        self.entity_data.update(self.attr)
        self.entity_data.update(self.relation)

    def test_cb_attribute(self) -> None:
        """
        Test context attribute models

        Returns:
            None
        """
        attr = ContextAttribute(**{"value": 20, "type": "Text"})
        self.assertIsInstance(attr.value, str)
        self.assertEqual(attr.value, "20")
        attr = ContextAttribute(**{"value": 20, "type": "Number"})
        self.assertIsInstance(attr.value, float)
        self.assertEqual(str(attr.value), str(20.0))
        attr = ContextAttribute(**{"value": [20, 20], "type": "Float"})
        self.assertIsInstance(attr.value, list)
        attr = ContextAttribute(**{"value": [20.0, 20.0], "type": "Integer"})
        self.assertIsInstance(attr.value, list)
        attr = ContextAttribute(**{"value": [20, 20], "type": "Array"})
        self.assertIsInstance(attr.value, list)
        with self.assertRaises(ValueError) as context:
            ContextAttribute(**{"value": "2<0", "type": "Text"})

    def test_geojson_attribute(self):
        """
        Test the GeoJsonAttribute model
        """
        # test Point
        geojson = ContextAttribute(
            type=DataType.GEOJSON, value={"type": "Point", "coordinates": (125.6, 10.1)}
        )
        self.assertIsInstance(geojson.value, Point)
        self.assertEqual(
            geojson.value.model_dump(exclude={"bbox"}),
            {"type": "Point", "coordinates": (125.6, 10.1)},
        )
        # test MultiPoint
        geojson = ContextAttribute(
            type=DataType.GEOJSON,
            value={"type": "MultiPoint", "coordinates": [(125.6, 10.1), (125.6, 10.2)]},
        )
        self.assertIsInstance(geojson.value, MultiPoint)
        self.assertEqual(
            geojson.value.model_dump(exclude={"bbox"}),
            {"type": "MultiPoint", "coordinates": [(125.6, 10.1), (125.6, 10.2)]},
        )
        # test LineString
        geojson = ContextAttribute(
            type=DataType.GEOJSON,
            value={"type": "LineString", "coordinates": [(125.6, 10.1), (125.6, 10.2)]},
        )
        self.assertIsInstance(geojson.value, LineString)
        self.assertEqual(
            geojson.value.model_dump(exclude={"bbox"}),
            {"type": "LineString", "coordinates": [(125.6, 10.1), (125.6, 10.2)]},
        )
        # test MultiLineString
        geojson = ContextAttribute(
            type=DataType.GEOJSON,
            value={
                "type": "MultiLineString",
                "coordinates": [
                    [(125.6, 10.1), (125.6, 10.2)],
                    [
                        (125.6, 10.1),
                        (125.6, 10.2),
                    ],
                ],
            },
        )
        self.assertIsInstance(geojson.value, MultiLineString)
        self.assertEqual(
            geojson.value.model_dump(exclude={"bbox"}),
            {
                "type": "MultiLineString",
                "coordinates": [
                    [(125.6, 10.1), (125.6, 10.2)],
                    [
                        (125.6, 10.1),
                        (125.6, 10.2),
                    ],
                ],
            },
        )
        # test Polygon
        geojson = ContextAttribute(
            type=DataType.GEOJSON,
            value={
                "type": "Polygon",
                "coordinates": [
                    [
                        (125.6, 10.1),
                        (126.6, 10.2),
                        (126.6, 10.3),
                        (125.6, 10.1),
                    ]
                ],
            },
        )
        self.assertIsInstance(geojson.value, Polygon)
        self.assertEqual(
            geojson.value.model_dump(exclude={"bbox"}),
            {
                "type": "Polygon",
                "coordinates": [
                    [
                        (125.6, 10.1),
                        (126.6, 10.2),
                        (126.6, 10.3),
                        (125.6, 10.1),
                    ]
                ],
            },
        )
        # test MultiPolygon
        geojson = ContextAttribute(
            type=DataType.GEOJSON,
            value={
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [
                            (125.6, 10.1),
                            (126.6, 10.2),
                            (126.6, 10.3),
                            (125.6, 10.1),
                        ]
                    ],
                    [
                        [
                            (125.6, 10.1),
                            (126.6, 10.2),
                            (126.6, 10.3),
                            (125.6, 10.1),
                        ]
                    ],
                ],
            },
        )
        self.assertIsInstance(geojson.value, MultiPolygon)
        self.assertEqual(
            geojson.value.model_dump(exclude={"bbox"}),
            {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [
                            (125.6, 10.1),
                            (126.6, 10.2),
                            (126.6, 10.3),
                            (125.6, 10.1),
                        ]
                    ],
                    [
                        [
                            (125.6, 10.1),
                            (126.6, 10.2),
                            (126.6, 10.3),
                            (125.6, 10.1),
                        ]
                    ],
                ],
            },
        )
        # test Feature
        feature = Feature(
            **{
                "type": "Feature",
                "bbox": [-10.0, -10.0, 10.0, 10.0],
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            (-10.0, -10.0),
                            (10.0, -10.0),
                            (10.0, 10.0),
                            (-10.0, -10.0),
                        ]
                    ],
                },
                "properties": {"name": "MyPolygon"},
                "id": 1,
            }
        )
        geojson = ContextAttribute(
            type=DataType.GEOJSON,
            value={
                "type": "Feature",
                "bbox": [-10.0, -10.0, 10.0, 10.0],
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            (-10.0, -10.0),
                            (10.0, -10.0),
                            (10.0, 10.0),
                            (-10.0, -10.0),
                        ]
                    ],
                },
                "properties": {"name": "MyPolygon"},
                "id": 1,
            },
        )
        self.assertIsInstance(geojson.value, Feature)
        self.assertEqual(
            geojson.value.model_dump(),
            {
                "type": "Feature",
                "bbox": (-10.0, -10.0, 10.0, 10.0),
                "geometry": {
                    "bbox": None,
                    "type": "Polygon",
                    "coordinates": [
                        [
                            (-10.0, -10.0),
                            (10.0, -10.0),
                            (10.0, 10.0),
                            (-10.0, -10.0),
                        ]
                    ],
                },
                "properties": {"name": "MyPolygon"},
                "id": 1,
            },
        )
        # test FeatureCollection
        geojson = ContextAttribute(
            type=DataType.GEOJSON,
            value={
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "bbox": (-10.0, -10.0, 10.0, 10.0),
                        "geometry": {
                            "bbox": None,
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    (-10.0, -10.0),
                                    (10.0, -10.0),
                                    (10.0, 10.0),
                                    (-10.0, -10.0),
                                ]
                            ],
                        },
                        "properties": {"name": "MyFirstPolygon"},
                        "id": 1,
                    },
                    {
                        "type": "Feature",
                        "bbox": (-10.0, -10.0, 10.0, 10.0),
                        "geometry": {
                            "bbox": None,
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    (-10.0, -10.0),
                                    (10.0, -10.0),
                                    (10.0, 10.0),
                                    (-10.0, -10.0),
                                ]
                            ],
                        },
                        "properties": {"name": "MySecondPolygon"},
                        "id": 2,
                    },
                ],
            },
        )
        self.assertIsInstance(geojson.value, FeatureCollection)
        self.assertEqual(
            geojson.value.model_dump(exclude={"bbox"}),
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "bbox": (-10.0, -10.0, 10.0, 10.0),
                        "geometry": {
                            "bbox": None,
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    (-10.0, -10.0),
                                    (10.0, -10.0),
                                    (10.0, 10.0),
                                    (-10.0, -10.0),
                                ]
                            ],
                        },
                        "properties": {"name": "MyFirstPolygon"},
                        "id": 1,
                    },
                    {
                        "type": "Feature",
                        "bbox": (-10.0, -10.0, 10.0, 10.0),
                        "geometry": {
                            "bbox": None,
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    (-10.0, -10.0),
                                    (10.0, -10.0),
                                    (10.0, 10.0),
                                    (-10.0, -10.0),
                                ]
                            ],
                        },
                        "properties": {"name": "MySecondPolygon"},
                        "id": 2,
                    },
                ],
            },
        )

    def test_cb_metadata(self) -> None:
        """
        Test context metadata model
        Returns:
            None
        """
        md1 = Metadata(type="Text", value="test")
        md2 = NamedMetadata(name="info", type="Text", value="test")
        md3 = [NamedMetadata(name="info", type="Text", value="test")]
        attr1 = ContextAttribute(value=20, type="Integer", metadata={"info": md1})
        attr2 = ContextAttribute(**attr1.model_dump(exclude={"metadata"}), metadata=md2)
        attr3 = ContextAttribute(**attr1.model_dump(exclude={"metadata"}), metadata=md3)
        self.assertEqual(attr1, attr2)
        self.assertEqual(attr1, attr3)

    def test_cb_entity(self) -> None:
        """
        Test context entity models
        Returns:
            None
        """
        entity = ContextEntity(**self.entity_data)
        self.assertEqual(self.entity_data, entity.model_dump(exclude_unset=True))
        entity = ContextEntity.model_validate(self.entity_data)
        self.assertEqual(self.entity_data, entity.model_dump(exclude_unset=True))

        properties = entity.get_properties(response_format="list")
        self.assertEqual(
            self.attr,
            {
                properties[0]
                .name: properties[0]
                .model_dump(exclude={"name", "metadata"}, exclude_unset=True)
            },
        )
        properties = entity.get_properties(response_format="dict")
        self.assertEqual(
            self.attr["temperature"],
            properties["temperature"].model_dump(
                exclude={"metadata"}, exclude_unset=True
            ),
        )

        relations = entity.get_relationships()
        self.assertEqual(
            self.relation,
            {
                relations[0]
                .name: relations[0]
                .model_dump(exclude={"name", "metadata"}, exclude_unset=True)
            },
        )

        # add attribute via API
        new_attr = {"new_attr": ContextAttribute(type="Number", value=25)}
        entity.add_attributes(new_attr)

        # add attribute directly to the entity
        entity.new_attr = new_attr["new_attr"]

        # add attribute directly without proper type conversion
        with self.assertRaises(ValueError):
            new_attr["new_attr"] = new_attr["new_attr"].model_dump(exclude_unset=True)
            entity.new_attr = new_attr

        # try to generate a model with the entity data
        generated_model = create_context_entity_model(data=self.entity_data)
        entity = generated_model(**self.entity_data)
        self.assertEqual(self.entity_data, entity.model_dump(exclude_unset=True))
        entity = generated_model.model_validate(self.entity_data)
        self.assertEqual(self.entity_data, entity.model_dump(exclude_unset=True))

        # try to generate a entity with one of dissalowed character in attribute name
        attribute_name = [
            "<",
            ">",
            '"',
            "'",
            "=",
            ";",
            "(",
            ")",
            " ",
            "§",
            "&",
            "/",
            "#",
            "?",
        ]
        for char in attribute_name:
            with self.assertRaises(PydanticCustomError) as context:
                ContextEntity(
                    **{
                        "id": "Room",
                        "type": "Room",
                        "temper" + char + "ature": {"value": "20", "type": "Text"},
                    }
                )

        # try to generate an entity with one of disallowed characters in attribute value
        attribute_value_not_allowed = ["<", ">", '"', "'", "=", ";", "(", ")"]
        for char in attribute_value_not_allowed:
            with self.assertRaises(ValueError) as context:
                ContextEntity(
                    **{
                        "id": "Room",
                        "type": "Room",
                        "temperature": {"value": "2" + char + "0", "type": "Text"},
                    }
                )
        # utf-8 characters are allowed in attribute values
        attribute_value_allowed = ["ä", "ö", "ü", "ß", "é", "è"]
        for char in attribute_value_allowed:
            entity = ContextEntity(
                **{
                    "id": "Room",
                    "type": "Room",
                    "temperature": {"value": "2" + char + "0", "type": "Text"},
                }
            )
            self.assertEqual(entity.temperature.value, "2" + char + "0")

    def test_command(self):
        """
        Test command model
        Returns:

        """
        cmd_data = {"type": "command", "value": [5]}
        Command(**cmd_data)
        Command(value=[0])
        with self.assertRaises(ValueError):

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
        entities = [ContextEntity(id="1", type="myType")]
        action_type = ActionType.APPEND
        Update(actionType=action_type, entities=entities)
        with self.assertRaises(ValueError):
            Update(actionType="test", entities=entities)

    def test_fiware_safe_fields(self):
        """
        Tests all fields of models/ngsi_v2/context.py that have a regex to
        be FIWARE safe
        Returns:
            None
        """
        valid_strings: List[str] = ["name", "test123", "3_:strange-Name!"]
        invalid_strings: List[str] = ["my name", "Test?", "#False", "/notvalid"]
        with self.assertRaises(ValueError):
            NamedContextAttribute(name="type")
        special_strings: List[str] = ["id", "type", "geo:json"]
        # Test if all needed fields, detect all invalid strings
        for string in invalid_strings:
            self.assertRaises(ValueError, Metadata, type=string)
            self.assertRaises(ValueError, NamedMetadata, name=string)
            self.assertRaises(ValueError, ContextAttribute, type=string)
            self.assertRaises(ValueError, NamedContextAttribute, name=string)
            self.assertRaises(
                ValueError, ContextEntityKeyValues, id=string, type="name"
            )
            self.assertRaises(
                ValueError, ContextEntityKeyValues, id="name", type=string
            )
            self.assertRaises(ValueError, NamedCommand, name=string)

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
            self.assertRaises(ValueError, ContextAttribute, type=string)
            self.assertRaises(ValueError, NamedContextAttribute, name=string)
            self.assertRaises(ValueError, NamedCommand, name=string)
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
        attr = ContextAttribute(**{"value": 20, "type": "Text"})
        named_attr = NamedContextAttribute(
            **{"name": "test2", "value": 20, "type": "Text"}
        )
        attr3 = ContextAttribute(**{"value": 20, "type": "Text"})

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

        self.assertEqual(len(entity.get_commands()), 0)
        with self.assertRaises(KeyError):
            entity.get_command_triple("myCommand")
        with self.assertRaises(KeyError):
            entity.get_command_triple("--")

        # test the automated command creation via Fiware and DeviceModel
        device = Device(
            device_id="device_id",
            service=settings.FIWARE_SERVICE,
            service_path=settings.FIWARE_SERVICEPATH,
            entity_name="name",
            entity_type="type",
            transport=TransportProtocol.HTTP,
            endpoint="http://localhost:1234",
        )

        device.add_command(DeviceCommand(name="myCommand"))
        device.add_command(DeviceCommand(name="myCommand2", type=DataType.TEXT))

        with IoTAClient(
            url=settings.IOTA_JSON_URL,
            fiware_header=FiwareHeader(
                service=settings.FIWARE_SERVICE,
                service_path=settings.FIWARE_SERVICEPATH,
            ),
        ) as client:
            client.post_device(device=device)

        with ContextBrokerClient(
            url=settings.CB_URL,
            fiware_header=FiwareHeader(
                service=settings.FIWARE_SERVICE,
                service_path=settings.FIWARE_SERVICEPATH,
            ),
        ) as client:
            entity = client.get_entity(entity_id="name", entity_type="type")

            (command, c_status, c_info) = entity.get_command_triple("myCommand")
            self.assertEqual(command.type, DataType.COMMAND)
            self.assertEqual(c_status.type, DataType.COMMAND_STATUS)
            self.assertEqual(c_info.type, DataType.COMMAND_RESULT)

            (command, c_status, c_info) = entity.get_command_triple("myCommand2")
            self.assertEqual(command.type, DataType.TEXT)
            self.assertEqual(c_status.type, DataType.COMMAND_STATUS)
            self.assertEqual(c_info.type, DataType.COMMAND_RESULT)

            self.assertEqual(
                entity.get_commands(response_format=PropertyFormat.DICT).keys(),
                {"myCommand", "myCommand2"},
            )

    def test_get_attributes(self):
        """
        Test the get_attributes method
        """
        entity = ContextEntity(id="test", type="Tester")
        attributes = [
            NamedContextAttribute(name="attr1", type="Number"),
            NamedContextAttribute(name="attr2", type="string"),
        ]
        entity.add_attributes(attributes)
        self.assertEqual(entity.get_attributes(strict_data_type=False), attributes)
        self.assertNotEqual(entity.get_attributes(strict_data_type=True), attributes)
        self.assertNotEqual(entity.get_attributes(), attributes)

    def test_format_conversion(self):
        entity_data = [
            {
                "id": "MyId1",
                "type": "MyType",
                "temperature": {"value": 20.2, "type": "Number"},
            },
            {
                "id": "MyId2",
                "type": "MyType",
                "temperature": {"value": 20, "type": "Number"},
            },
            {
                "id": "MyId3",
                "type": "MyType",
                "temperature": {"value": "20", "type": "Text"},
            },
            {
                "id": "MyId4",
                "type": "MyType",
                "temperature": {"value": None, "type": "Number"},
            },
            {
                "id": "MyId5",
                "type": "MyType",
                "relatedTo": {"value": "MyId1", "type": "Relationship"},
            },
        ]
        for format_entity_data in entity_data:
            format_entity_normalized = ContextEntity(**format_entity_data)
            format_entity_data_kv = dict()
            for attr, value in format_entity_data.items():
                if isinstance(value, dict):
                    value = value.get("value")
                format_entity_data_kv[attr] = value
            format_entity_key_values = ContextEntityKeyValues(**format_entity_data_kv)
            entity_kv2normalized = format_entity_key_values.to_normalized()
            self.assertEqual(format_entity_normalized.id, entity_kv2normalized.id)
            self.assertEqual(format_entity_normalized.type, entity_kv2normalized.type)
            # We cannot guarantee the type of the attribute is the same
            for attr_name, attr in format_entity_normalized.get_attributes(
                response_format="dict"
            ).items():
                self.assertEqual(
                    entity_kv2normalized.get_attribute(attr_name).value, attr.value
                )

            entity_normalized2kv = format_entity_normalized.to_keyvalues()
            for attr_name, value in format_entity_key_values.model_dump().items():
                self.assertEqual(
                    entity_normalized2kv.model_dump().get(attr_name), value
                )

    def tearDown(self) -> None:
        """
        Cleanup test server
        """
        clear_all(
            fiware_header=FiwareHeader(
                service=settings.FIWARE_SERVICE,
                service_path=settings.FIWARE_SERVICEPATH,
            ),
            cb_url=settings.CB_URL,
            iota_url=settings.IOTA_JSON_URL,
        )
