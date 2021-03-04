import itertools
import regex as re
from json import JSONEncoder
from aenum import Enum
from typing import Union, List, Tuple, Set
from pydantic import BaseModel, Field, validator

"""
The Simple Query Language provides a simplified syntax to retrieve entities
which match a set of conditions. A query is composed by a list of
statements separated by the ';' character. Each statement expresses a
matching condition. The query returns all the entities that match all
the matching conditions (AND logical operator).

For further details of the language please refer to:

http://telefonicaid.github.io/fiware-orion/api/v2/stable/
"""


class Operator(str, Enum):
    """
    The list of operators (and the format of the values they use) is as follows:
    """
    _init_ = 'value __doc__'

    EQUAL = '==', "Single element, e.g. temperature!=41. For an entity to " \
                  "match, it must contain the target property (temperature) " \
                  "and the target property value must not be the query value " \
                  "(41). " \
                  "A list of comma-separated values, e.g. color!=black," \
                  "red. For an entity to match, it must contain the target " \
                  "property and the target property value must not be any of " \
                  "the values in the list (AND clause) (or not include any of " \
                  "the values in the list in case the target property value " \
                  "is an array). Eg. entities whose attribute color is set to " \
                  "black will not match, while entities whose attribute color " \
                  "is set to white will match." \
                  "A range, specified as a minimum and maximum separated by " \
                  ".., e.g. temperature!=10..20. For an entity to match, " \
                  "it must contain the target property (temperature) and the " \
                  "target property value must not be between the upper and " \
                  "lower limits (both included). Ranges can only be used with " \
                  "elements target properties that represent dates (in " \
                  "ISO8601 format), numbers or strings. "
    UNEQUAL = '!=', "Single element, e.g. temperature!=41. For an entity to " \
                    "match, it must contain the target property (temperature) " \
                    "and the target property value must not be the query " \
                    "value (41). A list of comma-separated values, " \
                    "e.g. color!=black,red. For an entity to match, it must " \
                    "contain the target property and the target property " \
                    "value must not be any of the values in the list (AND " \
                    "clause) (or not include any of the values in the list in " \
                    "case the target property value is an array). Eg. " \
                    "entities whose attribute color is set to black will not " \
                    "match, while entities whose attribute color is set to " \
                    "white will match. A range, specified as a minimum and " \
                    "maximum separated by .., e.g. temperature!=10..20. For " \
                    "an entity to match, it must contain the target property " \
                    "(temperature) and the target property value must not be " \
                    "between the upper and lower limits (both included). " \
                    "Ranges can only be used with elements target properties " \
                    "that represent dates (in ISO8601 format), numbers or " \
                    "strings. "
    GREATER_THAN = '>', "The right-hand side must be a single element, e.g. " \
                        "temperature>42. For an entity to match, it must " \
                        "contain the target property (temperature) and the " \
                        "target property value must be strictly greater than " \
                        "the query value (42). This operation is only valid " \
                        "for target properties of type date, number or string " \
                        "(used with target properties of other types may lead " \
                        "to unpredictable results). "
    LESS_THAN = '<', "The right-hand side must be a single element, e.g. " \
                     "temperature<43. For an entity to match, it must contain " \
                     "the target property (temperature) and the target " \
                     "property value must be strictly less than the value (" \
                     "43). This operation is only valid for target properties " \
                     "of type date, number or string (used with target " \
                     "properties of other types may lead to unpredictable " \
                     "results). "
    GREATER_OR_EQUAL = '>=', "The right-hand side must be a single element, " \
                             "e.g. temperature>=44. For an entity to match, " \
                             "it must contain the target property (" \
                             "temperature) and the target property value must " \
                             "be greater than or equal to that value (44). " \
                             "This operation is only valid for target " \
                             "properties of type date, number or string (used " \
                             "with target properties of other types may lead " \
                             "to unpredictable results). "
    LESS_OR_EQUAL = '<=', "The right-hand side must be a single element, " \
                          "e.g. temperature<=45. For an entity to match, " \
                          "it must contain the target property (temperature) " \
                          "and the target property value must be less than or " \
                          "equal to that value (45). This operation is only " \
                          "valid for target properties of type date, number " \
                          "or string (used with target properties of other " \
                          "types may lead to unpredictable results). "
    MATCH_PATTERN = '~=', "The value matches a given pattern, expressed as a " \
                          "regular expression, e.g. color~=ow. For an entity " \
                          "to match, it must contain the target property (" \
                          "color) and the target property value must match the " \
                          "string in the right-hand side, 'ow' in this example " \
                          "(brown and yellow would match, black and white " \
                          "would not). This operation is only valid for target " \
                          "properties of type string. "

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class Statement(tuple):
    """
    Query statement for simple query language
    """
    # Todo: Make Statements serializable
    def __new__(self, left_hand_side: str,
                operator: str,
                right_hand_side: Union[str, float, int]):
        assert operator in list(Operator), f"No valid operator string. String " \
                                           f"must be one of the following: " \
                                           f"{Operator.list()}"
        if operator not in [Operator.EQUAL,
                            Operator.UNEQUAL,
                            Operator.MATCH_PATTERN]:
            try:
                float(right_hand_side)
            except ValueError as e:
                e.args += ("Combination of operator and right hand side "
                           "is not allowed", )
                raise
        return tuple.__new__(Statement,
                             (left_hand_side, operator, right_hand_side))

    def __str__(self):
        return ''.join([str(item) for item in self])




class SimpleQuery(BaseModel):
    """
    Represents a simple query object that can handed to a request for
    filtering responses.
    """
    statements: Set[Statement] = Field(
        title="Statements",
        description="List of simple query statement")

    def __init__(self, statements:
        Union[
          List[Union[Statement, Tuple[str, str, Union[str, float, int]]]],
          Set[Union[Statement, Tuple[str, str, Union[str, float, int]]]]]):
        statements = self.validate_statements(statements)
        super().__init__(statements=statements)

    @validator('statements')
    def validate_statements(cls, statements):
        if not isinstance(statements, (list, set)):
            statements = [statements]
        for idx, statement in enumerate(statements):
            if not isinstance(statement, Statement):
                statements[idx] = Statement(*statement)
        return set(statements)

    def __str__(self):
        return self.str()

    def __repr__(self):
        return f'{super().__repr_name__()}({super().__repr_str__(", ")})'

    def str(self):
        return ';'.join([str(statement) for statement in self.statements])

    @classmethod
    def parse_str(cls, query_string: str):
        query_parts = query_string.split(';')
        statements = set()
        for part, op in itertools.product(query_parts, Operator.list()):
            if re.search(f"^[\w]*{op}+[\w]", part):
                args =part.split(op)
                if len(args) == 2:
                    statements.add(Statement(args[0], op, args[1]))
                else:
                    raise ValueError
        return cls(statements=statements)
