"""
Test for filip.core.client
"""
import unittest
import requests
from pathlib import Path
from filip.core.models import FiwareHeader
from filip.core.client import Client

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
        self.fh = FiwareHeader(service='n5geh',
                               service_path='/#')

        self.config = {'cb_url': 'http://134.130.166.184:1026',
                       'iota_url': 'http://134.130.166.184:4041',
                       'ql_url': 'http://134.130.166.184:8668'}

    def test_config_dict(self):
        with requests.Session() as s:
            client=Client(config=self.config, session=s, fiware_header=self.fh)
            client.fiware_service_path = '/someOther'
            print(client.cb.get_version())
            print(client.cb.get_entity_list())
            print(client.cb.session)

    def test_config_json(self):
        config_path = Path("./test_core_client.json")
        client = Client(config=config_path, fiware_header=self.fh)
        print(client.cb.get_version())
        print(client.cb.get_resources())
        print(client.cb.get_entity_list())

    def test_config_env(self):
        client = Client(fiware_header=self.fh)
        print(client.cb.get_version())
        print(client.iota.get_version())
        print(client.timeseries.get_version())

    def tearDown(self) -> None:
        """

        Returns:
            pass
        """
        pass