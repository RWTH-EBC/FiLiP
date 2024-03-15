"""
Tests for filip.cb.client
"""
import unittest
import logging
import time
import random
import json
import paho.mqtt.client as mqtt
from datetime import datetime
from requests import RequestException

from filip.clients.ngsi_ld.cb import ContextBrokerLDClient
from filip.models.base import  DataType, FiwareLDHeader
from filip.models.ngsi_ld.context import ActionTypeLD, ContextLDEntity, ContextProperty, NamedContextProperty
from filip.utils.simple_ql import QueryString

from filip.models.ngsi_v2.base import AttrsFormat
from filip.models.ngsi_v2.subscriptions import Subscription

from filip.models.ngsi_v2.context import \
    NamedCommand, \
    Query, \
    ContextEntity


# Setting up logging
logging.basicConfig(
    level='ERROR',
    format='%(asctime)s %(name)s %(levelname)s: %(message)s')


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
            "types_url": "/ngsi-ld/v1/types"
        }
        self.attr = {'testtemperature': {'value': 20.0}}
        self.entity = ContextLDEntity(id='urn:ngsi-ld:my:id', type='MyType', **self.attr)
        self.fiware_header = FiwareLDHeader()

        self.client = ContextBrokerLDClient(fiware_header=self.fiware_header)


    def test_management_endpoints(self):
        """
        Test management functions of context broker client
        """
        with ContextBrokerLDClient(fiware_header=self.fiware_header) as client:
            self.assertIsNotNone(client.get_version())
            # there is no resources endpoint like in NGSI v2
            # TODO: check whether there are other "management" endpoints

    def test_statistics(self):
        """
        Test statistics of context broker client
        """
        with ContextBrokerLDClient(fiware_header=self.fiware_header) as client:
            self.assertIsNotNone(client.get_statistics())

    def aatest_pagination(self):
        """
        Test pagination of context broker client
        Test pagination. only works if enough entities are available
        """
        fiware_header = FiwareLDHeader()
        with ContextBrokerLDClient(fiware_header=fiware_header) as client:
            entities_a = [ContextLDEntity(id=f"urn:ngsi-ld:test:{str(i)}",
                                        type=f'filip:object:TypeA') for i in
                          range(0, 1000)]
            client.update(action_type=ActionTypeLD.CREATE, entities=entities_a)
            entities_b = [ContextLDEntity(id=f"urn:ngsi-ld:test:{str(i)}",
                                        type=f'filip:object:TypeB') for i in
                          range(1000, 2001)]
            client.update(action_type=ActionTypeLD.CREATE, entities=entities_b)
            self.assertLessEqual(len(client.get_entity_list(limit=1)), 1)
            self.assertLessEqual(len(client.get_entity_list(limit=999)), 999)
            self.assertLessEqual(len(client.get_entity_list(limit=1001)), 1001)
            self.assertLessEqual(len(client.get_entity_list(limit=2001)), 2001)

            client.update(action_type=ActionTypeLD.DELETE, entities=entities_a)
            client.update(action_type=ActionTypeLD.DELETE, entities=entities_b)

    def aatest_entity_filtering(self):
        """
        Test filter operations of context broker client
        """

        with ContextBrokerLDClient(fiware_header=self.fiware_header) as client:
            print(client.session.headers)
            # test patterns
            with self.assertRaises(ValueError):
                client.get_entity_list(id_pattern='(&()?')
            with self.assertRaises(ValueError):
                client.get_entity_list(type_pattern='(&()?')
            entities_a = [ContextLDEntity(id=f"urn:ngsi-ld:TypeA:{str(i)}",
                                        type=f'filip:object:TypeA') for i in
                          range(0, 5)]

            client.update(action_type=ActionTypeLD.CREATE, entities=entities_a)
            entities_b = [ContextLDEntity(id=f"urn:ngsi-ld:TypeB:{str(i)}",
                                        type=f'filip:object:TypeB') for i in
                          range(6, 10)]

            client.update(action_type=ActionTypeLD.CREATE, entities=entities_b)

            entities_all = client.get_entity_list()
            entities_by_id_pattern = client.get_entity_list(
                id_pattern='.*[1-5]')
            self.assertLess(len(entities_by_id_pattern), len(entities_all))

            # entities_by_type_pattern = client.get_entity_list(
            #     type_pattern=".*TypeA$")
            # self.assertLess(len(entities_by_type_pattern), len(entities_all))

            qs = QueryString(qs=[('presentValue', '>', 0)])
            entities_by_query = client.get_entity_list(q=qs)
            self.assertLess(len(entities_by_query), len(entities_all))

            # test options
            for opt in list(AttrsFormat):
                entities_by_option = client.get_entity_list(response_format=opt)
                self.assertEqual(len(entities_by_option), len(entities_all))
                self.assertEqual(client.get_entity(
                    entity_id='urn:ngsi-ld:TypeA:0',
                    response_format=opt),
                    ContextLDEntity(id="urn:ngsi-ld:TypeA:0",
                                    type='filip:object:TypeA'))
            with self.assertRaises(ValueError):
                client.get_entity_list(response_format='not in AttrFormat')

            client.update(action_type=ActionTypeLD.DELETE, entities=entities_a)

            client.update(action_type=ActionTypeLD.DELETE, entities=entities_b)

    def aatest_entity_operations(self):
        """
        Test entity operations of context broker client
        """
        with ContextBrokerLDClient(fiware_header=self.fiware_header) as client:
            client.post_entity(entity=self.entity, update=True)
            res_entity = client.get_entity(entity_id=self.entity.id)
            client.get_entity(entity_id=self.entity.id, attrs=['testtemperature'])
            self.assertEqual(client.get_entity_attributes(
                entity_id=self.entity.id), res_entity.get_properties(
                response_format='dict'))
            res_entity.testtemperature.value = 25
            client.update_entity(entity=res_entity)  # TODO: how to use context?
            self.assertEqual(client.get_entity(entity_id=self.entity.id),
                             res_entity)
            res_entity.add_properties({'pressure': ContextProperty(
                type='Number', value=1050)})
            client.update_entity(entity=res_entity)
            self.assertEqual(client.get_entity(entity_id=self.entity.id),
                             res_entity)

    def aatest_attribute_operations(self):
        """
        Test attribute operations of context broker client
        """
        with ContextBrokerLDClient(fiware_header=self.fiware_header) as client:
            entity = self.entity
            attr_txt = NamedContextProperty(name='attr_txt',
                                             value="Test")
            attr_bool = NamedContextProperty(name='attr_bool',
                                              value=True)
            attr_float = NamedContextProperty(name='attr_float',
                                               value=round(random.random(), 5))
            attr_list = NamedContextProperty(name='attr_list',
                                              value=[1, 2, 3])
            attr_dict = NamedContextProperty(name='attr_dict',
                                              value={'key': 'value'})
            entity.add_properties([attr_txt,
                                   attr_bool,
                                   attr_float,
                                   attr_list,
                                   attr_dict])

            self.assertIsNotNone(client.post_entity(entity=entity,
                                                    update=True))
            res_entity = client.get_entity(entity_id=entity.id)

            for attr in entity.get_properties():
                self.assertIn(attr, res_entity.get_properties())
                res_attr = client.get_attribute(entity_id=entity.id,
                                                attr_name=attr.name)

                self.assertEqual(type(res_attr.value), type(attr.value))
                self.assertEqual(res_attr.value, attr.value)
                value = client.get_attribute_value(entity_id=entity.id,
                                                   attr_name=attr.name)
                # unfortunately FIWARE returns an int for 20.0 although float
                # is expected
                if isinstance(value, int) and not isinstance(value, bool):
                    value = float(value)
                self.assertEqual(type(value), type(attr.value))
                self.assertEqual(value, attr.value)

            for attr_name, attr in entity.get_properties(
                    response_format='dict').items():

                client.update_entity_attribute(entity_id=entity.id,
                                               attr_name=attr_name,
                                               attr=attr)
                value = client.get_attribute_value(entity_id=entity.id,
                                                   attr_name=attr_name)
                # unfortunately FIWARE returns an int for 20.0 although float
                # is expected
                if isinstance(value, int) and not isinstance(value, bool):
                    value = float(value)
                self.assertEqual(type(value), type(attr.value))
                self.assertEqual(value, attr.value)

            new_value = 1337.0
            client.update_attribute_value(entity_id=entity.id,
                                          attr_name='testtemperature',
                                          value=new_value)
            attr_value = client.get_attribute_value(entity_id=entity.id,
                                                    attr_name='testtemperature')
            self.assertEqual(attr_value, new_value)

            client.delete_entity(entity_id=entity.id)

    def aatest_type_operations(self):
        """
        Test type operations of context broker client
        """
        with ContextBrokerLDClient(fiware_header=self.fiware_header) as client:
            self.assertIsNotNone(client.post_entity(entity=self.entity,
                                                    update=True))
            client.get_entity_types()
            #client.get_entity_types(options='count') # TODO ask Thomas
            #client.get_entity_types(options='values')
            client.get_entity_type(entity_type='MyType')
            client.delete_entity(entity_id=self.entity.id)

    def aatest_batch_operations(self):
        """
        Test batch operations of context broker client
        """
        fiware_header = FiwareLDHeader(service='filip',
                                     service_path='/testing')
        with ContextBrokerLDClient(fiware_header=fiware_header) as client:
            entities = [ContextLDEntity(id=str(i),
                                      type=f'filip:object:TypeA') for i in
                        range(0, 1000)]
            client.update(entities=entities, action_type=ActionTypeLD.CREATE)
            entities = [ContextLDEntity(id=str(i),
                                      type=f'filip:object:TypeB') for i in
                        range(0, 1000)]
            client.update(entities=entities, action_type=ActionTypeLD.CREATE)
            e = ContextEntity(idPattern=".*", typePattern=".*TypeA$")

    def aatest_get_all_attributes(self):
        fiware_header = FiwareLDHeader(service='filip',
                                       service_path='/testing')
        with ContextBrokerLDClient(fiware_header=self.fiware_header) as client:
            entity = self.entity
            attr_txt = NamedContextProperty(name='attr_txt',
                                            value="Test")
            attr_bool = NamedContextProperty(name='attr_bool',
                                             value=True)
            attr_float = NamedContextProperty(name='attr_float',
                                              value=round(random.random(), 5))
            attr_list = NamedContextProperty(name='attr_list',
                                             value=[1, 2, 3])
            attr_dict = NamedContextProperty(name='attr_dict',
                                             value={'key': 'value'})
            entity.add_properties([attr_txt,
                                   attr_bool,
                                   attr_float,
                                   attr_list,
                                   attr_dict])

            client.post_entity(entity=entity, update=True)
            attrs_list = client.get_all_attributes()
            self.assertEqual(['attr_bool', 'attr_dict', 'attr_float', 'attr_list', 'attr_txt', 'testtemperature'],
                             attrs_list)






    def tearDown(self) -> None:
        """
        Cleanup test server
        """
        try:
            entities = [ContextLDEntity(id=entity.id, type=entity.type) for
                        entity in self.client.get_entity_list()]
            self.client.update(entities=entities, action_type='delete')
        except RequestException:
            pass

        self.client.close()