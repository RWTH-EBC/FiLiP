"""
Test for filip.core.client
"""
import os
import unittest
import json
import requests

from pathlib import Path
from filip.models.base import FiwareHeader
from filip.clients.ngsi_v2.client import HttpClient

from tests.config import settings, generate_servicepath


class TestClient(unittest.TestCase):
    """
    Test case for global client
    """

    def setUp(self) -> None:
        """
        Setup test data
        Returns:
            None
        """
        self.fh = FiwareHeader(service=settings.FIWARE_SERVICE,
                               service_path=settings.FIWARE_SERVICEPATH)

        with open(self.get_json_path()) as f:
            self.config = json.load(f)

    @staticmethod
    def get_json_path() -> str:
        """
        Get the correct path to the json file needed for this test
        """

        # Test if the testcase was run directly or over in a global test-run.
        # Match the needed path to the config file in both cases
        if os.getcwd().split("\\")[-1] == "clients":
            return 'test_ngsi_v2_client.json'
        else:
            return './tests/clients/test_ngsi_v2_client.json'

    def _test_change_of_headers(self, client: HttpClient):
        """
        Test changes in fiware headers
        Args:
            client (HttpClient): Client under test
        Returns:
            None
        """
        self.assertEqual(id(client.fiware_service_path),
                         id(client.cb.fiware_service_path),
                         'FIWARE Service path out of sync')
        self.assertEqual(id(client.fiware_service_path),
                         id(client.iota.fiware_service_path),
                         'FIWARE Service path out of sync')
        self.assertEqual(id(client.fiware_service_path),
                         id(client.timeseries.fiware_service_path),
                         'FIWARE Service path out of sync')

        client.fiware_service = 'filip_other'

        self.assertEqual(client.fiware_service_path,
                         client.cb.fiware_service_path,
                         'FIWARE service out of sync')
        self.assertEqual(client.fiware_service_path,
                         client.iota.fiware_service_path,
                         'FIWARE service out of sync')
        self.assertEqual(client.fiware_service_path,
                         client.timeseries.fiware_service_path,
                         'FIWARE service out of sync')

        client.fiware_service_path = generate_servicepath()

        self.assertEqual(client.fiware_service_path,
                         client.cb.fiware_service_path,
                         'FIWARE Service path out of sync')
        self.assertEqual(client.fiware_service_path,
                         client.iota.fiware_service_path,
                         'FIWARE Service path out of sync')
        self.assertEqual(client.fiware_service_path,
                         client.timeseries.fiware_service_path,
                         'FIWARE Service path out of sync')

    def _test_connections(self, client: HttpClient):
        """
        Test connections of sub clients
        Args:
            client (HttpClient): Client under test
        Returns:
            None
        """
        client.cb.get_version()
        client.iota.get_version()
        client.timeseries.get_version()

    def test_config_dict(self):
        client = HttpClient(config=self.config, fiware_header=self.fh)
        self._test_connections(client=client)
        self._test_change_of_headers(client=client)

    def test_config_json(self):
        """
        Test with configuration with json-file
        Returns:

        """
        config_path = Path(self.get_json_path())
        client = HttpClient(config=config_path, fiware_header=self.fh)
        self._test_connections(client=client)
        self._test_change_of_headers(client=client)

    def test_config_env(self):
        """
        Test configuration using .env.filip or environment variables the
        latter is handled in core.config
        Returns:
            None
        """
        client = HttpClient(fiware_header=self.fh)
        self._test_connections(client=client)
        self._test_change_of_headers(client=client)

    def test_session_handling(self):
        """
        Test session handling for performance boost and credential handling
        Returns:
            None
        """
        # with new session object
        with HttpClient(config=self.config,
                        fiware_header=self.fh) as client:
            self.assertIsNotNone(client.session)
            self._test_connections(client=client)
            self._test_change_of_headers(client=client)

        # with external session
        with requests.Session() as s:
            client = HttpClient(config=self.config,
                                session=s,
                                fiware_header=self.fh)
            self.assertEqual(client.session, s)
            self._test_connections(client=client)
            self._test_change_of_headers(client=client)

        # with external session but unnecessary 'with'-statement
        with requests.Session() as s:
            with HttpClient(config=self.config,
                            session=s,
                            fiware_header=self.fh) as client:
                self.assertEqual(client.session, s)
                self._test_connections(client=client)
                self._test_change_of_headers(client=client)

    def tearDown(self) -> None:
        """
        Clean up artifacts
        Returns:
            None
        """
        pass
