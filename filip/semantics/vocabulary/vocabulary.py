"""Main Vocabulary Model, and Submodels"""

import operator
from enum import Enum

from pydantic import BaseModel, Field
from . import *
from typing import List, Dict, Union, Optional, Tuple

from ...models.base import LogLevel


class LabelSummary(BaseModel):
    """
    Model holding all information for label conflicts in a vocabulary
    """
    class_label_duplicates: Dict[str, List[Entity]] = Field(
        description="All Labels that are used more than once for class_names "
                    "on export."
                    "Key: Label, Values: List of entities with key label"
    )
    field_label_duplicates: Dict[str, List[Entity]] = Field(
        description="All Labels that are used more than once for property_names"
                    "on export."
                    "Key: Label, Values: List of entities with key label"
    )
    datatype_label_duplicates: Dict[str, List[Entity]] = Field(
        description="All Labels that are used more than once for datatype "
                    "on export." 
                    "Key: Label, Values: List of entities with key label"
    )

    blacklisted_labels: List[Tuple[str, Entity]] = Field(
        description="All Labels that are blacklisted, "
                    "Tuple(Label, Entity with label)"
    )
    labels_with_illegal_chars: List[Tuple[str, Entity]] = Field(
        description="All Labels that contain illegal characters, "
                    "Tuple(Label, Entity with label)"
    )

    def is_valid(self) -> bool:
        """Test if Labels are valid

        Returns:
            bool, True if no entries exist
        """
        return len(self.class_label_duplicates) == 0 and \
               len(self.field_label_duplicates) == 0 and \
               len(self.datatype_label_duplicates) == 0 and \
               len(self.blacklisted_labels) == 0 and \
               len(self.labels_with_illegal_chars) == 0

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
                sub_res += "\t/\n"
            return sub_res

        def print_list(collection):
            sub_res = ""
            for key, value in collection:
                sub_res += f"\t{key}: \t {value.iri}"
                sub_res += "\n"
            if len(collection) == 0:
                sub_res += "\t/\n"
            return sub_res

        res += "class_label_duplicates:\n"
        res += print_collection(self.class_label_duplicates)
        res += "field_label_duplicates:\n"
        res += print_collection(self.field_label_duplicates)
        res += "datatype_label_duplicates:\n"
        res += print_collection(self.datatype_label_duplicates)
        res += "blacklisted_labels:\n"
        res += print_list(self.blacklisted_labels)
        res += "labels_with_illegal_chars:\n"
        res += print_list(self.labels_with_illegal_chars)
        return res


class IdType(str, Enum):
    """Type of object that is referenced by an id/iri"""
    class_ = 'Class'
    object_property = 'Object Property'
    data_property = 'Data Property'
    datatype = 'Datatype'
    relation = 'Relation'
    combined_relation = 'Combined Relation'
    individual = 'Individual'
    source = 'Source'


class VocabularySettings(BaseModel):
    """
    Settings that state how labels of ontology entities should be
    automatically converted on parsing
    """
    pascal_case_class_labels: bool = Field(
        default=True,
        description="If true, convert all class labels given in the ontologies "
                    "to PascalCase"
    )
    pascal_case_individual_labels: bool = Field(
        default=True,
        description="If true, convert all labels of individuals given in the "
                    "ontologies to PascalCase"
    )
    camel_case_property_labels: bool = Field(
        default=True,
        description="If true, convert all labels of properties given in the "
                    "ontologies to camelCase"
    )
    camel_case_datatype_labels: bool = Field(
        default=True,
        description="If true, convert all labels of datatypes given in the "
                    "ontologies to camelCase"
    )
    pascal_case_datatype_enum_labels: bool = Field(
        default=True,
        description="If true, convert all values of enum datatypes given in "
                    "the to PascalCase"
    )


