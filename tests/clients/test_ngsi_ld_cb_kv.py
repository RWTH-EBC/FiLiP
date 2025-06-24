"""
Tests for filip.cb.client
"""

import time
import unittest
import logging
from random import Random
from pydantic import ValidationError
from requests import RequestException, Session
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError
from urllib3.util.retry import Retry
from filip.clients.ngsi_ld.cb import ContextBrokerLDClient
from filip.models.base import FiwareLDHeader, core_context
from filip.models.ngsi_ld.context import ActionTypeLD, ContextLDEntityKeyValues
from tests.config import settings
import requests
from filip.utils.cleanup import clear_context_broker_ld


# Setting up logging
logging.basicConfig(
    level="ERROR", format="%(asctime)s %(name)s %(levelname)s: %(message)s"
)


class TestContextBroker(unittest.TestCase):
    """
    Test class for ContextBrokerClient
    """

    def setUp(self) -> None:
        """
        Setup test data
        Returns:
            None
        """
        self.resources = {
            "entities_url": "/ngsi-ld/v1/entities",
            "types_url": "/ngsi-ld/v1/types",
        }
        self.attr = {"testtemperature": 20.0}
        self.entity = ContextLDEntityKeyValues(
            id="urn:ngsi-ld:my:id4", type="MyType", **self.attr
        )
        self.entity_2 = ContextLDEntityKeyValues(id="urn:ngsi-ld:room2", type="room")
        self.fiware_header = FiwareLDHeader(ngsild_tenant=settings.FIWARE_SERVICE)
        # Set up retry strategy
        session = Session()
        retry_strategy = Retry(
            total=5,  # Maximum number of retries
            backoff_factor=1,  # Exponential backoff (1, 2, 4, 8, etc.)
            status_forcelist=[
                429,
                500,
                502,
                503,
                504,
            ],  # Retry on these HTTP status codes
        )
        # Set the HTTP adapter with retry strategy
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        self.client = ContextBrokerLDClient(
            fiware_header=self.fiware_header, session=session, url=settings.LD_CB_URL
        )
        clear_context_broker_ld(cb_ld_client=self.client)

    def tearDown(self) -> None:
        """
        Cleanup test server
        """
        clear_context_broker_ld(cb_ld_client=self.client)
        self.client.close()

    def test_post_entity(self):
        """
        Post an entity.
        Args:
            - Entity{
                @context: LdContext{}
                location: GeoProperty{}
                observationSpace: GeoProperty{}
                operationSpace: GeoProperty{}
                id: string($uri) required
                type: Name(string) required
                (NGSI-LD Name)
                createdAt: string($date-time)
                modifiedAt: string($date_time)
                <*>: Property{}
                     Relationship{}
                     GeoProperty{}
            }
        Returns:
            - (201) Created. Contains the resource URI of the created Entity
            - (400) Bad request.
            - (409) Already exists.
            - (422) Unprocessable Entity.
        Tests:
            - Post an entity -> Does it return 201?
            - Post an entity again -> Does it return 409?
            - Post an entity without requires args -> Does it return 422?
            - Post entity from class with default value
        """
        # create entity
        self.client.post_entity(entity=self.entity)
        entity_list = self.client.get_entity_list(
            entity_type=self.entity.type, options="keyValues"
        )
        self.assertEqual(len(entity_list), 1)
        self.assertEqual(entity_list[0].id, self.entity.id)
        self.assertEqual(entity_list[0].type, self.entity.type)
        self.assertEqual(entity_list[0].testtemperature, self.entity.testtemperature)

        # existed entity
        self.entity_identical = self.entity.model_copy()
        with self.assertRaises(requests.exceptions.HTTPError) as contextmanager:
            self.client.post_entity(entity=self.entity_identical)
        response = contextmanager.exception.response
        self.assertEqual(response.status_code, 409)
        entity_list = self.client.get_entity_list(
            entity_type=self.entity_identical.type, options="keyValues"
        )
        self.assertEqual(len(entity_list), 1)

        # append new attribute to existed entity
        self.entity_append = self.entity.model_copy()
        del self.entity_append.testtemperature
        self.entity_append.humidity = 50
        self.client.post_entity(entity=self.entity_append, append=True)
        entity_append_res = self.client.get_entity(
            entity_id=self.entity_append.id, options="keyValues"
        )
        self.assertEqual(entity_append_res.humidity, self.entity_append.humidity)
        self.assertEqual(entity_append_res.testtemperature, self.entity.testtemperature)

        # override existed entity
        new_attr = {"newattr": 999}
        self.entity_override = ContextLDEntityKeyValues(
            id=self.entity.id, type=self.entity.type, **new_attr
        )
        self.client.post_entity(entity=self.entity_override, update=True)
        entity_override_res = self.client.get_entity(
            entity_id=self.entity.id, options="keyValues"
        )
        self.assertEqual(entity_override_res.newattr, self.entity_override.newattr)
        self.assertNotIn("testtemperature", entity_override_res.model_dump())

        # post without entity type is not allowed
        with self.assertRaises(Exception):
            self.client.post_entity(ContextLDEntityKeyValues(id="room2"))
        entity_list = self.client.get_entity_list(options="keyValues")
        self.assertNotIn("room2", entity_list)

        # delete entity
        self.client.entity_batch_operation(
            entities=entity_list, action_type=ActionTypeLD.DELETE
        )

    def test_different_context(self):
        """
        Get entities with different contexts.
        Returns:
        """
        temperature_sensor_dict = {
            "id": "urn:ngsi-ld:temperatureSensor",
            "type": "TemperatureSensor",
            "temperature": 23,
        }

        # client with custom context
        custom_context = (
            "https://n5geh.github.io/n5geh.test-context.io/context_saref.jsonld"
        )
        custom_header = FiwareLDHeader(
            ngsild_tenant=settings.FIWARE_SERVICE,
        )
        custom_header.set_context(custom_context)
        client_custom_context = ContextBrokerLDClient(
            fiware_header=custom_header, url=settings.LD_CB_URL
        )

        # default context
        temperature_sensor = ContextLDEntityKeyValues(**temperature_sensor_dict)
        self.client.post_entity(entity=temperature_sensor)
        entity_default = self.client.get_entity(entity_id=temperature_sensor.id)
        self.assertEqual(entity_default.context, core_context)
        self.assertEqual(
            entity_default.id,
            temperature_sensor_dict["id"],
        )
        self.assertEqual(
            entity_default.type,
            temperature_sensor_dict["type"],
        )
        self.assertEqual(
            entity_default.temperature.value,
            temperature_sensor_dict["temperature"],
        )
        entity_custom_context = client_custom_context.get_entity(
            entity_id=temperature_sensor.id
        )
        self.assertEqual(entity_custom_context.context, custom_context)
        self.assertEqual(
            entity_custom_context.id,
            temperature_sensor_dict["id"],
        )
        self.assertEqual(
            entity_custom_context.type,
            temperature_sensor_dict["type"],
        )
        self.assertEqual(
            entity_custom_context.temperature.value,
            temperature_sensor_dict["temperature"],
        )
        self.client.delete_entity_by_id(entity_id=temperature_sensor.id)

        # custom context in client
        temperature_sensor = ContextLDEntityKeyValues(**temperature_sensor_dict)
        client_custom_context.post_entity(entity=temperature_sensor)
        entity_custom = client_custom_context.get_entity(
            entity_id=temperature_sensor.id
        )
        self.assertEqual(entity_custom.context, custom_context)
        self.assertEqual(
            entity_custom_context.id,
            temperature_sensor_dict["id"],
        )
        self.assertEqual(
            entity_custom_context.type,
            temperature_sensor_dict["type"],
        )
        self.assertEqual(
            entity_custom_context.temperature.value,
            temperature_sensor_dict["temperature"],
        )
        entity_default_context = self.client.get_entity(entity_id=temperature_sensor.id)
        self.assertEqual(entity_default_context.context, core_context)
        self.assertNotEqual(
            entity_default_context.model_dump(exclude_unset=True, exclude={"context"}),
            temperature_sensor_dict,
        )
        client_custom_context.delete_entity_by_id(entity_id=temperature_sensor.id)

        # custom context in entity
        temperature_sensor = ContextLDEntityKeyValues(
            **dict(
                {
                    "@context": [
                        "https://n5geh.github.io/n5geh.test-context.io/context_saref.jsonld"
                    ]
                }
            ),
            **temperature_sensor_dict,
        )

        self.client.post_entity(entity=temperature_sensor)
        entity_custom = client_custom_context.get_entity(
            entity_id=temperature_sensor.id
        )
        self.assertEqual(entity_custom.context, custom_context)
        self.assertEqual(
            entity_custom_context.id,
            temperature_sensor_dict["id"],
        )
        self.assertEqual(
            entity_custom_context.type,
            temperature_sensor_dict["type"],
        )
        self.assertEqual(
            entity_custom_context.temperature.value,
            temperature_sensor_dict["temperature"],
        )
        entity_default_context = self.client.get_entity(entity_id=temperature_sensor.id)
        self.assertEqual(entity_default_context.context, core_context)
        self.assertNotEqual(
            entity_default_context.model_dump(exclude_unset=True, exclude={"context"}),
            temperature_sensor_dict,
        )
        self.client.delete_entity_by_id(entity_id=temperature_sensor.id)

    def test_add_attributes_entity(self):
        """
        Append new Entity attributes to an existing Entity within an NGSI-LD system.
        Args:
            - entityID(string): Entity ID; required
            - options(string): Indicates that no attribute overwrite shall be performed.
                Available values: noOverwrite
        Returns:
            - (204) No Content
            - (207) Partial Success. Only the attributes included in the response payload were successfully appended.
            - (400) Bad Request
            - (404) Not Found
        Tests:
            - Post an entity and add an attribute. Test if the attribute is added when Get is done.
            - Try to add an attribute to an non existent entity -> Return 404
            - Try to overwrite an attribute even though noOverwrite option is used
        """
        """
        Test 1:
            post an entity with entity_ID and entity_type
            add attribute to the entity with entity_ID
            get entity with entity_ID and new attribute
            Is new attribute not added to enitity ? 
                yes:
                    Raise Error
        Test 2: 
            add attribute to an non existent entity
            Raise Error
        Test 3:
            post an entity with entity_ID, entity_type, entity_attribute
            add attribute that already exists with noOverwrite
                Raise Error
            get entity and compare previous with entity attributes
            If attributes are different?
                Raise Error
        """
        """Test 1"""
        self.client.post_entity(self.entity)

        self.entity.test_value = 20
        self.client.append_entity_attributes(self.entity)

        entity = self.client.get_entity(entity_id=self.entity.id, options="keyValues")
        self.assertEqual(first=entity.test_value, second=self.entity.test_value)
        self.client.delete_entity_by_id(entity_id=entity.id)

        """Test 2"""
        with self.assertRaises(Exception):
            self.entity.test_value = 20
            self.client.append_entity_attributes(self.entity)
        time.sleep(1)

        """Test 3"""
        self.client.post_entity(self.entity)
        # What makes an property/ attribute unique ???

        self.entity.test_value = 20
        self.client.append_entity_attributes(self.entity)
        self.entity.test_value = 40

        with self.assertRaises(RequestException):
            self.client.append_entity_attributes(self.entity, options="noOverwrite")
        entity = self.client.get_entity(entity_id=self.entity.id, options="keyValues")
        self.assertEqual(first=entity.test_value, second=20)
        self.assertNotEqual(first=entity.test_value, second=40)

    def test_delete_entity_attribute(self):
        """
        Delete existing Entity atrribute within an NGSI-LD system.
        Args:
            - entityId: Entity Id; required
            - attrId: Attribute Id; required
        Returns:
            - (204) No Content
            - (400) Bad Request
            - (404) Not Found
        Tests:
            - Post an entity with attributes. Try to delete non existent attribute with non existent attribute
                id. Then check response code.
            - Post an entity with attributes. Try to delete one the attributes. Test if the attribute is really
                removed by either posting the entity or by trying to delete it again.
        """
        """
        Test 1: 
            post an enitity with entity_ID, entity_type and attribute with attribute_ID
            delete an attribute with an non existent attribute_ID of the entity with the entity_ID
                Raise Error
        Test 2:
            post an entity with entity_ID, entitiy_name and attribute with attribute_ID
            delete the attribute with the attribute_ID of the entity with the entity_ID
            get entity with entity_ID 
            If attribute with attribute_ID is still there?
                Raise Error
            delete the attribute with the attribute_ID of the entity with the entity_ID
                Raise Error
        """
        """Test 1"""

        self.entity.test_value = 20
        self.client.post_entity(entity=self.entity)
        with self.assertRaises(Exception):
            self.client.delete_attribute(
                entity_id=self.entity.id, attribute_id="does_not_exist"
            )
        self.client.delete_entity_by_id(entity_id=self.entity.id)

        """Test 2"""
        self.entity.test_value = 20
        self.client.post_entity(entity=self.entity)
        self.client.delete_attribute(
            entity_id=self.entity.id, attribute_id="test_value"
        )
        entity_response = self.client.get_entity(entity_id=self.entity.id)
        self.assertNotIn("test_value", entity_response.model_dump())
        with self.assertRaises(requests.exceptions.HTTPError) as contextmanager:
            self.client.delete_attribute(
                entity_id=self.entity.id, attribute_id="test_value"
            )
        response = contextmanager.exception.response
        self.assertEqual(response.status_code, 404)

    def test_replacing_attributes(self):
        """
        Patch existing Entity attributes within an NGSI-LD system.
        Args:
            - entityId: Entity Id; required
        Returns:
            - (204) No Content
            - (400) Bad Request
            - (404) Not Found
        Tests:
            - Post an entity with attribute. Change the attributes with patch.
        """
        """
        Test 1:
            replace attribute with same name and different value
        Test 2:
            replace two attributes
        """

        """Test 1"""
        self.entity.test_value = 20
        self.client.post_entity(entity=self.entity)
        entity = self.client.get_entity(entity_id=self.entity.id, options="keyValues")
        prop_dict = entity.model_dump()
        self.assertIn("test_value", prop_dict)
        self.assertEqual(prop_dict["test_value"], 20)

        del self.entity.test_value
        self.entity.test_value = 44
        self.client.replace_existing_attributes_of_entity(entity=self.entity)
        entity = self.client.get_entity(entity_id=self.entity.id, options="keyValues")
        prop_dict = entity.model_dump()
        self.assertIn("test_value", prop_dict)
        self.assertEqual(prop_dict["test_value"], 44)

        self.client.delete_entity_by_id(entity_id=self.entity.id)

        """Test 2"""
        self.entity.test_value = 20
        self.entity.my_value = 44
        self.client.post_entity(entity=self.entity)
        entity = self.client.get_entity(entity_id=self.entity.id, options="keyValues")
        prop_dict = entity.model_dump()
        self.assertIn("test_value", prop_dict)
        self.assertEqual(prop_dict["test_value"], 20)
        self.assertIn("my_value", prop_dict)
        self.assertEqual(prop_dict["my_value"], 44)

        del self.entity.test_value
        del self.entity.my_value
        self.entity.test_value = 25
        self.entity.my_value = 45
        self.client.replace_existing_attributes_of_entity(entity=self.entity)
        entity = self.client.get_entity(entity_id=self.entity.id, options="keyValues")
        prop_dict = entity.model_dump()
        self.assertIn("test_value", prop_dict)
        self.assertEqual(prop_dict["test_value"], 25)
        self.assertIn("my_value", prop_dict)
        self.assertEqual(prop_dict["my_value"], 45)


