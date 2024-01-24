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