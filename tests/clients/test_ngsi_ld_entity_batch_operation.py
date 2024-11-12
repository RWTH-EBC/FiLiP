from random import Random
import unittest
from requests.exceptions import HTTPError
from requests import RequestException
from pydantic import ValidationError

from filip.models.base import FiwareLDHeader
# FiwareLDHeader issue with pydantic
from filip.clients.ngsi_ld.cb import ContextBrokerLDClient
from filip.models.ngsi_ld.context import ContextLDEntity, ActionTypeLD
from tests.config import settings
from filip.utils.cleanup import clear_context_broker_ld


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
        self.cb_client = ContextBrokerLDClient(fiware_header=self.fiware_header,
                                               url=settings.LD_CB_URL)
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
        entities_a = [ContextLDEntity(id=f"urn:ngsi-ld:test:{str(i)}",
                                      type=f'filip:object:test') for i in
                      range(0, 10)]
        self.cb_client.entity_batch_operation(entities=entities_a, action_type=ActionTypeLD.CREATE)
        entity_list = self.cb_client.get_entity_list(entity_type=f'filip:object:test')
        id_list = [entity.id for entity in entity_list]
        self.assertEqual(len(entities_a), len(entity_list))
        for entity in entities_a:
            self.assertIsInstance(entity, ContextLDEntity)
            self.assertIn(entity.id, id_list)
        for entity in entity_list:
            self.cb_client.delete_entity_by_id(entity_id=entity.id)

        """Test 2"""
        entities_b = [ContextLDEntity(id=f"urn:ngsi-ld:test:eins",
                                      type=f'filip:object:test'),
                      ContextLDEntity(id=f"urn:ngsi-ld:test:eins",
                                      type=f'filip:object:test')]
        entity_list_b = []
        try:
            self.cb_client.entity_batch_operation(entities=entities_b, action_type=ActionTypeLD.CREATE)
            entity_list_b = self.cb_client.get_entity_list(
                entity_type=f'filip:object:test')
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
        entities_a = [ContextLDEntity(id=f"urn:ngsi-ld:test:{str(i)}",
                                      type=f'filip:object:test',
                                      **{'temperature': {
                                          'value': self.r.randint(20,50),
                                          "type": "Property"
                                      }}) for i in
                      range(0, 5)]

        self.cb_client.entity_batch_operation(entities=entities_a, action_type=ActionTypeLD.CREATE)

        entities_update = [ContextLDEntity(id=f"urn:ngsi-ld:test:{str(i)}",
                                           type=f'filip:object:test',
                                           **{'temperature':
                                                  {'value': self.r.randint(0,20),
                                                   "type": "Property"
                                                   }}) for i in
                           range(3, 6)]
        self.cb_client.entity_batch_operation(entities=entities_update, action_type=ActionTypeLD.UPDATE)
        entity_list = self.cb_client.get_entity_list(entity_type=f'filip:object:test')
        self.assertEqual(len(entity_list),5)
        updated = [x.model_dump(exclude_unset=True, exclude={"context"})
                   for x in entity_list if int(x.id.split(':')[3]) in range(3,5)]
        nupdated = [x.model_dump(exclude_unset=True, exclude={"context"})
                    for x in entity_list if int(x.id.split(':')[3]) in range(0,3)]

        self.assertCountEqual([entity.model_dump(exclude_unset=True)
                               for entity in entities_a[0:3]],
                              nupdated)

        self.assertCountEqual([entity.model_dump(exclude_unset=True)
                               for entity in entities_update[0:2]],
                              updated)

        """Test 2"""
        # presssure will be appended while the existing temperature will
        # not be overwritten
        entities_update = [ContextLDEntity(id=f"urn:ngsi-ld:test:{str(i)}",
                                           type=f'filip:object:test',
                                           **{'temperature':
                                                  {'value': self.r.randint(50, 100),
                                                   "type": "Property"},
                                              'pressure': {
                                                  'value': self.r.randint(1,100),
                                                  "type": "Property"
                                              }
                                              }) for i in range(0, 5)]
        
        self.cb_client.entity_batch_operation(entities=entities_update,
                                              action_type=ActionTypeLD.UPDATE,
                                              options="noOverwrite")
        
        previous = entity_list
        previous.sort(key=lambda x: int(x.id.split(':')[3]))
        
        entity_list = self.cb_client.get_entity_list(entity_type=f'filip:object:test')
        entity_list.sort(key=lambda x: int(x.id.split(':')[3]))
        
        self.assertEqual(len(entity_list),len(entities_update))
        
        for (updated,entity,prev) in zip(entities_update,entity_list,previous):
            self.assertEqual(updated.model_dump().get('pressure'),
                             entity.model_dump().get('pressure'))
            self.assertNotEqual(updated.model_dump().get('temperature'),
                                entity.model_dump().get('temperature'))
            self.assertEqual(prev.model_dump().get('temperature'),
                             entity.model_dump().get('temperature'))

        with self.assertRaises(HTTPError):
            self.cb_client.entity_batch_operation(entities=[],action_type=ActionTypeLD.UPDATE)
        
        # according to spec, this should raise bad request data,
        # but pydantic is intercepting
        with self.assertRaises(ValidationError):
            self.cb_client.entity_batch_operation(entities=[None],action_type=ActionTypeLD.UPDATE)
            
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
        entities_a = [ContextLDEntity(id=f"urn:ngsi-ld:test:{str(i)}",
                                      type=f'filip:object:test',
                                      **{'temperature':
                                             {'value': self.r.randint(0,20),
                                              "type": "Property"
                                              }}) for i in
                      range(1, 4)]
        self.cb_client.entity_batch_operation(entities=entities_a, action_type=ActionTypeLD.CREATE)

        # replace entities 0 - 1
        entities_replace = [ContextLDEntity(id=f"urn:ngsi-ld:test:{str(i)}",
                                            type=f'filip:object:test',
                                            **{'pressure':
                                                   {'value': self.r.randint(50,100),
                                                    "type": "Property"
                                                    }}) for i in
                      range(0, 2)]
        self.cb_client.entity_batch_operation(entities=entities_replace, action_type=ActionTypeLD.UPSERT,
                                              options="replace")

        # update entities 3 - 4,
        # pressure will be appended for 3
        # temperature will be appended for 4
        entities_update = [ContextLDEntity(id=f"urn:ngsi-ld:test:{str(i)}",
                                           type=f'filip:object:test',
                                           **{'pressure':
                                                  {'value': self.r.randint(50,100),
                                                   "type": "Property"
                                                   }}) for i in
                      range(3, 5)]
        self.cb_client.entity_batch_operation(entities=entities_update,
                                              action_type=ActionTypeLD.UPSERT,
                                              options="update")
   
        # 0,1 and 4 should have pressure only
        # 2 should have temperature only
        # 3 should have both
        # can be made modular for variable size batches
        entity_list = self.cb_client.get_entity_list()
        self.assertEqual(len(entity_list),5)
        for _e in entity_list:
            _id = int(_e.id.split(':')[3])
            e = _e.model_dump(exclude_unset=True, exclude={'context'})
            if _id in [0,1]:
                self.assertIsNone(e.get('temperature',None))
                self.assertIsNotNone(e.get('pressure',None))
                self.assertCountEqual([e],
                                      [x.model_dump(exclude_unset=True)
                                       for x in entities_replace if x.id == _e.id])
            elif _id == 4:
                self.assertIsNone(e.get('temperature',None))
                self.assertIsNotNone(e.get('pressure',None))
                self.assertCountEqual([e],
                                      [x.model_dump(exclude_unset=True)
                                       for x in entities_update if x.id == _e.id])
            elif _id == 2:
                self.assertIsNone(e.get('pressure',None))
                self.assertIsNotNone(e.get('temperature',None))
                self.assertCountEqual([e],
                                      [x.model_dump(exclude_unset=True)
                                       for x in entities_a if x.id == _e.id])
            elif _id == 3:
                self.assertIsNotNone(e.get('temperature',None))
                self.assertIsNotNone(e.get('pressure',None))
                self.assertCountEqual([e.get('temperature')],
                                      [x.model_dump(exclude_unset=True).get('temperature')
                                       for x in entities_a if x.id == _e.id])
                self.assertCountEqual([e.get('pressure')],
                                      [x.model_dump(exclude_unset=True).get('pressure')
                                       for x in entities_update if x.id == _e.id])
                
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
        entities_delete = [ContextLDEntity(id=f"urn:ngsi-ld:test:{str(i)}",
                                           type=f'filip:object:test') for i in
                           range(0, 1)]
        with self.assertRaises(Exception):
            self.cb_client.entity_batch_operation(entities=entities_delete,
                                                  action_type=ActionTypeLD.DELETE)

        """Test 2"""
        entity_del_type = 'filip:object:test'
        entities_ids_a = [f"urn:ngsi-ld:test:{str(i)}" for i in
                          range(0, 4)]
        entities_a = [ContextLDEntity(id=id_a,
                                      type=entity_del_type) for id_a in
                      entities_ids_a]

        self.cb_client.entity_batch_operation(entities=entities_a, action_type=ActionTypeLD.CREATE)

        entities_delete = [ContextLDEntity(id=id_a,
                                           type=entity_del_type) for id_a in
                           entities_ids_a[:3]]
        entities_delete_ids = [entity.id for entity in entities_delete]

        # send update to delete entities
        self.cb_client.entity_batch_operation(entities=entities_delete, action_type=ActionTypeLD.DELETE)

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
