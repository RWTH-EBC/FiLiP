"""
Tests for filip.semantics.vocabulary_configurator
"""
import unittest

from pathlib import Path

from filip.semantics.vocabulary.data_property import DataFieldType
from filip.semantics.vocabulary.vocabulary import VocabularySettings
from filip.semantics.vocabulary_configurator import VocabularyConfigurator


class TestModels(unittest.TestCase):
    """
    Test class for Vocabulary Configuration
    """
    def setUp(self) -> None:
        # Build vocabularies
        vocabulary = VocabularyConfigurator.create_vocabulary(
            VocabularySettings(
                pascal_case_class_labels=False,
                pascal_case_individual_labels=False,
                camel_case_property_labels=False,
                camel_case_datatype_labels=False,
                pascal_case_datatype_enum_labels=False
            )
        )

        vocabulary_1 = \
            VocabularyConfigurator.add_ontology_to_vocabulary_as_file(
                vocabulary=vocabulary,
                path_to_file=self.get_file_path(
                    'ontology_files/RoomFloorOntology.ttl'))

        with open(self.get_file_path(
                'ontology_files/RoomFloor_Duplicate_Labels.ttl'), 'r') \
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
                path_to_file=self.get_file_path(
                    'ontology_files/RoomFloorOntology.ttl'),
                source_name='test_name'
            )
        vocabulary_3 = \
            VocabularyConfigurator.add_ontology_to_vocabulary_as_file(
                vocabulary=vocabulary_3,
                path_to_file=self.get_file_path(
                    'ontology_files/ParsingTesterOntology.ttl')
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
        self.assertEqual(len(vocabulary_3.classes), 18)

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

        conflict_summary = VocabularyConfigurator.\
            get_label_conflicts_in_vocabulary(conflict_voc)

        self.assertIn('Sensor', conflict_summary.class_label_duplicates)
        self.assertIn('isOnFloor', conflict_summary.field_label_duplicates)
        self.assertIn('MeasurmentType',
                      conflict_summary.datatype_label_duplicates)

        self.assertEqual(len(conflict_summary.class_label_duplicates[
                                 'Sensor']), 2)

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

        if not VocabularyConfigurator.is_vocabulary_valid(self.vocabulary_1):
            raise Exception

    def test_device_class(self):
        vocabulary = self.vocabulary_3

        class_thing = vocabulary.get_class_by_iri(
            "http://www.w3.org/2002/07/owl#Thing")

        class_1 = vocabulary.get_class_by_iri(
            "http://www.semanticweb.org/redin/ontologies/2020/11/untitled"
            "-ontology-25#Class1")
        class_2 = vocabulary.get_class_by_iri(
            "http://www.semanticweb.org/redin/ontologies/2020/11/untitled"
            "-ontology-25#Class2")
        class_3 = vocabulary.get_class_by_iri(
            "http://www.semanticweb.org/redin/ontologies/2020/11/untitled"
            "-ontology-25#Class3")
        class_123 = vocabulary.get_class_by_iri(
            "http://www.semanticweb.org/redin/ontologies/2020/11/untitled"
            "-ontology-25#Class123")

        data_prop_1 = vocabulary.get_data_property(
            "http://www.semanticweb.org/redin/ontologies/2020/11/untitled"
            "-ontology-25#dataProp1")
        data_prop_2 = vocabulary.get_data_property(
            "http://www.semanticweb.org/redin/ontologies/2020/11/untitled"
            "-ontology-25#dataProp2")

        self.assertFalse(class_thing.is_iot_class(vocabulary))
        self.assertFalse(class_1.is_iot_class(vocabulary))
        self.assertFalse(class_2.is_iot_class(vocabulary))
        self.assertFalse(class_3.is_iot_class(vocabulary))
        self.assertFalse(class_123.is_iot_class(vocabulary))

        data_prop_1.field_type = DataFieldType.command

        self.assertFalse(class_thing.is_iot_class(vocabulary))
        self.assertFalse(class_1.is_iot_class(vocabulary))
        self.assertFalse(class_2.is_iot_class(vocabulary))
        self.assertTrue(class_3.is_iot_class(vocabulary))
        self.assertTrue(class_123.is_iot_class(vocabulary))

        data_prop_2.field_type = DataFieldType.device_attribute

        self.assertFalse(class_thing.is_iot_class(vocabulary))
        self.assertTrue(class_1.is_iot_class(vocabulary))
        self.assertFalse(class_2.is_iot_class(vocabulary))
        self.assertTrue(class_3.is_iot_class(vocabulary))
        self.assertTrue(class_123.is_iot_class(vocabulary))

    def tearDown(self) -> None:
        pass

    @staticmethod
    def get_file_path(path_end: str) -> str:
        """
        Get the correct path to the file needed for this test
        """

        # Test if the testcase was run directly or over in a global test-run.
        # Match the needed path to the config file in both cases

        path = Path(__file__).parent.resolve()
        return str(path.joinpath(path_end))
