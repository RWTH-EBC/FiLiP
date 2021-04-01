import unittest
from filip.core.simple_query_language import \
    Statement, \
    Operator, \
    SimpleQuery


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

    def test_simple_query(self):
        # create queries for testing
        test_query_string = ''
        test_statements = []
        test_tuples = []
        for op in Operator.list():
            statement_string = ''.join(
                [self.left_hand_side, op, str(self.numeric_right_hand_side)])
            test_query_string = ';'.join([test_query_string, statement_string])

            test_statements.append(
                Statement(self.left_hand_side, op, self.numeric_right_hand_side)
            )
            test_tuples.append(
                (self.left_hand_side, op, self.numeric_right_hand_side)
            )
        test_query_string = test_query_string.strip(';')

        query_from_statements = SimpleQuery(statements=test_statements)
        print(query_from_statements.json(indent=2))

        query_from_tuples = SimpleQuery(statements=test_tuples)
        query_from_string = SimpleQuery.parse_str(test_query_string)

        # Test string conversion
        self.assertEqual(str(query_from_statements),
                         query_from_statements.str())
        self.assertEqual(str(query_from_tuples), query_from_tuples.str())
        self.assertEqual(str(query_from_string), query_from_string.str())

        # The implementation does not maintain order of statements.
        # Hence we compare sets of the different Methods.
        set_from_test_string = set(test_query_string.split(';'))
        set_from_statements = set(str(query_from_statements).split(';'))
        set_from_tuples = set(str(query_from_tuples).split(';'))
        set_from_string = set(str(query_from_string).split(';'))
        self.assertEqual(set_from_test_string, set_from_statements)
        self.assertEqual(set_from_test_string, set_from_tuples)
        self.assertEqual(set_from_test_string, set_from_string)
