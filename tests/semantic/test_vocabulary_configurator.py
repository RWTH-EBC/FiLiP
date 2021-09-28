"""
Tests for filip.semantics.vocabulary_configurator
"""
import json
import unittest

from filip.semantics.vocabulary import Vocabulary
from filip.semantics.vocabulary_configurator import VocabularyConfigurator


class TestModels(unittest.TestCase):
    """
    Test class for Vocabulary Configuration
    """
    def setUp(self) -> None:
        # Build vocabularies
        vocabulary = VocabularyConfigurator.create_vocabulary()

        vocabulary_1 = \
            VocabularyConfigurator.add_ontology_to_vocabulary_as_file(
                vocabulary=vocabulary,
                path_to_file='./ontology_files/RoomFloorOntology.ttl')

        with open(
                './ontology_files/RoomFloor_Duplicate_Labels.ttl', 'r') \
                as file:
            data = file.read()

        vocabulary_2 = \
            VocabularyConfigurator.add_ontology_to_vocabulary_as_string(
                vocabulary=vocabulary_1,
                source_name='RoomFloorOntology_Duplicate_Labels',
                source_content=data
            )

        vocabulary_3 = \
            VocabularyConfigurator.add_ontology_to_vocabulary_as_file(
                vocabulary=vocabulary,
                path_to_file='./ontology_files/RoomFloorOntology.ttl',
                source_name='test_name'
            )
        vocabulary_3 = \
            VocabularyConfigurator.add_ontology_to_vocabulary_as_file(
                vocabulary=vocabulary_3,
                path_to_file='./ontology_files/ParsingTesterOntology.ttl'
            )

        self.vocabulary = vocabulary
        self.vocabulary_1 = vocabulary_1
        self.vocabulary_2 = vocabulary_2
        self.vocabulary_3 = vocabulary_3


    def test_vocabulary_composition(self):
        """
        Test for fiware header
        """
        # makes lines a bit shorter and more readable
        vocabulary = self.vocabulary
        vocabulary_1 = self.vocabulary_1
        vocabulary_2 = self.vocabulary_2
        vocabulary_3 = self.vocabulary_3

        # test number of sources; each vocabulary has one PREDEFINED source
        self.assertEqual(len(vocabulary_1.sources), 2)
        self.assertEqual(len(vocabulary_2.sources), 3)
        self.assertEqual(len(vocabulary_3.sources), 3)

        # test source names
        self.assertIn('RoomFloorOntology',
                      [n.source_name for n in vocabulary_1.sources.values()])

        self.assertIn('RoomFloorOntology',
                      [n.source_name for n in vocabulary_2.sources.values()])
        self.assertIn('RoomFloorOntology_Duplicate_Labels',
                      [n.source_name for n in vocabulary_2.sources.values()])

        self.assertIn('test_name',
                      [n.source_name for n in vocabulary_3.sources.values()])

        # test content of vocabulary
        self.assertEqual(len(vocabulary_2.classes), 10)
        self.assertEqual(len(vocabulary_3.classes), 19)

        # test deletion of source
        source_id = [s.id for s in vocabulary_3.sources.values()
                     if s.source_name == "test_name"][0]
        vocabulary_4 = VocabularyConfigurator.delete_source_from_vocabulary(
            vocabulary=vocabulary_3,
            source_id=source_id
        )
        self.assertIn('test_name',
                      [n.source_name for n in vocabulary_3.sources.values()])
        self.assertNotIn('test_name',
                         [n.source_name for n in vocabulary_4.sources.values()])

    def test_duplicate_label_detection(self):

        conflict_voc = self.vocabulary_2

        conflict_dict = VocabularyConfigurator.\
            get_label_conflicts_in_vocabulary(conflict_voc)

        self.assertIn('Sensor', conflict_dict.keys())
        self.assertIn('isOnFloor', conflict_dict.keys())
        self.assertEqual(len(conflict_dict.keys()), 2)

        self.assertEqual(len(conflict_dict['Sensor']), 2)

    def test_valid_test(self):
        self.assertEqual(
            VocabularyConfigurator.is_vocabulary_valid(self.vocabulary_2),
            False
        )
        self.assertEqual(
            VocabularyConfigurator.is_vocabulary_valid(self.vocabulary_1),
            True
        )
        self.assertEqual(
            VocabularyConfigurator.is_vocabulary_valid(self.vocabulary_3),
            True
        )

    def test_build_models(self):
        VocabularyConfigurator.build_class_models(vocabulary=self.vocabulary_1)


    def tearDown(self) -> None:
        pass
