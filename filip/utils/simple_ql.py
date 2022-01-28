"""
The Simple Query Language provides a simplified syntax to retrieve entities
which match a set of conditions. A query is composed by a list of
statements separated by the ';' character. Each statement expresses a
matching condition. The query returns all the entities that match all
the matching conditions (AND logical operator).

For further details of the language please refer to:

https://telefonicaid.github.io/fiware-orion/api/v2/stable/
"""
import regex as re
from aenum import Enum
from typing import Union, List, Tuple, Any


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
                  "property and the target property value must not be any " \
                  "of the values in the list (AND clause) (or not include any "\
                  "of the values in the list in case the target property " \
                  "value is an array). Eg. entities whose attribute color is " \
                  "set to black will not match, while entities whose " \
                  "attribute color is set to white will match." \
                  "A range, specified as a minimum and maximum separated by " \
                  ".., e.g. temperature!=10..20. For an entity to match, " \
                  "it must contain the target property (temperature) and the " \
                  "target property value must not be between the upper and " \
                  "lower limits (both included). Ranges can only be used " \
                  "with elements target properties that represent dates (in " \
                  "ISO8601 format), numbers or strings. "
    UNEQUAL = '!=', "Single element, e.g. temperature!=41. For an entity to " \
                    "match, it must contain the target property " \
                    "(temperature) and the target property value must not be " \
                    "the query value (41). A list of comma-separated values, " \
                    "e.g. color!=black,red. For an entity to match, it must " \
                    "contain the target property and the target property " \
                    "value must not be any of the values in the list (AND " \
                    "clause) (or not include any of the values in the list " \
                    "in case the target property value is an array). Eg. " \
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
                        "for target properties of type date, number or " \
                        "string (used with target properties of other types " \
                        "may lead to unpredictable results). "
    LESS_THAN = '<', "The right-hand side must be a single element, e.g. " \
                     "temperature<43. For an entity to match, it must " \
                     "contain the target property (temperature) and the " \
                     "target property value must be strictly less than the " \
                     "value (43). This operation is only valid for target " \
                     "properties of type date, number or string (used with " \
                     "target properties of other types may lead to " \
                     "unpredictable results). "
    GREATER_OR_EQUAL = '>=', "The right-hand side must be a single element, " \
                             "e.g. temperature>=44. For an entity to match, " \
                             "it must contain the target property (" \
                             "temperature) and the target property value " \
                             "must be greater than or equal to that value " \
                             "(44). This operation is only valid for target " \
                             "properties of type date, number or string " \
                             "(used with target properties of other types " \
                             "may lead to unpredictable results). "
    LESS_OR_EQUAL = '<=', "The right-hand side must be a single element, " \
                          "e.g. temperature<=45. For an entity to match, " \
                          "it must contain the target property (temperature) " \
                          "and the target property value must be less than " \
                          "or equal to that value (45). This operation is " \
                          "only valid for target properties of type date, " \
                          "number or string (used with target properties of " \
                          "other types may lead to unpredictable results). "
    MATCH_PATTERN = '~=', "The value matches a given pattern, expressed as a " \
                          "regular expression, e.g. color~=ow. For an entity " \
                          "to match, it must contain the target property (" \
                          "color) and the target property value must match " \
                          "the string in the right-hand side, 'ow' in this " \
                          "example (brown and yellow would match, black and " \
                          "white would not). This operation is only valid " \
                          "for target properties of type string. "

    @classmethod
    def list(cls):
        """

        Returns:
            list of all valid values
        """
        return list(map(lambda c: c.value, cls))


