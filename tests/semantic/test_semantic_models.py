import unittest

from filip.models import FiwareHeader

from filip.semantics.entity_model_generator import generate_vocabulary_models
from filip.semantics.semantic_models import ClientSetting, InstanceRegistry
from filip.semantics.vocabulary_configurator import VocabularyConfigurator


class TestSemanticModels(unittest.TestCase):

    def test_1_model_creation(self):
        vocabulary = VocabularyConfigurator.create_vocabulary()

        vocabulary = \
            VocabularyConfigurator.add_ontology_to_vocabulary_as_file(
                vocabulary=vocabulary,
                path_to_file='./ontology_files/ParsingTesterOntology.ttl')

        generate_vocabulary_models(vocabulary, "./", "models")

    def test_2_model_relation_validation(self):
        from models import Class1, Class13, Class2, Class4, Class123, \
            Individual1, semantic_manager, Thing

        semantic_manager.client_setting = ClientSetting.v2

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
        self.assertFalse(class13.objProp2.is_valid())
        class13.objProp2.append(class1)
        self.assertFalse(class13.objProp2.is_valid())
        class13.objProp2.append(Class123())
        self.assertFalse(class13.objProp2.is_valid())
        del class13.objProp2[1]
        class13.objProp2.append(Individual1())
        self.assertTrue(class13.objProp2.is_valid())


        # todo test statement cases: min, max,...

    def test_3_back_referencing(self):
        from models import Class1, Class3, Class2, Class4

        c1 = Class1()
        c2 = Class2()
        c3 = Class3()

        c1.oProp1.append(c2)
        self.assertEqual(c2._references[c1.get_identifier()], ["oProp1"])
        c1.oProp1.extend([c2])
        self.assertEqual(c2._references[c1.get_identifier()],
                         ["oProp1", "oProp1"])
        c1.objProp2.extend([c2])
        c3.objProp2.append(c2)
        self.assertEqual(c2._references[c1.get_identifier()],
                         ["oProp1", "oProp1", "objProp2"])
        self.assertEqual(c2._references[c3.get_identifier()], ["objProp2"])

        c1.oProp1.remove(c2)
        self.assertEqual(c2._references[c1.get_identifier()],
                         ["oProp1", "objProp2"])

        c1.oProp1.remove(c2)
        del c1.objProp2[0]
        self.assertNotIn(c1.get_identifier(), c2._references)

    def test_4_test_instance_creation_inject(self):
        from models import Class1, Class13, Class3, Class4, Class123, \
            Individual1, Gertrude, semantic_manager

        # clear local state to ensure standard test condition
        semantic_manager.instance_registry = InstanceRegistry()

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


    def test_5_test_saving_and_loading(self):
        from models import Class1, Class13, Class3, Class4, Class123, \
            Individual1, Gertrude

        class13 = Class13()
        class13.objProp3.append(Class1())
        # class13.save(FiwareHeader(), assert_validity=False)



