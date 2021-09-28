from typing import List, Any, Tuple

from pydantic import BaseModel
from pydantic.dataclasses import dataclass


@dataclass
class Relationship(list):

    rule: str
    _rules: Tuple[str, List[List]]
    _module_path: str = ""

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

                        # import the classes from the module to compute the
                        # subclasses.
                        # The path to the module file is given in the
                        # constructor of the containing SemanticEntity

                        import importlib.util
                        spec = importlib.util.spec_from_file_location(
                            "models", self._module_path)
                        class_object = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(class_object)

                        # after the classes were imported, compute all possible
                        # classes that v can have
                        all_possible_classes: List[str] = eval(f'class_object'
                                                     f'.{c}.__subclasses__()')
                        all_possible_classes.\
                            append(eval(f'class_object.{c}().__class__'))

                        def extract_class_name(class_) -> str:
                            """
                            str(class_) has form: <class 'models.Class123'>
                            extract: Class123
                            """
                            second_half = str(class_).split(".")[1]
                            return second_half[:second_half.find("'")]

                        # Due to the import the classes are not completly
                        # identical for the system. We need to use string
                        # parsing to compare the class names.
                        # But due to the logic of the import there should be
                        # no side-conditions
                        all_possible_class_strings = \
                            [extract_class_name(cls) for
                             cls in all_possible_classes]

                        if extract_class_name(v.__class__) in\
                                all_possible_class_strings:
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

    # _inheritance_dict: Dict[str, str] =
    pass


class SemanticIndividual(SemanticClass):

    @staticmethod
    def _validate(values: List[Any], rules: Tuple[str, List[List]]):
        assert False, "Object is an instance, Instances are valueless"
