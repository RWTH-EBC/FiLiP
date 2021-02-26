import unittest
from core.simple_query_language import Statement, Operator, create_query


class TestContextBroker(unittest.TestCase):
    def setUp(self) -> None:
        self.left_hand_side = 'attr'
        self.numeric_right_hand_side = 20
        self.string_right_hand_side = "'20'"

    def test_statements(self):
        for op in list(Operator):
            Statement(self.left_hand_side, op, self.numeric_right_hand_side)
            if op not in [Operator.EQUAL,
                          Operator.UNEQUAL,
                          Operator.MATCH_PATTERN]:
                self.assertRaises(ValueError, Statement, self.left_hand_side,
                                op, self.string_right_hand_side)

    def test_create_query_string(self):
        test_query_string = ''
        test_statements = []
        test_tuples = []
        for op in Operator.list():
            statement_string = ''.join([self.left_hand_side, op,
                                      str(self.numeric_right_hand_side)])
            test_query_string = ';'.join([test_query_string, statement_string])

            test_statements.append(
                Statement(
                    self.left_hand_side, op, self.numeric_right_hand_side)
            )
            test_tuples.append(
                (self.left_hand_side, op, self.numeric_right_hand_side)
            )
        test_query_string = test_query_string.strip(';')

        # The implementation does not maintain order of statements.
        # Hence we compare sets.
        set_from_string = set(test_query_string.split(';'))
        set_from_statements = set(create_query(test_statements).split(';'))
        set_from_tuples = set(create_query(test_tuples).split(';'))
        self.assertEqual(set_from_string, set_from_statements)
        self.assertEqual(set_from_string, set_from_tuples)
