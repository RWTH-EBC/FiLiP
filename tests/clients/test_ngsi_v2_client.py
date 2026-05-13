"""
Test for filip.core.client
"""

import unittest
import json
import requests
from unittest.mock import MagicMock
from pathlib import Path
from filip.clients.exceptions import BaseHttpClientException
import time
from filip.models.base import FiwareHeader, FiwareHeaderSecure
from filip.clients.base_http_client import BaseHttpClient
from pydantic import computed_field
from filip.clients.ngsi_v2.client import HttpClient, HttpClientConfig
from filip.models.ngsi_v2 import ContextEntity
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
        self.fh = FiwareHeader(
            service=settings.FIWARE_SERVICE, service_path=settings.FIWARE_SERVICEPATH
        )
        self.create_json_file()
        with open(self.get_json_path()) as f:
            self.config = json.load(f)

    def create_json_file(self) -> None:
        """
        Create a json settings file based on the current environment settings
        """
        content = {
            "cb_url": str(settings.CB_URL),
            "iota_url": str(settings.IOTA_JSON_URL),
            "ql_url": str(settings.QL_URL),
        }
        with open(self.get_json_path(), "w") as file:
            file.write(json.dumps(content, indent=4))

    @staticmethod
    def get_json_path() -> str:
        """
        Get the correct path to the json file needed for this test
        """

        # Test if the testcase was run directly or over in a global test-run.
        # Match the needed path to the config file in both cases

        path = Path(__file__).parent.resolve()
        return str(path.joinpath("test_ngsi_v2_client.json"))

    @staticmethod
    def get_env_path() -> str:
        """
        Get the correct path to the env file needed for this test
        """
        # Test if the testcase was run directly or over in a global test-run.
        # Match the needed path to the config file in both cases
        path = Path(__file__).parent.resolve()
        return str(path.joinpath(".env.filip"))

    def _test_change_of_headers(self, client: HttpClient):
        """
        Test changes in fiware headers

        Args:
            client (HttpClient): Client under test
        Returns:
            None
        """
        self.assertEqual(
            id(client.fiware_service_path),
            id(client.cb.fiware_service_path),
            "FIWARE Service path out of sync",
        )
        self.assertEqual(
            id(client.fiware_service_path),
            id(client.iota.fiware_service_path),
            "FIWARE Service path out of sync",
        )
        self.assertEqual(
            id(client.fiware_service_path),
            id(client.timeseries.fiware_service_path),
            "FIWARE Service path out of sync",
        )

        client.fiware_service = "filip_other"

        self.assertEqual(
            client.fiware_service_path,
            client.cb.fiware_service_path,
            "FIWARE service out of sync",
        )
        self.assertEqual(
            client.fiware_service_path,
            client.iota.fiware_service_path,
            "FIWARE service out of sync",
        )
        self.assertEqual(
            client.fiware_service_path,
            client.timeseries.fiware_service_path,
            "FIWARE service out of sync",
        )

        client.fiware_service_path = generate_servicepath()

        self.assertEqual(
            client.fiware_service_path,
            client.cb.fiware_service_path,
            "FIWARE Service path out of sync",
        )
        self.assertEqual(
            client.fiware_service_path,
            client.iota.fiware_service_path,
            "FIWARE Service path out of sync",
        )
        self.assertEqual(
            client.fiware_service_path,
            client.timeseries.fiware_service_path,
            "FIWARE Service path out of sync",
        )

    @staticmethod
    def _test_connections(client: HttpClient):
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

    @unittest.skip("Currently fails. Because env is already loaded before test")
    def test_config_env(self):
        """
        Test configuration using .env.filip or environment variables the
        latter is handled in core.config

        Returns:
            None
        """
        with open(self.get_env_path(), "w") as file:
            for key, value in self.config.items():
                file.write(key.upper() + "=" + str(value) + "\n")

        # ToDo: check how to reload the settings
        # reload .env.filip

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
        with HttpClient(config=self.config, fiware_header=self.fh) as client:
            self.assertIsNotNone(client.session)
            self._test_connections(client=client)
            self._test_change_of_headers(client=client)

        # with external session
        with requests.Session() as s:
            client = HttpClient(config=self.config, session=s, fiware_header=self.fh)
            self.assertEqual(client.session, s)
            self._test_connections(client=client)
            self._test_change_of_headers(client=client)

        # with external session but unnecessary 'with'-statement
        with requests.Session() as s:
            with HttpClient(
                config=self.config, session=s, fiware_header=self.fh
            ) as client:
                self.assertEqual(client.session, s)
                self._test_connections(client=client)
                self._test_change_of_headers(client=client)

    def test_handling_ssl_error(self):
        """
        Test if the client can handle SSL errors correctly

        Returns:
            None
        """
        url_with_ssl_error = "https://self-signed.badssl.com/"
        config = HttpClientConfig(
            cb_url=url_with_ssl_error,
            iota_url=url_with_ssl_error,
            ql_url=url_with_ssl_error,
        )
        with self.assertRaises(BaseHttpClientException):
            client = HttpClient(config=config, fiware_header=self.fh)

    def test_dynamic_header_update(self):
        """Ensure every HTTP helper re-fetches secure headers per request."""

        class DynamicFiwareHeader(FiwareHeader):
            @computed_field
            @property
            def authorization(self) -> str:
                return f"Bearer {time.time()}"

        secure_header = DynamicFiwareHeader(
            service=self.fh.service,
            service_path=self.fh.service_path,
        )

        mock_session = MagicMock(spec=requests.Session)
        mock_session.headers = {}
        mock_session.request.return_value = MagicMock()

        client = BaseHttpClient(
            url="https://example.com", session=mock_session, fiware_header=secure_header
        )

        verbs_with_payloads = {
            "get": {"params": {"q": "1"}},
            "post": {"json": {"foo": "bar"}},
            "put": {"data": "payload"},
            "patch": {"json": {"patch": True}},
            "delete": {},
            "options": {},
            "head": {},
        }

        seen_authorizations = set()

        for verb, payload in verbs_with_payloads.items():
            mock_session.request.reset_mock()
            client_method = getattr(client, verb)
            client_method(f"https://example.com/test_{verb}", **payload)

            call = mock_session.request.call_args
            call_headers = call.kwargs["headers"]
            auth_header = call_headers["authorization"]

            self.assertTrue(auth_header.startswith("Bearer"))
            self.assertNotIn(
                auth_header,
                seen_authorizations,
                f"Header failed to update for {verb.upper()} request",
            )
            self.assertEqual(call.kwargs["method"], verb.upper())

            seen_authorizations.add(auth_header)
            time.sleep(0.01)

        # Also verify direct usage of the shared request helper refreshes headers
        mock_session.request.reset_mock()
        client.request(
            method="POST",
            url="https://example.com/direct",
            json={"direct": True},
        )
        direct_headers = mock_session.request.call_args.kwargs["headers"]
        self.assertTrue(direct_headers["authorization"].startswith("Bearer"))

    def tearDown(self) -> None:
        """
        Clean up artifacts

        Returns:
            None
        """

        # remove create json and env config file
        import os

        os.remove(self.get_json_path())
        try:
            os.remove(self.get_env_path())
        except:
            pass
