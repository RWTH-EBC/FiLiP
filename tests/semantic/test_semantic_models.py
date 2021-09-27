import unittest

from filip.semantics.entity_model_generator import generate_vocabulary_models
from filip.semantics.vocabulary_configurator import VocabularyConfigurator


class TestSemanticModels(unittest.TestCase):

    def test_1_model_creation(self):
        vocabulary = VocabularyConfigurator.create_vocabulary()

        vocabulary = \
            VocabularyConfigurator.add_ontology_to_vocabulary_as_file(
                vocabulary=vocabulary,
                path_to_file='./ontology_files/ParsingTesterOntology.ttl')

        generate_vocabulary_models(vocabulary, "./", "models")

    def test_2_model(self):
        from models import Class1

        class1 = Class1()
        assert class1.oProp1__type == "Relationship"
        assert class1.oProp1__rule == "some (Class2 or Class4)"