class EntitiesBatchOperations(unittest.TestCase):
    """
    Test class for entity endpoints.
    Args:
        unittest (_type_): _description_
    """

    def setUp(self) -> None:
        """
        Setup test data
        Returns:
            None
        """
        self.r = Random()
        self.fiware_header = FiwareLDHeader(ngsild_tenant=settings.FIWARE_SERVICE)
        self.cb_client = ContextBrokerLDClient(
            fiware_header=self.fiware_header, url=settings.LD_CB_URL
        )
        clear_context_broker_ld(cb_ld_client=self.cb_client)

    def tearDown(self) -> None:
        """
        Cleanup test server
        """
        clear_context_broker_ld(cb_ld_client=self.cb_client)
        self.cb_client.close()

    def test_entity_batch_operations_create(self) -> None:
        """
        Batch Entity creation.
        Args:
            - Request body(Entity List); required
        Returns:
            - (200) Success
            - (400) Bad Request
        Tests:
            - Post the creation of batch entities. Check if each of the created entities exists and if all attributes exist.
        """
        """
        Test 1:
            post create batch entity 
            get entity list
            for all elements in entity list: 
                if entity list element != batch entity element:
                    Raise Error
        Test 2: 
            post create batch entity with two entities that have the same id
            post in try block
            no exception raised
            check if the entities list only contains one element (No duplicates)
            if not raise assert
        """
        """Test 1"""
        entities_a = [
            ContextLDEntityKeyValues(
                id=f"urn:ngsi-ld:test:{str(i)}",
                type=f"filip:object:test",
                temperature=i,
            )
            for i in range(0, 10)
        ]
        self.cb_client.entity_batch_operation(
            entities=entities_a, action_type=ActionTypeLD.CREATE
        )
        entity_list = self.cb_client.get_entity_list(
            entity_type=f"filip:object:test", options="keyValues"
        )
        id_list = [entity.id for entity in entity_list]
        self.assertEqual(len(entities_a), len(entity_list))
        for entity in entities_a:
            self.assertIsInstance(entity, ContextLDEntityKeyValues)
            self.assertIn(entity.id, id_list)
        for entity in entity_list:
            self.cb_client.delete_entity_by_id(entity_id=entity.id)

        """Test 2"""
        entities_b = [
            ContextLDEntityKeyValues(
                id=f"urn:ngsi-ld:test:eins", type=f"filip:object:test"
            ),
            ContextLDEntityKeyValues(
                id=f"urn:ngsi-ld:test:eins", type=f"filip:object:test"
            ),
        ]
        entity_list_b = []
        try:
            self.cb_client.entity_batch_operation(
                entities=entities_b, action_type=ActionTypeLD.CREATE
            )
            entity_list_b = self.cb_client.get_entity_list(
                entity_type=f"filip:object:test", options="keyValues"
            )
            self.assertEqual(len(entity_list), 1)
        except:
            pass
        finally:
            for entity in entity_list_b:
                self.cb_client.delete_entity_by_id(entity_id=entity.id)

    def test_entity_batch_operations_update(self) -> None:
        """
        Batch Entity update.
        Args:
            - options(string): Available values: noOverwrite
            - Request body(EntityList); required
        Returns:
            - (200) Success
            - (400) Bad Request
        Tests:
            - Post the update of batch entities. Check if each of the updated entities exists and if the updates appear.
            - Try the same with the noOverwrite statement and check if the nooverwrite is acknowledged.
        """
        """
        Test 1:
            post create entity batches
            post update of batch entity 
            get entities
            for all entities in entity list: 
                if entity list element != updated batch entity element:
                    Raise Error
        Test 2: 
            post create entity batches
            post update of batch entity with no overwrite
            get entities
            for all entities in entity list: 
                if entity list element != updated batch entity element but not the existings are overwritten:
                    Raise Error

        """
        """Test 1"""
        entities_a = [
            ContextLDEntityKeyValues(
                id=f"urn:ngsi-ld:test:{str(i)}",
                type=f"filip:object:test",
                **{"temperature": self.r.randint(20, 50)},
            )
            for i in range(0, 5)
        ]

        self.cb_client.entity_batch_operation(
            entities=entities_a, action_type=ActionTypeLD.CREATE
        )

        entities_update = [
            ContextLDEntityKeyValues(
                id=f"urn:ngsi-ld:test:{str(i)}",
                type=f"filip:object:test",
                **{"temperature": self.r.randint(0, 20)},
            )
            for i in range(3, 6)
        ]
        self.cb_client.entity_batch_operation(
            entities=entities_update, action_type=ActionTypeLD.UPDATE
        )
        entity_list = self.cb_client.get_entity_list(
            entity_type=f"filip:object:test", options="keyValues"
        )
        self.assertEqual(len(entity_list), 5)
        updated = [
            x.model_dump(exclude_unset=True, exclude={"context"})
            for x in entity_list
            if int(x.id.split(":")[3]) in range(3, 5)
        ]
        nupdated = [
            x.model_dump(exclude_unset=True, exclude={"context"})
            for x in entity_list
            if int(x.id.split(":")[3]) in range(0, 3)
        ]

        self.assertCountEqual(
            [entity.model_dump(exclude_unset=True) for entity in entities_a[0:3]],
            nupdated,
        )

        self.assertCountEqual(
            [entity.model_dump(exclude_unset=True) for entity in entities_update[0:2]],
            updated,
        )

        """Test 2"""
        # presssure will be appended while the existing temperature will
        # not be overwritten
        entities_update = [
            ContextLDEntityKeyValues(
                id=f"urn:ngsi-ld:test:{str(i)}",
                type=f"filip:object:test",
                **{
                    "temperature": self.r.randint(50, 100),
                    "pressure": self.r.randint(1, 100),
                },
            )
            for i in range(0, 5)
        ]

        self.cb_client.entity_batch_operation(
            entities=entities_update,
            action_type=ActionTypeLD.UPDATE,
            options="noOverwrite",
        )

        previous = entity_list
        previous.sort(key=lambda x: int(x.id.split(":")[3]))

        entity_list = self.cb_client.get_entity_list(
            entity_type=f"filip:object:test", options="keyValues"
        )
        entity_list.sort(key=lambda x: int(x.id.split(":")[3]))

        self.assertEqual(len(entity_list), len(entities_update))

        for updated, entity, prev in zip(entities_update, entity_list, previous):
            self.assertEqual(
                updated.model_dump().get("pressure"),
                entity.model_dump().get("pressure"),
            )
            self.assertNotEqual(
                updated.model_dump().get("temperature"),
                entity.model_dump().get("temperature"),
            )
            self.assertEqual(
                prev.model_dump().get("temperature"),
                entity.model_dump().get("temperature"),
            )

        with self.assertRaises(HTTPError):
            self.cb_client.entity_batch_operation(
                entities=[], action_type=ActionTypeLD.UPDATE
            )

        # according to spec, this should raise bad request data,
        # but pydantic is intercepting
        with self.assertRaises(ValidationError):
            self.cb_client.entity_batch_operation(
                entities=[None], action_type=ActionTypeLD.UPDATE
            )

        for entity in entity_list:
            self.cb_client.delete_entity_by_id(entity_id=entity.id)

    def test_entity_batch_operations_upsert(self) -> None:
        """
        Batch Entity upsert.
        Args:
            - options(string): Available values: replace, update
            - Request body(EntityList); required
        Returns:
            - (200) Success
            - (400) Bad request
        Tests:
            - Post entity list and then post the upsert with update and replace.
            - Get the entitiy list and see if the results are correct.

        """
        """
        Test 1: 
            post a create entity batch b0 with attr a0
            post entity upsert batch b1 with attr a1 with update, b0 ∩ b1 != ∅
            post entity upsert batch b2 with attr a1 with replace, b0 ∩ b2 != ∅ && b1 ∩ b2 == ∅
            get entity list
            for e in entity list:
                if e in b0 ∩ b1:
                    e should contain a1 and a0
                if e in b0 ∩ b2:
                    e should contain only a1
                else:
                    e should contain only a0
        """
        """Test 1"""
        # create entities 1 -3
        entities_a = [
            ContextLDEntityKeyValues(
                id=f"urn:ngsi-ld:test:{str(i)}",
                type=f"filip:object:test",
                **{"temperature": self.r.randint(0, 20)},
            )
            for i in range(1, 4)
        ]
        self.cb_client.entity_batch_operation(
            entities=entities_a, action_type=ActionTypeLD.CREATE
        )

        # replace entities 0 - 1
        entities_replace = [
            ContextLDEntityKeyValues(
                id=f"urn:ngsi-ld:test:{str(i)}",
                type=f"filip:object:test",
                **{"pressure": self.r.randint(50, 100)},
            )
            for i in range(0, 2)
        ]
        self.cb_client.entity_batch_operation(
            entities=entities_replace,
            action_type=ActionTypeLD.UPSERT,
            options="replace",
        )

        # update entities 3 - 4,
        # pressure will be appended for 3
        # temperature will be appended for 4
        entities_update = [
            ContextLDEntityKeyValues(
                id=f"urn:ngsi-ld:test:{str(i)}",
                type=f"filip:object:test",
                **{"pressure": self.r.randint(50, 100)},
            )
            for i in range(3, 5)
        ]
        self.cb_client.entity_batch_operation(
            entities=entities_update, action_type=ActionTypeLD.UPSERT, options="update"
        )

        # 0,1 and 4 should have pressure only
        # 2 should have temperature only
        # 3 should have both
        # can be made modular for variable size batches
        entity_list = self.cb_client.get_entity_list(options="keyValues")
        self.assertEqual(len(entity_list), 5)
        for _e in entity_list:
            _id = int(_e.id.split(":")[3])
            e = _e.model_dump(exclude_unset=True, exclude={"context"})
            if _id in [0, 1]:
                self.assertIsNone(e.get("temperature", None))
                self.assertIsNotNone(e.get("pressure", None))
                self.assertCountEqual(
                    [e],
                    [
                        x.model_dump(exclude_unset=True)
                        for x in entities_replace
                        if x.id == _e.id
                    ],
                )
            elif _id == 4:
                self.assertIsNone(e.get("temperature", None))
                self.assertIsNotNone(e.get("pressure", None))
                self.assertCountEqual(
                    [e],
                    [
                        x.model_dump(exclude_unset=True)
                        for x in entities_update
                        if x.id == _e.id
                    ],
                )
            elif _id == 2:
                self.assertIsNone(e.get("pressure", None))
                self.assertIsNotNone(e.get("temperature", None))
                self.assertCountEqual(
                    [e],
                    [
                        x.model_dump(exclude_unset=True)
                        for x in entities_a
                        if x.id == _e.id
                    ],
                )
            elif _id == 3:
                self.assertIsNotNone(e.get("temperature", None))
                self.assertIsNotNone(e.get("pressure", None))
                self.assertCountEqual(
                    [e.get("temperature")],
                    [
                        x.model_dump(exclude_unset=True).get("temperature")
                        for x in entities_a
                        if x.id == _e.id
                    ],
                )
                self.assertCountEqual(
                    [e.get("pressure")],
                    [
                        x.model_dump(exclude_unset=True).get("pressure")
                        for x in entities_update
                        if x.id == _e.id
                    ],
                )

        for entity in entity_list:
            self.cb_client.delete_entity_by_id(entity_id=entity.id)

    def test_entity_batch_operations_delete(self) -> None:
        """
        Batch entity delete.
        Args:
            - Request body(string list); required
        Returns
            - (200) Success
            - (400) Bad request
        Tests:
            - Try to delete non existent entity.
            - Try to delete existent entity and check if it is deleted.
        """
        """
        Test 1:
            delete batch entity that is non existent
            if return != 400: 
                Raise Error
        Test 2: 
            post batch entity
            delete batch entity
            if return != 200: 
                Raise Error
            get entity list
            if batch entities are still on entity list:
                Raise Error:
        """
        """Test 1"""
        entities_delete = [
            ContextLDEntityKeyValues(
                id=f"urn:ngsi-ld:test:{str(i)}", type=f"filip:object:test"
            )
            for i in range(0, 1)
        ]
        with self.assertRaises(Exception):
            self.cb_client.entity_batch_operation(
                entities=entities_delete, action_type=ActionTypeLD.DELETE
            )

        """Test 2"""
        entity_del_type = "filip:object:test"
        entities_ids_a = [f"urn:ngsi-ld:test:{str(i)}" for i in range(0, 4)]
        entities_a = [
            ContextLDEntityKeyValues(id=id_a, type=entity_del_type)
            for id_a in entities_ids_a
        ]

        self.cb_client.entity_batch_operation(
            entities=entities_a, action_type=ActionTypeLD.CREATE
        )

        entities_delete = [
            ContextLDEntityKeyValues(id=id_a, type=entity_del_type)
            for id_a in entities_ids_a[:3]
        ]
        entities_delete_ids = [entity.id for entity in entities_delete]

        # send update to delete entities
        self.cb_client.entity_batch_operation(
            entities=entities_delete, action_type=ActionTypeLD.DELETE
        )

        # get list of entities which is still stored
        entity_list = self.cb_client.get_entity_list(
            entity_type=entity_del_type, options="keyValues"
        )
        entity_ids = [entity.id for entity in entity_list]

        self.assertEqual(len(entity_list), 1)  # all but one entity were deleted

        for entityId in entity_ids:
            self.assertIn(entityId, entities_ids_a)
        for entityId in entities_delete_ids:
            self.assertNotIn(entityId, entity_ids)
        for entity in entity_list:
            self.cb_client.delete_entity_by_id(entity_id=entity.id)

        entity_list = self.cb_client.get_entity_list(
            entity_type=entity_del_type, options="keyValues"
        )
        self.assertEqual(len(entity_list), 0)  # all entities were deleted
