"""Vocabulary Models for Relations"""

from typing import Set, Dict, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from . import Vocabulary

from aenum import Enum
from typing import List, TYPE_CHECKING

from pydantic import BaseModel, Field

from .source import DependencyStatement

if TYPE_CHECKING:
    from . import Vocabulary, IdType


class StatementType(str, Enum):
    """
    A statement is either a leaf and holds an iri/label or it is a combination
    of leafs with or / and
    """
    OR = 'or'
    AND = 'and'
    LEAF = 'leaf'


class TargetStatement(BaseModel):
    """
    A target statement is the statement the sits in a relation statement behind
    the restrictionType:
    E.g: consists_of some Device or Sensor.
    here Device or Sensor is the targetstatement as it sits behind "some"

    A targetstatement is build recursively: It is either a Leaf: str or a union
    (or) or an intersection(and) of targetstatements

    the combination of statements is purely logical and not numerical: device
        and device is true as soon as one device is given,
        it does not need two separate devices.
    """

    target_data_value: Optional[str] = Field(
        default=None,
        description="Holds the value if the relation is a hasValue (LEAF only)")
    target_iri: str = Field(
        default="",
        description="The IRI of the target (LEAF only)")
    target_statements: List['TargetStatement'] = Field(
        default=[],
        description="The targetstatements that are combined with this "
                    "targetstatement (and/or only)"
    )
    type: StatementType = Field(default=StatementType.LEAF,
                                description="Statement types")

    def set_target(self, target_iri: str, target_data_value: str = None):
        """ Set target for this statement and make it a LEAF statement

        Args:
            target_iri (str): iri of the target (class or datatype iri)
            target_data_value (str): Value of the targetstatment if no IRI but
             a fixed default value is given

        Returns:
            None
        """
        self.type = StatementType.LEAF
        self.target_iri = target_iri
        self.target_data_value = target_data_value

    def get_all_targets(self) -> List[List[str]]:
        """Extract possible targets out of statements
        interpretation: [[a,b], [c]]-> (a and b) or c -> the target needs to
        have ancestors(or be): (both a anb b) or c

        items inside the inner brackets are connected via and the innerbrackets
        are all connect over or

        Returns:
            List[List[str]]
        """
        if self.type == StatementType.LEAF:
            if self.target_data_value is not None:
                return [[]]
            else:
                return [[self.target_iri]]
        else:
            collection = []  # form: [ [[]], [[],[]], ..]
            for statement in self.target_statements:
                collection.append(statement.get_all_targets())

            if self.type == StatementType.OR:
                result = []
                for sublist in collection:  # sublist form: [[],[],...]
                    result.extend(sublist)
                return result

            else:  # AND
                # with and we distribute our lists
                # example: col= [ [[1],[2]], [[3,4]] ] => [[1,3,4], [2,3,4]]
                # we build the results in an all in one way, we compute the
                # number of entries in the final solution
                # for each list li we fill the i-th position of all results

                # example: col= [ [[a,b]], [[c],[d]] , [[e],[f]] ] =>
                # statement: (a and b) and (c or d) and (e or f)
                # 0 : res = [[], [], [], []]
                # 1 : res = [[a,b], [a,b], [a,b], [a,b]]
                # 2 : res = [[a,b,c], [a,b,c], [a,b,d], [a,b,d]]
                # 3 : res = [[a,b,c,e], [a,b,c,f], [a,b,d,e], [a,b,d,f]]

                result = []  # result form: [[],[],...]
                lengths = []
                number_of_entries = 1
                for sublist in collection:  # sublist form: [[],[],...]
                    number_of_entries = number_of_entries * len(sublist)
                    lengths.append(len(sublist))

                # init with empty lists
                for empty in range(number_of_entries):
                    result.append([])

                for i in range(0, len(collection)):
                    mod = 1
                    for j in range(i + 1, len(lengths)):
                        mod = mod * lengths[j]

                    counter = 0
                    while counter < number_of_entries:
                        for sublist in collection[i]:
                            for entry in sublist:
                                for j in range(mod):
                                    result[counter].append(entry)
                                    counter += 1
                return result

    def to_string(self, vocabulary: 'Vocabulary') -> str:
        """Get a string representation of the targetstatment

        Args:
            vocabulary (Vocabulary): vocabulary of the project

        Returns:
            str
        """

        if self.type == StatementType.LEAF:
            label = self.retrieve_label(vocabulary)
            if label == "":
                return self.target_iri
            return label
        else:
            result = "(" + self.target_statements[0].to_string(vocabulary)
            for statement in self.target_statements[1:]:
                result += " " + self.type + " "
                result += statement.to_string(vocabulary) + ")"

            return result

    def is_fulfilled_by_iri_value(self, value: str, ancestor_values: List[str]) \
            -> bool:
        """
        Test if a set of values fulfills the targetstatement;
        Only for objectRelations

        Args:
            value (str): value to check: Class_iri of instance/individual
            ancestor_values(List[List[str]]): List containing the ancestors iris
                for each value (linked over index)
        Returns:
            bool
        """

        targets = self.get_all_targets()

        values = ancestor_values
        values.append(value)

        # one sublist of targets needs to be fulfilled targets:
        # [(a and b) or c or (d and a),....]
        for sublist in targets:
            sublist_fulfilled = True
            for item in sublist:
                if item not in values:
                    sublist_fulfilled = False

            if sublist_fulfilled:
                return True
        return False

    def is_fulfilled_by_data_value(self, value: str, vocabulary: 'Vocabulary') \
            -> bool:
        """
        Test if a set of values fulfills the targetstatement;
        Only for dataRelations

        Args:
            value (List[str]):  value to check
            vocabulary (Vocabulary)
        Returns:
            bool
        """

        # a data target_statement theoraticly only has one statement
        if self.target_data_value is not None:
            return value == self.target_data_value

        from .vocabulary import IdType
        if not vocabulary.is_id_of_type(self.target_iri, IdType.datatype):
            return False
        else:
            datatype = vocabulary.get_datatype(self.target_iri)
            return datatype.value_is_valid(value)

    def retrieve_label(self, vocabulary: 'Vocabulary') -> str:
        """Get the label of the target_iri. Only logical for Leaf statements

        Args:
            vocabulary (Vocabulary): Vocabulary of the project

        Returns:
            str
        """
        if self.type == StatementType.LEAF:
            if self.target_data_value is not None:
                return self.target_data_value
            else:
                return vocabulary.get_label_for_entity_iri(self.target_iri)
        return ""

    def get_dependency_statements(
            self,
            vocabulary: 'Vocabulary',
            ontology_iri: str,
            class_iri: str) -> List[DependencyStatement]:
        """
        Get a list of all pointers/iris that are not contained in the
        vocabulary. Purging is done in class

        Args:
            vocabulary (Vocabulary): Vocabulary of this project
            ontology_iri (str): IRI of the source ontology
            class_iri (str): IRI of class (legacy)

        Returns:
            List[Dict[str, str]]: List of purged statements dicts with keys:
            Parent Class, class, dependency, fulfilled
        """
        statements = []
        if self.type == StatementType.LEAF:

            # if we have a given data value, we do not have an iri
            if self.target_data_value is None:
                # check if predefined datatype
                if not vocabulary.iri_is_predefined_datatype(self.target_iri):
                    found = self.target_iri in vocabulary.classes or \
                            self.target_iri in vocabulary.datatypes or \
                            self.target_iri in vocabulary.individuals
                    statements.append(
                        DependencyStatement(
                            type="Relation Target",
                            class_iri=class_iri,
                            dependency_iri=self.target_iri,
                            fulfilled=found)
                    )
        else:
            for target_statement in self.target_statements:
                statements.extend(
                    target_statement.get_dependency_statements(
                        vocabulary, ontology_iri, class_iri))
        return statements


