import operator
import uuid
from enum import Enum

from pydantic import BaseModel
from . import *
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


class Vocabulary(BaseModel):
    """
    Semantic Vocabulary of a project

    This class holds all objects in a vocabulary as central unit.
    These objects can be accessed with the according ids/iris

    The vocabulary consists out of multiple sources, that each contribute
    objects
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

    current_source: Source = None
    """Current source to which entities are added, needed while parsing"""

    conflicting_label_entities: Dict[str, List[Entity]] = {}
    """ used to store these results from postprocessing until the vocabulary is 
    committed matches label to list of entities who currently have that label"""

    conflicting_original_labels: Set[str] = set()
    """used to store results from postprocessing
    contains all original labels that were found more than once """

    def clear(self):
        """Clear all objects form the vocabulary

        Returns:
            None
        """
        self.classes.clear()
        self.object_properties.clear()
        self.data_properties.clear()
        self.datatypes.clear()
        self.relations.clear()
        self.combined_object_relations.clear()
        self.combined_data_relations.clear()
        self.individuals.clear()
        self.id_types.clear()
        for source in self.sources.values():
            source.clear()

    def get_type_of_id(self, id:str) -> Union[IdType,None]:
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

    def add_class(self, class_: Class):
        """Add a class to the vocabulary

        Args:
            class_ (Class): class to be added

        Returns:
            None
        """

        self.add_log_entry_for_overwriting_entity(class_, self.classes,
                                                  IdType.class_)

        self.classes[class_.iri] = class_
        self.id_types[class_.iri] = IdType.class_
        class_.source_id = self.current_source.id

    def get_class_by_iri(self, class_iri: str) -> Union[Class, None]:
        """Get the class belonging to the class_iri

        Args:
            class_iri (str): iri

        Returns:
            Class or None if iri not a registered class
        """
        return self.classes.get(class_iri)

    def add_object_property(self, obj_prop: ObjectProperty):
        """Add an ObjectProperty to the vocabulary

        Args:
            obj_prop (ObjectProperty): ObjectProperty to be added

        Returns:
            None
        """

        self.add_log_entry_for_overwriting_entity(
            obj_prop, self.object_properties, IdType.object_property)

        self.object_properties[obj_prop.iri] = obj_prop
        self.id_types[obj_prop.iri] = IdType.object_property
        obj_prop.source_id = self.current_source.id

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

    def add_data_property(self, data_prop: DataProperty):
        """Add an DataProperty to the vocabulary

        Args:
            data_prop (DataProperty): DataProperty to be added

        Returns:
            None
        """

        self.add_log_entry_for_overwriting_entity(
            data_prop, self.data_properties, IdType.data_property)

        self.data_properties[data_prop.iri] = data_prop
        self.id_types[data_prop.iri] = IdType.data_property
        data_prop.source_id = self.current_source.id

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

    def add_datatype(self, datatype: Datatype):
        """Add a DataType to the vocabulary

        Args:
            datatype (Datatype): Datatype to be added

        Returns:
            None
        """

        self.add_log_entry_for_overwriting_entity(
            datatype, self.datatypes, IdType.datatype)

        self.id_types[datatype.iri] = IdType.datatype
        self.datatypes[datatype.iri] = datatype
        datatype.source_id = self.current_source.id

    def add_predefined_datatype(self, datatype: Datatype):
        """Add a DataType to the vocabulary, that belongs to the source:
            Predefined

        Args:
            datatype (Datatype): Datatype to be added

        Returns:
            None
        """
        self.id_types[datatype.iri] = IdType.datatype
        self.datatypes[datatype.iri] = datatype
        datatype.predefined = True
        datatype.source_id = "PREDEFINED"

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

    def add_individual(self, individual: Individual):
        """Add an Individual to the vocabulary

        Args:
            individual (Individual): Individual to be added

        Returns:
            None
        """

        self.add_log_entry_for_overwriting_entity(individual, self.individuals,
                                                  IdType.individual)

        self.individuals[individual.iri] = individual
        self.id_types[individual.iri] = IdType.individual
        individual.source_id = self.current_source.id

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
        return self.classes.values()

    def get_classes_sorted_by_label(self) -> List[Class]:
        return sorted(self.classes.values(),
                      key=operator.methodcaller("get_label"),
                      reverse=False)

    def sort_entity_list_by_label(self, list: List[Entity]) -> List[Entity]:
        """Sort a given entity list by their labels

        Args:
            list (List[Entity]) : entities to be sorted
        Returns:
            List[Entity]: sorted list
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

    def add_relation_for_class(self, class_iri: str, rel: Relation):
        self.relations[rel.id] = rel
        self.get_class_by_iri(class_iri).relation_ids.append(rel.id)
        self.id_types[rel.id] = IdType.relation

    def add_combined_object_relation_for_class(self, class_iri: str,
                                               crel: CombinedObjectRelation):
        self.combined_object_relations[crel.id] = crel
        self.get_class_by_iri(class_iri).\
            combined_object_relation_ids.append(crel.id)
        self.id_types[crel.id] = IdType.combined_relation

    def add_combined_data_relation_for_class(self, class_iri: str,
                                             cdata: CombinedDataRelation):
        self.combined_data_relations[cdata.id] = cdata
        self.get_class_by_iri(class_iri).\
            combined_data_relation_ids.append(cdata.id)
        self.id_types[cdata.id] = IdType.combined_relation

    def add_source(self, source: Source, id: str = None):
        if id is None:
            source.id = uuid.uuid4().hex
        else:
            source.id = id
        self.id_types[source.id] = IdType.source
        self.sources[source.id] = source
        self.current_source = source

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

    def get_sources(self) -> List[Source]:
        """Get all source objects of the vocabulary

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

    def entity_is_known(self, iri: str) -> bool:
        """Test if the given iri is in vocabulary, if not it belongs to a
        dependency which is not yet loaded

        Args:
            iri (str)

        Returns:
            bool
        """
        return iri in self.id_types

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

    def set_current_source(self, source_id: str):
        assert source_id in self.sources
        self.current_source = self.sources[source_id]

    def add_log_entry_for_overwriting_entity(self, entity: Entity,
                                             entity_dict: Dict[str, Entity],
                                             id_type: IdType):
        if entity.iri in entity_dict:
            old_entity = entity_dict[entity.iri]
            self.current_source.add_parsing_log_entry(
                LoggingLevel.warning, id_type, entity.iri,
                "{} {} from source {} was overwritten"
                .format(id_type, old_entity.get_label(),
                        old_entity.get_source_name(self)))

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
        Multiple individuals/datatypes can have the same label, this is no issue
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

    def transfer_settings(self, new_vocabulary: 'Vocabulary'):
        """Transfer all the user made settings (labels, key_colums, ia_agent,..)
        to a new vocabulary

        Args:
            new_vocabulary (Vocabulary): Vocabulary to which the settings of
            this vocabulary should be transferred

        Returns:
            None
        """

        # agent&device settings
        for class_ in self.get_classes():
            if class_.iri in new_vocabulary.classes:
                new_vocabulary.get_class_by_iri(class_.iri).is_agent_class = \
                    class_.is_agent_class
                new_vocabulary.get_class_by_iri(class_.iri).is_iot_class = \
                    class_.is_iot_class

        # label settings
        for entity in self.get_all_entities():
            new_entity = new_vocabulary.get_entity_by_iri(entity.iri)
            if new_entity is not None:
                new_entity.user_set_label = entity.user_set_label

        # combined relation settings
        combined_relation_pairs = [(self.combined_object_relations,
                                    new_vocabulary.combined_object_relations),
                                   (self.combined_data_relations,
                                    new_vocabulary.combined_data_relations)]
        for (old_list, new_list) in combined_relation_pairs:
            for cr_id in old_list:
                if cr_id in new_list:

                    old_cr = self.get_combined_relation_by_id(cr_id)
                    new_cr = new_vocabulary.get_combined_relation_by_id(cr_id)
                    new_cr.is_key_information = old_cr.is_key_information
                    new_cr.inspect = old_cr.inspect

        # CombinedDataRelation additional Settings
        for cdr_id in self.combined_data_relations:
            if cdr_id in new_vocabulary.combined_data_relations:
                old_cdr = self.get_combined_data_relation_by_id(cdr_id)
                new_cdr = new_vocabulary.\
                    get_combined_data_relation_by_id(cdr_id)
                new_cdr.type = old_cdr.type
