from typing import List, Any, Tuple, Dict

from filip.models import FiwareHeader
from pydantic import BaseModel
from pydantic.dataclasses import dataclass


@dataclass
class Relationship(list):

    rule: str
    _rules: Tuple[str, List[List]]
    _model_catalogue: Dict[str, type]

    def validate(self) -> bool:
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
                        if isinstance(v, self._model_catalogue[c]):
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

    def __init__(self, rule, _rules):
        super().__init__()
        self.rule = rule
        self._rules = _rules

    def __str__(self):
        return str([item for item in self])


class SemanticClass(BaseModel):

    def save(self, fiware_header: FiwareHeader, model_catalogue: Dict[str, type]):
        pass


class SemanticIndividual(SemanticClass):

    @staticmethod
    def _validate(values: List[Any], rules: Tuple[str, List[List]]):
        assert False, "Object is an instance, Instances are valueless"
