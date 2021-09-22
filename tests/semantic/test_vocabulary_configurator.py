"""
Tests for filip.semantics.vocabulary_configurator
"""
import unittest

from filip.semantics.vocabulary import Vocabulary
from filip.semantics.vocabulary_configurator import VocabularyConfigurator


class TestModels(unittest.TestCase):
    """
    Test class for Vocabulary Configuration
    """
    def setUp(self) -> None:
        pass

    def test_vocabulary_composition(self):
        """
        Test for fiware header
        """

        # Build vocabularies
        vocabulary = VocabularyConfigurator.create_vocabulary()

        vocabulary_1 = \
            VocabularyConfigurator.add_ontology_to_vocabulary_as_file(
                vocabulary=vocabulary,
                path_to_file='./ontology_files/RoomFloorOntology.ttl')

        with open(
                './ontology_files/RoomFloor_Duplicate_Labels.ttl', 'r')\
                as file:
            data = file.read().replace('\n', '')

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


    def tearDown(self) -> None:
        pass