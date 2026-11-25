import unittest
from filip.utils.simple_ql import QueryStatement, Operator, QueryString


class TestContextBroker(unittest.TestCase):

    def setUp(self) -> None:
        self.left_hand_side = "attr"
        self.numeric_right_hand_side = 20

    def test_simple_query(self):
        # create queries for testing
        test_query_string = ""
        test_statements = []
        test_tuples = []
        for op in Operator.list():
            statement_string = "".join(
                [self.left_hand_side, op, str(self.numeric_right_hand_side)]
            )
            test_query_string = ";".join([test_query_string, statement_string])

            test_statements.append(
                QueryStatement(self.left_hand_side, op, self.numeric_right_hand_side)
            )
            test_tuples.append((self.left_hand_side, op, self.numeric_right_hand_side))
        test_query_string = test_query_string.strip(";")

        query_from_statements = QueryString(qs=test_statements)
        query_from_tuples = QueryString(qs=test_tuples)
        query_from_string = QueryString.parse_str(test_query_string)

        # Test string conversion
        self.assertEqual(str(query_from_statements), query_from_statements.to_str())
        self.assertEqual(str(query_from_tuples), query_from_tuples.to_str())
        self.assertEqual(str(query_from_string), query_from_string.to_str())

        # The implementation does not maintain order of statements.
        # Hence we compare sets of the different Methods.
        set_from_test_string = set(test_query_string.split(";"))
        set_from_statements = set(str(query_from_statements).split(";"))
        set_from_tuples = set(str(query_from_tuples).split(";"))
        set_from_string = set(str(query_from_string).split(";"))
        self.assertEqual(set_from_test_string, set_from_statements)
        self.assertEqual(set_from_test_string, set_from_tuples)
        self.assertEqual(set_from_test_string, set_from_string)

    def test_parse_roundtrip(self):
        """
        Test that only plain-digit values are converted to numbers. Values
        like "1e5", "Infinity" or "1_000" must remain strings so that
        parsing and string conversion are inverse operations.
        """
        for statement in [
            "attr==1e5",
            "attr==Infinity",
            "attr==1_000",
            "attr==44.5",
            "attr==-5",
            "attr==nan",
        ]:
            self.assertEqual(str(QueryStatement.parse_str(statement)), statement)

    def test_parse_invalid_statements(self):
        """
        Test that malformed statements are rejected with a ValueError
        instead of being parsed into a wrong query.
        """
        for statement in [
            "attr",
            "==20",
            "attr==",
            "attr == 20",
            "attr==a b",
            "attr.==1",
            "a==1==2",
        ]:
            with self.assertRaises(ValueError):
                QueryStatement.parse_str(statement)

    def test_parse_special_field_names(self):
        """
        Test that attribute names may contain special characters as long as
        each of them is followed by a word character.
        """
        statement = QueryStatement.parse_str("attr:x>=1")
        self.assertEqual(tuple(statement), ("attr:x", ">=", 1))

    def test_parse_long_invalid_input(self):
        """
        Test that parsing an invalid statement terminates quickly regardless
        of the input length. This guards against catastrophic backtracking
        in the regular expression of QueryStatement.parse_str.
        """
        with self.assertRaises(ValueError):
            QueryStatement.parse_str("a" * 5000 + "!")
