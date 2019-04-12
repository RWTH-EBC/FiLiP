import os
import string
import random
import requests
import json
import errno


# IOTA_URL = os.getenv("IOTA_URL", "http://localhost:4041/")
# QUANTUM_URL = os.getenv("QUANTUM_URL", "http://localhost:8668/")
# FIWARE_SERVICE = os.getenv("FIWARE_SERVICE", "default")FIWARE_SERVICE_PATH = os.getenv("FIWARE_SERVICE_PATH", "/")
# CONFIG = create_config()


def test_connect(service_name: str, url: str) -> str:
    try:
        res = requests.get(url, auth=('user', 'pass'))
        if res.status_code == 200:
            print ("")
#            print("[INFO] " + service_name + " check success! Service is "
#                                             "up and running!")
#            print("[INFO] Response from service:")
#            print(res.text)
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
        # If CONFIG_FILE is set to true external config file will be used
        self.config_file = os.getenv("CONFIG_FILE", True)
        self.path = os.getenv("CONFIG_PATH", 'config.json')
        if self.config_file:
#            print("[INFO] CONFIG_PATH variable is updated to: " + self.path)
            self.read_config(self.path)
        else:
            self.orion_host = os.getenv("ORION_HOST", "http://localhost")
            self.orion_port = os.getenv("ORION_PORT", "1026")
            self.iota_host = os.getenv("IOTA_JSON_HOST", "http://localhost")
            self.iota_port = os.getenv("IOTA_PORT", "4041/")
            self.quantumleap_host = os.getenv("QUANTUM_LEAP_HOST",
                                          "http://localhost")
            self.quantumleap_port = os.getenv("IOTA_PORT", "8668/")
            # Needs to go to services
            # self.fiware_service = os.getenv("FIWARE_SERVICE", "default")
            # self.fiware_service_path = os.getenv("FIWARE_SERVICE_PATH",  "/")


    def test_config(self):
        try:
            self.test_config()
        except Exception:
            pass


    def read_config(self, path: str):
        """
        Reads configuration file and stores data in entity CONFIG
        :param path: Path to config file
        :return: True if operation works
        :return: False if operation fails
        """
        try:
            with open(path, 'r') as filename:
#                print("[INFO] Loading " + path)
                data = json.load(filename)
#            print(data)
            self.orion_host = data['orion']['host']
            self.orion_port = data['orion']['port']
            self.iota_host = data['iota']['host']
            self.iota_port = data['iota']['port']
            self.quantumleap_host = data['quantum_leap']['host']
            self.quantumleap_port = data['quantum_leap']['port']
        except IOError as err:
            if err.errno == errno.ENOENT:
                print('[ERROR]', path, '- does not exist')
            elif err.errno == errno.EACCES:
                print('[ERROR]', path, '- cannot be read')
            else:
                print('[ERROR]', path, '- some other error')
            return False
        return data

    # Needs to be moved to IoT-Client part
    def generate_key(self, length: int = 10):
        """This function generates a random key from lowercase letter and
        digit characters
        :ivar length: Number of characters in the key string"""
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
            if self.apikey == "" or self.apikey == self.config['DEFAULT'][
                'apikey']:
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

if __name__=="__main__":
    CONFIG = Config()
