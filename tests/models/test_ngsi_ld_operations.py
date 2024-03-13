import _json
import unittest
# from pydantic import ValidationError

from filip.models.base import FiwareLDHeader
from filip.clients.ngsi_ld.cb import ContextBrokerLDClient
from filip.models.ngsi_ld.context import ContextLDEntity, ActionTypeLD


class TestEntities(unittest.Testcase):
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
        self.fiware_header = FiwareHeader(
            service=settings.FIWARE_SERVICE,
            service_path=settings.FIWARE_SERVICEPATH)
        self.http_url = "https://test.de:80"
        self.mqtt_url = "mqtt://test.de:1883"
        self.mqtt_topic = '/filip/testing'

        CB_URL = "http://localhost:1026"
        self.cb_client = ContextBrokerClient(url=CB_URL,
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
    
    # def test_get_entites_batch(self) -> None:
    #     """
    #     Retrieve a set of entities which matches a specific query from an NGSI-LD system
    #     Args: 
    #         - id(string): Comma separated list of URIs to be retrieved
    #         - idPattern(string): Regular expression that must be matched by Entity ids
    #         - type(string): Comma separated list of Entity type names to be retrieved
    #         - attrs(string): Comma separated list of attribute names (properties or relationships) to be retrieved
    #         - q(string): Query
    #         - georel: Geo-relationship
    #         - geometry(string): Geometry; Available values : Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon
    #         - coordinates: Coordinates serialized as a string
    #         - geoproperty(string): The name of the property that contains the geo-spatial data that will be used to resolve the geoquery
    #         - csf(string): Context Source Filter
    #         - limit(integer): Pagination limit
    #         - options(string): Options dictionary; Available values : keyValues, sysAttrs
        
    #     """
    #     if 1 == 1:
    #         self.assertNotEqual(1,2)
    #     pass 
    
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
        fiware_header = FiwareLDHeader()
        with ContextBrokerLDClient(fiware_header=fiware_header) as client:
            entities_a = [ContextLDEntity(id=f"urn:ngsi-ld:test:{str(i)}",
                                        type=f'filip:object:TypeA') for i in
                          range(0, 10)]
            client.update(entities=entities_a, action_type=ActionTypeLD.CREATE)
            entity_list = client.get_entity_list()
            for entity in entities_a:
                self.assertIn(entity, entity_list)
            for entity in entities_a:
                client.delete_entity_by_id(entity_id=entity.id)
        """Test 2"""
        with ContextBrokerLDClient(fiware_header=fiware_header) as client:
            entities_a = [ContextLDEntity(id=f"urn:ngsi-ld:test:eins",
                                        type=f'filip:object:TypeA'),
                          ContextLDEntity(id=f"urn:ngsi-ld:test:eins",
                                        type=f'filip:object:TypeA')]
            try:
                client.update(entities=entities_a, action_type=ActionTypeLD.CREATE)
                entity_list = client.get_entity_list()
                self.assertEqual(len(entity_list), 1)
            except:
                pass

            
    
    def test_entity_operations_update(self) -> None:
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
        pass
    
    def test_entity_operations_upsert(self) -> None:
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
        pass
    
    def test_entity_operations_delete(self) -> None:
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
        pass