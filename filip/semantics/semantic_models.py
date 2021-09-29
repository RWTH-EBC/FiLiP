import uuid
from typing import List, Any, Tuple, Dict, Type, TypeVar, Generic

from filip.models.base import DataType

from filip.models.ngsi_v2.context import ContextEntity, NamedContextAttribute

from filip.clients.ngsi_v2 import ContextBrokerClient

from filip.models import FiwareHeader
from pydantic import BaseModel
from pydantic.dataclasses import dataclass

import abc

T = TypeVar('T')


class Field(List[T]):
    rule: str
    name: str

    def __init__(self, rule, name):
        super().__init__()

        self.rule = rule
        self.name = name

    def is_valid(self) -> bool:
        pass


class Relationship(Field[T]):
    rule: str
    _rules: List[Tuple[str, List[List[Type]]]]

    # _model_catalogue: Dict[str, type]

    def is_valid(self) -> bool:
        """
        Check if the values present in this relationship fulfill the semantic
        rule.

        returns:
            bool
        """

        # rule has form: (STATEMENT, [[a,b],[c],[a,..],..])
        # A value fulfills the rule if it is an instance of all the classes
        #       listed in at least one innerlist
        # A field is fulfilled if a number of values fulfill the rule,
        #       the number is depending on the statement

        # The STATEMENTs and their according numbers are (STATEMENT|min|max):
        #       - only | len(values) | len(values)
        #       - some | 1 | len(values)
        #       - min n | n | len(values)
        #       - max n | 0 | n
        #       - range n,m | n | m

        # the relationship itself is a list
        values = self

        # loop over all rules, if a rule is not fulfilled return False
        for rule in self._rules:
            # rule has form: (STATEMENT, [[a,b],[c],[a,..],..])
            statement: str = rule[0]
            outer_class_list: List[List] = rule[1]

            # count how  many values fulfill this rule
            fulfilling_values = 0
            for v in values:

                # A value fulfills the rule if there exists an innerlist of
                # which the value is an instance of each value
                fulfilled = False
                for inner_class_list in outer_class_list:

                    counter = 0
                    for c in inner_class_list:
                        if isinstance(v, c):
                            counter += 1

                    if len(inner_class_list) == counter:
                        fulfilled = True

                if fulfilled:
                    fulfilling_values += 1

            # test if rule failed by evaluating the statement and the
            # number of fulfilling values
            if "min" in statement:
                number = int(statement.split("|")[1])
                if not fulfilling_values >= number:
                    return False
            elif "max" in statement:
                number = int(statement.split("|")[1])
                if not fulfilling_values <= number:
                    return False
            elif "exactly" in statement:
                number = int(statement.split("|")[1])
                if not fulfilling_values == number:
                    return False
            elif "some" in statement:
                if not fulfilling_values >= 1:
                    return False
            elif "only" in statement:
                if not fulfilling_values == len(values):
                    return False
            elif "value" in statement:
                if not fulfilling_values >= 1:
                    return False

        # no rule failed -> relationship fulfilled
        return True

    def __init__(self, rule, name):
        super().__init__(rule, name)

    def __str__(self):
        return str([item for item in self])

    def build_context_attribute(self) -> NamedContextAttribute:
        return NamedContextAttribute(
            name=self.name,
            type=DataType.RELATIONSHIP,
            value=[v.id for v in self]
        )


class SemanticClass(BaseModel):
    id: str = ''
    old_state: ContextEntity = None

    def __init__(self):
        super(SemanticClass, self).__init__()
        self.id = f'{self._get_class_name()}-{uuid.uuid4().hex}'

    def are_fields_valid(self) -> bool:
        return len(self.get_invalid_fields()) == 0

    def get_invalid_fields(self) -> List[Field]:
        return [f for f in self.get_fields() if not f.is_valid()]

    def _get_class_name(self):
        return type(self).__name__

    def save(self, fiware_header: FiwareHeader, assert_validity: bool = False):

        if assert_validity:
            assert self.are_fields_valid(), \
                f"Attempted to save the SemanticEntity {self.id} of type " \
                f"{self._get_class_name()} with invalid fields " \
                f"{[f.name for f in self.get_invalid_fields()]}"

        with ContextBrokerClient(fiware_header=fiware_header) as client:
            client.patch_entity(entity=self.build_context_entity(),
                                old_entity=self.old_state)

    def get_fields(self) -> List[Field]:
        fields: List[Field] = self.get_relationships()
        # todo datafields
        return fields

    def get_relationships(self) -> List[Relationship]:
        relationships = []
        for key, value in self.__dict__.items():
            if isinstance(value, Relationship):
                rel: Relationship = value
                relationships.append(rel)
        return relationships

    def build_context_entity(self) -> ContextEntity:

        entity = ContextEntity(
            id=self.id,
            type=self._get_class_name()
        )

        for rel in self.get_relationships():
            entity.add_properties([rel.build_context_attribute()])

        # todo datafields
        return entity


class SemanticIndividual(SemanticClass):

    @staticmethod
    def _validate(values: List[Any], rules: Tuple[str, List[List]]):
        assert False, "Object is an instance, Instances are valueless"
