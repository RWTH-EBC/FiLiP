import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth

import logging

logger = logging.getLogger('testing')


def test_connection(url: str, client: requests.Session, service_name: str,
                    auth_method: str = None, **kwargs):
    """
    This function tests the a webservice is reachable
    :param service_name: Name of the webservice
    :param url: url of the webservice to be tested
    :param auth_method: Authorization method for connecting to the service
    default==None, currently supported options are implemented in the request
    library (HTTPBasicAuth and HTTPDigestAuth)
    :param kwargs: If authmethod is not None, kwargs can be used to pass auth
    credentials
    :return: Boolean, whether connection exists or not
    """
    try:
        res=client.get(url=url)
        if res.ok:
            logger.info(f"{service_name}: Check Success! Service is up and "
                     f"running!")
            logger.info(res.text)
        else:
            logger.error(f"{service_name}: Check Failed! Please check "
                      f"configuration! Response code: {res.status_code}")
    except Exception:
        logger.error(f"{service_name}: Check Failed! Is the service up and "
                  f"running? Please check configuration!")
        return False


def test_config(service_name: str, config_data: dict):
    """
    Checking configuration for plausibility and correct types
    :param service_name: Name of the client instance for that the
    configuration should be tested.
    :param config_data: Global of dictionary for configuration parameters
    :return:
    """
    # TODO: Adding type checking and logical tests
    from filip.iota import agent as iot
    list_protocols = iot.PROTOCOLS.copy()
    protocols = ', '.join(list_protocols)
    try:
        if service_name not in config_data:
            raise Exception(f" Missing configuration for {service_name}!")

        if 'host' not in config_data[service_name]:
            raise Exception(f" Host configuration for {service_name} is "
                            f"missing!")
        assert isinstance(config_data[service_name]['host'], str),\
            (f"Host configuration for {service_name} must be string!")

        if 'port' not in config_data[service_name]:
            raise Exception(f"Port configuration for {service_name} is "
                            f"missing!")

        elif isinstance(config_data[service_name]['port'], str):
            port = config_data[service_name]['port']
            if port.isdigit() and int(port) <= 65535:
                pass
            else:
                raise Exception("No valid Port configuration for '" +
                                service_name + "'!")
        else:
            if isinstance(config_data[service_name]['port'], int) and \
                    config_data[service_name]['port'] <= 65535:
                pass
            else:
                raise Exception("No valid port configuration for' " +
                                service_name + "'!")
        if 'protocol' in config_data[service_name]:
            assert isinstance(config_data[service_name]['protocol'], str), \
                f"Host configuration for {service_name} must be string!"
            # Additional allowed protocols may be added here, e.g. 'IoTA-LWM2M'
            assert config_data[service_name]['protocol'] in list_protocols, \
                f" Protocol for {service_name} not supported! The following " \
                f"protocols are supported: {protocols}"

        logger.info("Configuration successfully tested!")
        return True

    except Exception as error:
        logger.error(f"  Config test failed! {error}")
        return False




