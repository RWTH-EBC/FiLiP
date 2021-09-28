from typing import List, Set, Dict, TYPE_CHECKING

from pydantic import BaseModel
from enum import Enum


from . import TargetStatement, StatementType

if TYPE_CHECKING:
    from . import Vocabulary, Class


class RestrictionType(str, Enum):
    """RestrictionTypes, as defined for OWL:
        some: at least 1 value of that target
        only: only value of that target
        min: min n values of that target
        max: max n values of that target
        exactly: exactly n values of that target
        value: predefined value
    """
    some = 'some'
    only = 'only'
    min = 'min'
    max = 'max'
    exactly = 'exactly'
    value = 'value'


class Relation(BaseModel):
    """
    A Relation is defined in the source for a class.
    It has the form: RestrictionType property target_statement

    It defines a set of allowed/required values which each instance of this
    class can/should have under this property

    A Relation is defined in a OWL:class, but all child classes of that class
    inherit it
    """

    id: str
    """Unique generated Relation ID, for internal use"""
    restriction_type: RestrictionType = None
    """Restriction type of this relation"""
    restriction_cardinality: int = -1
    """Only needed for min, max, equaly states the 'n'"""
    property_iri: str = ""
    """IRI of the property (data- or object-)"""
    target_statement: TargetStatement = None
    """Complex statement which classes/datatypes are allowed/required"""

    def get_targets(self) -> List[List[str]]:
        """Get all targets specified in the target statement in AND-OR Notation

        Returns:
            List[List[str]]: [[a,b],[c]] either a and b needs to present, or c
        """
        return self.target_statement.get_all_targets()

    def to_string(self, vocabulary: 'Vocabulary') -> str:
        """ Get a string representation of the relation

        Args:
            vocabulary (Vocabulary): Vocabulary of this project

        Returns:
            str
        """

        if self.restriction_cardinality == -1:
            return "{} {}".format(self.restriction_type, self.target_statement.
                                  to_string(vocabulary))
        else:
            return self.restriction_type + " " + \
                   str(self.restriction_cardinality) + " " \
                   + self.target_statement.to_string(vocabulary)

    def is_restriction_fulfilled(self, number_of_fulfilling_values: int,
                                 total_number_of_values: int) -> bool:
        """Test if the restriction type is fulfilled by comparing the number of
        fulfilling values against the total
        number of values given

        Args:
            number_of_fulfilling_values (int): Number of values that fulfill the
                relation
            total_number_of_values (int): the number of values given for this
                relation

        Returns:
            bool
        """

        if self.restriction_type == RestrictionType.some:
            return number_of_fulfilling_values >= 1
        if self.restriction_type == RestrictionType.only:
            return number_of_fulfilling_values == total_number_of_values
        if self.restriction_type == RestrictionType.min:
            return number_of_fulfilling_values >= \
                   (int)(self.restriction_cardinality)
        if self.restriction_type == RestrictionType.max:
            return number_of_fulfilling_values <= \
                   (int)(self.restriction_cardinality)
        if self.restriction_type == RestrictionType.exactly:
            return number_of_fulfilling_values == \
                   (int)(self.restriction_cardinality)
        if self.restriction_type == RestrictionType.value:
            return number_of_fulfilling_values >= 1


    def get_dependency_statements(
            self, vocabulary: 'Vocabulary', ontology_iri: str, class_iri: str) \
            -> List[Dict[str, str]]:
        """ Get a list of all pointers/iris that are not contained in the vocabulary
            Purging is done in class

        Args:
            vocabulary (Vocabulary): Vocabulary of this project
            ontology_iri (str): IRI of the source ontology
            class_iri (str): IRI of class (legacy)

        Returns:
            List[Dict[str, str]]: List of purged statements dicts with keys:
                Parent Class, class, dependency, fulfilled
        """
        statements = []

        found = self.property_iri in vocabulary.object_properties or \
                self.property_iri in vocabulary.data_properties
        statements.append({"type": "Relation Property", "class": class_iri,
                           "dependency": self.property_iri, "fulfilled": found})

        statements.extend(self.target_statement.get_dependency_statements(
            vocabulary, ontology_iri, class_iri))

        return statements

    def is_fulfilled_with_iris(
            self, vocabulary: 'Vocabulary', values: List[str],
            ancestor_values: List[List[str]]) -> bool:
        """Test if a set of values fulfills the rules of the relation

        Args:
            vocabulary (Vocabulary): Vocabulary of the project
            values (List[str]):  List of values to check
            ancestor_values(List[List[str]]): List containing the ancestors iris
                for each value (linked over index)
        Returns:
            bool
        """
        number_of_fulfilling_values = 0
        for i in range(len(values)):
            if self.target_statement.is_fulfilled_by_iri_value(
                    values[i], ancestor_values[i]):
                number_of_fulfilling_values += 1

        return self.is_restriction_fulfilled(number_of_fulfilling_values,
                                             len(values))

    def is_fulfilled_with_values(self, vocabulary: 'Vocabulary',
                                 values: List[str]) -> bool:
        """Test if a set of values fulfills the rules of the relation.
        Used if property is a data property

        Args:
            vocabulary (Vocabulary): Vocabulary of the project
            values (List[str]):  List of values to check

        Returns:
            bool
        """
        number_of_fulfilling_values = 0

        for i in range(len(values)):
            if self.target_statement.is_fulfilled_by_data_value(values[i],
                                                                vocabulary):
                number_of_fulfilling_values += 1

        return self.is_restriction_fulfilled(number_of_fulfilling_values,
                                             len(values))

    def get_all_possible_target_class_iris(self, vocabulary: 'Vocabulary') \
            -> Set[str]:
        """Get a set of class iris that are possible values for an
        objectRelation

        Args:
            vocabulary (Vocabulary): Vocabulary of this project

        Returns:
            Set[str]: class_iris
        """

        # if the relation is of type value it only defines that this relation
        # has the given values
        # not that it could have some more
        if self.restriction_type == RestrictionType.value:
            return set()

        possible_class_iris = set()
        targets = self.get_targets()
        for target_list in targets:
            for class_ in vocabulary.get_classes():
                if class_.is_child_of_all_classes(target_list):
                    possible_class_iris.add(class_.iri)
                    children = vocabulary.get_class_by_iri(class_.iri).\
                        child_class_iris
                    possible_class_iris.update(children)

        return possible_class_iris

    def get_possible_enum_target_values(self, vocabulary: 'Vocabulary') -> \
            List[str]:
        """Get all allowed enum target values for a data relation

        Args:
            vocabulary (Vocabulary): Vocabulary of this project

        Returns:
            List[str]
        """
        targets: List[List[str]] = self.target_statement.get_all_targets()

        from .vocabulary import IdType
        # methode only makes sense for data relations
        if not vocabulary.is_id_of_type(self.property_iri,
                                        IdType.data_property):
            return []

        res = []
        # as it is a datarelation the targets should only contain single lists,
        # to be flexible with changes we loop also
        # these lists
        for list in targets:
            for entry_iri in list:
                if vocabulary.is_id_of_type(entry_iri, IdType.datatype):
                    datatype = vocabulary.get_datatype(entry_iri)
                    res.extend(datatype.enum_values)

        return res

    def get_all_target_iris(self):
        iris = set()

        statements = [self.target_statement]

        while len(statements) > 0:
            statement = statements.pop()
            if statement.type == StatementType.LEAF:
                if not statement.target_iri == "":
                    iris.add(statement.target_iri)
            else:
                statements.extend(statement.target_statements)

        return iris

    def export_rule(self, vocabulary: 'Vocabulary') -> (str, str):
        # replace the iris in the target string with class labels
        targets = []
        for inner_list in self.get_targets():
            new_list = []
            targets.append(new_list)
            for iri in inner_list:
                new_list.append(vocabulary.get_label_for_entity_iri(iri))

        if (int)(self.restriction_cardinality) > 0:
            return f'"{self.restriction_type.value}|' \
                   f'{self.restriction_cardinality}"', targets
        else:
            return f'"{self.restriction_type.value}"', targets

