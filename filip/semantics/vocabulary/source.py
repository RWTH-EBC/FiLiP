"""Vocabulary Models for Ontology Sources"""

import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import ConfigDict, BaseModel, Field

from ...models.base import LogLevel

if TYPE_CHECKING:
    from . import Vocabulary, IdType, LoggingLevel


class DependencyStatement(BaseModel):
    """Information about one dependency statement in the source
    A dependency is a reference of one iri in an other entity definition
    """
    source_iri: str = Field(
        default="",
        description="Iri of the source containing the statement")
    source_name: str = Field(
        default="",
        description="Name of the source containing the statement")
    type: str = Field(
        description="Possible types: Parent Class, Relation Property, "
                    "Relation Target")
    class_iri: str = Field(
        description="Iri of the class containing the statement")
    dependency_iri: str = Field(description="Entity Iri of the dependency")
    fulfilled: bool = Field(
        description="True if the dependency_iri is registered in the "
                    "vocabulary")


class ParsingError(BaseModel):
    """Object represents one issue that arose while parsing a source,
       and holds all relevant details for that issue"""
    model_config = ConfigDict(use_enum_values=True)
    level: LogLevel = Field(description="Severity of error")
    source_iri: str = Field(description=
                            "Iri of the source containing the error")
    source_name: Optional[str] = Field(
        default=None,
        description="Name of the source, only set in get_function"
    )
    entity_type: str = Field(
        description="Type of the problematic entity: Class, Individual,.."
                    "ID_type in string form"
    )
    entity_iri: str = Field(description="Iri of the problematic entity")
    entity_label: Optional[str] = Field(
        default=None,
        description="Name of the source, only set in get_function"
    )
    message: str = Field(
        description="Message describing the error"
    )


class Source(BaseModel):
    """
    A source represent one file that was provided via file upload or link to the
    project and is parsed into the
    vocabulary
    """

    id: str = Field(default="",
                    description="unique ID of the source; for internal use")
    source_name: str = Field(default="",
                             description="Name of the source ")
    content: str = Field(
        default="",
        description="File content of the provided ontology file")
    parsing_log: List['ParsingError'] = Field(
        default=[],
        description="Log containing all issues that were discovered while "
                    "parsing")
    dependency_statements: List[DependencyStatement] = Field(
        default=[],
        description="List of all statements in source")
    timestamp: datetime.datetime = Field(
        description="timestamp when the source was added to the project")
    ontology_iri: str = Field(
        default=None,
        description="Iri of the ontology of the source")
    predefined: bool = Field(
        default=False,
        description="Stating if the source is a predefined source; "
                    "a predefined source is added to each project containing "
                    "owl:Thing and predefined Datatypes")

    def get_number_of_id_type(self, vocabulary: 'Vocabulary',
                              id_type: 'IdType') -> int:
        """Get the number how many entities of a given type are created by or
        influenced by this source

        Args:
            vocabulary (Vocabulary): Vocabulary of this project
            id_type (IdType): Idtype that should be counted

        Returns:
            int
        """

        from . import IdType
        id_func = "/"
        iri_list = []

        if id_type is IdType.class_:
            id_func = vocabulary.get_class_by_iri
            iri_list = vocabulary.classes
        elif id_type is IdType.object_property:
            id_func = vocabulary.get_object_property
            iri_list = vocabulary.object_properties
        elif id_type is IdType.data_property:
            id_func = vocabulary.get_data_property
            iri_list = vocabulary.data_properties
        elif id_type is IdType.individual:
            id_func = vocabulary.get_individual
            iri_list = vocabulary.individuals
        elif id_type is IdType.datatype:
            id_func = vocabulary.get_datatype
            iri_list = vocabulary.datatypes

        if id_func == "/":
            return -1

        counter = 0
        for iri in iri_list:
            entity = id_func(iri)
            if self.id in entity.source_ids:
                counter += 1
        return counter

    def get_name(self) -> str:
        """Get the name of the source

        Returns:
            str
        """
        return self.source_name

    def treat_dependency_statements(self, vocabulary: 'Vocabulary'):
        """
        Log and purge all pointers/iris in entities that are not contained
        in the vocabulary

        Args:
            vocabulary (Vocabulary): Vocabulary of this project

        Returns:
            None
        """
        dependency_statements = []

        for class_ in vocabulary.get_classes():
            if self.id in class_.source_ids:
                dependency_statements.extend(
                    class_.treat_dependency_statements(vocabulary))

        for individual_iri in vocabulary.individuals:
            individual = vocabulary.get_individual(individual_iri)
            if self.id in individual.source_ids:
                dependency_statements.extend(
                    individual.treat_dependency_statements(vocabulary))

        for statement in dependency_statements:
            statement.source_iri = self.ontology_iri
            statement.source_name = self.source_name

        self.dependency_statements = dependency_statements

    def add_parsing_log_entry(self, level: 'LoggingLevel', entity_type: 'IdType',
                              entity_iri: str,  msg: str):
        """
        Add a parsing log entry for an entity, if an issue in parsing
        was discovered

        Args:
            level (LoggingLevel): Logging level of the entry
            entity_type (IdType): Type of the enitity (Class, Individual,..)
            entity_iri (str): iri of the entity
            msg (str): message to display in log

        Returns:
            None
        """

        from . import ParsingError
        self.parsing_log.append(ParsingError(
            level=level,
            entity_type=str(entity_type),
            entity_iri=entity_iri,
            message=msg,
            source_iri=self.ontology_iri
        ))

    def get_parsing_log(self, vocabulary: 'Vocabulary') -> List['ParsingError']:
        """Get the Parsinglog, where the labels of the entities are filled in

        Args:
            vocabulary (Vocabulary): Vocabulary of this project

        Returns:
            List[Dict[str, Union[LoggingLevel,'IdType',str]]]
        """
        for entry in self.parsing_log:

            entry.source_name = self.source_name
            try:
                label = vocabulary.get_label_for_entity_iri(entry.entity_iri)
                entry.entity_label = label
            except Exception:
                pass

        return self.parsing_log

    def clear(self):
        """Clear all logging and dependency data of the source

        Returns:
            None
        """
        self.parsing_log = []
        self.dependency_statements = []


