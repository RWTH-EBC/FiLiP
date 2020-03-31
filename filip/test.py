import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import json
import pprint
import datetime


import logging

log = logging.getLogger('test')


def test_connection(url: str, service_name: str, auth_method: str =None,
                    **kwargs):
    """
    This function tests the a webservice is reachable
    :param service_name: Name of the webservice
    :param url: url of the webservice to be tested
    :param auth_method: Authorization method for connecting to the service
    default==None, currently suported options are implemented in the request libray (HTTPBasicAuth and HTTPDigestAuth)
    :param kwargs: If authmethod is not None, kwargs can be used to pass auth credentials
    :return: Boolean, whether connnection exists or not
    """
    try:
        if auth_method is None:
            res = requests.get(url)
            if res.status_code == 200:
                log.info(f"{datetime.datetime.now()} - {service_name} : Check Success! Service is up and running!")
            else:
                log.error(f"{datetime.datetime.now()} - {service_name} : Check has Errors! Please check Service response: {res.text}")

        if auth_method is not None:
            if auth_method is "HTTPBasicAuth":
                authorization =kwargs.get("auth")
                res = requests.get(url, auth=authorization)

            elif auth_method is "HTTPDigestAuth":
                authorization = kwargs.get("auth")
                requests.get(url, auth=HTTPDigestAuth(authorization))

            else:
                log.error(f"{datetime.datetime.now()} - {service_name} : Authentification method: {auth_method} currently not supported")
                raise NotImplementedError

            if res.status_code == 200:
                log.info(f"{datetime.datetime.now()} - {service_name} : Check Success! Service is up and running!")
            else:
                log.error(f"{datetime.datetime.now()} - {service_name} :Check has Errors! Please check Service response: {res.text}")

    except Exception:
        log.error(f"{datetime.datetime.now()} - {service_name} : Check Failed! Is the service up and running? Please check configuration! ")



def test_iota_connection():
    """
    Function tests that the IoT-Agent connection is working.
    :return:
    """
    pass


def test_config(service_name: str, config_data: dict):
    """
    Checking configuration for plausibility and correct types
    :param service_name: Name of the client instance for that the
    configuration should be tested.
    :param config: Global of dictionary for configuration parameters
    :return:
    """
    #TODO: Adding type checking and logical tests
    import filip.iot_agent as iot
    list_protocols = iot.PROTOCOLS.copy()
    protocols = ', '.join(list_protocols)
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
                    config_data[service_name]['port']<= 65535:
                pass
            else:
                raise Exception("No valid port configuration for' " +
                                service_name + "'!")
        if 'protocol' in config_data[service_name]:
            print("True")
            assert isinstance(config_data[service_name]['protocol'], str),\
                ("Host configuration for'" + service_name + "' must be string!")
            # Additional allowed protocols may be added here, e.g. 'IoTA-LWM2M'
            assert config_data[service_name]['protocol'] in list_protocols, \
                ("Protocol for '" + service_name + "' not supported! The "
                "following protocols are supported: " + protocols)


        log.info("Configuration successfully tested!")
        return True


    except Exception as error:
        log.error(f" {datetime.datetime.now()} -  Config test failed! {error}")




