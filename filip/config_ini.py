import os
import configparser
import string
import random
import requests

#IOTA_URL = os.getenv("IOTA_URL", "http://localhost:4041/")
#QUANTUM_URL = os.getenv("QUANTUM_URL", "http://localhost:8668/")
#FIWARE_SERVICE = os.getenv("FIWARE_SERVICE", "default")FIWARE_SERVICE_PATH = os.getenv("FIWARE_SERVICE_PATH", "/")
#CONFIG = create_config()

CONFIG_PATH = os.getenv("CONFIG_PATH", 'conf.ini')
ORION_URL = os.getenv("ORION_URL", "http://localhost:1028/")
IOTA_URL = os.getenv("IOTA_URL", "http://localhost:1026/")





DEFAULT_SECTION = 'FIWARE1'


class Config:
    def __init__(self, path: str, section: str):
        self.path = path
        self.section = section
        try:
            self.config = configparser.ConfigParser()
            self.config.read(self.path)
            self.orion_url = self.config[self.section]['orion_url']
            self.iota_json_url = self.config[self.section]['iota_json_url']
            self.quantumleap_url = self.config[self.section]['quantumleap_url']
            self.fiware_service = self.config[self.section]['fiware_service']
            self.fiware_service_path = self.config[self.section][
                'fiware_service_path']
            self.apikey = self.config[self.section]['apikey']
        except Exception:
            print("[ERROR] Reading config failed!")

    def generate_key(self, length: int = 10):
        """This function generates a random key from lowercase letter and
        digit characters
        :ivar length: Number of characters in the key string"""
        return ''.join(random.choice(
                string.ascii_lowercase+string.digits) for _ in range(
                length))

    def check_apikey(self):
        """
        This function checks if an apikey is defined in the configfile.
        Otherwise it will ask the user to generate one and saves it to the
        configfile in the given sections.
        """

        try:
            if self.apikey == "" or self.apikey == self.config['DEFAULT']['apikey']:
                res = input("No APIkey defined. Do you want to generate one? "
                            "y/Y ")
                if res == "y" or res == "Y":
                    res = input("Please specify number of key (default is "
                                "10)? ")
                    if res != 10:
                        self.apikey = self.generate_key(int(res))
                    else:
                        self.apikey = self.generate_key()
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

    def test_connect(self, service_name: str, endpoint: str):
        try:
            res = requests.get(endpoint, auth=('user', 'pass'))
            if res.status_code == 200:
                print("[INFO] " + service_name + " check success! Service is "
                      "up and running!")
                print("[INFO] Response from service: \n" + str(res.json()))
            else:
                print("[ERROR] " + service_name + " check failed! Is the "
                        "service up and running? Please check configuration!"
                      "Response: " + res.status_code)
        except Exception:
            print("[ERROR] " + service_name + " check failed! Is the "
                  "service up and running? Please check configuration!")

    def check_config(self):
        """This function checks the configuration and tests connections to
        necessary server endpoints"""
        self.test_connect('Orion Context Broker', self.orion_url+'version')
        self.test_connect('IoT Agent JSON', self.iota_json_url+'iot/about')
        self.test_connect('Quantum Leap', self.quantumleap_url+'v2/version')
        self.check_apikey()
        print("[INFO] Chosen service: " + self.fiware_service)
        print("[INFO] Chosen service path: " + self.fiware_service_path)


CONFIG = Config(DEFAULT_PATH, DEFAULT_SECTION)