# target_statements is a forward reference, so that the class can refer to
# itself this forward reference need to be resolved after the class has fully
# loaded
TargetStatement.model_rebuild()


class RestrictionType(str, Enum):
    """RestrictionTypes, as defined for OWL"""
    _init_ = 'value __doc__'

    some = 'some', 'at least 1 value of that target'
    only = 'only', 'only value of that target'
    min = 'min', 'min n values of that target'
    max = 'max', 'max n values of that target'
    exactly = 'exactly', 'exactly n values of that target'
    value = 'value', 'predefined value'


class Relation(BaseModel):
    """
    A Relation is defined in the source for a class.
    It has the form: RestrictionType property target_statement

    It defines a set of allowed/required values which each instance of this
    class can/should have under this property

    A Relation is defined in a OWL:class, but all child classes of that class
    inherit it
    """

    id: str = Field(description="Unique generated Relation ID, "
                                "for internal use")
    restriction_type: RestrictionType = Field(
        default=None,
        description="Restriction type of this relation")
    restriction_cardinality: int = Field(
        default=-1,
        description="Only needed for min, max, equaly states the 'n'")
    property_iri: str = Field(
        default="",
        description="IRI of the property (data- or object-)")
    target_statement: TargetStatement = Field(
        default=None,
        description="Complex statement which classes/datatype_catalogue "
                    "are allowed/required")

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
            -> List[DependencyStatement]:
        """ Get a list of all pointers/iris that are not contained in the
            vocabulary
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

        statements.append(DependencyStatement(type="Relation Property",
                                              class_iri=class_iri,
                                              dependency_iri=self.property_iri,
                                              fulfilled=found))

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
                    children = vocabulary.get_class_by_iri(class_.iri). \
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

    def get_all_target_iris(self) -> Set[str]:
        """Get all iris of targets

        Returns:
            Set(str)
        """
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
        """Get the rule as string

        Args:
           vocabulary (Vocabulary): Vocabulary of the project

        Returns:
           str
        """
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

