import unittest
from pydantic import ValidationError

from filip.clients.ngsi_ld.cb import ContextBrokerLDClient
from filip.models.base import FiwareLDHeader
from filip.utils.cleanup import clear_all, clean_test
from tests.config import settings
from filip.models.ngsi_ld.context import \
    ContextLDEntity, \
    ContextProperty, \
    NamedContextProperty, \
    ActionTypeLD
import requests
from tests.config import settings


class TestEntities(unittest.TestCase):
    """
    Test class for entity endpoints.
    """

    def cleanup(self):
        """
        Cleanup entities from test server
        """
        entity_test_types = [ self.entity.type, self.entity_2.type ]
        for entity_type in entity_test_types:
            entity_list = self.cb_client.get_entity_list(entity_type=entity_type)
            for entity in entity_list:
                self.cb_client.delete_entity_by_id(entity_id=entity.id)

    def setUp(self) -> None:
        """
        Setup test data
        Returns:
            None
        """
        self.fiware_header = FiwareLDHeader(ngsild_tenant=settings.FIWARE_SERVICE)
        self.cb_client = ContextBrokerLDClient(fiware_header=self.fiware_header,
                                            url=settings.LD_CB_URL)
        self.http_url = "https://test.de:80"
        self.mqtt_url = "mqtt://test.de:1883"
        self.mqtt_topic = '/filip/testing'

        #CB_URL = "http://localhost:1026"
        CB_URL = "http://137.226.248.200:1027"

        self.attr = {'testtemperature': {'value': 20.0}}
        self.entity = ContextLDEntity(id='urn:ngsi-ld:my:id', type="MyType", **self.attr)
        self.entity_2 = ContextLDEntity(id="urn:ngsi-ld:room2", type="room")
        self.cleanup()

    def tearDown(self) -> None:
        self.cleanup()

    def test_get_entites(self):
        """
        Retrieve a set of entities which matches a specific query from an NGSI-LD system
        Args: 
            - id(string): Comma separated list of URIs to be retrieved
            - idPattern(string): Regular expression that must be matched by Entity ids
            - type(string): Comma separated list of Entity type names to be retrieved
            - attrs(string): Comma separated list of attribute names (properties or relationships) to be retrieved
            - q(string): Query
            - georel: Geo-relationship
            - geometry(string): Geometry; Available values : Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon
            - coordinates: Coordinates serialized as a string
            - geoproperty(string): The name of the property that contains the geo-spatial data that will be used to resolve the geoquery
            - csf(string): Context Source Filter
            - limit(integer): Pagination limit
            - options(string): Options dictionary; Available values : keyValues, sysAttrs
        """
        entity_list = self.cb_client.get_entity_list()
        self.assertEqual(len(entity_list), 0)

        self.cb_client.post_entity(entity=self.entity)
        entity_list_idpattern = self.cb_client.get_entity_list(id_pattern="urn:ngsi-ld:my*")
        self.assertEqual(len(entity_list_idpattern), 1)
        self.assertEqual(entity_list_idpattern[0].id, self.entity.id)

        entity_list_attrs = self.cb_client.get_entity_list(attrs=["testtemperature"])
        self.assertEqual(len(entity_list_attrs), 1)
        self.assertEqual(entity_list_attrs[0].id, self.entity.id)

    
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
        """
        """
        Test 1:
            Post enitity with entity_ID and entity_type
            if return != 201:
                Raise Error
            Get entity list
            If entity with entity_ID is not on entity list:
                Raise Error
        Test 2: 
            Post entity with entity_ID and entity_type
            Post entity with the same entity_ID and entity_type as before
            If return != 409: 
                Raise Error
            Get entity list
            If there are duplicates on entity list:
                Raise Error
        Test 3: 
            Post an entity with an entity_ID and without an entity_type 
            If return != 422:
                Raise Error
            Get entity list 
            If the entity list does contain the posted entity:
                Raise Error
        Test Additonal:
            post two entities with the same enitity id but different entity type-> should throw error.
        """
        """Test1"""
        self.cb_client.post_entity(entity=self.entity)
        entity_list = self.cb_client.get_entity_list(entity_type=self.entity.type)
        self.assertEqual(len(entity_list), 1)
        self.assertEqual(entity_list[0].id, self.entity.id)
        self.assertEqual(entity_list[0].type, self.entity.type)
        self.assertEqual(entity_list[0].testtemperature, self.entity.testtemperature.value)
        
        """Test2"""
        self.entity_identical= self.entity.model_copy()
        with self.assertRaises(requests.exceptions.HTTPError) as contextmanager:
            self.cb_client.post_entity(entity=self.entity_identical)
        response = contextmanager.exception.response
        self.assertEqual(response.status_code, 409)

        entity_list = self.cb_client.get_entity_list(entity_type=self.entity_identical.type)
        self.assertEqual(len(entity_list), 1)

        """Test3"""
        with self.assertRaises(Exception):
            self.cb_client.post_entity(ContextLDEntity(id="room2"))
        entity_list = self.cb_client.get_entity_list()
        self.assertNotIn("room2", entity_list)

        """delete"""
        self.cb_client.update(entities=entity_list, action_type=ActionTypeLD.DELETE)
    
    def test_get_entity(self):
        """
        Get an entity with an specific ID.
        Args:
            - entityID(string): Entity ID, required
            - attrs(string): Comma separated list of attribute names (properties or relationships) to be retrieved
            - type(string): Entity Type
            - options(string): Options dictionary; Available values : keyValues, sysAttrs
        Returns:
            - (200) Entity
            - (400) Bad request
            - (404) Not found
        Tests for get entity: 
            - Post entity and see if get entity with the same ID returns the entity
                with the correct values
            - Get entity with an ID that does not exit. See if Not found error is 
                raised
        """
        
        """
        Test 1:
            post entity_1 with entity_1_ID
            get enntity_1 with enity_1_ID
            compare if the posted entity_1 is the same as the get_enity_1
                If attributes posted entity.id !=  ID get entity:
                    Raise Error
                If type posted entity != type get entity:
                    Raise Error
        Test 2:
            get enitity with enitity_ID that does not exit
            If return != 404:
                Raise Error
        """
        """Test1"""
        self.cb_client.post_entity(entity=self.entity)
        ret_entity = self.cb_client.get_entity(entity_id=self.entity.id)
        ret_entity_with_type = self.cb_client.get_entity(entity_id=self.entity.id, entity_type=self.entity.type)
        ret_entity_keyValues = self.cb_client.get_entity(entity_id=self.entity.id, options="keyValues")
        ret_entity_sysAttrs = self.cb_client.get_entity(entity_id=self.entity.id, options="sysAttrs")

        self.assertEqual(ret_entity.id,self.entity.id)
        self.assertEqual(ret_entity.type,self.entity.type)
        self.assertEqual(ret_entity_with_type.id,self.entity.id)
        self.assertEqual(ret_entity_with_type.type,self.entity.type)
        self.assertEqual(ret_entity_keyValues.id,self.entity.id)
        self.assertEqual(ret_entity_keyValues.type,self.entity.type)
        self.assertEqual(ret_entity_sysAttrs.id,self.entity.id)
        self.assertEqual(ret_entity_sysAttrs.type,self.entity.type)
        self.assertNotEqual(ret_entity_sysAttrs.createdAt, None)

        """Test2"""
        with self.assertRaises(requests.exceptions.HTTPError) as contextmanager:
            self.cb_client.get_entity("urn:roomDoesnotExist")
        response = contextmanager.exception.response
        self.assertEqual(response.status_code, 404)

        with self.assertRaises(requests.exceptions.HTTPError) as contextmanager:
            self.cb_client.get_entity("roomDoesnotExist")
        response = contextmanager.exception.response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Not a URL nor a URN")
    
    # TODO: write test which tries to delete entity with id AND type
    # for orion-ld version 1.4.0, error BadRequestData (title: Unsupported URI parameter) happens
    # def test_delete_entity_with_type(self):

    def test_delete_entity(self):
        """
        Removes an specific Entity from an NGSI-LD system.
        Args:
            - entityID(string): Entity ID; required
            - type(string): Entity Type
        Returns: 
            - (204) No Content. The entity was removed successfully.
            - (400) Bad request.
            - (404) Not found.
        Tests:
            - Try to delete an non existent entity -> Does it return a Not found?
            - Post an entity and try to delete the entity -> Does it return 204?
            - Try to get to delete an deleted entity -> Does it return 404?
        """

        """
        Test 1:
            delete entity with non existent entity_ID
            If return != 404:
                Raise Error
        
        Test 2: 
            post an entity with entity_ID and entity_type
            delete entity with entity_ID
            get entity list 
            If entity with entity_ID in entity list:
                Raise Error
        
        Test 3: 
            delete entity with entity_ID 
                return != 404 ? 
                    yes: 
                        Raise Error
        """
            
        """Test1"""
        # try to delete nonexistent entity
        with self.assertRaises(requests.exceptions.HTTPError) as contextmanager:
            self.cb_client.get_entity(entity_id=self.entity.id)
        response = contextmanager.exception.response
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["title"], "Entity Not Found")

        """Test2"""
        self.cb_client.post_entity(entity=self.entity)
        self.cb_client.post_entity(entity=self.entity_2)
        entity_list = self.cb_client.get_entity_list()
        entity_ids = [entity.id for entity in entity_list]
        self.assertIn(self.entity.id, entity_ids)

        self.cb_client.delete_entity_by_id(entity_id=self.entity.id)
        entity_list = self.cb_client.get_entity_list()
        entity_ids = [entity.id for entity in entity_list]
        self.assertNotIn(self.entity.id, entity_ids)
        self.assertIn(self.entity_2.id, entity_ids)

        """Test3"""
        # entity was already deleted
        with self.assertRaises(requests.exceptions.HTTPError) as contextmanager:
            self.cb_client.get_entity(entity_id=self.entity.id)
        response = contextmanager.exception.response
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["title"], "Entity Not Found")
    
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
        self.cb_client.post_entity(self.entity)
        attr = ContextProperty(**{'value': 20, 'unitCode': 'Number'})
        # noOverwrite Option missing ???
        self.entity.add_properties({"test_value": attr})
        self.cb_client.append_entity_attributes(self.entity)
        entity_list = self.cb_client.get_entity_list()
        for entity in entity_list:
            self.assertEqual(first=entity.test_value, second=attr.value)
        for entity in entity_list:
            self.cb_client.delete_entity_by_id(entity_id=entity.id)
        
        """Test 2"""
        attr = ContextProperty(**{'value': 20, 'type': 'Number'})
        with self.assertRaises(Exception):
            self.entity.add_properties({"test_value": attr})
            self.cb_client.append_entity_attributes(self.entity)

            
        """Test 3"""
        self.cb_client.post_entity(self.entity)
        # What makes an property/ attribute unique ???
        attr = ContextProperty(**{'value': 20, 'type': 'Number'})
        attr_same = ContextProperty(**{'value': 40, 'type': 'Number'})
        
        self.entity.add_properties({"test_value": attr})
        self.cb_client.append_entity_attributes(self.entity)
        self.entity.add_properties({"test_value": attr_same})
        self.cb_client.append_entity_attributes(self.entity, options="noOverwrite")

        entity_list = self.cb_client.get_entity_list()
        for entity in entity_list:
            self.assertEqual(first=entity.test_value, second=attr.value)
        
        for entity in entity_list:
            self.cb_client.delete_entity_by_id(entity_id=entity.id)
        
    def test_patch_entity_attrs(self):
        """
        Update existing Entity attributes within an NGSI-LD system
        Args:
            - entityId(string): Entity ID; required
            - Request body; required
        Returns:
            - (201) Created. Contains the resource URI of the created Entity
            - (400) Bad request
            - (409) Already exists
            - (422) Unprocessable Entity
        Tests:
            - Post an enitity with specific attributes. Change the attributes with patch.
        """
        """
        Test 1:
            post an enitity with entity_ID and entity_type and attributes
            patch one of the attributes with entity_id by sending request body
            get entity list
            If new attribute is not added to the entity?
                Raise Error
        """
        """Test1"""
        new_prop = {'new_prop': ContextProperty(value=25)}
        newer_prop = NamedContextProperty(value=40, name='new_prop')
        
        self.entity.add_properties(new_prop)
        self.cb_client.post_entity(entity=self.entity)        
        self.cb_client.update_entity_attribute(entity_id=self.entity.id, attr=newer_prop, attr_name='new_prop')
        entity = self.cb_client.get_entity(entity_id=self.entity.id)
        prop_dict = entity.model_dump()
        self.assertIn("new_prop", prop_dict)
        self.assertEqual(prop_dict["new_prop"], 40)


    def test_patch_entity_attrs_contextprop(self):
        """
        Update existing Entity attributes within an NGSI-LD system
        Args:
            - entityId(string): Entity ID; required
            - Request body; required
        Returns:
            - (201) Created. Contains the resource URI of the created Entity
            - (400) Bad request
            - (409) Already exists
            - (422) Unprocessable Entity
        Tests:
            - Post an enitity with specific attributes. Change the attributes with patch.
        """
        """
        Test 1:
            post an enitity with entity_ID and entity_type and attributes
            patch one of the attributes with entity_id by sending request body
            get entity list
            If new attribute is not added to the entity?
                Raise Error
        """
        """Test1"""
        new_prop = {'new_prop': ContextProperty(value=25)}
        newer_prop = ContextProperty(value=55)

        self.entity.add_properties(new_prop)
        self.cb_client.post_entity(entity=self.entity)
        self.cb_client.update_entity_attribute(entity_id=self.entity.id, attr=newer_prop, attr_name='new_prop')
        entity = self.cb_client.get_entity(entity_id=self.entity.id)
        prop_dict = entity.model_dump()
        self.assertIn("new_prop", prop_dict)
        self.assertEqual(prop_dict["new_prop"], 55)

               
    def test_patch_entity_attrs_attrId(self):
        """
        Update existing Entity attribute ID within an NGSI-LD system
        Args: 
            - entityId(string): Entity Id; required
            - attrId(string): Attribute Id; required
        Returns: 
            - (204) No Content
            - (400) Bad Request
            - (404) Not Found
        Tests:
            - Post an enitity with specific attributes. Change the attributes with patch.
        """
        """
        Test 1: 
            post an entity with entity_ID, entity_type and attributes
            patch with entity_ID and attribute_ID 
            return != 204: 
                yes: 
                    Raise Error
        """
        """Test 1"""
        attr = NamedContextProperty(name="test_value", 
                                        value=20)
        self.entity.add_properties(attrs=[attr])
        self.cb_client.post_entity(entity=self.entity)

        attr.value = 40
        self.cb_client.update_entity_attribute(entity_id=self.entity.id, attr=attr, attr_name="test_value")
        entity = self.cb_client.get_entity(entity_id=self.entity.id)
        prop_dict = entity.model_dump()
        self.assertIn("test_value", prop_dict)
        self.assertEqual(prop_dict["test_value"], 40)


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
    
        attr = NamedContextProperty(name="test_value", 
                                        value=20)
        self.entity.add_properties(attrs=[attr])
        self.cb_client.post_entity(entity=self.entity)
        with self.assertRaises(Exception):
            self.cb_client.delete_attribute(entity_id=self.entity.id, attribute_id="does_not_exist")
        
        entity_list = self.cb_client.get_entity_list()
        
        for entity in entity_list:
            self.cb_client.delete_entity_by_id(entity_id=entity.id)    
            
        """Test 2"""
        attr = NamedContextProperty(name="test_value", 
                                        value=20)
        self.entity.add_properties(attrs=[attr])
        self.cb_client.post_entity(entity=self.entity)
        self.cb_client.delete_attribute(entity_id=self.entity.id, attribute_id="test_value")
        
        with self.assertRaises(requests.exceptions.HTTPError) as contextmanager:
            self.cb_client.delete_attribute(entity_id=self.entity.id, attribute_id="test_value")
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
        attr1 = NamedContextProperty(name="test_value", value=20)
        self.entity.add_properties(attrs=[attr1])
        self.cb_client.post_entity(entity=self.entity)
        entity = self.cb_client.get_entity(entity_id=self.entity.id)
        prop_dict = entity.model_dump()
        self.assertIn("test_value", prop_dict)
        self.assertEqual(prop_dict["test_value"], 20)

        attr2 = NamedContextProperty(name="test_value", value=44)
        self.entity.delete_properties(props=[attr1])
        self.entity.add_properties(attrs=[attr2])
        self.cb_client.replace_existing_attributes_of_entity(entity=self.entity)
        entity = self.cb_client.get_entity(entity_id=self.entity.id)
        prop_dict = entity.model_dump()
        self.assertIn("test_value", prop_dict)
        self.assertEqual(prop_dict["test_value"], 44)

        self.cb_client.delete_entity_by_id(entity_id=self.entity.id)

        """Test 2"""
        attr1 = NamedContextProperty(name="test_value", value=20)
        attr2 = NamedContextProperty(name="my_value", value=44)
        self.entity.add_properties(attrs=[attr1, attr2])
        self.cb_client.post_entity(entity=self.entity)
        entity = self.cb_client.get_entity(entity_id=self.entity.id)
        prop_dict = entity.model_dump()
        self.assertIn("test_value", prop_dict)
        self.assertEqual(prop_dict["test_value"], 20)
        self.assertIn("my_value", prop_dict)
        self.assertEqual(prop_dict["my_value"], 44)

        self.entity.delete_properties(props=[attr1])
        self.entity.delete_properties(props=[attr2])
        attr3 = NamedContextProperty(name="test_value", value=25)
        attr4 = NamedContextProperty(name="my_value", value=45)
        self.entity.add_properties(attrs=[attr3, attr4])
        self.cb_client.replace_existing_attributes_of_entity(entity=self.entity)
        entity = self.cb_client.get_entity(entity_id=self.entity.id)
        prop_dict = entity.model_dump()
        self.assertIn("test_value", prop_dict)
        self.assertEqual(prop_dict["test_value"], 25)
        self.assertIn("my_value", prop_dict)
        self.assertEqual(prop_dict["my_value"], 45)
