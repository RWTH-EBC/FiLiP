import copy
import datetime
import operator
import uuid
from enum import Enum

from pydantic import BaseModel
from . import *
from typing import List, Dict, Union, Set, Optional


class IdType(str, Enum):
    class_ = 'Class'
    object_property = 'Object Property'
    data_property = 'Data Property'
    datatype = 'Datatype'
    relation = 'Relation'
    combined_relation = 'Combined Relation'
    individual = 'Individual'
    source = 'Source'


class LoggingLevel(str, Enum):
    """LoggingLevel for parsing statements"""
    severe = "severe"
    warning = "warning"
    info = "info"


class ParsingError(BaseModel):
    level: LoggingLevel
    """Severity of error"""
    source_iri: str
    """Iri of the source containing the error"""
    source_name: Optional[str] = None
    """Name of the source, only set in get_function"""
    entity_type: 'IdType'
    "Type of the problematic entity: Class, Individual,.."
    entity_iri: str
    """Iri of the problematic entity"""
    entity_label: Optional[str] = None
    """Name of the source, only set in get_function"""
    message: str
    """Message describing the error"""

    class Config:
        use_enum_values = True


class VocabularySettings(BaseModel):
    pascal_case_class_labels: bool = True
    pascal_case_individual_labels: bool = True
    snake_case_property_labels: bool = True
    snake_case_datatype_labels: bool = True
    pascal_case_datatype_enum_labels: bool = True


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

    classes: Dict[str, Class] = {}
    """Classes of the vocabulary. Key: class_iri"""
    object_properties: Dict[str, ObjectProperty] = {}
    """ObjectProperties of the vocabulary. Key: object_property_iri"""
    data_properties: Dict[str, DataProperty] = {}
    """DataProperties of the vocabulary. Key: data_property_iri"""
    datatypes: Dict[str, Datatype] = {}
    """Datatypes of the vocabulary. Key: datatype_iri"""
    individuals: Dict[str, Individual] = {}
    """Individuals in the vocabulary. Key: individual_iri"""

    relations: Dict[str, Relation] = {}
    """Relations of classes in the vocabulary. Key: relation_id"""
    combined_object_relations: Dict[str, CombinedObjectRelation] = {}
    """CombinedObjectRelations of classes in the vocabulary. 
        Key: combined_relation_id"""
    combined_data_relations: Dict[str, CombinedDataRelation] = {}
    """CombinedDataRelations of classes in the vocabulary. 
        Key: combined_data_id"""

    sources: Dict[str, Source] = {}
    """Sources of the vocabulary. Key: source_id"""

    id_types: Dict[str, IdType] = {}
    """Maps all entity iris and (combined)relations to their Entity/Object 
        type, to speed up lookups"""

    settings: VocabularySettings = VocabularySettings()

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
        """Test if an id is from an Individual. Used to distinguish between
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
        """Get all classes in this vocabulary

        Returns:
            List[Class]
        """
        return list(self.classes.values())

    def get_classes_sorted_by_label(self) -> List[Class]:
        return sorted(self.classes.values(),
                      key=operator.methodcaller("get_label"),
                      reverse=False)

    def get_entity_list_sorted_by_label(self, list: List[Entity]) \
            -> List[Entity]:
        """Sort a given entity _list by their labels

        Args:
            list (List[Entity]) : entities to be sorted
        Returns:
            List[Entity]: sorted _list
        """
        return sorted(list, key=operator.methodcaller("get_label"),
                      reverse=False)

    def get_object_properties_sorted_by_label(self) -> List[ObjectProperty]:
        return sorted(self.object_properties.values(),
                      key=operator.methodcaller("get_label"), reverse=False)

    def get_data_properties_sorted_by_label(self) -> List[DataProperty]:
        return sorted(self.data_properties.values(),
                      key=operator.methodcaller("get_label"), reverse=False)

    def get_individuals_sorted_by_label(self) -> List[Individual]:
        return sorted(self.individuals.values(),
                      key=operator.methodcaller("get_label"), reverse=False)

    def get_datatypes_sorted_by_label(self) -> List[Datatype]:
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
        """Get all source objects of the vocabulary as _list

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

    def get_base_out_of_iri(self, iri: str):

        if "#" in iri:
            index = iri.find("#")
            return iri[:index]
        else:
            #for example if uri looks like:
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

    def is_label_a_duplicate(self, label: str, entity_iri: str = "",
                             id_type: IdType = None,
                             ignore_iri: str = "" ) -> bool:
        """Tests if an entity has currently the same label as the given label.

        Duplicates are only evaluated for class, and properties as Indivuals
        and Datatype labels are never used as keys in Fiware.
        Multiple individuals/datatype_catalogue can have the same label, this is no issue
        for the system it may disturb the user, but it is his own choice

        Args:
            label (str): label to test
            entity_iri (str): Iri of the entity to whcih the checked label will
                belong
            id_type (IdType): Alternativ to entity_iri, directly give the
                entity_type. Exactly One of both needs to ge given
            ignore_iri (str): OPTIONAL, iri of an entity to ignore when testing

        Returns:
            bool
        """

        assert not entity_iri == "" or id_type is not None
        assert not(entity_iri == "" and id_type is None)

        if not entity_iri == "":
            id_type = self.get_type_of_id(entity_iri)

        if id_type == IdType.class_ or id_type == IdType.object_property or \
                id_type == IdType.data_property:
            lists = [self.classes.values(), self.object_properties.values(),
                     self.data_properties.values()]
        else:
            return False
            # do not check label for this categories duplicates are allowed

        for l in lists:
            for entity in l:
                label_2 = entity.get_label()
                if label == label_2 and not entity.iri == ignore_iri:
                    return True

        return False

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

    def get_entities_with_overwritten_labels_without_conflict(self) ->\
            List[Entity]:
        """Get all entities that have a userset label and whose original label
        is unique

        Returns:
            List[Entity]
        """
        res = []
        for entity in self.get_all_entities():
            if entity.is_renamed():
                if not entity.get_original_label() in \
                       self.conflicting_original_labels:
                    res.append(entity)

        return res

    def get_enum_dataytypes(self) -> Dict[str, Datatype]:
        return {datatype.iri: datatype for datatype in self.datatypes.values()
                if len(datatype.enum_values) > 0 and not datatype.predefined}
