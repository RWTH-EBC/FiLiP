import os
import unittest
from filip.config import Settings


class TestSettings(unittest.TestCase):
    def setUp(self) -> None:
        self.settings_parsing = Settings(_env_file='test_config.env')
        for k, v in self.settings_parsing.dict().items():
            os.environ[k] = v
        self.settings_dotenv = Settings()

    def test_load_dotenv(self):
        self.assertEqual(self.settings_parsing.IOTA_URL, "http://myHost:4041")
        self.assertEqual(self.settings_parsing.CB_URL, "http://myHost:1026")
        self.assertEqual(self.settings_parsing.QL_URL, "http://myHost:8668")

    def test_example_dotenv(self):
        self.assertEqual(self.settings_parsing, self.settings_dotenv)

    def tearDown(self) -> None:
        for k in self.settings_parsing.dict().keys():
            del os.environ[k]
