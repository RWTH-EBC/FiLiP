import copy
import keyword
import os
from datetime import datetime
from typing import List, Optional, Dict

from pydantic import BaseModel

from filip.semantics.ontology_parser.post_processer import \
    post_process_vocabulary
from filip.semantics.ontology_parser.rdfparser import RdfParser
from filip.semantics.vocabulary import Vocabulary, Source, Entity, Class, \
    Individual, Datatype, DataProperty, ObjectProperty

# result: Dict[str, Dict[str, List[Entity]]] = {
#     'Class_duplicates': get_conflicts_in_group([
#         vocabulary.classes, vocabulary.individuals]),
#     'Field_duplicates': get_conflicts_in_group([
#         vocabulary.data_properties, vocabulary.object_properties]),
#     'Datatype_duplicates': get_conflicts_in_group([
#         vocabulary.datatypes])}


class LabelSummary(BaseModel):
    class_label_duplicates: Dict[str, List[Entity]]
    field_label_duplicates: Dict[str, List[Entity]]
    datatype_label_duplicates: Dict[str, List[Entity]]

    black_listed_labels: Dict[str, List[Entity]]

    def is_valid(self) -> bool:
        return len(self.datatype_label_duplicates) == 0 and \
               len(self.field_label_duplicates) == 0 and \
               len(self.datatype_label_duplicates) == 0 and \
               len(self.black_listed_labels) == 0

    def __str__(self):
        res = ""

        def print_collection(collection):
            sub_res = ""
            for key, values in collection.items():
                sub_res += f"\t{key}: "
                for v in values:
                    sub_res += f" \n\t\t{v.iri}"
                sub_res += "\n"

            if len(collection) == 0:
                sub_res +=f"\t/"
            return sub_res

        res += "class_label_duplicates:\n"
        res += print_collection(self.class_label_duplicates)
        res += "field_label_duplicates:\n"
        res += print_collection(self.field_label_duplicates)
        res += "datatype_label_duplicates:\n"
        res += print_collection(self.datatype_label_duplicates)
        res += "blacklisted_labels:\n"
        res += print_collection(self.black_listed_labels)
        return res


class VocabularyConfigurator:

    @staticmethod
    def create_vocabulary() -> Vocabulary:
        return Vocabulary()

    @staticmethod
    def delete_source_from_vocabulary(vocabulary: Vocabulary,
                                      source_id: str) -> Vocabulary:
        new_vocabulary = Vocabulary()
        parser = RdfParser()
        for source in vocabulary.sources.values():
            if not source_id == source.id:
                parser.parse_source_into_vocabulary(
                    source=copy.deepcopy(source), vocabulary=new_vocabulary)

        return new_vocabulary

    @staticmethod
    def add_ontology_to_vocabulary_as_file(
            vocabulary: Vocabulary,
            path_to_file: str,
            source_name: Optional[str] = None) -> Vocabulary:

        with open(path_to_file, 'r') as file:
            data = file.read()

        if source_name is None:
            source_name = os.path.basename(path_to_file).split(".")[0]

        source = Source(source_name=source_name,
                        content=data,
                        timestamp=datetime.now())

        return VocabularyConfigurator.__parse_sources_into_vocabulary(
            vocabulary=vocabulary, sources=[source])

    @staticmethod
    def add_ontology_to_vocabulary_as_string(vocabulary: Vocabulary,
                                             source_name: str,
                                             source_content: str) -> Vocabulary:
        source = Source(source_name=source_name,
                        content=source_content,
                        timestamp=datetime.now())

        return VocabularyConfigurator.__parse_sources_into_vocabulary(
            vocabulary=vocabulary, sources=[source])

    @staticmethod
    def __parse_sources_into_vocabulary(vocabulary: Vocabulary,
                                        sources: List[Source]) -> Vocabulary:

        # create a new vocabulary by reparsing the existing sources
        new_vocabulary = Vocabulary()
        parser = RdfParser()
        for source in vocabulary.sources.values():
            parser.parse_source_into_vocabulary(source=copy.deepcopy(source),
                                                vocabulary=new_vocabulary)

        # try to parse in the new sources and post_process
        try:
            for source in sources:
                parser.parse_source_into_vocabulary(source=source,
                                                    vocabulary=new_vocabulary)
            post_process_vocabulary(vocabulary=new_vocabulary)
        except Exception:
            raise ParsingException

        return new_vocabulary

    @staticmethod
    def get_label_conflicts_in_vocabulary(vocabulary: Vocabulary) -> LabelSummary:

        def get_conflicts_in_group(entities_to_check: List[Dict]):
            # maps label to _list of entities with that label
            used_labels: Dict[str, List[Entity]] = {}
            duplicate_labels = set()

            # process entities to find conflicts
            for entity_list in entities_to_check:
                for entity in entity_list.values():
                    label = entity.get_label()
                    if label in used_labels:
                        duplicate_labels.add(label)
                        used_labels[label].append(entity)
                    else:
                        used_labels[label] = [entity]

            # sort duplicate_labels to have alphabetical order in _list
            dup_list = list(duplicate_labels)
            dup_list = sorted(dup_list, key=str.casefold)

            result: Dict[str, List[Entity]] = {}
            # store and log findings
            for label in dup_list:
                result[label] = used_labels[label]

            return result

        def get_blacklisted_labels(entities_to_check: List[Dict]):

            result: Dict[str, List[Entity]] = {}

            blacklist = list(keyword.kwlist)
            blacklist.extend(["__references", "__device_settings"])

            result: Dict[str, List[Entity]] = {}
            for entity_list in entities_to_check:
                for entity in entity_list.values():
                    label = entity.get_label()
                    if label in blacklist:
                        if label not in result:
                            result[label] = []
                        result[label].append(entity)

            return result

        summary = LabelSummary(
            class_label_duplicates=get_conflicts_in_group(
                [vocabulary.classes, vocabulary.individuals]),
            field_label_duplicates=get_conflicts_in_group(
                [vocabulary.data_properties, vocabulary.object_properties]),
            datatype_label_duplicates=get_conflicts_in_group(
                [vocabulary.datatypes]),
            black_listed_labels=get_blacklisted_labels([
                vocabulary.classes, vocabulary.individuals,
                vocabulary.data_properties, vocabulary.object_properties,
                vocabulary.datatypes
            ])
        )

        return summary

    @staticmethod
    def is_vocabulary_valid(vocabulary: Vocabulary):
        return VocabularyConfigurator.get_label_conflicts_in_vocabulary(
            vocabulary).is_valid()

    @staticmethod
    def build_class_models(vocabulary: Vocabulary):

        if not VocabularyConfigurator.is_vocabulary_valid(vocabulary):
            raise Exception

        for class_ in vocabulary.classes.values():
            print()
            print(class_.dict())


class ParsingException(Exception):

    # Constructor or Initializer
    def __init__(self, value):
        self.value = value

    # __str__ is to print() the value
    def __str__(self):
        return repr(self.value)