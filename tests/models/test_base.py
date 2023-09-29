"""
Tests for filip.core.models
"""
import copy
import json
import unittest
from typing import List, Dict

from pydantic import ValidationError
from filip.models.base import FiwareHeader
from filip.clients.ngsi_v2 import ContextBrokerClient
from filip.models.ngsi_v2.context import ContextEntity
from filip.utils.cleanup import clear_all, clean_test
from tests.config import settings, generate_servicepath


class TestModels(unittest.TestCase):
    """
    Test class for core.models
    """

    def setUp(self) -> None:
        # create variables for test
        self.service_paths = [generate_servicepath(), generate_servicepath()]
        self.fiware_header = {'fiware-service': settings.FIWARE_SERVICE,
                              'fiware-servicepath': settings.FIWARE_SERVICEPATH}

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                cb_url=settings.CB_URL)
    def test_fiware_header(self):
        """
        Test for fiware header
        """
        header = FiwareHeader.model_validate(self.fiware_header)
        self.assertEqual(header.model_dump(by_alias=True),
                         self.fiware_header)
        self.assertEqual(json.loads(header.model_dump_json(by_alias=True)),
                         self.fiware_header)
        # TODO maybe implement in this way
        # with self.assertRaises(ValidationError):
        #     FiwareHeader(service='jkgsadh ', service_path='/testing')
        # TODO I can not see any error, because service allowed all text
        # self.assertRaises(ValidationError, FiwareHeader,
        #                   service='jkgsadh ', service_path='/testing')
        # self.assertRaises(ValidationError, FiwareHeader,
        #                   service='%', service_path='/testing')
        self.assertRaises(ValidationError, FiwareHeader,
                          service='filip', service_path='testing/')
        self.assertRaises(ValidationError, FiwareHeader,
                          service='filip', service_path='/$testing')
        self.assertRaises(ValidationError, FiwareHeader,
                          service='filip', service_path='/testing ')
        self.assertRaises(ValidationError, FiwareHeader,
                          service='filip', service_path='#')
        headers = FiwareHeader.model_validate(self.fiware_header)
        with ContextBrokerClient(url=settings.CB_URL,
                                 fiware_header=headers) as client:
            entity = ContextEntity(id='myId', type='MyType')
            for path in self.service_paths:
                client.fiware_service_path = path
                client.post_entity(entity=entity)
                client.get_entity(entity_id=entity.id)
            client.fiware_service_path = '/#'
            self.assertGreaterEqual(len(client.get_entity_list()),
                                    len(self.service_paths))
            for path in self.service_paths:
                client.fiware_service_path = path
                client.delete_entity(entity_id=entity.id,
                                     entity_type=entity.type)

    def test_strings_in_models(self) -> None:
        """
        Tests for each not fixed key, and for each value the reaction if
        a ' or " is added to the string

        Either it is allowed, than the posting of an entity with the
        key/string succeeds
        Or it is forbidden than the Model needs to throw an error
        """

        entity_dict = {
            "id": 'MyId',
            "type": 'MyType',
            'at1': {'value': "20.0", 'type': 'Text'},
            'at2': {'value': {'field_value': "20.0"},
                    'type': 'StructuredValue',
                    'metadata':{
                            'name': 'test-name',
                            'type': 'StructuredValue',
                            'value':  {'field_value': "20.0"},
                        }
                    }
            }

        def field_value_tests(dictionary: dict, keychain: List[str],
                              test_keys: bool = False):
            """Recursively test the keys, values of a dictionary that will be
            transformed into an entity.

            Args:
                dictionary: Entity in dictionary form
                keychain: List of keys from the top level of the dict to the
                        currently analysed level
                test_keys: True if also the modification of the keys should
                        be checked

            """
            for field, value in dictionary.items():
                if isinstance(value, dict):
                    # If still a dict than continue recursively
                    keychain_ = copy.copy(keychain)
                    keychain_.append(field)

                    field_value_tests(value, keychain_, field == "value")
                else:
                    # we have a key value pair both strings
                    for test_char, needs_to_succeed in [("'", False),
                                                        ('"', False),
                                                        ("", True)]:
                        # Append ', " or nothing. The last is not allowed to
                        # fail

                        def test(dictionary: Dict):
                            # either the assignment throws an error or
                            # the entity can get posted and gets found

                            assignment_error = False
                            try:
                                entity = ContextEntity(**dictionary)
                            except:
                                assignment_error = True
                                self.assertFalse(needs_to_succeed)

                            if not assignment_error:
                                client.post_entity(entity=entity)
                                # if post successful get will not throw an
                                # error
                                client.get_entity(entity_id=entity.id,
                                                  entity_type=entity.type)
                                client.delete_entity(entity_id=entity.id,
                                                     entity_type=entity.type)

                        # work on a copy
                        new_dict = copy.deepcopy(entity_dict)

                        # find the current key pair in the dict
                        dict_field = new_dict
                        for key in keychain:
                            dict_field = dict_field[key]

                        # apply the modification and test
                        value_ = dict_field[field]
                        dict_field[field] = f'{value}{test_char}'
                        test(new_dict)

                        # if keys should be tested, apply the modification to
                        # key and test
                        if test_keys:
                            del dict_field[field]
                            dict_field[f'{field}{test_char}'] = value_
                            test(new_dict)

        header = FiwareHeader.model_validate(self.fiware_header)
        with ContextBrokerClient(url=settings.CB_URL,
                                 fiware_header=header) as client:

            field_value_tests(entity_dict, [])

    def tearDown(self) -> None:
        # Cleanup test server
        with ContextBrokerClient(url=settings.CB_URL) as client:
            client.fiware_service = settings.FIWARE_SERVICE

            for path in self.service_paths:
                header = FiwareHeader(
                    service=settings.FIWARE_SERVICE,
                    service_path=path)
                clear_all(fiware_header=header, cb_url=settings.CB_URL)
            client.close()
