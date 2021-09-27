from typing import List, Any, Tuple

from pydantic import BaseModel
from pydantic.dataclasses import dataclass


@dataclass
class Relationship(List):

    rule: str
    _rules: Tuple[str, List[List]]
    _models_path = "D:/Git Projects/FiLiP/tests/semantic/models.py"

    def validate(self):
        # rule has form: STATEMENT, [[a,b],[c],[a,..],..]
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

        values = self

        for rule in self._rules:
            statement: str = rule[0]
            outer_class_list: List[List] = rule[1]

            fulfilling_values = 0

            for v in values:

                # A value fulfills the rule if it is an instance of all the
                # classes listed in at least one innerlist
                fulfilled = False
                for inner_class_list in outer_class_list:
                    for c in inner_class_list:
                        print(c)
                        print(self.__class__)

                        print(eval("Class1"))
                        counter = 0
                        end = str(v.__class__).split(".")[1]
                        if end[:end.find("'")] == c:
                            counter += 1

                        if len(inner_class_list) == counter:
                            fulfilled = True

                if fulfilled:
                    fulfilling_values += 1

            # test if rule is failed, else it is passed
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

        # no rule failed -> field fulfilled
        return True

    def __init__(self, rule, _rules):
        super().__init__()
        self.rule = rule
        self._rules = _rules

    def __str__(self):
        return str([item for item in self])

class SemanticClass(BaseModel):

    # _inheritance_dict: Dict[str, str] =
    pass

class SemanticIndividual(SemanticClass):

    @staticmethod
    def _validate(values: List[Any], rules: Tuple[str, List[List]]):
        assert False, "Object is an instance, Instances are valueless"