class Vocabulary(BaseModel):
    """
    Semantic Vocabulary of a project

    This class holds all objects in a vocabulary as central unit.
    These objects can be accessed with the according ids/iris

    The vocabulary consists out of multiple sources, that each contribute
    objects

    From the vocabulary nothing should be added or deleted manually. The sources
    are added and removed through the respective methods. Everything else should
    be used as READ-ONLY
    """

    classes: Dict[str, Class] = Field(
        default={},
        description="Classes of the vocabulary. Key: class_iri")
    object_properties: Dict[str, ObjectProperty] = Field(
        default={},
        description="ObjectProperties of the vocabulary. "
                    "Key: object_property_iri")
    data_properties: Dict[str, DataProperty] = Field(
        default={},
        description="DataProperties of the vocabulary. Key: data_property_iri")
    datatypes: Dict[str, Datatype] = Field(
        default={},
        description="Datatypes of the vocabulary. Key: datatype_iri")
    individuals: Dict[str, Individual] = Field(
        default={},
        description="Individuals in the vocabulary. Key: individual_iri")

    relations: Dict[str, Relation] = Field(
        default={},
        description="Relations of classes in the vocabulary. Key: relation_id")
    combined_object_relations: Dict[str, CombinedObjectRelation] = Field(
        default={},
        description="CombinedObjectRelations of classes in the vocabulary."
                    " Key: combined_relation_id")
    combined_data_relations: Dict[str, CombinedDataRelation] = Field(
        default={},
        description="CombinedDataRelations of classes in the vocabulary."
                    "Key: combined_data_id")

    sources: Dict[str, Source] = Field(
        default={},
        description="Sources of the vocabulary. Key: source_id")

    id_types: Dict[str, IdType] = Field(
        default={},
        description="Maps all entity iris and (combined)relations to their "
                    "Entity/Object type, to speed up lookups")

    original_label_summary: Optional[LabelSummary] = Field(
        default=None,
        description="Original label after parsing, before the user made "
                    "changes")

    settings: VocabularySettings = Field(
        default=VocabularySettings(),
        description="Settings how to auto transform the entity labels")

    def get_type_of_id(self, id: str) -> Union[IdType,None]:
        """Get the type (class, relation,...) of an iri/id

        Args:
            id (str): id/iri of which the type should be returned

        Returns:
            IdType or None if id/iri not registered
        """
        try:
            return self.id_types[id]
        except KeyError:
            return None

    def get_class_by_iri(self, class_iri: str) -> Union[Class, None]:
        """Get the class belonging to the class_iri

        Args:
            class_iri (str): iri

        Returns:
            Class or None if iri not a registered class
        """
        return self.classes.get(class_iri)

    def get_object_property(self, obj_prop_iri: str) -> ObjectProperty:
        """Get the object property beloning to the iri

        Args:
            obj_prop_iri (str): iri

        Returns:
            ObjectProperty

        Raises:
            KeyError: if not a registered obj property

        """
        return self.object_properties[obj_prop_iri]

    def get_data_property(self, data_prop_iri: str) -> DataProperty:
        """Get the data property belonging to the iri

        Args:
            data_prop_iri (str): iri

        Returns:
            DataProperty

        Raises:
            KeyError: if not a registered obj property

        """
        return self.data_properties[data_prop_iri]

    def iri_is_predefined_datatype(self, iri: str) -> bool:
        """Test if an iri belongs to a predefined datatype

        Args:
            iri (str): Iri to test

        Returns:
            bool
        """
        if iri not in self.id_types.keys():
            return False
        if self.id_types[iri] is IdType.datatype:
            return self.get_datatype(iri).predefined

    def get_datatype(self, datatype_iri:str) -> Datatype:
        """Get the datatype belonging to the iri

        Args:
            datatype_iri (str): iri

        Returns:
            DataType

        Raises:
            KeyError: if not a registered datatype
        """
        return self.datatypes[datatype_iri]

    def get_individual(self, individual_iri: str) -> Individual:
        """Get the individual belonging to the iri

        Args:
            individual_iri (str): iri

        Returns:
             Individual

        Raises:
            KeyError: if not a registered  Individual
        """
        return self.individuals[individual_iri]

    def get_all_individuals_of_class(self, class_iri: str) -> List[Individual]:
        """Get all individual that have the class_iri as parent

        Args:
             class_iri (str): iri of parent class

        Returns:
             List[Individual]
        """
        result = []
        for individual in self.individuals.values():
            if class_iri in individual.parent_class_iris:
                result.append(individual)
        return result

    def is_id_from_individual(self, id: str) -> bool:
        """
        Test if an id is from an Individual. Used to distinguish between
        instances and individuals

        Args:
            id (str): id

        Returns:
            bool
        """
        try:
            return self.get_type_of_id(id) == IdType.individual
        except:
            return False

    def get_classes(self) -> List[Class]:
        """
        Get all classes in this vocabulary

        Returns:
            List[Class]
        """
        return list(self.classes.values())

    def get_classes_sorted_by_label(self) -> List[Class]:
        """Get all classes sorted by their labels

         Returns:
            List[Class]: sorted classes, ascending
        """
        return sorted(self.classes.values(),
                      key=operator.methodcaller("get_label"),
                      reverse=False)

    def get_entity_list_sorted_by_label(self, list: List[Entity]) \
            -> List[Entity]:
        """Sort a given entity list by their labels

        Args:
            list (List[Entity]) : entities to be sorted
        Returns:
            List[Entity]: sorted list
        """
        return sorted(list, key=operator.methodcaller("get_label"),
                      reverse=False)

    def get_object_properties_sorted_by_label(self) -> List[ObjectProperty]:
        """Get all object properties of the vocabulary sorted by their labels

        Returns:
            List[ObjectProperty], sorted by ascending labels
        """
        return sorted(self.object_properties.values(),
                      key=operator.methodcaller("get_label"), reverse=False)

    def get_data_properties_sorted_by_label(self) -> List[DataProperty]:
        """Get all data properties of the vocabulary sorted by their labels

        Returns:
            List[DataProperty], sorted by ascending labels
        """
        return sorted(self.data_properties.values(),
                      key=operator.methodcaller("get_label"), reverse=False)

    def get_individuals_sorted_by_label(self) -> List[Individual]:
        """Get all individuals of the vocabulary sorted by their labels

        Returns:
            List[Individual], sorted by ascending labels
        """
        return sorted(self.individuals.values(),
                      key=operator.methodcaller("get_label"), reverse=False)

    def get_datatypes_sorted_by_label(self) -> List[Datatype]:
        """Get all datatypes of the vocabulary sorted by their labels

        Returns:
            List[Datatype], sorted by ascending labels
        """
        return sorted(self.datatypes.values(),
                      key=operator.methodcaller("get_label"), reverse=False)

    def get_relation_by_id(self, id: str) -> Relation:
        """Get Relation by relation id

        Args:
            id (str): relation_id

        Returns:
            Relation

        Raises:
            KeyError: if id not registered as relation
        """
        return self.relations[id]

    def get_combined_relation_by_id(self, id: str) -> CombinedRelation:
        """Get CombinedRelation by id

        Args:
            id (str): combined_relation_id

        Returns:
            CombinedRelation

        Raises:
            KeyError: if id not registered as CombinedObjectRelation
                        or CombinedDataRelation
        """
        if id in self.combined_object_relations:
            return self.combined_object_relations[id]
        else:
            return self.combined_data_relations[id]

    def get_combined_data_relation_by_id(self, id: str) -> CombinedDataRelation:
        """Get CombinedDataRelation by id

        Args:
            id (str): combined_relation_id

        Returns:
            CombinedDataRelation

        Raises:
            KeyError: if id not registered as CombinedDataRelation
        """
        return self.combined_data_relations[id]

    def get_combined_object_relation_by_id(self, id: str)\
            -> CombinedObjectRelation:
        """Get CombinedObjectRelation by id

        Args:
            id (str): combined_relation_id

        Returns:
            CombinedObjectRelation

        Raises:
            KeyError: if id not registered as CombinedObjectRelation
        """
        return self.combined_object_relations[id]

    def get_source(self, source_id: str) -> Source:
        """Get the source with the given id

        Args:
            source_id (str): id

        Returns:
            Source

        Raises:
            KeyError: if source_id is not registered
        """
        return self.sources[source_id]

    def get_source_list(self) -> List[Source]:
        """Get all source objects of the vocabulary as list

        Returns:
            List[Source]
        """
        res = []
        for iri in self.sources:
            res.append(self.sources[iri])
        return res

    def has_source(self, source_id: str) -> bool:
        """Test if the vocabulary contains a source with the given id

        Args:
            source_id (str): id to test

        Returns:
            bool
        """
        return source_id in self.sources

    def is_id_of_type(self, id: str, type: IdType) -> bool:
        """Test if an iri/id is of a given type

        Args:
            id (str): id to test
            type (str): Type to test against

        Returns:
            bool

        Raises:
            KeyError: if id not registered
        """
        return self.id_types[id] == type

    def get_label_for_entity_iri(self, iri: str) -> str:
        """Get the label of the entity with the given iri
        Fast efficient methode

        Args:
            iri (str)

        Returns:
            str, "" if iri does not belong to an entity
        """

        entity = self.get_entity_by_iri(iri)
        if entity is not None:
            return entity.get_label()
        else:
            return ""

    @staticmethod
    def get_base_out_of_iri(iri: str):
        """Extract out of a given iri the base aka ontology name

        Args:
            iri (str), iri to extract

        Returns:
            str, base of iri
        """

        if "#" in iri:
            index = iri.find("#")
            return iri[:index]
        else:
            # for example if uri looks like:
            # http://webprotege.stanford.edu/RDwpQ8vbi7HaApq8VoqJUXH
            index = iri.rfind("/")
            return iri[:index]

    def get_entity_by_iri(self, iri: str) -> Union[None, Entity]:
        """Get the entity with the given iri
        Fast efficient methode

        Args:
            iri (str)

        Returns:
            Entity or None if iri does not belong to an Entity
        """
        if iri not in self.id_types:
            return None
        else:
            id_type = self.get_type_of_id(iri)

            if id_type == IdType.individual:
                return self.get_individual(iri)
            if id_type == IdType.class_:
                return self.get_class_by_iri(iri)
            if id_type == IdType.datatype:
                return self.get_datatype(iri)
            if id_type == IdType.object_property:
                return self.get_object_property(iri)
            if id_type == IdType.data_property:
                return self.get_data_property(iri)
            else:
                return None

    def is_iri_registered(self, iri: str) -> bool:
        """Test if iri/id is registered (Entities or (Combined)relations)

        Args:
            iri (str): iri to test

        Returns:
            bool
        """
        return iri in self.id_types

    def set_label_for_entity(self, iri: str, label: str):
        """Set a userset label for the given entity

        Args:
            iri (str): entity iri
            label (str): new label

        Returns:
            None
        """
        entity = self.get_entity_by_iri(iri)

        if entity.get_original_label() == label:
            entity.user_set_label = ""
        elif label == "":
            entity.user_set_label = ""

        else:
            entity.user_set_label = label

    def get_all_entities(self) -> List[Entity]:
        """Get all registered Entities

        Returns:
            List[Entity]
        """
        lists = [self.classes.values(),
                 self.object_properties.values(),
                 self.data_properties.values(),
                 self.datatypes.values(),
                 self.individuals.values()
                 ]

        res = []
        for l in lists:
            res.extend(l)
        return res

    def get_enum_dataytypes(self) -> Dict[str, Datatype]:
        """Get all datatypes of vocabularies that are of type ENUM

        Returns:
            Dict[str, Datatype], {datatype.iri: Datatype}
        """
        return {datatype.iri: datatype for datatype in self.datatypes.values()
                if len(datatype.enum_values) > 0 and not datatype.predefined}
