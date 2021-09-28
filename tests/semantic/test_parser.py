"""
Tests for filip.semantics.ontology_parser.parser
"""
import collections
import datetime
import unittest

import rdflib.util

from filip.semantics.ontology_parser.post_processer import \
    post_process_vocabulary
from filip.semantics.ontology_parser.rdfparser import RdfParser
from filip.semantics.vocabulary import Vocabulary, Source, DatatypeType
from filip.semantics.vocabulary_configurator import VocabularyConfigurator


class TestModels(unittest.TestCase):
    """
    Test class for Vocabulary Parsing
    """

    def setUp(self) -> None:
        pass

    def test_parser(self):
        """
        Test if the parsing works correct
        """

        vocabulary = Vocabulary()
        with open('./ontology_files/ParsingTesterOntology.ttl', 'rb') as file:
            data = file.read()

        # source = Source(id="my_unique_id", source_name="TestSource",
        #                 content=data, timestamp=datetime.datetime.now())
        #
        # parser = RdfParser()
        # parser.parse_source_into_vocabulary(source=source,
        #                                     vocabulary=vocabulary)
        #
        # post_process_vocabulary(vocabulary=vocabulary)

        vocabulary = VocabularyConfigurator.\
            add_ontology_to_vocabulary_as_string(vocabulary, "test", data)


        # class annotations
        self.assertEqual(vocabulary.get_class_by_iri(iri("Class1")).label,
                         "Class1")
        self.assertEqual(vocabulary.get_class_by_iri(iri("Class2")).get_label(),
                         "Class2")
        self.assertEqual(vocabulary.get_class_by_iri(
            iri("Class1")).comment.lower(), "comment on class 1")

        # subclassing
        assertList(vocabulary.get_class_by_iri(iri("Class1")).parent_class_iris,
                   ["http://www.w3.org/2002/07/owl#Thing"])
        assertList(
            vocabulary.get_class_by_iri(iri("Class1a")).parent_class_iris,
            [iri("Class1")])
        assertList(
            vocabulary.get_class_by_iri(iri("Class12")).parent_class_iris,
            [iri("Class1"), iri("Class2")])
        assertList(
            vocabulary.get_class_by_iri(iri("Class12*")).parent_class_iris,
            [iri("Class1"), iri("Class2")])
        assertList(
            vocabulary.get_class_by_iri(iri("Class1b")).parent_class_iris,
            [iri("Class1")])
        assertList(
            vocabulary.get_class_by_iri(iri("Class123")).parent_class_iris,
            [iri("Class1"), iri("Class2"), iri("Class3")])

        assertList(
            vocabulary.get_class_by_iri(iri("Class1aa")).ancestor_class_iris,
            ["http://www.w3.org/2002/07/owl#Thing", iri("Class1"),
             iri("Class1a")])
        assertList(vocabulary.get_class_by_iri(iri("Class3")).child_class_iris,
                   [iri("Class3a"), iri("Class3a*"), iri("Class123"),
                    iri("Class13")])

        # Relation Target statments
        cor1 = get_cor_with_prop(vocabulary, iri("Class1"), iri("objProp3"))
        assertList(get_targets_for_combine_object_relation(vocabulary, cor1),
                   [iri("Class3"), iri("Class123"), iri("Class3a"),
                    iri("Class3a*"), iri("Class13")])
        cor1 = get_cor_with_prop(vocabulary, iri("Class1"), iri("objProp2"))
        assertList(get_targets_for_combine_object_relation(vocabulary, cor1),
                   [iri("Class12"), iri("Class12*"), iri("Class123")])
        cor1 = get_cor_with_prop(vocabulary, iri("Class1"), iri("objProp4"))
        assertList(get_targets_for_combine_object_relation(vocabulary, cor1),
                   [iri("Class123")])
        cor1 = get_cor_with_prop(vocabulary, iri("Class1"), iri("oProp1"))
        assertList(get_targets_for_combine_object_relation(vocabulary, cor1),
                   [iri("Class4"), iri("Class2"), iri("Class12"),
                    iri("Class12*"), iri("Class123")])
        cor1 = get_cor_with_prop(vocabulary, iri("Class1"), iri("objProp5"))
        assertList(get_targets_for_combine_object_relation(vocabulary, cor1),
                   [iri("Class12"), iri("Class12*"), iri("Class123"),
                    iri("Class13")])

        target_str = get_cor_with_prop(vocabulary, iri("Class1"),
                                       iri("objProp5")).get_relations(
            vocabulary)[0].target_statement.to_string(vocabulary)
        self.assertEqual(target_str, "(Class1 and (Class2 or Class3))")

        # Individuals
        assertList(
            vocabulary.get_individual(iri("Individual1")).parent_class_iris,
            [iri("Class1"), iri("Class2")])
        assertList(
            vocabulary.get_individual(iri("Individual2")).parent_class_iris,
            [iri("Class1")])
        assertList(
            vocabulary.get_individual(iri("Individual3")).parent_class_iris,
            [iri("Class1"), iri("Class2"), iri("Class3")])
        assertList(
            vocabulary.get_individual(iri("Individual4")).parent_class_iris,
            [iri("Class1"), iri("Class2")])

        # obj properties
        self.assertIn(iri("oProp1"), vocabulary.object_properties)
        assertList(
            vocabulary.get_object_property(iri("oProp1")).inverse_property_iris,
            [iri("objProp3")])
        assertList(vocabulary.get_object_property(
            iri("objProp3")).inverse_property_iris, [iri("oProp1")])

        # datatypes
        assertList(vocabulary.get_datatype(iri("customDataType1")).enum_values,
                   ["0", "15", "30"])
        assertList(vocabulary.get_datatype(iri("customDataType4")).enum_values,
                   ["1", "2", "3", "4"])
        self.assertEqual(vocabulary.get_datatype(
            iri("customDataType4")).type, DatatypeType.enum)

        # data properties
        self.assertIn(iri("dataProp1"), vocabulary.data_properties)

        # value target statments
        cdr1 = get_cdr_with_prop(vocabulary, iri("Class3"), iri("dataProp1"))
        assertList(cdr1.get_possible_enum_target_values(vocabulary),
                   ["1", "2", "3", "4"])

    def tearDown(self) -> None:
        pass


