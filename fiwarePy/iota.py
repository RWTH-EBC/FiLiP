import requests
import json
import fiwarePy
from fiwarePy.config import __CONFIG
import os

class Iota:
    def __init__(self, config=CONFIG):
        self.host = CONFIG.iota_host
        self.port = CONFIG.iota_host
        self.services = {}

    def register_configuration(self, service: str,
                           service_path: str,
                           **kwargs):
        """
        Register the default configuration that is used to set up new devices
        :param service: Fiware service (header)
        :param service_path: Fiware servic path (header)
        :param kwargs:
        :return: configuration data on success
        """
        data = {
            "services": [
                {
                    "entity_type": "Thing",
                    "protocol": kwargs.get("protocol", "IoTA-JSON"),
                    "transport": kwargs.get("transport", "MQTT"),
                    "apikey": kwargs.get("apikey", "1234"),
                    "attributes": [],
                    "lazy": [],
                    "commands": [],
                    "static_attributes": []
                }
            ]
        }

        req = requests.post(self.config.iota_json_url+ "iot/services",
                            headers=self._get_header(
                                self.config.fiware_service,
                                self.config.fiware_service_path), data=data)



        if req.status_code != 200:
            print("[WARN] Unable to register default configuration for service \"{}\", path \"{}\": {}"
                  .format(service, service_path, req.text))
            return None
        return data

    def _get_header(self, service: str, path: str) -> dict:
        return {
            "fiware_service": service,
            "fiware_servicepath": path
        }

    def fetch_configuration(self, service: str, service_path: str) -> [dict]:
        resp = requests.get(self.config.iota_json_url + "iot/services",
                            headers=self._get_header(
            service, service_path))

        if resp.status_code == 200:
            return resp.json()["services"]
        else:
            print("[WARN] Unable to fetch configuration for service \"{}\", path \"{}\": {}"
                  .format(service, service_path, resp.text))

