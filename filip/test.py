import requests
import filip.iot
import json
import pprint


import logging

log = logging.getLogger('test')


def test_connection(service_name: str, url: str, auth_method: str =None,
                    **kwargs):
    """
    This function tests the a webservice is reachable
    :param service_name: Name of the webservice
    :param url: url of the webservice to be tested
    :param auth_method: Authorization method for connecting to the service
    default==None
    :return:
    """
    try:
        if auth_method == None:
            res = requests.get(url, auth=('user', 'pass'))
            if res.status_code == 200:
                print("[INFO]: " + service_name + " check success! Service is "
                                                    "up and running!")
                print("[INFO]: Response from service:")
                print(res.text)
            else:
                print("[ERROR]: " + service_name + ' check failed! Is the '
                                                  'service up and running? '
                                                  'Please check configuration! '
                                                  'Response: ' +
                      res.status_code)
        #TODO: Other authorization methods need to be added here! and also
        # added to the exception handling!
        #if auth_method ==
    except Exception:
        print("[ERROR] " + service_name + ' check failed! Is the '
                                          'service up and running? Please '
                                              'check configuration!')


def test_config(service_name: str, config_data: dict):
    """
    Checking configuration for plausibility and correct types
    :param service_name: Name of the client instance for that the
    configuration should be tested.
    :param config: Global of dictionary for configuration parameters
    :return:
    """
    #TODO: Adding type checking and logical tests
    try:
        if service_name not in config_data:
            raise Exception("Missing configuration for '"+ service_name +
                            "'!")
        if 'host' not in config_data[service_name]:
            raise Exception("Host configuration for'" + service_name + "' is "
                                                                 "missing!")
        assert isinstance(config_data[service_name]['host'], str), ("Host "
                                                               "configuration "
                                                               "for'" +
                                                               service_name +
                                                               "' must be "
                                                               "string!")

        if 'port' not in config_data[service_name]:
            raise Exception("Port configuration for'" + service_name + "' is "
                                                                 "missing!")
        elif isinstance(config_data[service_name]['port'], str):
            port = config_data[service_name]['port']
            if port.isdigit() and int(port)<= 65535:
                pass
            else:
                raise Exception("No valid Port configuration for '" +
                                service_name + "'!")
        else:
            if isinstance(config_data[service_name]['port'], int) and \
                    config_data[
                service_name]['port']<= 65535:
                pass
            else:
                raise Exception("No valid port configuration for' " +
                                service_name + "'!")
        if 'protocol' in config_data[service_name]:
            assert isinstance(config_data[service_name]['protocol'], str),\
                ("Host configuration for'" + service_name + "' must be string!")
            # Additional allowed protocols may be added here, e.g. 'IoTA-LWM2M'
            assert config_data[service_name]['protocol'] in \
                   filip.iot.PROTOCOLS, \
                ("Protocol for '" + service_name + "' not supported! The "
                "following protocols are supported: " + str(
                    filip.iot.PROTOCOLS))

    except Exception as error:
        print("[ERROR]: "+ error.args[0])
        print('[ERROR]: Config test failed!')

    print("[INFO]: Configuration successfully tested!")
    return True


