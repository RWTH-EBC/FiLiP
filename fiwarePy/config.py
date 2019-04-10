import os
import string
import random
import requests
import json
import errno


def test_connect(service_name: str, url: str) -> str:
    """
    This function tests the a webservice is reachable
    :param service_name: Name of the webservice
    :param url: url of the webservice to be tested
    :return:
    """
    try:
        res = requests.get(url, auth=('user', 'pass'))
        if res.status_code == 200:
            print("[INFO] " + service_name + " check success! Service is "
                                             "up and running!")
            print("[INFO] Response from service:")
            print(res.text)
        else:
            print("[ERROR] " + service_name + ' check failed! Is the '
                                              'service up and running? '
                                              'Please check configuration! '
                                              'Response: ' + res.status_code)
    except Exception:
        print("[ERROR] " + service_name + ' check failed! Is the '
                                          'service up and running? Please '
                                          'check configuration!')


class Config:
    def __init__(self):
        """
        Class constructor for config class. At start up it parses either
        system environment variables or external config file in json format.
        If CONFIG_FILE is set to true external config file will be used
        NOTE: If list of parameters is extended do it here and in
        def update_config()
        """
        self.orion_host = None
        self.orion_port = None
        self.iota_host = None
        self.iota_port = None
        self.quantumleap_host = None
        self.quantumleap_port = None
        self.config_file = os.getenv("CONFIG_FILE", True)
        self.path = os.getenv("CONFIG_PATH", 'config.json')
        if self.config_file:
            print("[INFO] CONFIG_PATH variable is updated to: " + self.path)
            config_data = self.read_config_file(self.path)
        else:
            config_data = self.read_config_envs()
        if config_data is not None:
            pass
        #TODO:
        # 0. check if data dict is not None --> use some default values
        # 1. assert data dict
        self.update_config_param(config_data)
        try:
            self.test_config()
        except Exception:
            pass

            # Needs to go to services
            # self.fiware_service = os.getenv("FIWARE_SERVICE", "default")
            # self.fiware_service_path = os.getenv("FIWARE_SERVICE_PATH",  "/")

    def read_config_file(self, path: str):
        """
        Reads configuration file and stores data in entity CONFIG
        :param path: Path to config file
        :return: True if operation works
        :return: False if operation fails
        """
        try:
            with open(path, 'r') as filename:
                print("[INFO] Reading " + path)
                data = json.load(filename)
            print(json.dumps(data, indent=4))

        except IOError as err:
            if err.errno == errno.ENOENT:
                print('[ERROR]', path, '- does not exist')
            elif err.errno == errno.EACCES:
                print('[ERROR]', path, '- cannot be read')
            else:
                print('[ERROR]', path, '- some other error')
            return False
        return data

    def read_config_envs(self):
        """
        :return:
        """
        data = {}
        data['orion']['host'] = os.getenv("ORION_HOST", "http://localhost")
        data['orion']['port'] = os.getenv("ORION_PORT", "1026")
        data['iota']['host'] = os.getenv("IOTA_JSON_HOST",
                                         "http://localhost")
        data['iota']['port'] = os.getenv("IOTA_PORT", "4041/")
        data['quantumleap']['host'] = os.getenv("QUANTUM_LEAP_HOST",
                                          "http://localhost")
        data['quantumleap']['port'] = os.getenv("IOTA_PORT", "8668/")
        return data

    def update_config_param(self, data: dict):
        """
        This function updates the parameters of class config
        :param data: dict coming from parsing config file or environment
        varibles
        :return:
        """
        try:
            self.orion_host = data['orion']['host']
            self.orion_port = data['orion']['port']
            self.iota_host = data['iota']['host']
            self.iota_port = data['iota']['port']
            self.quantumleap_host = data['quantum_leap']['host']
            self.quantumleap_port = data['quantum_leap']['port']
            print("[INFO]: Configuration parameters updated:")
            print(json.dumps(data, indent=4))
        except Exception:
            print("[ERROR]: Failed to set config parameters!")
            pass
        return True

    # Needs to be moved to IoT-Client part
    def generate_key(self, length: int = 10):
        """
        This function generates a random key from lowercase letter and
        digit characters
        :ivar length: Number of characters in the key string
        """
        return ''.join(random.choice(
            string.ascii_lowercase + string.digits) for _ in range(
            length))

    # Needs to be moved to IoT-Client part
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

    def test_config(self):
        """This function checks the configuration and tests connections to
        necessary server endpoints"""
        test_connect('Orion Context Broker', self.orion_host + ':' +
                     self.orion_port + '/version')
        test_connect('IoT Agent JSON', self.iota_host + ':' + self.iota_port +
                     '/iot/about')
        test_connect('Quantum Leap', self.quantumleap_host + ':' +
                     self.quantumleap_port + '/v2/version')
        # self.check_apikey() # needs to be moved to IoTA
        # print("[INFO] Chosen service: " + self.fiware_service)
        # print("[INFO] Chosen service path: " + self.fiware_service_path)


__CONFIG = Config()
