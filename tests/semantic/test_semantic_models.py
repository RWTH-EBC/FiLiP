import unittest

from pathlib import Path

from filip.models import FiwareHeader

from filip.models.ngsi_v2.iot import TransportProtocol

from filip import settings
from filip.clients.ngsi_v2 import ContextBrokerClient, IoTAClient
from filip.semantics.semantic_models import SemanticClass, InstanceHeader, \
    Command, DeviceAttribute, DeviceAttributeType
from filip.semantics.vocabulary.data_property import DataFieldType
from filip.semantics.vocabulary.vocabulary import VocabularySettings
from filip.semantics.vocabulary_configurator import VocabularyConfigurator
from filip.utils.cleanup import clear_all


class TestSemanticModels(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def test_1_model_creation(self):
        """
        Build the model used by all other tests
        """
        vocabulary = VocabularyConfigurator.create_vocabulary(
            VocabularySettings(
                pascal_case_class_labels=False,
                pascal_case_individual_labels=False,
                camel_case_property_labels=False,
                camel_case_datatype_labels=False,
                pascal_case_datatype_enum_labels=False
            ))

        vocabulary = \
            VocabularyConfigurator.add_ontology_to_vocabulary_as_file(
                vocabulary=vocabulary,
                path_to_file=self.get_file_path(
                    'ontology_files/ParsingTesterOntology.ttl'))

        # Test part can only be executed locally, as the gitlab runner can´t
        # access the WWW
        vocabulary = \
            VocabularyConfigurator.add_ontology_to_vocabulary_as_link(
                vocabulary=vocabulary,
                link="https://ontology.tno.nl/saref.ttl")

        self.assertEqual(vocabulary.get_source_list()[1].source_name,
                         "saref.ttl")
        self.assertTrue("https://w3id.org/saref#LightingDevice"
                        in vocabulary.classes)

        VocabularyConfigurator.generate_vocabulary_models(vocabulary,
                                                          "./",
                                                          "models")

    def test_2_default_header(self):
        """
        Test if a new class without header gets teh default header
        """
        from tests.semantic.models import Class1, semantic_manager

        test_header = InstanceHeader(
            cb_url=settings.CB_URL,
            service="testing",
            service_path="/"
        )
        semantic_manager.set_default_header(test_header)

        class1 = Class1()

        self.assertEqual(class1.header, test_header)

    def test_3_individuals(self):
        """
        Test the instantiation of Individuals and their uniqueness
        """
        from tests.semantic.models import Individual1, Individual2

        individual1 = Individual1()
        self.assertTrue(Individual1() == individual1)
        self.assertFalse(Individual2() == individual1)

    def test_4_model_relation_field_validation(self):
        """
        Test if relation field rules are correctly validated
        """
        from tests.semantic.models import Class1, Class13, Class2, Class4, \
            Class123, Individual1

        class1 = Class1(id="12")
        class13 = Class13()

        # check for correct rules
        self.assertEqual(class1.oProp1.rule, "some (Class2 or Class4)")
        self.assertEqual(class13.objProp2.rule,
               "some Class1, value Individual1, some (Class1 and Class2)")

        # test simple rule
        self.assertFalse(class1.oProp1.is_valid())
        class1.oProp1.append(Class2())
        self.assertTrue(class1.oProp1.is_valid())
        class1.oProp1.append(Class4())
        self.assertTrue(class1.oProp1.is_valid())
        class1.oProp1.append(Class123())
        self.assertTrue(class1.oProp1.is_valid())

        # test complex rule
        self.assertTrue(class13.objProp2.is_valid())
        del class13.objProp2[0]
        self.assertFalse(class13.objProp2.is_valid())
        class13.objProp2.append(class1)
        self.assertFalse(class13.objProp2.is_valid())
        class13.objProp2.append(Class123())
        self.assertFalse(class13.objProp2.is_valid())
        del class13.objProp2[1]
        class13.objProp2.append(Individual1())
        self.assertTrue(class13.objProp2.is_valid())

        # todo test statement cases: min, max,...

    def test_5_model_data_field_validation(self):
        """
        Test if data fields are correctly validated
        """
        from tests.semantic.models import Class1, Class3
        class3 = Class3()

        self.assertTrue(class3.dataProp1.is_valid())

        class3.dataProp1.append("12")
        self.assertFalse(class3.dataProp1.is_valid())
        class3.dataProp1.append("2")
        self.assertFalse(class3.dataProp1.is_valid())
        class3.dataProp1.insert(0, "1")
        del class3.dataProp1[1]
        self.assertTrue(class3.dataProp1.is_valid())

        self.assertTrue(2 in Class1().dataProp2)

    def test_6_back_referencing(self):
        """
        Test if referencing of relations correctly works
        """
        from tests.semantic.models import Class1, Class3, Class2, Class4

        c1 = Class1()
        c2 = Class2()
        c3 = Class3()

        c1.oProp1.append(c2)
        self.assertEqual(c2.references[c1.get_identifier()], ["oProp1"])
        self.assertRaises(ValueError, c1.oProp1.extend, [c2])
        self.assertEqual(c2.references[c1.get_identifier()], ["oProp1"])
        c1.objProp2.extend([c2])
        c3.objProp2.append(c2)
        self.assertEqual(c2.references[c1.get_identifier()],
                         ["oProp1", "objProp2"])
        self.assertEqual(c2.references[c3.get_identifier()], ["objProp2"])

        c1.oProp1.remove(c2)
        self.assertEqual(c2.references[c1.get_identifier()], ["objProp2"])

        del c1.objProp2[0]
        self.assertNotIn(c1.get_identifier(), c2.references)

    def test_7_test_instance_creation_inject(self):
        """
        Test if instances with the same id point to the same object
        """
        from tests.semantic.models import Class1, Class13, Class123, \
            Individual1, Gertrude, semantic_manager


        # clear local state to ensure standard test condition
        self.clear_registry()

        class13 = Class13(id="13")
        rel1 = class13.oProp1
        class13.objProp3.append(Class1(id="1"))

        class13_ = Class13(id="13")
        class13__ = Class13(id="132")
        self.assertTrue(class13_ == class13)
        self.assertFalse(class13__ == class13)
        self.assertTrue(class13_.oProp1 == rel1)

        class1_ = Class1(id="1")
        self.assertTrue(class1_ == class13.objProp3[0])

    def test_8_test_saving_and_loading(self):
        """
        Test if instances can be saved to Fiware and correctly loaded again
        """
        from tests.semantic.models import Class1, Class13, Class123, \
            Individual1, Gertrude, semantic_manager

        # clear local state to ensure standard test condition
        self.clear_registry()

        # TEST1: Save local instances to Fiware, clear the local
        # state recreate an instance and check if it was properly loaded from
        # Fiware

        # created classes with cycle
        class13 = Class13(id="13")
        class1 = Class1(id="1")
        class13.objProp3.append(class1)
        class13.objProp3.append(class13)
        class13.objProp3.append(Individual1())
        class13.dataProp1.extend([1, 2, 4])

        # class1.oProp1.append(class13)

        self.assertRaises(AssertionError, semantic_manager.save_state)
        semantic_manager.save_state(assert_validity=False)

        # clear local state to ensure standard test condition
        self.clear_registry()
        self.assertFalse(class13.get_identifier() in
                         semantic_manager.instance_registry._registry)

        class13_ = Class13(id="13")
        self.assertTrue(2 in class13_.dataProp2)

        self.assertEqual(class13.get_identifier(), class13_.get_identifier())
        self.assertEqual(class13.id, class13_.id)
        self.assertEqual(class13.objProp3.get_all_raw(),
                         class13_.objProp3.get_all_raw())
        self.assertEqual(class13.dataProp1.get_all_raw(),
                         class13_.dataProp1.get_all_raw())
        self.assertTrue(class13.get_identifier() in
                        semantic_manager.instance_registry._registry)

    def test_9_deleting(self):
        """
        Test if a device is correctly deleted from fiware,
        deleted from other instances fields if deleted,
        and not be pulled again from Fiware once deleted locally
        """
        from tests.semantic.models import Class1, Class13, Class123, \
            Individual1, Gertrude, semantic_manager

        # clear local state to ensure standard test condition
        self.clear_registry()

        # Test 1: Local deletion

        # create classes
        class13 = Class13(id="13")

        class1 = Class1(id="1")
        class13.objProp3.append(class1)

        # make sure references are not global in all SemanticClasses
        # (happend in the past)
        self.assertFalse(str(class13.references) == str(class1.references))
        self.assertTrue(len(class13.references) == 1)  # inverse_ added
        self.assertTrue(len(class1.references) == 1)

        # test reference deletion
        class1.delete()
        self.assertTrue(len(class13.objProp3.get_all_raw()) == 0)

        # Test 2:  deletion with Fiware object
        self.clear_registry()

        class13 = Class13(id="13")
        class1 = Class1(id="1")
        class13.objProp3.append(class1)

        semantic_manager.save_state(assert_validity=False)
        self.clear_registry()

        # load class1 from Fiware, and delete it
        # class13 should be then also loaded have the reference deleted and
        # be saved
        class1 = Class1(id="1")
        identifier1 = class1.get_identifier()
        class1.delete()

        semantic_manager.save_state(assert_validity=False)
        self.clear_registry()
        self.assertTrue(len(semantic_manager.instance_registry.get_all()) == 0)

        # class 1 no longer exists in fiware, and the fiware entry of class13
        # should have no more reference to it
        self.assertFalse(semantic_manager.does_instance_exists(identifier1))
        self.assertTrue(len(Class13(id="13").objProp3.get_all_raw()) == 0)

        self.assertRaises(AssertionError, semantic_manager.save_state)
        semantic_manager.save_state(assert_validity=False)

        # Test 3:  if deleted locally, the instance should not be pulled
        # again from fiware.
        self.clear_registry()

        class13 = Class13(id="13")
        class13.dataProp1.append("Test")
        semantic_manager.save_state(assert_validity=False)

        class13.delete()
        class13_ = Class13(id="13")
        self.assertTrue(len(class13_.dataProp1.get_all_raw()) == 0)

    def test__10_field_set_methode(self):
        """
        Test if the values of fields are correctly set with the list methods
        """
        from tests.semantic.models import Class1, Class13, Class3, Class123

        # clear local state to ensure standard test condition
        self.clear_registry()

        class13 = Class13(id="13")
        class1 = Class1(id="1")
        class13.objProp3.append(class1)

        class13.dataProp1.append(1)
        class13.dataProp1.append(2)

        class13.dataProp1.set([9, 8, 7, 6])
        c123 = Class123(id=2)
        c3 = Class3()
        class13.objProp3.set([c3, c123])
        self.assertTrue(class13.dataProp1._list == [9, 8, 7, 6])
        self.assertTrue(class13.objProp3._list == [c3.get_identifier(),
                                                   c123.get_identifier()])

    def clear_registry(self):
        """
        Clear the local state. Needed to test the interaction with Fiware if
        the local state of an instance is missing
        """
        from tests.semantic.models import semantic_manager
        semantic_manager.instance_registry._registry.clear()
        semantic_manager.instance_registry._deleted_identifiers.clear()
        self.assertTrue(len(semantic_manager.instance_registry._registry) == 0)

    def test__11_model_creation_with_devices(self):
        """
        Test the creation of a models file with DeviceClasses.
        The models are used for further tests
        """
        vocabulary = VocabularyConfigurator.create_vocabulary(
            VocabularySettings(
                pascal_case_class_labels=False,
                pascal_case_individual_labels=False,
                camel_case_property_labels=False,
                camel_case_datatype_labels=False,
                pascal_case_datatype_enum_labels=False
            ))

        vocabulary = \
            VocabularyConfigurator.add_ontology_to_vocabulary_as_file(
                vocabulary=vocabulary,
                path_to_file=self.get_file_path(
                    'ontology_files/ParsingTesterOntology.ttl'))

        vocabulary.get_data_property(
            "http://www.semanticweb.org/redin/ontologies/2020/11/untitled"
            "-ontology-25#commandProp").field_type = DataFieldType.command
        vocabulary.get_data_property(
            "http://www.semanticweb.org/redin/ontologies/2020/11/untitled"
            "-ontology-25#attributeProp").field_type = \
            DataFieldType.device_attribute

        VocabularyConfigurator.generate_vocabulary_models(
            vocabulary, "./", "models2")

    def test__13_device_creation(self):
        """
        Test if a device is correctly instantiated
        And the settings can be set
        """
        from tests.semantic.models2 import Class3, semantic_manager

        test_header = InstanceHeader(
            cb_url=settings.CB_URL,
            iota_url=settings.IOTA_URL,
            service="testing",
            service_path="/"
        )
        semantic_manager.set_default_header(test_header)

        class3_ = Class3()
        class3_.device_settings.endpoint = "http://test.com"
        self.assertEqual(class3_.device_settings.endpoint, "http://test.com")

    def test__14_device_saving_and_loading(self):
        """
        Test if a Device can be correctly saved and loaded.
        And the live methods of Commands and DeviceAttributes
        """
        from tests.semantic.models2 import Class1,  Class3, semantic_manager

        test_header = InstanceHeader(
            cb_url=settings.CB_URL,
            iota_url=settings.IOTA_URL,
            service="testing",
            service_path="/"
        )
        semantic_manager.set_default_header(test_header)

        class3_ = Class3(id="3")
        class3_.device_settings.endpoint = "http://test.com"
        class3_.device_settings.transport = TransportProtocol.HTTP

        class3_.oProp1.append(Class1(id="19"))
        class3_.dataProp1.append("Test")

        # Class1(id="19").oProp1.append(class3_)

        class3_.commandProp.append(Command(name="on"))
        class3_.commandProp.append(Command(name="off"))
        class3_.attributeProp.append(
            DeviceAttribute(name="d1",
                            attribute_type=DeviceAttributeType.lazy))
        class3_.attributeProp.append(
            DeviceAttribute(name="d2",
                            attribute_type=DeviceAttributeType.active))

        # test that live access methods fail, because state was not saved
        self.assertRaises(Exception, class3_.attributeProp[0].get_value)
        self.assertRaises(Exception, class3_.commandProp[0].get_info)
        self.assertRaises(Exception, class3_.commandProp[0].get_status)
        self.assertRaises(Exception, class3_.commandProp[0].send)

        semantic_manager.save_state(assert_validity=False)

        # Test if device could be processed correctly -> corresponding entity
        # in Fiware
        with ContextBrokerClient(
                fiware_header=test_header.get_fiware_header()) as client:
            assert client.get_entity(entity_id="3", entity_type="Class3")

        self.clear_registry()

        loaded_class = Class3(id="3")

        attr2 = class3_.attributeProp[1]
        attr2_ = loaded_class.attributeProp[1]
        self.assertEqual(attr2.name, attr2_.name)
        self.assertEqual(attr2.attribute_type, attr2_.attribute_type)
        self.assertEqual(attr2._instance_link.instance_identifier,
                         attr2_._instance_link.instance_identifier)
        self.assertEqual(attr2._instance_link.field_name, attr2_._instance_link.field_name)

        com2 = class3_.commandProp[1]
        com2_ = loaded_class.commandProp[1]
        self.assertEqual(com2.name, com2_.name)
        self.assertEqual(com2._instance_link.instance_identifier,
                         com2_._instance_link.instance_identifier)
        self.assertEqual(attr2._instance_link.field_name, attr2_._instance_link.field_name)

        self.assertEqual(class3_.references, loaded_class.references)

        self.assertEqual(class3_.device_settings.dict(),
                         loaded_class.device_settings.dict())

        # test that live access methods succeed, because state was saved
        class3_.attributeProp[0].get_value()
        class3_.commandProp[0].get_info()
        class3_.commandProp[0].get_status()
        class3_.commandProp[0].send()

    def test__15_device_deleting(self):
        """
        Test if SemanticDeviceClass.delete() completly removes the device and
        context entry from Fiware.
        All other interactions are covered in the "deleting test"
        """
        from tests.semantic.models2 import Class1, Class3, semantic_manager

        # clear local state to ensure standard test condition
        self.clear_registry()

        # Test 1: Local deletion

        # create class
        class3_ = Class3(id="13")
        class3_.device_settings.endpoint = "http://test.com"
        class3_.device_settings.transport = TransportProtocol.HTTP

        semantic_manager.save_state(assert_validity=False)
        self.clear_registry()

        # load class from Fiware, and delete it
        class3_ = Class3(id="13")
        class3_.delete()

        semantic_manager.save_state(assert_validity=False)
        self.clear_registry()
        self.assertTrue(len(semantic_manager.instance_registry.get_all()) == 0)

        # class no longer exists in fiware iota or context broker
        with IoTAClient(
                fiware_header=semantic_manager.
                default_header.get_fiware_header()) as client:
            self.assertEqual(len(client.get_device_list()), 0)

        with ContextBrokerClient(
                fiware_header=semantic_manager.
                default_header.get_fiware_header()) as client:
            self.assertEqual(len(client.get_entity_list()), 0)

    def test__16_field_name_checks(self):
        """
        Test if Commands and Attributes are prevented from having blacklised
        names
        """
        from tests.semantic.models2 import Class3

        class3 = Class3(id="13")

        c = Command(name="dataProp1")

        self.assertEqual(c.get_all_field_names(),
                         ['dataProp1', 'dataProp1_info', 'dataProp1_result'])
        self.assertRaises(NameError, class3.commandProp.append, c)

        class3.commandProp.append(Command(name="c1"))
        self.assertRaises(NameError, class3.commandProp.append, Command(
            name="c1_info"))
        self.assertRaises(NameError, class3.commandProp.append, Command(
            name="type"))
        self.assertRaises(NameError, class3.commandProp.append, Command(
            name="referencedBy"))

        class3.attributeProp.append(
            DeviceAttribute(name="_type",
                            attribute_type=DeviceAttributeType.active))

        self.assertRaises(
            NameError,
            class3.attributeProp.append,
            DeviceAttribute(name="!type",
                            attribute_type=DeviceAttributeType.active))

        self.assertEqual(
            class3.get_all_field_names(),
            ['attributeProp', 'attributeProp__type', 'commandProp',
             'c1', 'c1_info', 'c1_result', 'dataProp1', 'oProp1', 'objProp2'])

    def test__17_save_and_load_local_state(self):
        """
        Test if the local state can be correctly saved as json and loaded again
        """
        from tests.semantic.models2 import Class3, Class1, semantic_manager

        class3 = Class3(id="15")
        class3.commandProp.append(Command(name="c1"))
        class3.attributeProp.append(
            DeviceAttribute(name="_type",
                            attribute_type=DeviceAttributeType.active))

        class3.dataProp1.append("test")
        class3.device_settings.apikey = "ttt"
        class1 = Class1(id="11")
        class3.objProp2.append(class1)

        save = semantic_manager.save_local_state_as_json()
        semantic_manager.instance_registry.clear()

        semantic_manager.load_local_state_from_json(json=save)

        class3_ = Class3(id="15")
        class1_ = Class1(id="11")
        self.assertTrue("test" in class3_.dataProp1.get_all_raw())
        self.assertEqual(class3_.device_settings.dict(),
                         class3.device_settings.dict())
        self.assertTrue(class3_.commandProp[0].name == "c1")
        self.assertTrue(class3_.attributeProp[0].name == "_type")
        self.assertTrue(class3_.attributeProp[0].attribute_type ==
                        DeviceAttributeType.active)

        self.assertTrue(class3_.objProp2[1].id == "11")
        self.assertTrue(class3_.objProp2[1].get_type() == class1.get_type())

        self.assertTrue(class1_.references == class1.references)

    def test__18_inverse_relations(self):
        """
        Test if a instance is added to the added instance, if an inverse
        logic exists
        """
        from tests.semantic.models2 import Class1

        inst_1 = Class1(id="100")
        inst_2 = Class1(id="101")
        inst_1.oProp1.append(inst_2)

        self.assertTrue(inst_2.get_identifier()
                        in inst_1.oProp1.get_all_raw())
        self.assertTrue(inst_1.get_identifier()
                        in inst_2.objProp3.get_all_raw())

        inst_2.objProp3.remove(inst_1)
        self.assertFalse(inst_2.get_identifier()
                         in inst_1.oProp1.get_all_raw())
        self.assertFalse(inst_1.get_identifier()
                         in inst_2.objProp3.get_all_raw())

    def test__19_merge_states(self):
        """
        Tests if a local state is correctly merged with changes on the live
        state
        """
        from tests.semantic.models2 import Class1, semantic_manager

        # used instances
        c1 = Class1(id="1")
        c2 = Class1(id="2")
        c3 = Class1(id="3")
        c4 = Class1(id="4")

        # create state
        inst_1 = Class1(id="100")
        inst_1.dataProp2.remove(2)  # default value
        inst_1.dataProp2.append("Test")
        inst_1.dataProp2.append("Test2")

        inst_1.oProp1.extend([c1,c2])

        old_state = inst_1.build_context_entity()

        semantic_manager.save_state(assert_validity=False)

        # change live state
        inst_1.dataProp2.append("Test3")
        inst_1.dataProp2.remove("Test")
        inst_1.oProp1.remove(c1)
        inst_1.oProp1.append(c3)

        self.assertEqual(set(inst_1.dataProp2.get_all()), {"Test2", "Test3"})
        self.assertEqual(set(inst_1.oProp1.get_all_raw()),
                         {c2.get_identifier(), c3.get_identifier()})
        self.assertEqual(inst_1.references.keys(),
                         {c2.get_identifier(), c3.get_identifier()})
        semantic_manager.save_state(assert_validity=False)
        self.assertEqual(set(inst_1.dataProp2.get_all()), {"Test2", "Test3"})
        self.assertEqual(set(inst_1.oProp1.get_all_raw()),
                         {c2.get_identifier(), c3.get_identifier()})

        # reset local state and change it
        inst_1.dataProp2.set(["Test", "Test4"])
        inst_1.oProp1.set([c1, c4])
        inst_1.old_state.state = old_state

        self.assertEqual(set(inst_1.dataProp2.get_all()), {"Test", "Test4"})
        self.assertEqual(set(inst_1.oProp1.get_all_raw()),
                         {c1.get_identifier(), c4.get_identifier()})
        self.assertEqual(inst_1.references.keys(),
                         {c1.get_identifier(), c4.get_identifier()})

        semantic_manager.save_state(assert_validity=False)

        # local state is merged correctly
        self.assertEqual(set(inst_1.dataProp2.get_all()), {"Test3", "Test4"})
        self.assertEqual(set(inst_1.oProp1.get_all_raw()),
                         {c3.get_identifier(), c4.get_identifier()})
        self.assertEqual(inst_1.references.keys(),
                         {c3.get_identifier(), c4.get_identifier()})

        # live state is merged correctly
        self.clear_registry()
        inst_1 = Class1(id="100")
        self.assertEqual(set(inst_1.dataProp2.get_all()), {"Test3", "Test4"})
        self.assertEqual(set(inst_1.oProp1.get_all_raw()),
                         {c3.get_identifier(), c4.get_identifier()})
        self.assertEqual(inst_1.references.keys(),
                         {c3.get_identifier(), c4.get_identifier()})

    def test__20_merge_states_for_devices(self):
        """
        Tests if a local state is correctly merged with changes on the live
        state. This test focuses on the special details of a
        SemanticDeviceClass the general things are covered by test 120
        """
        from tests.semantic.models2 import Class3, semantic_manager
        self.clear_registry()

        test_header = InstanceHeader(
            cb_url=settings.CB_URL,
            service="testing",
            service_path="/"
        )
        semantic_manager.set_default_header(test_header)

        # setup state
        inst_1 = Class3(id="3")

        inst_1.device_settings.endpoint = "http://localhost:88"
        inst_1.device_settings.transport = TransportProtocol.HTTP
        inst_1.commandProp.append(Command(name="testC"))
        inst_1.attributeProp.append(
            DeviceAttribute(name="test",
                            attribute_type=DeviceAttributeType.active))


        old_state = inst_1.build_context_entity()

        semantic_manager.save_state()
        self.assertEqual(inst_1.device_settings.apikey, None)

        # change live state
        inst_1.device_settings.apikey = "test"
        inst_1.device_settings.timezone = "MyZone"
        del inst_1.commandProp[0]
        inst_1.commandProp.append(Command(name="testC2"))
        del inst_1.attributeProp[0]
        inst_1.attributeProp.append(
            DeviceAttribute(name="test2",
                            attribute_type=DeviceAttributeType.lazy))

        semantic_manager.save_state()
        self.assertEqual(inst_1.device_settings.apikey, "test")
        self.assertEqual(len(inst_1.commandProp), 1)
        self.assertEqual(inst_1.commandProp[0].name, "testC2")
        self.assertEqual(len(inst_1.attributeProp), 1)
        self.assertEqual(inst_1.attributeProp[0].name, "test2")
        self.assertEqual(inst_1.attributeProp[0].attribute_type,
                         DeviceAttributeType.lazy)

        # reset local state and change it
        inst_1.old_state.state = old_state
        inst_1.device_settings.endpoint = "http://localhost:21"
        inst_1.device_settings.transport = TransportProtocol.HTTP
        inst_1.device_settings.apikey = None
        inst_1.attributeProp.clear()
        inst_1.commandProp.clear()
        inst_1.commandProp.append(Command(name="testC3"))
        inst_1.attributeProp.append(
            DeviceAttribute(name="test3",
                            attribute_type=DeviceAttributeType.active))

        inst_1.device_settings.timezone = "MyNewZone"

        semantic_manager.save_state()

        # local state is merged correctly
        self.assertEqual(inst_1.device_settings.endpoint, "http://localhost:21")
        self.assertEqual(inst_1.device_settings.apikey, "test")
        self.assertEqual(inst_1.device_settings.timezone, "MyNewZone")
        self.assertEqual(len(inst_1.commandProp), 2)
        self.assertEqual({inst_1.commandProp[0].name, inst_1.commandProp[
            1].name}, {"testC3", "testC2"})
        self.assertEqual(len(inst_1.attributeProp), 2)
        self.assertEqual({inst_1.attributeProp[0].name, inst_1.attributeProp[
            1].name}, {"test2", "test3"})


        # live state is merged correctly
        self.clear_registry()
        inst_1 = Class3(id="3")
        self.assertEqual(inst_1.device_settings.endpoint, "http://localhost:21")
        self.assertEqual(inst_1.device_settings.apikey, "test")
        self.assertEqual(inst_1.device_settings.timezone, "MyNewZone")
        self.assertEqual(len(inst_1.commandProp), 2)
        self.assertEqual({inst_1.commandProp[0].name, inst_1.commandProp[
            1].name}, {"testC3", "testC2"})
        self.assertEqual(len(inst_1.attributeProp), 2)
        self.assertEqual({inst_1.attributeProp[0].name, inst_1.attributeProp[
            1].name}, {"test2", "test3"})

    def tearDown(self) -> None:
        """
        Cleanup test server
        """
        self.clear_registry()
        clear_all(fiware_header=FiwareHeader(service="testing",
                                             service_path="/"),
                  cb_url=settings.CB_URL,
                  iota_url=settings.IOTA_URL)

    @staticmethod
    def get_file_path(path_end: str) -> str:
        """
        Get the correct path to the file needed for this test
        """

        # Test if the testcase was run directly or over in a global test-run.
        # Match the needed path to the config file in both cases

        path = Path(__file__).parent.resolve()
        return str(path.joinpath(path_end))






