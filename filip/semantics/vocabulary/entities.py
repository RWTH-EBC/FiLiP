"""Vocabulary Models for Ontology Entities"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import List, TYPE_CHECKING, Dict, Union, Set, Any

from .source import DependencyStatement

if TYPE_CHECKING:
    from . import \
        CombinedObjectRelation, \
        CombinedDataRelation, \
        CombinedRelation, \
        Relation, \
        Vocabulary, \
        Source


class Entity(BaseModel):
    """
    Representing an OWL Entity (Class, Datatype, DataProperty, ObjectProperty,
                                Individual)

    An Entity is characterised by a unique IRI and originates from a source

    An Entity needs a unique Label (displayname) as it is used in FIWARE as
    field key. The user can overwrite the given
    label
    """
    iri: str = Field(description="Unique Internationalized Resource Identifier")
    label: str = Field(
        default="",
        description="Label (displayname) extracted from source file "
                    "(multiple Entities could have the same label)")
    user_set_label: Any = Field(
        default="",
        description="Given by user and overwrites 'label'."
                    " Needed to make labels unique")
    comment: str = Field(
        default="",
        description="Comment extracted from the ontology/source")
    source_ids: Set[str] = Field(
        default=set(),
        description="IDs of the sources that influenced this class")
    predefined: bool = Field(
        default=False,
        description="Stats if the entity is not extracted from a source, "
                    "but predefined in the program (Standard Datatypes)")

    def get_label(self) -> str:
        """ Get the label for the entity.
        If the user has set a label it is returned, else the label extracted
        from the source

        Returns:
             str
        """
        if not self.user_set_label == "":
            return self.user_set_label

        return self.get_original_label()

    def set_label(self, label:str):
        """ Change the display label of the entity

        Args:
            label (str): Label that the label should have
        """
        self.user_set_label = label

    def get_ontology_iri(self) -> str:
        """ Get the IRI of the ontology that this entity belongs to
        (extracted from IRI)

        Returns:
            str
        """
        index = self.iri.find("#")
        return self.iri[:index]

    def get_source_names(self, vocabulary: 'Vocabulary') -> List[str]:
        """ Get the names of all the sources

        Args:
            vocabulary (Vocabulary): Vocabulary of the project

        Returns:
            str
        """
        names = [vocabulary.get_source(id).get_name() for
                 id in self.source_ids]

        return names

    def get_sources(self, vocabulary: 'Vocabulary') -> List['Source']:
        """ Get all the source objects that influenced this entity.
        The sources are sorted according to their names

        Args:
           vocabulary (Vocabulary): Vocabulary of the project

        Returns:
           str
        """

        sources = [vocabulary.get_source(id) for id in self.source_ids]

        sources.sort(key=lambda x: x.source_name, reverse=False)
        return sources

    def _lists_are_identical(self, a: List, b: List) -> bool:
        """ Methode to test if to lists contain the same entries

        Args:
            a (List): first list
            b (List): second list
        Returns:
            bool
        """
        return len(set(a).intersection(b)) == len(set(a)) and len(a) == len(b)

    def is_renamed(self) -> bool:
        """ Check if the entity was renamed by the user

        Returns:
            bool
        """
        return not self.user_set_label == ""

    def get_original_label(self) -> str:
        """ Get label as defined in the source
        It can be that the label is empty, then extract the label from the iri

        Returns:
            str
        """
        if not self.label == "":
            return self.label

        index = self.iri.find("#") + 1
        return self.iri[index:]


class Class(Entity):
    """
    Representation of OWL:CLASS

    A class has a set of relations that are combined into CombinedRelations

    Instances are instantiations of a class

    A class can represent Devices, Agents, None or both
    """

    # The objects whose ids/iris are listed here can be looked up in the
    # vocabulary of this class
    child_class_iris: List[str] = Field(
        default=[],
        description="All class_iris of classes that inherit from this class")
    ancestor_class_iris: List[str] = Field(
        default=[],
        description="All class_iris of classes from which this class inherits")
    parent_class_iris: List[str] = Field(
        default=[],
        description="All class_iris of classes that are direct parents of this "
                    "class")
    relation_ids: List[str] = Field(
        default=[],
        description="All ids of relations defined for this class")
    combined_object_relation_ids: List[str] = Field(
        default=[],
        description="All combined_object_relations ids defined for this class")
    combined_data_relation_ids: List[str] = Field(
        default=[],
        description="All combined_data_relations ids defined for this class")

    def get_relation_ids(self) -> List[str]:
        """Get all ids of relations belonging to this class

        Returns:
            List[str]
        """
        return self.relation_ids

    def get_relations(self, vocabulary: 'Vocabulary') -> List['Relation']:
        """Get all relations belonging to this class

        Args:
            vocabulary (Vocabulary): Vocabulary of this project

        Returns:
            List[Relation]
        """
        result = []
        for id in self.relation_ids:
            result.append(vocabulary.get_relation_by_id(id))

        return result

    def get_combined_object_relations(self, vocabulary: 'Vocabulary') -> \
            List['CombinedObjectRelation']:
        """Get all combined object relations belonging to this class

        Args:
            vocabulary (Vocabulary): Vocabulary of this project

        Returns:
            List[CombinedObjectRelation]
        """

        result = []
        for id in self.combined_object_relation_ids:
            result.append(vocabulary.get_combined_object_relation_by_id(id))

        return result

    def get_combined_data_relations(self, vocabulary: 'Vocabulary') -> \
            List['CombinedDataRelation']:
        """Get all combined data relations belonging to this class

        Args:
            vocabulary (Vocabulary): Vocabulary of this project

        Returns:
            List[CombinedDataRelation]
        """

        result = []
        for id in self.combined_data_relation_ids:
            result.append(vocabulary.get_combined_data_relation_by_id(id))

        return result

    def get_combined_relations(self, vocabulary: 'Vocabulary') -> \
            List['CombinedRelation']:
        """Get all combined relations belonging to this class

        Args:
            vocabulary (Vocabulary): Vocabulary of this project

        Returns:
            List[CombinedRelation]
        """

        result = self.get_combined_object_relations(vocabulary)
        result.extend(self.get_combined_data_relations(vocabulary))
        return result

    def is_child_of_all_classes(self, target_list: List[str]) -> bool:
        """Tests if this class is a child class for each of the given classes

        Args:
            target_list (List[str]): List of ancestor class_iris

        Returns:
            bool
        """

        for target in target_list:
            if not target == self.iri:
                if target not in self.ancestor_class_iris:
                    return False
        return True

    def get_combined_object_relation_with_property_iri(
            self, obj_prop_iri: str, vocabulary: 'Vocabulary') \
            -> 'CombinedObjectRelation':
        """
        Get the CombinedObjectRelation of this class that combines the
        relations of the given ObjectProperty

        Args:
            obj_prop_iri (str): Iri of the ObjectProperty
            vocabulary (Vocabulary): Vocabulary of this project

        Returns:
            CombinedObjectRelation
        """
        for cor in self.get_combined_object_relations(vocabulary):
            if cor.property_iri == obj_prop_iri:
                return cor
        return None

    def get_combined_data_relation_with_property_iri(self, property_iri,
                                                     vocabulary):
        """
        Get the CombinedDataRelation of this class that combines the
        relations of the given DataProperty

        Args:
            property_iri (str): Iri of the DataProperty
            vocabulary (Vocabulary): Vocabulary of this project

        Returns:
            CombinedDataRelation
        """
        for cdr in self.get_combined_data_relations(vocabulary):
            if cdr.property_iri == property_iri:
                return cdr
        return None

    def get_combined_relation_with_property_iri(self, property_iri, vocabulary)\
            -> Union['CombinedRelation', None]:
        """
        Get the CombinedRelation of this class that combines the relations
        of the given Property

        If possible use the more specific access functions to save runtime.

        Args:
            property_iri (str): Iri of the Property
            vocabulary (Vocabulary): Vocabulary of this project

        Returns:
            CombinedRelation, None if iri is unknown
       """
        for cdr in self.get_combined_data_relations(vocabulary):
            if cdr.property_iri == property_iri:
                return cdr
        for cor in self.get_combined_object_relations(vocabulary):
            if cor.property_iri == property_iri:
                return cor
        return None

    def get_ancestor_classes(self, vocabulary: 'Vocabulary') -> List['Class']:
        """Get all ancestor classes of this class

        Args:
            vocabulary (Vocabulary): Vocabulary of this project

        Returns:
            List[Class]
        """
        ancestors = []
        for ancestor_iri in self.ancestor_class_iris:
            ancestors.append(vocabulary.get_class_by_iri(ancestor_iri))
        return ancestors

    def get_parent_classes(self,
                           vocabulary: 'Vocabulary',
                           remove_redundancy: bool = False) -> List['Class']:
        """Get all parent classes of this class

        Args:
            vocabulary (Vocabulary): Vocabulary of this project
            remove_redundancy (bool): if true the parents that are child of
                other parents are not included

        Returns:
            List[Class]
        """
        parents = []

        for parent_iri in self.parent_class_iris:
            parents.append(vocabulary.get_class_by_iri(parent_iri))

        if remove_redundancy:
            child_iris = set()
            for parent in parents:
                child_iris.update(parent.child_class_iris)
            for parent in parents:
                if parent.iri in child_iris:
                    parents.remove(parent)

        return parents

    def treat_dependency_statements(self, vocabulary: 'Vocabulary') -> \
            List[DependencyStatement]:
        """
        Purge and list all pointers/iris that are not contained in
        the vocabulary

        Args:
            vocabulary (Vocabulary): Vocabulary of this project

        Returns:
            List[Dict[str, str]]: List of purged statements dicts with keys:
            Parent Class, class, dependency, fulfilled
        """

        statements = []
        # parent classes:
        parents_to_purge = []
        for parent_iri in self.parent_class_iris:
            found = parent_iri in vocabulary.classes
            statements.append(DependencyStatement(type="Parent Class",
                                                  class_iri=self.iri,
                                                  dependency_iri=parent_iri,
                                                  fulfilled=found
                                                  ))
            if not found:
                parents_to_purge.append(parent_iri)
        for iri in parents_to_purge:
            self.parent_class_iris.remove(iri)

        # relations
        relation_ids_to_purge = set()
        for relation in self.get_relations(vocabulary):

            relation_statements = relation.get_dependency_statements(
                vocabulary, self.get_ontology_iri(), self.iri)
            for statement in relation_statements:
                if statement.fulfilled == False:
                    relation_ids_to_purge.add(relation.id)
            statements.extend(relation_statements)

        for id in relation_ids_to_purge:
            self.relation_ids.remove(id)
            del vocabulary.relations[id]

        return statements

    def get_next_combined_relation_id(self, current_cr_id: str,
                                      object_relations: bool) -> str:
        """Get the alphabetically(Property label) next CombinedRelation.

        If no CR is after the given one, the first is returned

        Args:
            current_cr_id (str): ID of the CombinedRelation of which the next
                should be found
            object_relations (bool):
                True if Searching for  CombinedObjectRelations

        Returns:
            str: ID of next CR
        """
        list_ = self.combined_data_relation_ids
        if object_relations:
            list_ = self.combined_object_relation_ids

        current_index = list_.index(current_cr_id)
        res_index = current_index+1
        if res_index >= len(list_):
            res_index = 0
        return list_[res_index]

    def get_previous_combined_relation_id(self, current_cr_id: str,
                                          object_relations: bool) -> str:
        """Get the alphabetically(Property label) previous CombinedRelation.

        If no CR is before the given one, the last is returned

        Args:
            current_cr_id (str): ID of the CombinedRelation of which the
                previous should be found
            object_relations (bool): True if Searching for
                CombinedObjectRelations

        Returns:
            str: ID of previous CR
        """

        list_ = self.combined_data_relation_ids
        if object_relations:
            list_ = self.combined_object_relation_ids

        current_index = list_.index(current_cr_id)
        res_index = current_index - 1
        if res_index < 0:
            res_index = len(list_)-1
        return list_[res_index]

    def is_logically_equivalent_to(self, class_: 'Class',
                                   vocabulary: 'Vocabulary',
                                   old_vocabulary: 'Vocabulary') -> bool:
        """Test if a class is logically equivalent in two vocabularies.

        Args:
            class_ (Class): Class to be tested against, from the old_vocabulary
            vocabulary (Vocabulary): New project vocabulary
            old_vocabulary (Vocabulary): Old project vocabulary

        Returns:
            bool
        """

        # test if parent classes are identical
        if not self._lists_are_identical(class_.parent_class_iris,
                                         self.parent_class_iris):
            return False

        # test if combined object relation ids are identical
        if not self._lists_are_identical(class_.combined_object_relation_ids,
                                         self.combined_object_relation_ids):
            return False

        # test if combined data  relation ids are identical
        if not self._lists_are_identical(class_.combined_data_relation_ids,
                                         self.combined_data_relation_ids):
            return False

        # test if combined relations are identical
        for cr in self.get_combined_relations(vocabulary):
            old_cr = old_vocabulary.get_combined_relation_by_id(cr.id)

            relation_strings = []
            for relation in cr.get_relations(vocabulary):
                relation_strings.append(relation.to_string(vocabulary))

            old_relation_strings = []
            for old_relation in old_cr.get_relations(old_vocabulary):
                old_relation_strings.append(old_relation.to_string(vocabulary))

            if not self._lists_are_identical(relation_strings,
                                             old_relation_strings):

                return False

        return True

    def is_iot_class(self, vocabulary: 'Vocabulary') -> bool:
        """
        A class is an iot/device class if it contains one CDR, where the
        relation is marked as a device relation: DeviceAttribute/Command

        Args:
            vocabulary (Vocabulary): Vocabulary of the project

        Returns:
            bool
        """

        for cdr_id in self.combined_data_relation_ids:
            cdr = vocabulary.get_combined_data_relation_by_id(cdr_id)
            prop = vocabulary.get_data_property(cdr.property_iri)
            if not prop.field_type == DataFieldType.simple:
                return True
        return False


class DatatypeType(str, Enum):
    """
    Types of a Datatype
    """
    string = 'string'
    number = 'number'
    date = 'date'
    enum = 'enum'


class DatatypeFields(BaseModel):
    """Key Fields describing a Datatype"""
    type: DatatypeType = Field(default=DatatypeType.string,
                               description="Type of the datatype")
    number_has_range: Any = Field(
        default=False,
        description="If Type==Number: Does the datatype define a range")
    number_range_min: Union[int, str] = Field(
        default="/",
        description="If Type==Number: Min value of the datatype range, "
                    "if a range is defined")
    number_range_max: Union[int, str] = Field(
        default="/",
        description="If Type==Number: Max value of the datatype range, "
                    "if a range is defined")
    number_decimal_allowed: bool = Field(
        default=False,
        description="If Type==Number: Are decimal numbers allowed?")
    forbidden_chars: List[str] = Field(
        default=[],
        description="If Type==String: Blacklisted chars")
    allowed_chars: List[str] = Field(
        default=[],
        description="If Type==String: Whitelisted chars")
    enum_values: List[str] = Field(
        default=[],
        description="If Type==Enum: Enum values")


class Datatype(Entity, DatatypeFields):
    """
    Represents OWL:Datatype

    A Datatype is the target of a DataRelation. The Datatype stats a set of
    values that are valid.
    This can be an ENUM, a number range, or a check for black/whitelisted chars

    In the Parsing PostProcesseor predefined datatype_catalogue are added to the
    vocabulary
    """

    def export(self) -> Dict[str,str]:
        """ Export datatype as dict

        Returns:
            Dict[str,str]
        """
        res = self.model_dump(include={'type', 'number_has_range',
                                 'number_range_min', 'number_range_max',
                                 'number_decimal_allowed', 'forbidden_chars',
                                 'allowed_chars', 'enum_values'},
                              exclude_defaults=True)
        res['type'] = self.type.value
        return res

    def value_is_valid(self, value: str) -> bool:
        """Test if value is valid for this datatype.
        Numbers are also given as strings

        Args:
            value (str): value to be tested

        Returns:
            bool
        """

        if self.type == DatatypeType.string:
            if len(self.allowed_chars) > 0:
                # if allowed chars is empty all chars are allowed
                for char in value:
                    if char not in self.allowed_chars:
                        return False
            for char in self.forbidden_chars:
                if char in value:
                    return False
            return True

        if self.type == DatatypeType.number:

            if self.number_decimal_allowed:
                try:
                    number = float(value)
                except:
                    return False
            else:
                try:
                    number = int(value)
                except:
                    return False

            if not self.number_range_min == "/":
                if number < self.number_range_min:
                    return False
            if not self.number_range_max == "/":
                if number > self.number_range_max:
                    return False

            return True

        if self.type == DatatypeType.enum:
            return value in self.enum_values

        if self.type == DatatypeType.date:
            try:
                from dateutil.parser import parse
                parse(value, fuzzy=False)
                return True

            except ValueError:
                return False

        return True

    def is_logically_equivalent_to(self, datatype:'Datatype',
                                   vocabulary: 'Vocabulary',
                                   old_vocabulary: 'Vocabulary') -> bool:
        """Test if this datatype is logically equivalent to the given datatype

        Args:
            datatype (Datatype): Datatype to compare against
            vocabulary (Vocabulary): Not used, but needed to keep signature the
                same as other entities
            old_vocabulary (Vocabulary): Not used, but needed to keep signature
                the same as other entities
        Returns:
            bool
        """

        if not self.type == datatype.type:
            return False
        if not self.number_has_range == datatype.number_has_range:
            return False
        if not self.enum_values == datatype.enum_values:
            return False

        return True


class Individual(Entity):
    """
    Represents OWL:Individual

    An individual is a predefined "instance" of a class
    But they are here only used as values for Relations

    They are not instances, no value can be assigned to them, they are no
    agents or devices
    """

    parent_class_iris: List[str] = Field(
        default=[],
        description="List of all parent class iris, "
                    "an individual can have multiple parents")

    def to_string(self) -> str:
        """Get a string representation of the Individual

        Returns:
            str
        """
        return "(Individual)"+self.get_label()

    def get_ancestor_iris(self, vocabulary: 'Vocabulary') -> List[str]:
        """ Get all iris of ancestor classes

        Args:
            vocabulary (Vocabulary): Vocabulary of the project

        Returns:
            List[str]
        """
        ancestor_iris = set()
        for parent_iri in self.parent_class_iris:
            ancestor_iris.add(parent_iri)
            ancestor_iris.update(vocabulary.get_class_by_iri(parent_iri).
                                 ancestor_class_iris)

        return list(ancestor_iris)

    def get_parent_classes(self, vocabulary: 'Vocabulary') -> List['Class']:
        """ Get all parent class objects

        Args:
            vocabulary (Vocabulary): Vocabulary of the project

        Returns:
            List[Class]
        """
        parents = []
        for parent_iri in self.parent_class_iris:
            parents.append(vocabulary.get_class_by_iri(parent_iri))
        return parents

    def is_logically_equivalent_to(self, individual: 'Individual',
                                   vocabulary: 'Vocabulary',
                                   old_vocabulary: 'Vocabulary') -> bool:
        """Test if this individal is logically equivalent in two vocabularies.

        Args:
            individual (Individual): Individual to be tested against, from the
                old vocabulary
            vocabulary (Vocabulary): New project vocabulary, not used but needed
                to keep signature the same
            old_vocabulary (Vocabulary): Old project vocabulary, not used but
                needed to keep signature the same

        Returns:
            bool
        """

        if not self._lists_are_identical(self.parent_class_iris,
                                         individual.parent_class_iris):
            return False
        return True

    def treat_dependency_statements(self, vocabulary: 'Vocabulary') -> \
            List[DependencyStatement]:
        """ Purge and list all pointers/iris that are not contained in the
        vocabulary

        Args:
            vocabulary (Vocabulary): Vocabulary of this project

        Returns:
            List[Dict[str, str]]: List of purged statements dicts with keys:
            Parent Class, class, dependency, fulfilled
        """
        statements = []

        for parent_iri in self.parent_class_iris:
            found = parent_iri in vocabulary.classes
            statements.append(DependencyStatement(type="Parent Class",
                                                  class_iri=self.iri,
                                                  dependency_iri=parent_iri,
                                                  fulfilled=found
                                                  ))

            if not found:
                self.parent_class_iris.remove(parent_iri)

        return statements


class DataFieldType(str, Enum):
    """Type of the field that represents the DataProperty"""
    command = "command"
    device_attribute = "device_attribute"
    simple = "simple"


class DataProperty(Entity):
    """
    Representation of OWL:DataProperty
    """

    field_type: DataFieldType = Field(
        default=DataFieldType.simple,
        description="Type of the dataproperty; set by the user while "
                    "configuring the vocabulary"
    )


class ObjectProperty(Entity):
    """
    Representation of OWL:ObjectProperty
    """

    inverse_property_iris: Set[str] = Field(
        default=set(),
        description="List of property iris that are inverse:Of; "
                    "If an instance i2 is added in an instance i1 "
                    "for this property. Then i1 is added to i2 under the"
                    " inverseProperty (if the class has that property)")

    def add_inverse_property_iri(self, iri: str):
        """Add an inverse property

        Args:
            iri (str): Iri of the inverse objectProperty

        Returns:
            None
        """
        self.inverse_property_iris.add(iri)

    def is_logically_equivalent_to(self, object_property: 'ObjectProperty',
                                   vocabulary: 'Vocabulary',
                                   old_vocabulary: 'Vocabulary') -> bool:
        """Test if this Property in the new_vocabulary is logically equivalent
        to the object_property in the old_vocabulary

        Args:
            object_property (ObjectProperty): ObjectProperty to be tested
                against, from the old vocabulary
            vocabulary (Vocabulary): New project vocabulary, not used but
                needed to keep signature the same
            old_vocabulary (Vocabulary): Old project vocabulary, not used but
                needed to keep signature the same

        Returns:
            bool
        """
        if not self.inverse_property_iris == \
                object_property.inverse_property_iris:
            return False

        return True
