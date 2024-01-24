import _json
import unittest


class TestEntities(unittest.Testcase):
    """
    Test class for entity endpoints.
    Args:
        unittest (_type_): _description_
    """

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
        """

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
                If attributes posted entity != attributes get entity:
                    Raise Error
                type posted entity != type get entity:
                    yes:
                        Raise Error
        Test 2: 
            get enitity with enitity_ID that does not exit
            return != 404 not found?
                yes:
                    Raise Error
        """


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
            return != 404 ?
                yes:
                    Raise Error
        
        Test 2: 
            post an entity with entity_ID and entity_name
            delete entity with entity_ID
            return != 204 ? 
                yes:
                    Raise Error
            get entity list 
            Is eneity with entity_ID in enity list ? 
                yes: 
                    Raise Error
        
        Test 3: 
            delete entity with entity_ID 
                return != 404 ? 
                    yes: 
                        Raise Error

        """
        
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
            return != 204 ? 
                yes:
                    Raise Error

            get entity with entity_ID and new attribute
            Is new attribute not added to enitity ? 
                yes:
                    Raise Error
        Test 2: 
            add attribute to an non existent entity
            return != 404:
                Raise Error
        Test 3:
            post an entity with entity_ID, entity_name, entity_attribute
            add attribute that already exists with noOverwrite
            return != 207?
                yes: 
                    Raise Error
            get entity and compare previous with entity attributes
            If attributes are different?
                yes:
                    Raise Error
        """

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
            return != 201 ? 
                yes: 
                    Raise Error
            get entity list
            Is the new attribute not added to the entity?
                yes:
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


        def test_entityOperations_create(self):
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
            return != 200 ? 
                yes: 
                    Raise Error
            get entity list
            for all elements in entity list: 
                if entity list element != batch entity element:
                    Raise Error
        """

        def test_entityOperations_update(self):
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
            if return != 200:
                Raise Error
            get entities
            for all entities in entity list: 
                if entity list element != updated batch entity element:
                    Raise Error
        Test 2: 
            post create entity batches
            post update of batch entity with no overwrite
            if return != 200:
                Raise Error
            get entities
            for all entities in entity list: 
                if entity list element != updated batch entity element but not the existings are overwritten:
                    Raise Error

        """
        def test_entityOperations_upsert(self):
            """
            Batch Entity upsert.
            Args:
                - options(string): Available values: replace, update
                - Request body(EntityList); required
            Returns: 
                - (200) Success
                - (400) Bad request
            Tests: 
                - Post entity list and then post the upsert with replace or update. Get the entitiy list and see if the results are correct. 
            """

        """
        Test 1: 
            post a create entity batch
            post entity upsert
            if return != 200:
                Raise Error
            get entity list
            for all entities in entity list: 
                if entity list element != upsert entity list:
                    Raise Error
        """
        def test_entityOperations_delete(self):
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