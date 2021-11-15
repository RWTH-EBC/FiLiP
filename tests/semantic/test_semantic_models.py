import time
import unittest

from pathlib import Path

from filip.models import FiwareHeader

from filip.models.ngsi_v2.iot import TransportProtocol

from tests.config import settings
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

        VocabularyConfigurator.generate_vocabulary_models(
            vocabulary, f"{self.get_file_path('')}/","models")

    def test_2_default_header(self):
        """
        Test if a new class without header gets teh default header
        """
        from tests.semantic.models import Class1, semantic_manager

        test_header = InstanceHeader(
            cb_url=settings.CB_URL,
            iota_url=settings.IOTA_JSON_URL,
            service=settings.FIWARE_SERVICE,
            service_path=settings.FIWARE_SERVICEPATH
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
            Class123, Individual1, Close_Command, State, Open_Close_State, \
            Measurement

        class1 = Class1(id="12")
        class13 = Class13()

        # check for correct rules
        self.assertEqual(class1.oProp1.rule, "some (Class2 or Class4)")
        self.assertEqual(class13.objProp2.rule,
                         "some Class1, value Individual1, some (Class1 and Class2)")

        # test simple rule
        self.assertFalse(class1.oProp1.is_valid())
        class1.oProp1.add(Class2())
        self.assertTrue(class1.oProp1.is_valid())
        class1.oProp1.add(Class4())
        self.assertTrue(class1.oProp1.is_valid())
        class1.oProp1.add(Class123())
        self.assertTrue(class1.oProp1.is_valid())

        # test complex rule
        self.assertTrue(class13.objProp2.is_valid())
        class13.objProp2.clear()
        self.assertFalse(class13.objProp2.is_valid())
        class13.objProp2.add(class1)
        self.assertFalse(class13.objProp2.is_valid())
        class13.objProp2.add(Class123(id="311"))
        self.assertFalse(class13.objProp2.is_valid())
        class13.objProp2.remove(Class123(id="311"))
        class13.objProp2.add(Individual1())
        self.assertTrue(class13.objProp2.is_valid())

        # Test statement cases:

        # min
        c4 = Class4(id="c4")
        self.assertFalse(c4.objProp4.is_valid())
        c4.objProp4.add(c4)
        self.assertFalse(c4.objProp4.is_valid())
        c4.objProp4.add(Class1(id="c1"))
        self.assertTrue(c4.objProp4.is_valid())
        c4.objProp4.add(Class1(id="c1"))
        self.assertTrue(c4.objProp4.is_valid())

        # max
        ccc = Close_Command(id="ccc")
        self.assertTrue(ccc.Has_Description.is_valid())
        ccc.Has_Description.add("2")
        self.assertTrue(ccc.Has_Description.is_valid())
        ccc.Has_Description.add("3")
        self.assertFalse(ccc.Has_Description.is_valid())

        # only
        self.assertTrue(ccc.Acts_Upon.is_valid())
        ccc.Acts_Upon.add(State(id="s1"))
        self.assertFalse(ccc.Acts_Upon.is_valid())
        ccc.Acts_Upon.clear()
        ccc.Acts_Upon.add(Open_Close_State())
        self.assertTrue(ccc.Acts_Upon.is_valid())
        ccc.Acts_Upon.add(Open_Close_State())
        self.assertTrue(ccc.Acts_Upon.is_valid())
        ccc.Acts_Upon.add(ccc)
        self.assertFalse(ccc.Acts_Upon.is_valid())

        # some
        c13 = Class13(id="c13")
        self.assertFalse(c13.objProp3.is_valid())
        c13.objProp3.add(ccc)
        self.assertFalse(c13.objProp3.is_valid())
        c13.objProp3.add(c13)
        self.assertTrue(c13.objProp3.is_valid())

        # exactly
        m = Measurement(id="m")
        self.assertFalse(m.Has_Value.is_valid())
        m.Has_Value.add(1.2)
        self.assertTrue(m.Has_Value.is_valid())
        m.Has_Value.add(5)
        self.assertFalse(m.Has_Value.is_valid())

    def test_5_model_data_field_validation(self):
        """
        Test if data fields are correctly validated
        """
        from tests.semantic.models import Class1, Class3
        class3 = Class3()

        self.assertTrue(class3.dataProp1.is_valid())

        class3.dataProp1.add("12")
        self.assertFalse(class3.dataProp1.is_valid())
        class3.dataProp1.add("2")
        self.assertFalse(class3.dataProp1.is_valid())
        class3.dataProp1.add("1")
        class3.dataProp1.remove("12")
        self.assertTrue(class3.dataProp1.is_valid())
        self.assertTrue(2 in Class1().dataProp2.get_all())

    def test_6_back_referencing(self):
        """
        Test if referencing of relations correctly works
        """
        from tests.semantic.models import Class1, Class3, Class2, Class4

        c1 = Class1()
        c2 = Class2()
        c3 = Class3()

        c1.oProp1.add(c2)
        self.assertEqual(c2.references[c1.get_identifier()], ["oProp1"])
        # self.assertRaises(ValueError, c1.oProp1.update, [c2])
        self.assertEqual(c2.references[c1.get_identifier()], ["oProp1"])
        c1.objProp2.update([c2])
        c3.objProp2.add(c2)
        self.assertEqual(c2.references[c1.get_identifier()],
                         ["oProp1", "objProp2"])
        self.assertEqual(c2.references[c3.get_identifier()], ["objProp2"])

        c1.oProp1.remove(c2)
        self.assertEqual(c2.references[c1.get_identifier()], ["objProp2"])

        c1.objProp2.remove(c2)
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
        class13.objProp3.add(Class1(id="1"))

        class13_ = Class13(id="13")
        class13__ = Class13(id="132")
        self.assertTrue(class13_ == class13)
        self.assertFalse(class13__ == class13)
        self.assertTrue(class13_.oProp1 == rel1)

        class1_ = Class1(id="1")
        self.assertTrue(class1_ == class13.objProp3.get_all()[0])

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
        class13.objProp3.add(class1)
        class13.objProp3.add(class13)
        class13.objProp3.add(Individual1())
        class13.dataProp1.update([1, 2, 4])

        # class1.oProp1.add(class13)

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
        class13.objProp3.add(class1)

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
        class13.objProp3.add(class1)

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
        class13.dataProp1.add("Test")
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
        class13.objProp3.add(class1)

        class13.dataProp1.add(1)
        class13.dataProp1.add(2)

        class13.dataProp1.set([9, 8, 7, 6])
        c123 = Class123(id=2)
        c3 = Class3()
        class13.objProp3.set([c3, c123])
        self.assertTrue(class13.dataProp1._set == {9, 8, 7, 6})
        self.assertTrue(class13.objProp3._set == {c3.get_identifier(),
                                                  c123.get_identifier()})

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
            vocabulary, f"{self.get_file_path('')}/", "models2")

    def test__12_device_creation(self):
        """
        Test if a device is correctly instantiated
        And the settings can be set
        """
        from tests.semantic.models2 import Class3, semantic_manager
        test_header = InstanceHeader(
            cb_url=settings.CB_URL,
            iota_url=settings.IOTA_JSON_URL,
            service=settings.FIWARE_SERVICE,
            service_path=settings.FIWARE_SERVICEPATH
        )
        semantic_manager.set_default_header(test_header)

        class3_ = Class3()
        class3_.device_settings.endpoint = "http://test.com"
        self.assertEqual(class3_.device_settings.endpoint, "http://test.com")

    def test__13_device_saving_and_loading(self):
        """
        Test if a Device can be correctly saved and loaded.
        And the live methods of Commands and DeviceAttributes
        """
        from tests.semantic.models2 import Class1, Class3, semantic_manager

        class3_ = Class3(id="3")
        class3_.device_settings.endpoint = "http://test.com"
        class3_.device_settings.transport = TransportProtocol.HTTP

        class3_.oProp1.add(Class1(id="19"))
        class3_.dataProp1.add("Test")

        # Class1(id="19").oProp1.add(class3_)

        class3_.commandProp.add(Command(name="on"))
        class3_.commandProp.add(Command(name="off"))
        class3_.attributeProp.add(
            DeviceAttribute(name="d1",
                            attribute_type=DeviceAttributeType.lazy))
        class3_.attributeProp.add(
            DeviceAttribute(name="d2",
                            attribute_type=DeviceAttributeType.active))

        # test that live access methods fail, because state was not saved
        self.assertRaises(Exception,
                          class3_.attributeProp.get_all()[0].get_value)
        self.assertRaises(Exception,
                          class3_.commandProp.get_all()[0].get_info)
        self.assertRaises(Exception,
                          class3_.commandProp.get_all()[0].get_status)
        self.assertRaises(Exception,
                          class3_.commandProp.get_all()[0].send)

        semantic_manager.save_state(assert_validity=False)

        # Test if device could be processed correctly -> corresponding entity
        # in Fiware
        with ContextBrokerClient(
                fiware_header=class3_.header.get_fiware_header()) as client:
            assert client.get_entity(entity_id="3", entity_type="Class3")

        self.clear_registry()

        loaded_class = Class3(id="3")

        attr2 = [a for a in class3_.attributeProp.get_all()
                 if a.name == "d2"][ 0]
        attr2_ = [a for a in loaded_class.attributeProp.get_all() if
                  a.name == "d2"][0]
        self.assertEqual(attr2.name, attr2_.name)
        self.assertEqual(attr2.attribute_type, attr2_.attribute_type)
        self.assertEqual(attr2._instance_link.instance_identifier,
                         attr2_._instance_link.instance_identifier)
        self.assertEqual(attr2._instance_link.field_name,
                         attr2_._instance_link.field_name)

        com2 = [c for c in class3_.commandProp.get_all()
                if c.name == "off"][0]
        com2_ = [c for c in loaded_class.commandProp.get_all()
                 if c.name == "off"][0]
        self.assertEqual(com2.name, com2_.name)
        self.assertEqual(com2._instance_link.instance_identifier,
                         com2_._instance_link.instance_identifier)
        self.assertEqual(attr2._instance_link.field_name,
                         attr2_._instance_link.field_name)

        self.assertEqual(class3_.references, loaded_class.references)

        self.assertEqual(class3_.device_settings.dict(),
                         loaded_class.device_settings.dict())

        # test that live access methods succeed, because state was saved
        class3_.attributeProp.get_all()[0].get_value()
        class3_.commandProp.get_all()[0].get_info()
        class3_.commandProp.get_all()[0].get_status()
        class3_.commandProp.get_all()[0].send()

        # test if fields are removed and updated
        class3_.commandProp.clear()
        class3_.attributeProp.clear()
        class3_.commandProp.add(Command(name="NEW_COMMAND"))
        class3_.attributeProp.add(
            DeviceAttribute(name="NEW_ATT",
                            attribute_type=DeviceAttributeType.lazy))

        class3_.dataProp1.add("TEST!!!")
        semantic_manager.save_state(assert_validity=False)
        self.clear_registry()
        with semantic_manager.get_iota_client(class3_.header) as client:
            device = client.get_device(device_id=class3_.get_device_id())
            self.assertTrue(len(device.commands), 1)
            self.assertTrue(len(device.attributes), 1)
            for command in device.commands:
                self.assertTrue(command.name, "NEW_COMMAND")
            for attr in device.attributes:
                self.assertTrue(attr.name, "NEW_ATT")

            for static_attr in device.static_attributes:
                if static_attr.name == "dataProp1":
                    self.assertTrue(static_attr.value, ["TEST!!!"])

    def test__14_device_deleting(self):
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

    def test__15_field_name_checks(self):
        """
        Test if Commands and Attributes are prevented from having blacklised
        names
        """
        from tests.semantic.models2 import Class3

        class3 = Class3(id="13")

        c = Command(name="dataProp1")

        self.assertEqual(c.get_all_field_names(),
                         ['dataProp1', 'dataProp1_info', 'dataProp1_result'])
        self.assertRaises(NameError, class3.commandProp.add, c)

        class3.commandProp.add(Command(name="c1"))
        self.assertRaises(NameError, class3.commandProp.add, Command(
            name="c1_info"))
        self.assertRaises(NameError, class3.commandProp.add, Command(
            name="type"))
        self.assertRaises(NameError, class3.commandProp.add, Command(
            name="referencedBy"))

        class3.attributeProp.add(
            DeviceAttribute(name="_type",
                            attribute_type=DeviceAttributeType.active))

        self.assertRaises(
            NameError,
            class3.attributeProp.add,
            DeviceAttribute(name="!type",
                            attribute_type=DeviceAttributeType.active))

        self.assertEqual(
            class3.get_all_field_names(),
            ['attributeProp', 'attributeProp__type', 'commandProp',
             'c1', 'c1_info', 'c1_result', 'dataProp1', 'oProp1', 'objProp2'])

    def test__16_save_and_load_local_state(self):
        """
        Test if the local state can be correctly saved as json and loaded again
        """
        from tests.semantic.models2 import Class3, Class1, semantic_manager

        class3 = Class3(id="15")
        class3.commandProp.add(Command(name="c1"))
        class3.attributeProp.add(
            DeviceAttribute(name="_type",
                            attribute_type=DeviceAttributeType.active))

        class3.dataProp1.add("test")
        class3.device_settings.apikey = "ttt"
        class1 = Class1(id="11")
        class3.objProp2.add(class1)

        save = semantic_manager.save_local_state_as_json()
        semantic_manager.instance_registry.clear()

        semantic_manager.load_local_state_from_json(json=save)

        class3_ = Class3(id="15")
        class1_ = Class1(id="11")
        self.assertTrue("test" in class3_.dataProp1.get_all_raw())
        self.assertEqual(class3_.device_settings.dict(),
                         class3.device_settings.dict())
        self.assertTrue(class3_.commandProp.get_all()[0].name == "c1")
        self.assertTrue(class3_.attributeProp.get_all()[0].name == "_type")
        self.assertTrue(class3_.attributeProp.get_all()[0].attribute_type ==
                        DeviceAttributeType.active)

        added_class = [c for c in class3_.objProp2.get_all() if
                       isinstance(c, SemanticClass)][0]
        self.assertTrue(added_class.id == "11")
        self.assertTrue(added_class.get_type() == class1.get_type())

        self.assertTrue(class1_.references == class1.references)

    def test__17_inverse_relations(self):
        """
        Test if a instance is added to the added instance, if an inverse
        logic exists
        """
        from tests.semantic.models2 import Class1

        inst_1 = Class1(id="100")
        inst_2 = Class1(id="101")
        inst_1.oProp1.add(inst_2)

        self.assertTrue(inst_2.get_identifier()
                        in inst_1.oProp1.get_all_raw())
        self.assertTrue(inst_1.get_identifier()
                        in inst_2.objProp3.get_all_raw())

        inst_2.objProp3.remove(inst_1)
        self.assertFalse(inst_2.get_identifier()
                         in inst_1.oProp1.get_all_raw())
        self.assertFalse(inst_1.get_identifier()
                         in inst_2.objProp3.get_all_raw())

    def test__18_merge_states(self):
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
        inst_1.dataProp2.add("Test")
        inst_1.dataProp2.add("Test2")

        inst_1.oProp1.update([c1, c2])

        old_state = inst_1.build_context_entity()

        semantic_manager.save_state(assert_validity=False)

        # change live state
        inst_1.dataProp2.add("Test3")
        inst_1.dataProp2.remove("Test")
        inst_1.oProp1.remove(c1)
        inst_1.oProp1.add(c3)

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
        self.assertEqual({k for k in inst_1.references.keys()},
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

    def test__19_merge_states_for_devices(self):
        """
        Tests if a local state is correctly merged with changes on the live
        state. This test focuses on the special details of a
        SemanticDeviceClass the general things are covered by test 120
        """
        from tests.semantic.models2 import Class3, semantic_manager, \
            customDataType4


        # setup state
        inst_1 = Class3(id="3")

        inst_1.device_settings.endpoint = "http://localhost:88"
        inst_1.device_settings.transport = TransportProtocol.HTTP
        inst_1.commandProp.add(Command(name="testC"))
        inst_1.attributeProp.add(
            DeviceAttribute(name="test",
                            attribute_type=DeviceAttributeType.active))

        old_state = inst_1.build_context_entity()

        semantic_manager.save_state()
        self.assertEqual(inst_1.device_settings.apikey, None)

        # change live state
        inst_1.device_settings.apikey = "test"
        inst_1.device_settings.timezone = "MyZone"
        inst_1.commandProp.remove(Command(name="testC"))
        inst_1.commandProp.add(Command(name="testC2"))
        inst_1.attributeProp.remove(
            DeviceAttribute(name="test",
                            attribute_type=DeviceAttributeType.active))
        at2 = DeviceAttribute(name="test2",
                              attribute_type=DeviceAttributeType.lazy)
        inst_1.attributeProp.add(at2)
        inst_1.dataProp1.add(customDataType4.value_1)

        semantic_manager.save_state()
        self.assertEqual(inst_1.device_settings.apikey, "test")
        self.assertEqual(len(inst_1.commandProp), 1)
        self.assertIn(Command(name="testC2"), inst_1.commandProp.get_all())
        self.assertEqual(len(inst_1.attributeProp), 1)
        self.assertIn(at2, inst_1.attributeProp)

        # reset local state and change it
        inst_1.old_state.state = old_state
        inst_1.device_settings.endpoint = "http://localhost:21"
        inst_1.device_settings.transport = TransportProtocol.HTTP
        inst_1.device_settings.apikey = None
        inst_1.attributeProp.clear()
        inst_1.commandProp.clear()
        inst_1.commandProp.add(Command(name="testC3"))
        inst_1.attributeProp.add(
            DeviceAttribute(name="test3",
                            attribute_type=DeviceAttributeType.active))

        inst_1.device_settings.timezone = "MyNewZone"

        semantic_manager.save_state()

        # local state is merged correctly
        self.assertEqual(inst_1.device_settings.endpoint, "http://localhost:21")
        self.assertEqual(inst_1.device_settings.apikey, "test")
        self.assertEqual(inst_1.device_settings.timezone, "MyNewZone")
        self.assertEqual(len(inst_1.commandProp), 2)
        self.assertEqual({c.name for c in inst_1.commandProp},
                         {"testC3", "testC2"})
        self.assertEqual(len(inst_1.attributeProp), 2)
        self.assertEqual({a.name for a in inst_1.attributeProp},
                         {"test2", "test3"})

        # live state is merged correctly
        self.clear_registry()
        inst_1 = Class3(id="3")
        self.assertEqual(inst_1.device_settings.endpoint, "http://localhost:21")
        self.assertEqual(inst_1.device_settings.apikey, "test")
        self.assertEqual(inst_1.device_settings.timezone, "MyNewZone")
        self.assertEqual(len(inst_1.commandProp), 2)
        self.assertEqual({c.name for c in inst_1.commandProp},
                         {"testC3", "testC2"})
        self.assertEqual(len(inst_1.attributeProp), 2)
        self.assertEqual({a.name for a in inst_1.attributeProp},
                         {"test2", "test3"})

        # test if data in device gets updated, not only in the context entity
        with IoTAClient(url=settings.IOTA_JSON_URL,
                        fiware_header=inst_1.header) as client:
            device_entity = client.get_device(device_id=inst_1.get_device_id())

            for attr in device_entity.static_attributes:
                if attr.name == "dataProp1":
                    self.assertEqual(attr.value, ['1'])

    def tearDown(self) -> None:
        """
        Cleanup test server
        """
        self.clear_registry()
        clear_all(fiware_header=FiwareHeader(
            service=settings.FIWARE_SERVICE,
            service_path=settings.FIWARE_SERVICEPATH),
            cb_url=settings.CB_URL,
            iota_url=settings.IOTA_JSON_URL)

    @staticmethod
    def get_file_path(path_end: str) -> str:
        """
        Get the correct path to the file needed for this test
        """

        # Test if the testcase was run directly or over in a global test-run.
        # Match the needed path to the config file in both cases

        path = Path(__file__).parent.resolve()
        return str(path.joinpath(path_end))
