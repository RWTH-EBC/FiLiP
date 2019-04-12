import requests
import fiwarePy.test as test
import json
import fiwarePy
from fiwarePy import FIWAREPY_CONFIG
import os
import string
import random


#
supported_iota_protocols = ['IoTA-JSON','IoTA-UL']

class Iota:
    def __init__(self, agent_name: str, config = FIWAREPY_CONFIG):
        self.name = agent_name
        self.host = config.data[self.name]['host']
        self.port = config.data[self.name]['port']
        self.protocol = config.data[self.name]['protocol']
        self.test_configuration()
        #TODO: Figuring our how to register the service and conncet with devices
        self.registered_services = []

    def test_configuration(self):
        test.test_config(self.name, FIWAREPY_CONFIG)
        test.test_connection(self.name, self.host + ':' + self.port +
                           '/iot/about')

    def create_iot_service(self, service_name: str, service_path: str,
                           **kwargs):
        iot_service=
        {'service': service_name,
        'service_path': service_path,
            'data'{
            "entity_type": "Thing",
            "protocol": kwargs.get("protocol", self.protocol),
            "transport": kwargs.get("transport", "MQTT"),
            "apikey": kwargs.get("apikey", "1234"),
            "attributes": [],
            "lazy": [],
            "commands": [],
            "static_attributes": []
        }


    def register_iot_service(self, iot_service: dict):
        """
        Register the default configuration that is used to set up new devices
        :param service: Fiware service (header)
        :param service_path: Fiware servic path (header)
        :param kwargs:
        :return: configuration data on success
        """

        data = {
            "services": [
                iot_service
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

    def fetch_service(self, service: str, service_path: str) -> [dict]:
        resp = requests.get(self.config.iota_json_url + "iot/services",
                            headers=self._get_header(
            service, service_path))

        if resp.status_code == 200:
            return resp.json()["services"]
        else:
            print("[WARN] Unable to fetch configuration for service "
                  "\"{}\", path \"{}\": {}"
                  .format(service, service_path, resp.text))

    # Needs to be moved to IoT-Client part
    def generate_apikey(self, length: int = 10):
        """
        This function generates a random key from lowercase letter and
        digit characters
        :ivar length: Number of characters in the key string
        """
        return ''.join(random.choice(
            string.ascii_lowercase + string.digits) for _ in range(
            length))

    # Needs to be moved to IoT-Client part
    def test_apikey(self, iot_service, apikey):
        """
        This function tests if an apikey is defined in the configfile.
        Otherwise it will ask the user to generate one and saves it to the
        configfile in the given sections.
        """
        try:
            if self.apikey == "" or self.apikey == self.['DEFAULT'][
             'apikey']:
                res = input("No APIkey defined. Do you want to generate one? "
                            "y/Y ")
                if res == "y" or res == "Y":
                    res = input("Please specify number of key (default is "
                                "10)? ")
                    if res != 10:
                        self.apikey = self.generate_apikey(int(res))
                    else:
                        self.apikey = self.generate_apikey()
                    self.config[self.section]['apikey'] = str(self.apikey)
                    with open(self.path, 'w') as configfile:
                        self.config.write(configfile)
                    print("Random Key generated: " + self.apikey +
                          " and saved in configfile!")
                else:
                    print("Default Key will be used: " +
                          self.config['DEFAULT']['APIKEY'])
            print("[INFO] APIkey check success!")
        except Exception:
            print("[ERROR] APIkey check failed. Please check configuration!")

