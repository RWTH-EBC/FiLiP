import os
import json
import errno
import logging
import logging.config
import yaml
import json

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

class Log_Config:
    def __init__(self, path = None):
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
            file_extension = path.split(".")[1]
            with open(path, 'rt') as f:
                if file_extension in ['yaml', 'yml']:
                    cfg = yaml.load(f, Loader=yaml.Loader)
                elif file_extension == 'json':
                    cfg = json.load(f)
                logging.config.dictConfig(cfg)



                print(json.dumps(cfg, indent=4))

        except IOError as err:
            if err.errno == errno.ENOENT:
                print('[ERROR]', path, '- does not exist')
            elif err.errno == errno.EACCES:
                print('[ERROR]', path, '- cannot be read')
            else:
                print('[ERROR]', path, '- some other error')
            return False
        return cfg


    def _read_config_envs(self):
        """
        reads envrionment variables for module loggers. The default setting is DEBUG
        """
        cfg = {}
        cfg["version"] = 1
        cfg["disable_existing_loggers"] = False
        cfg["formatters"]["standard"]["format"] = os.getenv("LOG_FORMAT_STANDARD",  "%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        cfg["formatters"]["error"]["format"] = os.getenv("LOG_FORMAT_ERROR",
                                                         "%(asctime)s - %(levelname)s <PID %(process)d:%(processName)s> %(name)s.%(funcName)s(): %(message)s" )

        cfg["handlers"]["console"]["class"] = os.getenv("LOG_CLASS_CONSOLE", "logging.StreamHandler")
        cfg["handlers"]["console"]["level"] = os.getenv("LOG_LEVEL_CONSOLE", "DEBUG")
        cfg["handlers"]["console"]["formatter"] = os.getenv("LOG_FORMATTER_CONSOLE", "standard")
        cfg["handlers"]["console"]["class"] = os.getenv("LOG_STREAM_CONSOLE", "ext://sys.stdout")

        cfg["handlers"]["info_file_handler"]["class"] = os.getenv("LOG_CLASS_INFO", "logging.handlers.RotatingFileHandler")
        cfg["handlers"]["info_file_handler"]["level"] = os.getenv("LOG_LEVEL_INFO", "INFO")
        cfg["handlers"]["info_file_handler"]["formatter"] = os.getenv("LOG_FORMATTER_INFO", "standard")
        cfg["handlers"]["info_file_handler"]["filename"] = os.getenv("LOG_FILENAME_INFO", "info.log")
        cfg["handlers"]["info_file_handler"]["maxBytes"] = os.getenv("LOG_MAXBYTES_INFO", 10485760)
        cfg["handlers"]["info_file_handler"]["backupCount"] = os.getenv("LOG_BACKUPCOUNT_INFO", 20)
        cfg["handlers"]["info_file_handler"]["encoding"] = os.getenv("LOG_ENCODING_INFO", "utf8")

        cfg["handlers"]["error_file_handler"]["class"] = os.getenv("LOG_CLASS_ERROR", "logging.handlers.RotatingFileHandler")
        cfg["handlers"]["error_file_handler"]["level"] = os.getenv("LOG_LEVEL_ERROR", "ERROR")
        cfg["handlers"]["error_file_handler"]["formatter"] = os.getenv("LOG_FORMATTER_ERROR", "error")
        cfg["handlers"]["error_file_handler"]["filename"] = os.getenv("LOG_FILENAME_ERROR", "error.log")
        cfg["handlers"]["error_file_handler"]["maxBytes"] = os.getenv("LOG_MAXBYTES_ERROR", 10485760)
        cfg["handlers"]["error_file_handler"]["backupCount"] = os.getenv("LOG_BACKUPCOUNT_ERROR", 20)
        cfg["handlers"]["error_file_handler"]["encoding"] = os.getenv("LOG_ENCODING_ERROR", "utf8")

        cfg["handlers"]["debug_file_handler"]["class"] = os.getenv("LOG_CLASS_DEBUG", "logging.handlers.RotatingFileHandler")
        cfg["handlers"]["debug_file_handler"]["level"] = os.getenv("LOG_LEVEL_DEBUG", "DEBUG")
        cfg["handlers"]["debug_file_handler"]["formatter"] = os.getenv("LOG_FORMATTER_DEBUG", "error")
        cfg["handlers"]["debug_file_handler"]["filename"] = os.getenv("LOG_FILENAME_DEBUG", "debug.log")
        cfg["handlers"]["debug_file_handler"]["maxBytes"] = os.getenv("LOG_MAXBYTES_DEBUG", 10485760)
        cfg["handlers"]["debug_file_handler"]["backupCount"] = os.getenv("LOG_BACKUPCOUNT_DEBUG", 20)
        cfg["handlers"]["debug_file_handler"]["encoding"] = os.getenv("LOG_ENCODING_DEBUG", "utf8")

        cfg["loggers"]["iot"]["level"] = os.getenv("LOGGER_LEVEL_IOT", "DEBUG")
        cfg["loggers"]["iot"]["handlers"] = os.getenv("LOGGER_HANDLERS_IOT", ["console", "info_file_handler",
                                                                              "error_file_handler", "debug_file_handler"])
        cfg["loggers"]["iot"]["propagate"] = os.getenv("LOGGER_PROPAGATE_IOT", "no")

        cfg["loggers"]["orion"]["level"] = os.getenv("LOGGER_LEVEL_ORION", "DEBUG")
        cfg["loggers"]["orion"]["handlers"] = os.getenv("LOGGER_HANDLERS_ORION", ["console", "info_file_handler",
                                                                                  "error_file_handler", "debug_file_handler"])
        cfg["loggers"]["orion"]["propagate"] = os.getenv("LOGGER_PROPAGATE_ORION", "no")

        cfg["loggers"]["subscription"]["level"] = os.getenv("LOGGER_LEVEL_SUBSCRIPTION", "DEBUG")
        cfg["loggers"]["subscription"]["handlers"] = os.getenv("LOGGER_HANDLERS_SUBSCRIPTION", ["console", "info_file_handler",
                                                                                                "error_file_handler", "debug_file_handler"])
        cfg["loggers"]["subscription"]["propagate"] = os.getenv("LOGGER_PROPAGATE_SUBSCRIPTION", "no")

        cfg["loggers"]["timeseries"]["level"] = os.getenv("LOGGER_LEVEL_TIMESERIES", "DEBUG")
        cfg["loggers"]["timeseries"]["handlers"] = os.getenv("LOGGER_HANDLERS_TIMESERIES", ["console", "info_file_handler",
                                                                                            "error_file_handler", "debug_file_handler"])
        cfg["loggers"]["timeseries"]["propagate"] = os.getenv("LOGGER_PROPAGATE_TIMESERIES", "no")


        cfg["root"]["level"] = os.getenv("LOGGER_LEVEL_ROOT", "DEBUG")
        cfg["root"]["handlers"] = os.getenv("LOGGER_HANDLERS_ROOT", ["console", "info_file_handler",
                                                              "error_file_handler", "debug_file_handler"])

        logging.config.dictConfig(cfg)

        return cfg


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




if __name__=="__main__":
    CONFIG = Config('/Users/Felix/PycharmProjects/compare_duplicate/filip/config.json')
    #print(CONFIG.data['fiwareService'])

    LOG_CONFIG = Log_Config("/Users/Felix/PycharmProjects/compare_duplicate/filip/log_config.json")
    print("List of services and paths:")
    #for service in CONFIG.data['fiwareService']:
    #    print("{:<30}{:<20}".format('Service: ',service['service']))
    #    for path in service['service_path']:
    #        print("{:<30}{:<40}".format('',path))
