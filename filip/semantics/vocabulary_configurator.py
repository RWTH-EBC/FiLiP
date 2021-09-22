import copy
import os
from datetime import datetime
from typing import List, Optional

from filip.semantics.ontology_parser.post_processer import \
    post_process_vocabulary
from filip.semantics.ontology_parser.rdfparser import RdfParser
from filip.semantics.vocabulary import Vocabulary, Source


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
                    source=copy.deepcopy(source),vocabulary=new_vocabulary)

        return new_vocabulary

    @staticmethod
    def add_ontology_to_vocabulary_as_file(
            vocabulary: Vocabulary,
            path_to_file: str,
            source_name: Optional[str] = None) -> Vocabulary:

        with open(path_to_file, 'r') as file:
            data = file.read().replace('\n', '')

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
                                             source_content: str):
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
            post_process_vocabulary(vocabulary=new_vocabulary,
                                    old_vocabulary=vocabulary)
        except Exception:
            raise ParsingException

        return new_vocabulary


class ParsingException(Exception):

    # Constructor or Initializer
    def __init__(self, value):
        self.value = value

    # __str__ is to print() the value
    def __str__(self):
        return repr(self.value)