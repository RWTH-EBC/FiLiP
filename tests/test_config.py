"""
Test module for configuration functions
"""
import os
import unittest
from filip.config import Settings
import json
from pydantic import AnyHttpUrl


class TestSettings(unittest.TestCase):
    """
    Test case for loading settings
    """
    def setUp(self) -> None:

        # Test if the testcase was run directly or over in a global test-run.
        # Match the needed path to the config file in both cases
        if os.getcwd().split("\\")[-1] == "tests":
            self.settings_parsing = Settings(_env_file='test_config.env')
        else:
            self.settings_parsing = \
                Settings(_env_file='./tests/test_config.env')

        for key, value in json.loads(self.settings_parsing.model_dump_json()).items():
            os.environ[key] = value
        self.settings_dotenv = Settings()

    def test_load_dotenv(self):
        """
        Tests loading form dotenv file

        Returns:
            None
        """
        self.assertEqual(str(self.settings_parsing.IOTA_URL), str(AnyHttpUrl("http://myHost:4041/")))
        self.assertEqual(str(self.settings_parsing.CB_URL), str(AnyHttpUrl("http://myHost:1026/")))
        self.assertEqual(str(self.settings_parsing.QL_URL), str(AnyHttpUrl("http://myHost:8668/")))

    def test_example_dotenv(self):
        """
        Tests to parse settings

        Returns:
            None
        """
        self.assertEqual(self.settings_parsing, self.settings_dotenv)

    def tearDown(self) -> None:
        for k in self.settings_parsing.model_dump().keys():
            del os.environ[k]
