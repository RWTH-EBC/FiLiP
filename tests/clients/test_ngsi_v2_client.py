"""
Test for filip.core.client
"""
import unittest
import requests
import json
from pathlib import Path
from filip.models.base import FiwareHeader
from filip.clients.ngsi_v2.client import Client


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
        self.fh = FiwareHeader(service='filip',
                               service_path='/testing')
        with open("test_ngsi_v2_client.json") as f:
            self.config = json.load(f)

    def _test_change_of_headers(self, client: Client):
        """
        Test changes in fiware headers
        Args:
            client (Client): Client under test
        Returns:
            None
        """
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
        print(client.headers)

        client.fiware_service_path = '/someOther'
        self.assertEqual(client.fiware_service_path,
                         client.cb.fiware_service_path,
                         'FIWARE Service path out of sync')
        self.assertEqual(client.fiware_service_path,
                         client.iota.fiware_service_path,
                         'FIWARE Service path out of sync')
        self.assertEqual(client.fiware_service_path,
                         client.timeseries.fiware_service_path,
                         'FIWARE Service path out of sync')
        print(client.headers)

    def _test_connections(self, client: Client):
        """
        Test connections of sub clients
        Args:
            client (Client): Client under test
        Returns:
            None
        """
        client.cb.get_version()
        client.iota.get_version()
        client.timeseries.get_version()

    def test_config_dict(self):
        client = Client(config=self.config, fiware_header=self.fh)
        self._test_connections(client=client)
        self._test_change_of_headers(client=client)

    def test_config_json(self):
        """
        Test with configuration with json-file
        Returns:

        """
        config_path = Path("test_ngsi_v2_client.json")
        client = Client(config=config_path, fiware_header=self.fh)
        self._test_connections(client=client)
        self._test_change_of_headers(client=client)

    def test_config_env(self):
        """
        Test configuration using .env.filip or environment variables the
        latter is handled in core.config
        Returns:
            None
        """
        client = Client(fiware_header=self.fh)
        self._test_connections(client=client)
        self._test_change_of_headers(client=client)

    def test_session_handling(self):
        """
        Test session handling for performance boost and credential handling
        Returns:
            None
        """
        # with new session object
        with Client(config=self.config,
                    fiware_header=self.fh) as client:
            self.assertIsNotNone(client.session)
            self._test_connections(client=client)
            self._test_change_of_headers(client=client)

        # with external session
        with requests.Session() as s:
            client = Client(config=self.config,
                            session=s,
                            fiware_header=self.fh)
            self.assertEqual(client.session, s)
            self._test_connections(client=client)
            self._test_change_of_headers(client=client)

        # with external session but unnecessary 'with'-statement
        with requests.Session() as s:
            with Client(config=self.config,
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
