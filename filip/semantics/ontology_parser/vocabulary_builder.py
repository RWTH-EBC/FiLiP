
import uuid
from enum import Enum

from pydantic import BaseModel
from filip.semantics.vocabulary import *
from typing import List, Dict, Union, Set


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

    vocabulary: Vocabulary

    current_source: Source = None
    """Current source to which entities are added, needed while parsing"""

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

        self.add_log_entry_for_overwriting_entity(class_,
                                                  self.vocabulary.classes,
                                                  IdType.class_)

        self.vocabulary.classes[class_.iri] = class_
        self.vocabulary.id_types[class_.iri] = IdType.class_
        class_.source_id = self.current_source.id

    def add_object_property(self, obj_prop: ObjectProperty):
        """Add an ObjectProperty to the vocabulary

        Args:
            obj_prop (ObjectProperty): ObjectProperty to be added

        Returns:
            None
        """

        self.add_log_entry_for_overwriting_entity(
            obj_prop, self.vocabulary.object_properties, IdType.object_property)

        self.vocabulary.object_properties[obj_prop.iri] = obj_prop
        self.vocabulary.id_types[obj_prop.iri] = IdType.object_property
        obj_prop.source_id = self.current_source.id


    def add_data_property(self, data_prop: DataProperty):
        """Add an DataProperty to the vocabulary

        Args:
            data_prop (DataProperty): DataProperty to be added

        Returns:
            None
        """

        self.add_log_entry_for_overwriting_entity(
            data_prop, self.vocabulary.data_properties, IdType.data_property)

        self.vocabulary.data_properties[data_prop.iri] = data_prop
        self.vocabulary.id_types[data_prop.iri] = IdType.data_property
        data_prop.source_id = self.current_source.id


    def add_datatype(self, datatype: Datatype):
        """Add a DataType to the vocabulary

        Args:
            datatype (Datatype): Datatype to be added

        Returns:
            None
        """

        self.add_log_entry_for_overwriting_entity(
            datatype, self.vocabulary.datatypes, IdType.datatype)

        self.vocabulary.id_types[datatype.iri] = IdType.datatype
        self.vocabulary.datatypes[datatype.iri] = datatype
        datatype.source_id = self.current_source.id

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
        datatype.source_id = "PREDEFINED"

    def add_individual(self, individual: Individual):
        """Add an Individual to the vocabulary

        Args:
            individual (Individual): Individual to be added

        Returns:
            None
        """

        self.add_log_entry_for_overwriting_entity(individual,
                                                  self.vocabulary.individuals,
                                                  IdType.individual)

        self.vocabulary.individuals[individual.iri] = individual
        self.vocabulary.id_types[individual.iri] = IdType.individual
        individual.source_id = self.current_source.id

    def add_relation_for_class(self, class_iri: str, rel: Relation):
        self.vocabulary.relations[rel.id] = rel
        self.vocabulary.get_class_by_iri(class_iri).relation_ids.append(rel.id)
        self.vocabulary.id_types[rel.id] = IdType.relation

    def add_combined_object_relation_for_class(self, class_iri: str,
                                               crel: CombinedObjectRelation):
        self.vocabulary.combined_object_relations[crel.id] = crel
        self.vocabulary.get_class_by_iri(class_iri).\
            combined_object_relation_ids.append(crel.id)
        self.vocabulary.id_types[crel.id] = IdType.combined_relation

    def add_combined_data_relation_for_class(self, class_iri: str,
                                             cdata: CombinedDataRelation):
        self.vocabulary.combined_data_relations[cdata.id] = cdata
        self.vocabulary.get_class_by_iri(class_iri).\
            combined_data_relation_ids.append(cdata.id)
        self.vocabulary.id_types[cdata.id] = IdType.combined_relation

    def add_source(self, source: Source, id: str = None):
        if id is None:
            source.id = uuid.uuid4().hex
        else:
            source.id = id
        self.vocabulary.id_types[source.id] = IdType.source
        self.vocabulary.sources[source.id] = source
        self.current_source = source

    def set_current_source(self, source_id: str):
        assert source_id in self.vocabulary.sources
        self.current_source = self.vocabulary.sources[source_id]

    def add_log_entry_for_overwriting_entity(self, entity: Entity,
                                             entity_dict: Dict[str, Entity],
                                             id_type: IdType):
        if entity.iri in entity_dict:
            old_entity = entity_dict[entity.iri]
            self.current_source.add_parsing_log_entry(
                LoggingLevel.warning, id_type, entity.iri,
                "{} {} from source {} was overwritten"
                .format(id_type, old_entity.get_label(),
                        old_entity.get_source_name(self.vocabulary)))

    def entity_is_known(self, iri: str) -> bool:
        """Test if the given iri is in vocabulary, if not it belongs to a
        dependency which is not yet loaded

        Args:
            iri (str)

        Returns:
            bool
        """
        return iri in self.vocabulary.id_types