class QueryStatement(Tuple):
    """
    Simple query statement
    """

    def __new__(cls, left: str, op: Union[str, Operator], right: Any):
        q = tuple.__new__(QueryStatement, (left, op, right))
        q = cls.validate(q)
        return q

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        """
        Validates statements

        Args:
            value:

        Returns:
        """
        if isinstance(value, (tuple, QueryStatement)):
            if len(value) != 3:
                raise TypeError('3-tuple required')
            if not isinstance(value[0], str):
                raise TypeError('First argument must be a string!')
            if value[1] not in Operator.list():
                raise TypeError('Invalid comparison operator!')
            if value[1] not in [Operator.EQUAL,
                                Operator.UNEQUAL,
                                Operator.MATCH_PATTERN]:
                try:
                    float(value[2])
                except ValueError as err:
                    err.args += ("Invalid combination of operator and right "
                                 "hand side!",)
                    raise
            return value
        elif isinstance(value, str):
            return cls.parse_str(value)
        raise TypeError

    def to_str(self):
        """
        Parses QueryStatement to String

        Returns:
            String
        """
        if not isinstance(self[2], str):
            right = str(self[2])
        elif self[2].isnumeric():
            right = f"{self[2]}"
        else:
            right = self[2]
        return ''.join([self[0], self[1], right])

    @classmethod
    def parse_str(cls, string: str):
        """
        Generates QueryStatement form string

        Args:
            string:

        Returns:
            QueryStatement
        """
        for op in Operator.list():
            if re.fullmatch(rf"^\w((\w|[^&,?,/,#,\*,\s]\w)?)*{op}\w+$", string):
                args = string.split(op)
                if len(args) == 2:
                    if args[1].isnumeric():
                        try:
                            right = int(args[1])
                        except ValueError:
                            right = float(args[1])
                        return QueryStatement(args[0], op, right)
                    return QueryStatement(args[0], op, args[1])
                raise ValueError

    def __str__(self):
        """ Return str(self). """
        return self.to_str()

    def __repr__(self):
        """ Return repr(self). """
        return self.to_str().__repr__()


class QueryString:
    """
    Class for validated QueryStrings that can be used in api clients
    """
    def __init__(self, qs: Union[Tuple,
                                 QueryStatement,
                                 List[Union[QueryStatement, Tuple]]]):
        qs = self.__check_arguments(qs=qs)
        self._qs = qs

    @classmethod
    def __check_arguments(cls, qs):
        """
        Check arguments on consistency

        Args:
            qs: queny statement object

        returns:
            List of QueryStatements
        """
        if isinstance(qs, List):
            for idx, item in enumerate(qs):
                if not isinstance(item, QueryStatement):
                    qs[idx] = QueryStatement(*item)
            # Remove duplicates
            qs = list(dict.fromkeys(qs))
        elif isinstance(qs, QueryStatement):
            qs = [qs]
        elif isinstance(qs, tuple):
            qs = [QueryStatement(*qs)]
        else:
            raise ValueError('Invalid argument!')
        return qs

    def update(self, qs: Union[Tuple, QueryStatement, List[QueryStatement]]):
        """
        Adds or updates QueryStatement within QueryString. First to arguments
        must match an existing argument for update. This redundant rules

        Args:
            qs: Query statement to add to the string object

        Returns:
            None
        """
        qs = self.__check_arguments(qs=qs)
        self._qs.extend(qs)
        self._qs = list(dict.fromkeys(qs))

    def remove(self, qs: Union[Tuple, QueryStatement, List[QueryStatement]]):
        """
        Remove Statement from QueryString
        Args:
            qs:

        Returns:

        """
        qs = self.__check_arguments(qs=qs)
        for q in qs:
            self._qs.remove(q)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        """validate QueryString"""
        if isinstance(v, QueryString):
            return v
        if isinstance(v, str):
            return cls.parse_str(v)
        raise ValueError('Invalid argument!')

    def to_str(self):
        """
        Parsing self.qs to string object

        Returns:
            String: query string that can be added to requests as parameter
        """
        return ';'.join([q.to_str() for q in self._qs])

    @classmethod
    def parse_str(cls, string: str):
        """
        Creates QueryString from string

        Args:
            string:

        Returns:
            QueryString
        """
        q_parts = string.split(';')
        qs = []
        for part in q_parts:
            q = QueryStatement.parse_str(part)
            qs.append(q)
        return QueryString(qs=qs)

    def __str__(self):
        """ Return str(self). """
        return self.to_str()

    def __repr__(self):
        """ Return repr(self). """
        return self.to_str().__repr__()
