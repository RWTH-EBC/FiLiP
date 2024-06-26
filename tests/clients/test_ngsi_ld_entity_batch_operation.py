import _json
import unittest
# from pydantic import ValidationError

from filip.models.base import FiwareLDHeader
# FiwareLDHeader issue with pydantic
from filip.clients.ngsi_ld.cb import ContextBrokerLDClient
from filip.models.ngsi_ld.context import ContextLDEntity, ActionTypeLD
from tests.config import settings


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
        self.fiware_header = FiwareLDHeader(ngsild_tenant=settings.FIWARE_SERVICE)
        self.cb_client = ContextBrokerLDClient(fiware_header=self.fiware_header,
                                               url=settings.LD_CB_URL)

        # self.attr = {'testtemperature': {'value': 20.0}}
        # self.entity = ContextLDEntity(id='urn:ngsi-ld:my:id', type='MyType', **self.attr)
        # #self.entity = ContextLDEntity(id="urn:ngsi-ld:room1", type="Room", data={})

        # # self.entity = ContextLDEntity(id="urn:ngsi-ld:room1", type="Room", **room1_data)
        # # self.entity = ContextLDEntity(id="urn:ngsi-ld:room1", 
        #                             #   type="room",
        #                             #   data={})
        # self.entity_2 = ContextLDEntity(id="urn:ngsi-ld:room2",
        #                                 type="room",
        #                               data={})

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

    def tearDown(self) -> None:
        """
        Cleanup entities from test server
        """
        entity_test_types = ["filip:object:TypeA", "filip:object:TypeB",
                             "filip:object:TypeUpdate", "filip:object:TypeDELETE"]
        for entity_type in entity_test_types:
            entity_list = self.cb_client.get_entity_list(entity_type=entity_type)
            for entity in entity_list:
                self.cb_client.delete_entity_by_id(entity_id=entity.id)

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
        entities_a = [ContextLDEntity(id=f"urn:ngsi-ld:test:{str(i)}",
                                      type=f'filip:object:TypeA') for i in
                      range(0, 10)]
        self.cb_client.update(entities=entities_a, action_type=ActionTypeLD.CREATE)
        entity_list = self.cb_client.get_entity_list(entity_type=f'filip:object:TypeA')
        id_list = [entity.id for entity in entity_list]
        self.assertEqual(len(entities_a), len(entity_list))
        for entity in entities_a:
            self.assertIsInstance(entity, ContextLDEntity)
            self.assertIn(entity.id, id_list)
        for entity in entity_list:
            self.cb_client.delete_entity_by_id(entity_id=entity.id)

        """Test 2"""
        entities_b = [ContextLDEntity(id=f"urn:ngsi-ld:test:eins",
                                      type=f'filip:object:TypeB'),
                      ContextLDEntity(id=f"urn:ngsi-ld:test:eins",
                                      type=f'filip:object:TypeB')]
        entity_list_b = []
        try:
            self.cb_client.update(entities=entities_b, action_type=ActionTypeLD.CREATE)
            entity_list_b = self.cb_client.get_entity_list(
                entity_type=f'filip:object:TypeB')
            self.assertEqual(len(entity_list), 1)
        except:
            pass
        finally:
            for entity in entity_list_b:
                self.cb_client.delete_entity_by_id(entity_id=entity.id)

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
        ContextLDEntity(id=f"urn:ngsi-ld:test:10", type=f'filip:object:TypeA')
        entities_a = [ContextLDEntity(id=f"urn:ngsi-ld:test:{str(i)}",
                                      type=f'filip:object:TypeA') for i in
                      range(0, 5)]

        self.cb_client.update(entities=entities_a, action_type=ActionTypeLD.CREATE)

        entities_update = [ContextLDEntity(id=f"urn:ngsi-ld:test:{str(i)}",
                                           type=f'filip:object:TypeUpdate') for i in
                           range(3, 6)]
        self.cb_client.update(entities=entities_update, action_type=ActionTypeLD.UPDATE)
        entity_list_a = self.cb_client.get_entity_list(entity_type=f'filip:object:TypeA')
        entity_list_b = self.cb_client.get_entity_list(
            entity_type=f'filip:object:TypeUpdate')
        # TODO @lro: does Test 1 still provide any benefit when the entities are retrieved with two calls?
        for entity in entity_list_a:
            if entity.id in ["urn:ngsi-ld:test:0",
                             "urn:ngsi-ld:test:1",
                             "urn:ngsi-ld:test:2",
                             "urn:ngsi-ld:test:3"]:
                self.assertEqual(entity.type, 'filip:object:TypeA')
        for entity in entity_list_b:
            if entity.id in ["urn:ngsi-ld:test:3",
                             "urn:ngsi-ld:test:4",
                             "urn:ngsi-ld:test:5"]:
                self.assertEqual(entity.type, 'filip:object:TypeUpdate')

        for entity in entity_list_a:
            self.cb_client.delete_entity_by_id(entity_id=entity.id)
        for entity in entity_list_b:
            self.cb_client.delete_entity_by_id(entity_id=entity.id)

        """Test 2"""
        entities_a = [ContextLDEntity(id=f"urn:ngsi-ld:test:{str(i)}",
                                      type=f'filip:object:TypeA') for i in
                      range(0, 4)]
        self.cb_client.update(entities=entities_a, action_type=ActionTypeLD.CREATE)

        entities_update = [ContextLDEntity(id=f"urn:ngsi-ld:test:{str(i)}",
                                           type=f'filip:object:TypeUpdate') for i in
                           range(2, 6)]
        self.cb_client.update(entities=entities_update, action_type=ActionTypeLD.UPDATE,
                              update_format="noOverwrite")
        entity_list_a = self.cb_client.get_entity_list(entity_type=f'filip:object:TypeA')
        entity_list_b = self.cb_client.get_entity_list(
            entity_type=f'filip:object:TypeUpdate')
        for entity in entity_list_a:
            if entity.id in ["urn:ngsi-ld:test:0",
                             "urn:ngsi-ld:test:1",
                             "urn:ngsi-ld:test:2",
                             "urn:ngsi-ld:test:3"]:
                self.assertEqual(entity.type, 'filip:object:TypeA')
        for entity in entity_list_b:
            if entity.id in ["urn:ngsi-ld:test:4",
                             "urn:ngsi-ld:test:5"]:
                self.assertEqual(entity.type, 'filip:object:TypeUpdate')

        for entity in entity_list_a:
            self.cb_client.delete_entity_by_id(entity_id=entity.id)
        for entity in entity_list_b:
            self.cb_client.delete_entity_by_id(entity_id=entity.id)

            # TODO @lro:

    # - changing the entity type needs to be tested with new release, did not work so far
    # - a test with empty array and/or containing null value would also be good,
    # should result in BadRequestData error
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
            - Post entity list and then post the upsert with update. Get the entitiy list and see if the results are correct. 
            - Post entity list and then post the upsert with replace. Get the entitiy list and see if the results are correct. 

        """
        """
        Test 1: 
            post a create entity batch
            post entity upsert with update
            get entity list
            for all entities in entity list: 
                if entity list element != upsert entity list:
                    Raise Error
        Test 2: 
            post a create entity batch
            post entity upsert with replace
            get entity list
            for all entities in entity list: 
                if entity list element != upsert entity list:
                    Raise Error
        """
        """Test 1"""
        # create entities and upsert (update, not replace)
        entities_a = [ContextLDEntity(id=f"urn:ngsi-ld:test:{str(i)}",
                                      type=f'filip:object:TypeA') for i in
                      range(0, 4)]
        self.cb_client.update(entities=entities_a, action_type=ActionTypeLD.CREATE)

        entities_upsert = [ContextLDEntity(id=f"urn:ngsi-ld:test:{str(i)}",
                                           type=f'filip:object:TypeUpdate') for i in
                           range(2, 6)]
        # TODO: this should work with newer release of orion-ld broker
        self.cb_client.update(entities=entities_upsert, action_type=ActionTypeLD.UPSERT,
                              update_format="update")

        # read entities from broker and check that entities were not replaced
        entity_list_a = self.cb_client.get_entity_list(entity_type=f'filip:object:TypeA')
        entity_list_b = self.cb_client.get_entity_list(
            entity_type=f'filip:object:TypeUpdate')
        ids_TypeA = ["urn:ngsi-ld:test:0",
                     "urn:ngsi-ld:test:1",
                     "urn:ngsi-ld:test:2",
                     "urn:ngsi-ld:test:3"]
        ids_TypeUpdate = ["urn:ngsi-ld:test:4",
                          "urn:ngsi-ld:test:5"]
        self.assertEqual(len(entity_list_a), len(ids_TypeA))
        self.assertEqual(len(entity_list_b), len(ids_TypeUpdate))
        for entity in entity_list_a:
            self.assertIsInstance(entity, ContextLDEntity)
            self.assertIn(entity.id, ids_TypeA)
        for entity in entity_list_b:
            self.assertIsInstance(entity, ContextLDEntity)
            self.assertIn(entity.id, ids_TypeUpdate)

        # cleanup
        for entity in entity_list_a:
            self.cb_client.delete_entity_by_id(entity_id=entity.id)
        for entity in entity_list_b:
            self.cb_client.delete_entity_by_id(entity_id=entity.id)

        """Test 2"""
        # create entities and upsert (replace)
        entities_a = [ContextLDEntity(id=f"urn:ngsi-ld:test:{str(i)}",
                                      type=f'filip:object:TypeA') for i in
                      range(0, 4)]
        self.cb_client.update(entities=entities_a, action_type=ActionTypeLD.CREATE)

        entities_upsert = [ContextLDEntity(id=f"urn:ngsi-ld:test:{str(i)}",
                                           type=f'filip:object:TypeUpdate') for i in
                           range(3, 6)]
        self.cb_client.update(entities=entities_upsert, action_type=ActionTypeLD.UPSERT,
                              update_format="replace")

        # read entities from broker and check that entities were replaced
        entity_list_a = self.cb_client.get_entity_list(entity_type=f'filip:object:TypeA')
        entity_list_b = self.cb_client.get_entity_list(
            entity_type=f'filip:object:TypeUpdate')
        ids_TypeA = ["urn:ngsi-ld:test:0",
                     "urn:ngsi-ld:test:1",
                     "urn:ngsi-ld:test:2"]
        ids_TypeUpdate = ["urn:ngsi-ld:test:3",
                          "urn:ngsi-ld:test:4",
                          "urn:ngsi-ld:test:5"]
        self.assertEqual(len(entity_list_a), len(ids_TypeA))
        self.assertEqual(len(entity_list_b), len(ids_TypeUpdate))
        for entity in entity_list_a:
            self.assertIsInstance(entity, ContextLDEntity)
            self.assertIn(entity.id, ids_TypeA)
        for entity in entity_list_b:
            self.assertIsInstance(entity, ContextLDEntity)
            self.assertIn(entity.id, ids_TypeUpdate)

        # cleanup
        for entity in entity_list_a:
            self.cb_client.delete_entity_by_id(entity_id=entity.id)
        for entity in entity_list_b:
            self.cb_client.delete_entity_by_id(entity_id=entity.id)

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
        """Test 1"""
        entities_delete = [ContextLDEntity(id=f"urn:ngsi-ld:test:{str(i)}",
                                           type=f'filip:object:TypeDELETE') for i in
                           range(0, 1)]
        with self.assertRaises(Exception):
            self.cb_client.update(entities=entities_delete,
                                  action_type=ActionTypeLD.DELETE)

        """Test 2"""
        entity_del_type = 'filip:object:TypeDELETE'
        entity_del_type = 'filip:object:TypeDELETE'
        entities_ids_a = [f"urn:ngsi-ld:test:{str(i)}" for i in
                          range(0, 4)]
        entities_a = [ContextLDEntity(id=id_a,
                                      type=entity_del_type) for id_a in
                      entities_ids_a]

        self.cb_client.update(entities=entities_a, action_type=ActionTypeLD.CREATE)

        entities_delete = [ContextLDEntity(id=id_a,
                                           type=entity_del_type) for id_a in
                           entities_ids_a[:3]]
        entities_delete_ids = [entity.id for entity in entities_delete]

        # send update to delete entities
        self.cb_client.update(entities=entities_delete, action_type=ActionTypeLD.DELETE)

        # get list of entities which is still stored
        entity_list = self.cb_client.get_entity_list(entity_type=entity_del_type)
        entity_ids = [entity.id for entity in entity_list]

        self.assertEqual(len(entity_list), 1)  # all but one entity were deleted

        for entityId in entity_ids:
            self.assertIn(entityId, entities_ids_a)
        for entityId in entities_delete_ids:
            self.assertNotIn(entityId, entity_ids)
        for entity in entity_list:
            self.cb_client.delete_entity_by_id(entity_id=entity.id)

        entity_list = self.cb_client.get_entity_list(entity_type=entity_del_type)
        self.assertEqual(len(entity_list), 0)  # all entities were deleted
