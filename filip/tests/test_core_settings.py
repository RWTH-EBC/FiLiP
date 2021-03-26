import unittest
from core.settings import _Settings


class TestSettings(unittest.TestCase):
    def setUp(self) -> None:
        self.settings_parsing = _Settings(_env_file='test.env')
        self.settings_dotenv = _Settings(_env_file='../../example.env')

    def test_load_dotenv(self):
        self.assertEqual(self.settings_parsing.IOTA_URL, "http://myHost:4041")
        self.assertEqual(self.settings_parsing.OCB_URL, "http://myHost:1026")
        self.assertEqual(self.settings_parsing.QL_URL, "http://myHost:8668")

    def test_example_dotenv(self):
        self.assertEqual(self.settings_parsing, self.settings_dotenv)
