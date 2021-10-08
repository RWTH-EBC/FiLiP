import unittest

from filip.clients.ngsi_v2 import ContextBrokerClient
from requests import RequestException

from filip.models.ngsi_v2.context import ContextEntity

from filip.models import FiwareHeader

from filip.semantics.entity_model_generator import generate_vocabulary_models
from filip.semantics.semantic_models import InstanceRegistry, SemanticClass
from filip.semantics.vocabulary_configurator import VocabularyConfigurator


class TestSemanticModels(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def test_1_model_creation(self):
        vocabulary = VocabularyConfigurator.create_vocabulary()

        vocabulary = \
            VocabularyConfigurator.add_ontology_to_vocabulary_as_file(
                vocabulary=vocabulary,
                path_to_file='./ontology_files/ParsingTesterOntology.ttl')

        generate_vocabulary_models(vocabulary, "./", "models")

    def test_2_individuals(self):
        from tests.semantic.models import Individual1, Individual2

        individual1 = Individual1()
        self.assertTrue(Individual1() == individual1)
        self.assertFalse(Individual2() == individual1)

    def test_3_model_relation_field_validation(self):
        from models import Class1, Class13, Class2, Class4, Class123, \
            Individual1, semantic_manager, Thing

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

    def test_4_model_data_field_validation(self):
        from models import Class1, Class3, Class2, Class4, Class123, \
            Individual1, semantic_manager, Thing
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

    def test_5_back_referencing(self):
        from models import Class1, Class3, Class2, Class4

        c1 = Class1()
        c2 = Class2()
        c3 = Class3()

        c1.oProp1.append(c2)
        self.assertEqual(c2.references[c1.get_identifier()], ["oProp1"])
        c1.oProp1.extend([c2])
        self.assertEqual(c2.references[c1.get_identifier()],
                         ["oProp1", "oProp1"])
        c1.objProp2.extend([c2])
        c3.objProp2.append(c2)
        self.assertEqual(c2.references[c1.get_identifier()],
                         ["oProp1", "oProp1", "objProp2"])
        self.assertEqual(c2.references[c3.get_identifier()], ["objProp2"])

        c1.oProp1.remove(c2)
        self.assertEqual(c2.references[c1.get_identifier()],
                         ["oProp1", "objProp2"])

        c1.oProp1.remove(c2)
        del c1.objProp2[0]
        self.assertNotIn(c1.get_identifier(), c2.references)

    def test_6_test_instance_creation_inject(self):
        from models import Class1, Class13, Class3, Class4, Class123, \
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

    def test_7_test_saving_and_loading(self):
        from models import Class1, Class13, Class3, Class4, Class123, \
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
        class13.dataProp1.extend([1,2,4])

        class1.oProp1.append(class13)

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
        self.assertEqual(class13.objProp3.get_all(),
                         class13_.objProp3.get_all())
        self.assertEqual(class13.dataProp1.get_all(),
                         class13_.dataProp1.get_all())
        self.assertTrue(class13.get_identifier() in
                         semantic_manager.instance_registry._registry)

    def test_8_deleting(self):
        from models import Class1, Class13, Class3, Class4, Class123, \
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
        self.assertTrue(len(class13.references) == 0)
        self.assertTrue(len(class1.references) == 1)

        # test reference deletion
        class1.delete()
        self.assertTrue(len(class13.objProp3.get_all()) == 0)

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

        # class 1 no longer exists in fiware, and the fiware entry of class13
        # should have no more reference to it
        self.assertFalse(semantic_manager.does_instance_exists(identifier1))
        self.assertTrue(len(Class13(id="13").objProp3.get_all()) == 0)

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
        self.assertTrue(len(class13_.dataProp1.get_all()) == 0)



    def clear_registry(self):
        from models import semantic_manager
        semantic_manager.instance_registry._registry.clear()


    def tearDown(self) -> None:
        """
        Cleanup test server
        """
        client = ContextBrokerClient()

        try:
            entities = [ContextEntity(id=entity.id, type=entity.type) for
                        entity in client.get_entity_list()]
            client.update(entities=entities, action_type='delete')
        except RequestException:
            pass

        client.close()


