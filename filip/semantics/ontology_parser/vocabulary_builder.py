"""Wrapper module to provide manipulation functions for vocabulary that
    should later be hidden from the user"""
import uuid
from enum import Enum


from pydantic import BaseModel, Field
from typing import Dict

from filip.models.base import LogLevel
from filip.semantics.vocabulary import *


class IdType(str, Enum):
    class_ = 'Class'
    object_property = 'Object Property'
    data_property = 'Data Property'
    datatype = 'Datatype'
    relation = 'Relation'
    combined_relation = 'Combined Relation'
    individual = 'Individual'
    source = 'Source'


class VocabularyBuilder(BaseModel):
    """Wrapper class to provide manipulation functions for vocabulary that
    should later be hidden from the user"""

    vocabulary: Vocabulary = Field(
        description="Vocabulary to manipulate"
    )

    current_source: Source = Field(
        default=None,
        description="Current source to which entities are added,"
                    "needed while parsing")

    def clear(self):
        """Clear all objects form the vocabulary

        Returns:
            None
        """
        self.vocabulary.classes.clear()
        self.vocabulary.object_properties.clear()
        self.vocabulary.data_properties.clear()
        self.vocabulary.datatypes.clear()
        self.vocabulary.relations.clear()
        self.vocabulary.combined_object_relations.clear()
        self.vocabulary.combined_data_relations.clear()
        self.vocabulary.individuals.clear()
        self.vocabulary.id_types.clear()
        for source in self.vocabulary.sources.values():
            source.clear()

    def add_class(self, class_: Class):
        """Add a class to the vocabulary

        Args:
            class_ (Class): class to be added

        Returns:
            None
        """
        self._add_and_merge_entity(class_,
                                   self.vocabulary.classes,
                                   IdType.class_)

    def add_object_property(self, obj_prop: ObjectProperty):
        """Add an ObjectProperty to the vocabulary

        Args:
            obj_prop (ObjectProperty): ObjectProperty to be added

        Returns:
            None
        """
        self._add_and_merge_entity(
            obj_prop, self.vocabulary.object_properties, IdType.object_property)

    def add_data_property(self, data_prop: DataProperty):
        """Add an DataProperty to the vocabulary

        Args:
            data_prop (DataProperty): DataProperty to be added

        Returns:
            None
        """
        self._add_and_merge_entity(
            data_prop, self.vocabulary.data_properties, IdType.data_property)

    def add_datatype(self, datatype: Datatype):
        """Add a DataType to the vocabulary

        Args:
            datatype (Datatype): Datatype to be added

        Returns:
            None
        """
        self._add_and_merge_entity(
            datatype, self.vocabulary.datatypes, IdType.datatype)

    def add_predefined_datatype(self, datatype: Datatype):
        """Add a DataType to the vocabulary, that belongs to the source:
            Predefined

        Args:
            datatype (Datatype): Datatype to be added

        Returns:
            None
        """
        self.vocabulary.id_types[datatype.iri] = IdType.datatype
        self.vocabulary.datatypes[datatype.iri] = datatype
        datatype.predefined = True
        datatype.source_ids.add("PREDEFINED")

    def add_individual(self, individual: Individual):
        """Add an Individual to the vocabulary

        Args:
            individual (Individual): Individual to be added

        Returns:
            None
        """
        self._add_and_merge_entity(individual,
                                   self.vocabulary.individuals,
                                   IdType.individual)

    def add_relation_for_class(self, class_iri: str, rel: Relation):
        """Add a relation object to a class

        Args:
            class_iri: Iri of the class to which the relation should be added
            rel: Relation to add

        Returns:
            None
        """

        class_ = self.vocabulary.get_class_by_iri(class_iri)

        # for rel_id in class_.relation_ids:
        #     ex_rel = self.vocabulary.get_relation_by_id(rel_id)
        #     if rel.target_statement== rel.target_statement:
        #         return

        self.vocabulary.relations[rel.id] = rel
        class_.relation_ids.append(rel.id)
        self.vocabulary.id_types[rel.id] = IdType.relation

    def add_combined_object_relation_for_class(self, class_iri: str,
                                               crel: CombinedObjectRelation):
        """Add a combined object relation object to a class

        Args:
            class_iri: Iri of the class to which the co-relation should be added
            crel: CombinedObjectRelation to add

        Returns:
            None
        """
        self.vocabulary.combined_object_relations[crel.id] = crel
        self.vocabulary.get_class_by_iri(class_iri).\
            combined_object_relation_ids.append(crel.id)
        self.vocabulary.id_types[crel.id] = IdType.combined_relation

    def add_combined_data_relation_for_class(self, class_iri: str,
                                             cdata: CombinedDataRelation):
        """Add a combined data relation object to a class

        Args:
            class_iri: Iri of the class to which the cd-relation should be added
            cdata: CombinedDataRelation to add

        Returns:
            None
        """
        self.vocabulary.combined_data_relations[cdata.id] = cdata
        self.vocabulary.get_class_by_iri(class_iri).\
            combined_data_relation_ids.append(cdata.id)
        self.vocabulary.id_types[cdata.id] = IdType.combined_relation

    def add_source(self, source: Source, id: str = None):
        """Add a source to the vocabulary

        Args:
            source: source to add
            id: id of source, if none is given a random id is generated

        Returns:
            None
        """
        if id is None:
            source.id = uuid.uuid4().hex
        else:
            source.id = id
        self.vocabulary.id_types[source.id] = IdType.source
        self.vocabulary.sources[source.id] = source
        self.current_source = source

    def set_current_source(self, source_id: str):
        """Set the source of the vocabulary to which new added objects belong

        Args:
            source_id: id of source to activate

        Returns:
            None
        """
        assert source_id in self.vocabulary.sources
        self.current_source = self.vocabulary.sources[source_id]

    def _add_and_merge_entity(self,
                              entity: Entity,
                              entity_dict: Dict[str, Entity],
                              id_type: IdType):
        """Adds an entity to the vocabulary. If an entity with teh same iri
        already exists the label and comment are "merged" and both sources
        are noted

        Args:
            entity: Entity to check
            entity_dict: Existing entities
            id_type: Type of entity

        Raises:
            ParsingError: if Entity of iri exists but has a different IdType

        Returns:
            None
        """

        if entity.iri in self.vocabulary.id_types:
            if not id_type == self.vocabulary.id_types[entity.iri]:
                self.current_source.add_parsing_log_entry(
                    LogLevel.CRITICAL, id_type, entity.iri,
                    f"{entity.iri} from source "
                    f"{self.current_source.get_name()} "
                    f"exists multiple times in different catagories. It was "
                    f"only added for the category "
                    f"{self.vocabulary.id_types[entity.iri].value}")
                return

            old_entity = entity_dict[entity.iri]

            def select_from(old: str, new: str, property: str) -> str:
                """
                Given two strings, one from the old_entity , one form the new
                one. It is selected which one to use.
                """
                if old == "":
                    return new
                elif new == "":
                    return ""
                else:
                    self.current_source.add_parsing_log_entry(
                        LogLevel.WARNING, id_type, entity.iri,
                        f"{property} from source "
                        f"{old_entity.get_source_names(self.vocabulary)} "
                        f"was overwritten")
                    return new

            entity.label = select_from(old_entity.label, entity.label, "label")
            entity.comment = select_from(old_entity.comment, entity.comment,
                                         "comment")

        self.vocabulary.id_types[entity.iri] = id_type
        entity.source_ids.add(self.current_source.id)
        entity_dict[entity.iri] = entity

    def entity_is_known(self, iri: str) -> bool:
        """Test if the given iri is in vocabulary, if not it belongs to a
        dependency which is not yet loaded

        Args:
            iri (str)

        Returns:
            bool
        """
        return iri in self.vocabulary.id_types
