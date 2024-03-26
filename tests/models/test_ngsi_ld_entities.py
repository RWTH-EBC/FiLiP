import _json
import unittest
from pydantic import ValidationError
#from filip.clients.ngsi_v2.cb import ContextBrokerClient	

from filip.clients.ngsi_ld.cb import ContextBrokerLDClient
# from filip.models.ngsi_v2.subscriptions import \
#     Http, \
#     HttpCustom, \
#     Mqtt, \
#     MqttCustom, \
#     Notification, \
#     Subscription
from filip.models.base import FiwareLDHeader
from filip.utils.cleanup import clear_all, clean_test
from tests.config import settings
from filip.models.ngsi_ld.context import \
    ContextLDEntity, \
    ContextProperty, \
    ContextRelationship
import requests

class TestEntities(unittest.TestCase):
    """
    Test class for entity endpoints.
    """

    def setUp(self) -> None:
        """
        Setup test data
        Returns:
            None
        """
        # self.fiware_header = FiwareLDHeader(
        #     service=settings.FIWARE_SERVICE,
        #     service_path=settings.FIWARE_SERVICEPATH)
        self.fiware_header = FiwareLDHeader()
        self.http_url = "https://test.de:80"
        self.mqtt_url = "mqtt://test.de:1883"
        self.mqtt_topic = '/filip/testing'

        CB_URL = "http://localhost:1026"
        self.cb_client = ContextBrokerLDClient(url=CB_URL,
                                    fiware_header=self.fiware_header)
        

        self.attr = {'testtemperature': {'value': 20.0}}
        self.entity = ContextLDEntity(id='urn:ngsi-ld:my:id', type='MyType', **self.attr)
        #self.entity = ContextLDEntity(id="urn:ngsi-ld:room1", type="Room", data={})
        
        # self.entity = ContextLDEntity(id="urn:ngsi-ld:room1", type="Room", **room1_data)
        # self.entity = ContextLDEntity(id="urn:ngsi-ld:room1", 
                                    #   type="room",
                                    #   data={})
        self.entity_2 = ContextLDEntity(id="urn:ngsi-ld:room2",
                                        type="room",
                                      data={})
    

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
        pass
    
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
            Post enitity with entity_ID and entity_name
            if return != 201:
                Raise Error
            Get enitity list 
            If entity with entity_ID is not on entity list:
                Raise Error
        Test 2: 
            Post enitity with entity_ID and entity_name
            Post entity with the same entity_ID and entity_name as before
            If return != 409: 
                Raise Error
            Get enitity list
            If there are duplicates on enity list:
                Raise Error
        Test 3: 
            Post an entity with an entity_ID and without an entity_name 
            If return != 422:
                Raise Error
            Get entity list 
            If the entity list does contain the posted entity:
                Raise Error
        Test Additonal:
            post two entities with the same enitity id but different entity type-> should throw error.
        """
        """Test1"""
        ret_post = self.cb_client.post_entity(entity=self.entity)
        # Raise already done in cb
        entity_list = self.cb_client.get_entity_list()
        self.assertIn(self.entity, entity_list)   
        
        """Test2"""
        self.entity_identical= self.entity.model_copy()
        ret_post = self.cb_client.post_entity(entity=self.entity_identical)
        # What is gonna be the return? Is already an error being raised?
        entity_list = self.cb_client.get_entity_list()
        for element in entity_list: 
            self.assertNotEqual(element.id, self.entity.id)

        """Test3"""
        with self.assertRaises(Exception):
            self.cb_client.post_entity(ContextLDEntity(id="room2"))
        entity_list = self.cb_client.get_entity_list()
        self.assertNotIn("room2", entity_list)

        """delete"""
        self.cb_client.delete_entities(entities=entity_list)
    
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
        self.assertEqual(ret_entity.id,self.entity.id)
        self.assertEqual(ret_entity.type,self.entity.type)

        """Test2"""
        ret_entity = self.cb_client.get_entity("roomDoesnotExist")
        # Error should be raised in get_entity function
        if ret_entity:
            raise ValueError("There should not be any return.")

        """delete"""
        self.cb_client.delete_entity(entity_id=self.entity.id, entity_type=self.entity.type)
    
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
            post an entity with entity_ID and entity_name
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
        ret = self.cb_client.delete_entity(entity_id=self.entity.id, entity_type=self.entity.type)
        # Error should be raised in delete_entity function
        if not ret:
            raise ValueError("There should have been an error raised because of the deletion of an non existent entity.")
        """Test2"""
        self.cb_client.post_entity(entity=self.entity)
        self.cb_client.post_entity(entity=self.entity_2)
        self.cb_client.delete_entity(entity_id=self.entity.id, entity_type=self.entity.type)
        entity_list = self.cb_client.get_entity_list()
        for element in entity_list: 
            self.assertNotEqual(element.id,self.entity.id)
            # raise ValueError("This element was deleted and should not be visible in the entity list.")
        """Test3"""
        ret = self.cb_client.delete_entity(entity_id=self.entity, entity_type=self.entity.type)
            # Error should be raised in delete_entity function because enitity was already deleted
        if not ret:
            raise ValueError("There should have been an error raised because of the deletion of an non existent entity.")  
    
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
            post an entity with entity_ID and entity_name
            add attribute to the entity with entity_ID
            get entity with entity_ID and new attribute
            Is new attribute not added to enitity ? 
                yes:
                    Raise Error
        Test 2: 
            add attribute to an non existent entity
            Raise Error
        Test 3:
            post an entity with entity_ID, entity_name, entity_attribute
            add attribute that already exists with noOverwrite
                Raise Error
            get entity and compare previous with entity attributes
            If attributes are different?
                Raise Error
        """
        """Test 1"""
        self.cb_client.post_entity(self.entity)
        attr = ContextProperty(**{'value': 20, 'type': 'Number'})
        # noOverwrite Option missing ???
        self.entity.add_properties(attrs=["test_value", attr])
        entity_list = self.cb_client.get_entity_list()
        for entity in entity_list:
            self.assertEqual(first=entity.property, second=attr)
        for entity in entity_list:
            self.cb_client.delete_entity_by_id(entity_id=entity.id)
        
        """Test 2"""
        attr = ContextProperty(**{'value': 20, 'type': 'Number'})
        with self.asserRaises(Exception):
            self.entity.add_properties(attrs=["test_value", attr])
            
        """Test 3"""
        self.cb_client.post_entity(self.entity)
        # What makes an property/ attribute unique ???
        attr = ContextProperty(**{'value': 20, 'type': 'Number'})
        attr_same = ContextProperty(**{'value': 40, 'type': 'Number'})
        
        # noOverwrite Option missing ???
        self.entity.add_properties(attrs=["test_value", attr])
        self.entity.add_properties(attrs=["test_value", attr_same])

        entity_list = self.cb_client.get_entity_list()
        for entity in entity_list:
            self.assertEqual(first=entity.property, second=attr)
        
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
            - Post an enitity with specific attributes and Change non existent attributes. 
        """
        """
        Test 1:
            post an enitity with entity_ID and entity_name and attributes
            patch one of the attributes with entity_id by sending request body
            get entity list
            If new attribute is not added to the entity?
                Raise Error
        Test 2: 
            post an entity with entity_ID and entity_name and attributes
            patch an non existent attribute
            return != 400:
                yes:
                    Raise Error
                       get entity list
            Is the new attribute added to the entity?
                yes:
                    Raise Error     
        """
        """Test1"""
        self.test_post_entity(self.entity)


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
            - Post an enitity with specific attributes and Change non existent attributes.             
        """
        """
        Test 1: 
            post an entity with entity_ID, entity_name and attributes
            patch with entity_ID and attribute_ID 
            return != 204: 
                yes: 
                    Raise Error
        Test 2: 
            post an entity with entity_ID, entity_name and attributes
            patch attribute with non existent attribute_ID with existing entity_ID
            return != 404: 
                yes:
                    Raise Error
        """
        # No function for patch entity attribute???
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
            post an enitity with entity_ID, entity_name and attribute with attribute_ID
            delete an attribute with an non existent attribute_ID of the entity with the entity_ID
            return != 404: 
                Raise Error
        Test 2: 
            post an entity with entity_ID, entitiy_name and attribute with attribute_ID
            delete the attribute with the attribute_ID of the entity with the entity_ID
            return != 204?
                yes: 
                    Raise Error
            get entity wit entity_ID 
            Is attribute with attribute_ID still there?
                yes: 
                    Raise Error
            delete the attribute with the attribute_ID of the entity with the entity_ID
            return != 404?
                yes:
                    Raise Error
        """