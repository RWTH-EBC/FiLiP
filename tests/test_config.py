"""
Test module for configuration functions

created: 1st April, 2021

@author Thomas Storek
"""
import os
import unittest
from filip.config import Settings


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

        for key, value in self.settings_parsing.dict().items():
            os.environ[key] = value
        self.settings_dotenv = Settings()

    def test_load_dotenv(self):
        """
        Tests loading form dotenv file

        Returns:
            None
        """
        self.assertEqual(self.settings_parsing.IOTA_URL, "http://myHost:4041")
        self.assertEqual(self.settings_parsing.CB_URL, "http://myHost:1026")
        self.assertEqual(self.settings_parsing.QL_URL, "http://myHost:8668")

    def test_example_dotenv(self):
        """
        Tests to parse settings

        Returns:
            None
        """
        self.assertEqual(self.settings_parsing, self.settings_dotenv)

    def tearDown(self) -> None:
        for k in self.settings_parsing.dict().keys():
            del os.environ[k]