# Helping methods
def get_cor_with_prop(vocabulary: Vocabulary, class_iri: str, prop_iri: str):
    # cors = vocabulary.get_combined_object_relations_for_class(class_iri)
    class_ = vocabulary.get_class_by_iri(class_iri=class_iri)
    cors = class_.get_combined_object_relations(vocabulary)
    for c in cors:
        if c.property_iri == prop_iri:
            return c

    assert False, "{} has no combined obj rel with property {}".format(
        class_iri, prop_iri)


def get_cdr_with_prop(vocabulary: Vocabulary, class_iri: str,
                      prop_iri: str):
    # cors = vocabulary.get_combined_object_relations_for_class(class_iri)
    class_ = vocabulary.get_class_by_iri(class_iri=class_iri)
    cdrs = class_.get_combined_data_relations(vocabulary)
    for c in cdrs:
        if c.property_iri == prop_iri:
            return c

    assert False, "{} has no combined data rel with property {}".format(
        class_iri, prop_iri)


def assertList(actual, expected):

    assert len(actual) == len(expected), actual
    assert collections.Counter(actual) == collections.Counter(
        expected), actual


def iri(iriEnd: str):
    base_iri = "http://www.semanticweb.org/redin/ontologies/2020/11/" \
               "untitled-ontology-25#"
    return base_iri + iriEnd


def get_targets_for_combine_object_relation(vocabulary: Vocabulary,
                                            com_obj_rel):
    possible_class_iris = set()

    for rel_id in com_obj_rel.relation_ids:
        relation = vocabulary.get_relation_by_id(rel_id)
        target_iris = relation.get_all_possible_target_class_iris(vocabulary)
        for target_iri in target_iris:
            possible_class_iris.add(target_iri)

    return list(possible_class_iris)