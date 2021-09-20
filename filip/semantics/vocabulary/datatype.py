from enum import Enum
from typing import List, Union

from . import Entity


class DatatypeType(str, Enum):
    """
    Types of a Datatype
    """
    string = 'string'
    number = 'number'
    date = 'date'
    enum = 'enum'


class Datatype(Entity):
    """
    Represents OWL:Datatype

    A Datatype is the target of a DataRelation. The Datatype stats a set of
    values that are valid.
    This can be an ENUM, a number range, or a check for black/whitelisted chars

    In the Parsing PostProcesseor predefined datatypes are added to the
    vocabulary
    """

    type: DatatypeType = DatatypeType.string
    """Type of the datatype"""
    number_has_range = False
    """If Type==Number: Does the datatype define a range"""
    number_range_min: Union[int, str] = "/"
    """If Type==Number: Min value of the datatype range, 
        if a range is defined"""
    number_range_max: Union[int, str] = "/"
    """If Type==Number: Max value of the datatype range, 
        if a range is defined"""
    number_decimal_allowed: bool = False
    """If Type==Number: Are decimal numbers allowed?"""
    forbidden_chars: List[str] = []
    """If Type==String: Blacklisted chars"""
    allowed_chars: List[str] = []
    """If Type==String: Whitelisted chars"""
    enum_values: List[str] = []
    """If Type==Enum: Enum values"""

    def value_is_valid(self, value:str) -> bool:
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