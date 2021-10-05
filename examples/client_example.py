"""
Examples for initializing the different clients.
For each client we will retrieve the active service version.
Please, make sure to adjust the either the 'filip.env' for your server.
"""
import logging
import requests
from filip.clients.ngsi_v2 import \
    ContextBrokerClient, \
    IoTAClient, \
    QuantumLeapClient
from filip.models.base import FiwareHeader

# Setting up logging
logging.basicConfig(
    level='INFO',
    format='%(asctime)s %(name)s %(levelname)s: %(message)s')

if __name__ == '__main__':
    # First a create a fiware header that you want to work with
    # For more details on the headers check the official documentation:
    # https://fiware-orion.readthedocs.io/en/master/user/multitenancy/index.html
    fiware_header = FiwareHeader(service='filip',
                                 service_path='/testing')

    # You can run the clients in different modes:
    # 1. Run it as pure python object. This will open and close a connection
    # each time you use a function.
    cb_client = ContextBrokerClient(fiware_header=fiware_header)
    print(f"OCB Version: {cb_client.get_version()}")

    # 2. Run the client via the python's context protocol. THis will
    # initialize requests.session that the client will reuse for each function.
    # Formally, this usually lead to an performance boost because the
    # connection was reused reused. The client and its connection will be
    # closed after the end of the with-statement. However, thanks to urllib3
    # the keep-alive and session reuse is handled totally automatically.
    with ContextBrokerClient(fiware_header=fiware_header) as cb_client:
        print(f"OCB Version: {cb_client.get_version()}")

    # 3. Run the client with an externally provided requests.Sessions object
    # This mode is recommend when you want to reuse requests.Session and mix
    # different clients. It is also useful in combination with OAuth2Session
    # objects that handle authentication mechanisms and third party libraries.
    # Please be aware that you need to do the session handling yourself.
    # Hence, always create the session by using python's context protocol or
    # manually close the connection.
    with requests.Session() as s:
        cb_client = ContextBrokerClient(session=s, fiware_header=fiware_header)
        print(f"OCB Version: {cb_client.get_version()}")

    # You can use this procedure for all NGSIv2 clients
    iota_client = IoTAClient(fiware_header=fiware_header)
    print(f"Iot-Agent Version: {iota_client.get_version()}")
    ql_client = QuantumLeapClient(fiware_header=fiware_header)
    print(f"QuantumLeap Version: {ql_client.get_version()}")

    # Instead of using an .env.filip or environment variables you can also
    # provide the url directly to the specific clients. It also takes any
    # additional keyword arguments a requests.request would also take,
    # e.g. headers, params etc.
    """
    iota_client = ContextBrokerClient(url="http://<yourHost>:1026",
                                      header=header)
    """

    # The library also contains a client that contains all the other
    # particular clients. It works almost the same as the other agents but
    # takes a config. This can be either a dict or the path to a json file:
    # Example:
    # {
    #   "cb_url": "http://<yourHost>:1026",
    #   "iota_url": "http://<yourHost>:4041",
    #   "ql_url": "http://<yourHost>:8668"
    # }
    """
    config = {
                "cb_url": "http://<yourHost>:1026",
                "iota_url": "http://<yourHost>:4041",
                "ql_url": "http://<yourHost>:8668"
            }
    from filip.clients.ngsi_v2 import HttpClient
    client = HttpClient(config=config)
    
    """
