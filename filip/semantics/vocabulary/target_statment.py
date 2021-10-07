from enum import Enum
from typing import ForwardRef, List, TYPE_CHECKING

from pydantic import BaseModel
if TYPE_CHECKING:
    from . import Vocabulary,IdType


class StatementType(str, Enum):
    """
    A statement is either a leaf and holds an iri/label or it is a combination
    of leafs with or / and
    """
    OR = 'or'
    AND = 'and'
    LEAF = 'leaf'


# TargetStatement = ForwardRef('TargetStatement')
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

    target_data_value: str = None
    """Holds the value if the relation is a hasValue (LEAF only)"""
    target_iri: str = ""
    """The IRI of the target (LEAF only)"""
    target_statements: List['TargetStatement'] = []
    """The targetstatements that are combined with this targetstatement 
     (and/or only)"""
    type: StatementType = StatementType.LEAF
    """Statement types"""

    def set_target(self, target_iri: str, target_data_value:str = None):
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
                # for each _list li we fill the i-th position of all results

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
                for c in range(number_of_entries):
                    result.append([])

                for i in range(0, len(collection)):
                    mod = 1
                    for j in range(i+1, len(lengths)):
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

    def is_fulfilled_by_iri_value(self, value: str, ancestor_values: List[str])\
            -> bool:
        """Test if a set of values fulfills the targetstatement;
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

    def is_fulfilled_by_data_value(self, value: str, vocabulary: 'Vocabulary')\
            -> bool:
        """Test if a set of values fulfills the targetstatement;
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

    def get_dependency_statements(self, vocabulary: 'Vocabulary',
                                  ontology_iri: str, class_iri: str):
        """ Get a _list of all pointers/iris that are not contained in the
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
        if self.type == StatementType.LEAF:

            # if we have a given data value, we do not have an iri
            if self.target_data_value is None:
                # check if predefined datatype
                if not vocabulary.iri_is_predefined_datatype(self.target_iri):
                    found = self.target_iri in vocabulary.classes or \
                            self.target_iri in vocabulary.datatypes or \
                            self.target_iri in vocabulary.individuals
                    statements.append({"type": "Relation Target",
                                       "class": class_iri,
                                       "dependency": self.target_iri,
                                       "fulfilled": found})
        else:
            for target_statement in self.target_statements:
                statements.extend(
                    target_statement.get_dependency_statements(
                        vocabulary, ontology_iri, class_iri))
        return statements

# target_statements is a forward reference, so that the class can refer to
# itself this forward reference need to be resolved after the class has fully
# loaded
TargetStatement.update_forward_refs()

