import os
import json
import errno
import logging
import logging.config
import yaml
import json


# setup Environmental parameters
TIMEZONE = os.getenv("TIMEZONE", "UTC/Zulu")


def setup_logging(path_to_config: str ='/Users/Felix/PycharmProjects/Logger/filip/log_config.yaml',
                  default_level=logging.INFO):
    """
    Function to setup the logging configuration from a file
    var: path_to_config: a file configuring the logging setup, either a JSON or a YAML
    var: default_level: if no valid config file is present, this sets the default logging level
    """
    if os.path.exists(path_to_config):
        file_extension = (path_to_config.split('.')[-1]).lower()
        with open(path_to_config, 'rt') as f:
            if file_extension in ['yaml', 'yml']:
                cfg = yaml.load(f, Loader=yaml.Loader)
            elif file_extension == 'json':
                cfg = json.load(f)
        logging.config.dictConfig(cfg)
    else:
        logging.basicConfig(level=default_level)


class Config:
    def __init__(self, path = 'config.json'):
        """
        Class constructor for config class. At start up it parses either
        system environment variables or external config file in json format.
        If CONFIG_FILE is set to true external config file will be used
        NOTE: If list of parameters is extended do it here and in
        def update_config()
        """
        self.file = os.getenv("CONFIG_FILE", 'True')
        self.path = os.getenv("CONFIG_PATH", path)
        self.data = None
        if eval(self.file):
            print("[INFO] CONFIG_PATH variable is updated to: " + self.path)
            self.data = self._read_config_file(self.path)
        else:
            print("[INFO] Configuration loaded from environment variables")
            self.data = self._read_config_envs()
        if self.data is not None:
            pass
        #TODO:
        # 0. check if data dict is not None --> use some default values
        # 1. assert data dict

        # self.update_config_param(self.data)
        #try:
#        self.test_services(self.data)
        #except Exception:
         #   pass

            # Needs to go to services
            # self.fiware_service = os.getenv("FIWARE_SERVICE", "default")
            # self.fiware_service_path = os.getenv("FIWARE_SERVICE_PATH",  "/")

    def __repr__(self):
        """
        Returns the Representation (= Data) of the object as string
        :return:
        """
        return "{}".format(self.data)


    def _read_config_file(self, path: str):
        """
        Reads configuration file and stores data in entity CONFIG
        :param path: Path to config file
        :return: True if operation works
        :return: False if operation fails
        """
        #TODO: add use of ini: do strings processing split at last dot (if .json or .ini)
        #TODO: check if all data is defined
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


    def _read_config_envs(self):
        """
        reads environment variables for host urls and ports of orion, IoTA,
        quantumleap, crate. Default URL of Orion is "http://localhost", 
        the default ULR of IoTA, quantumleap and Crate is the URL of Orion.
        """
        data = {}
        data['orion']={}
        data['orion']['host'] = os.getenv("ORION_HOST", "http://localhost")
        data['orion']['port'] = os.getenv("ORION_PORT", "1026")
        
        data['iota']={}
        data['iota']['host'] = os.getenv("IOTA_HOST", data['orion']['host'])
        data['iota']['port'] = os.getenv("IOTA_PORT", "4041")
        data['iota']['protocol'] = os.getenv("IOTA_PROTOCOL", "IoTA-UL") #or IoTA-JSON
        
        data['quantum_leap']={}
        data['quantum_leap']['host'] = os.getenv("QUANTUMLEAP_HOST", data['orion']['host'])
        data['quantum_leap']['port'] = os.getenv("QUANTUMLEAP_PORT", "8668")
        
        data['cratedb']={}
        data['cratedb']['host'] = os.getenv("CRATEDB_HOST", data['orion']['host'])
        data['cratedb']['port'] = os.getenv("CRATEDB_PORT", "4200")
        
        data['fiware']={}
        data['fiware']['service'] = os.getenv("FIWARE_SERVICE", "dummy_service")
        data['fiware']['service_path'] = os.getenv("FIWARE_SERVICE_PATH", "/dummy_path")
        return data


    def update_config_param(self, data: dict):
        """
        This function updates the parameters of class config
        :param data: dict coming from parsing config file or environment
        varibles
        :return:
        """
        try:
            self.data = data
            print("[INFO]: Configuration parameters updated:")
            print(json.dumps(data, indent=4))
        except Exception:
            print("[ERROR]: Failed to set config parameters!")
            pass
        '''try:
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
        return True'''
        
#TODO: move to single services
#    def test_services(self, config: dict):
#        """This function checks the configuration and tests connections to
#        necessary server endpoints"""
#        test.test_config('orion', config)
#        test.test_connection('Orion Context Broker', self.data['orion'][
#            'host'] + ':' + str(self.data['orion']['port']) + '/version')
#        test.test_config('iota', config)
#        test.test_connection('IoT Agent JSON', self.data['iota'][
#            'host'] + ':' + str(self.data['iota']['port']) + '/iot/about')
#        test.test_config('quantum_leap', config)
#        test.test_connection('Quantum Leap', self.data['quantum_leap'][
#            'host'] + ':' + str(self.data['quantum_leap']['port']) + \
#        '/v2/version')
#        print("[INFO]: Configuration seems fine!")



if __name__=="__main__":
    CONFIG = Config('/Users/Felix/PycharmProjects/compare_duplicate/filip/config.json')
    print(CONFIG)
    print(CONFIG.data['fiwareService'])
    print("List of services and paths:")
    for service in CONFIG.data['fiwareService']:
        print("{:<30}{:<20}".format('Service: ',service['service']))
        for path in service['service_path']:
            print("{:<30}{:<40}".format('',path))
