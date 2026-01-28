"""
# Examples for initializing the different clients.
# For each client we will retrieve the active service version.
# Please, make sure to adjust the '.env.filip' for your server.
"""

# ## Import packages
import requests
from filip.clients.ngsi_v2 import ContextBrokerClient, IoTAClient, QuantumLeapClient
from filip.models.base import FiwareHeader
from filip.config import settings

# ## Parameters
#
# Note: This example also reads parameters from the '.env.filip'-file
#
# Host address of Context Broker
CB_URL = settings.CB_URL
# Host address of IoT-Agent
IOTA_URL = settings.IOTA_URL
# Host address of QuantumLeap
QL_URL = settings.QL_URL
#
# Here you can also change the used Fiware service
# FIWARE-Service
service = "filip"
# FIWARE-Servicepath
service_path = "/example"


if __name__ == "__main__":

    # # 1 FiwareHeader
    #
    # First create a fiware header that you want to work with
    # For more details on the headers check the official documentation:
    # https://fiware-orion.readthedocs.io/en/master/user/multitenancy/index.html
    #
    # In short, a fiware header specifies a location in Fiware where the
    # created entities will be saved and requests are executed.
    # It can be thought of as a separate subdirectory where you work in.
    fiware_header = FiwareHeader(service="filip", service_path="/example")

    # # 2 Client modes
    # You can run the clients in different modes:
    #
    # ## 2.1 Run it as a pure python object.
    #
    # This will open and close a connection each time you use a function.
    cb_client = ContextBrokerClient(url=CB_URL, fiware_header=fiware_header)
    print(f"OCB Version: {cb_client.get_version()}")

    # ## 2.2 Run the client via python's context protocol.
    #
    # This will initialize requests.session that the client will reuse for
    # each function.
    # Formerly, this usually lead to a performance boost because the
    # connection was reused. The client and its connection are
    # closed after the end of the with-statement. However, thanks to urllib3,
    # the keep-alive and session reuse are handled totally automatically.
    with ContextBrokerClient(fiware_header=fiware_header) as cb_client:
        print(f"OCB Version: {cb_client.get_version()}")

    # ## 2.3 Run the client with an externally provided requests.Session object
    #
    # This mode is recommended when you want to reuse requests.Session and mix
    # different clients. It is also useful in combination with OAuth2Session
    # objects that handle authentication mechanisms and third party libraries.
    # Please be aware that you need to do the session handling yourself.
    # Hence, always create the session by using python's context protocol or
    # manually close the connection.
    with requests.Session() as s:
        cb_client = ContextBrokerClient(session=s, fiware_header=fiware_header)
        print(f"OCB Version: {cb_client.get_version()}")

    # # 3 Version information
    #
    # Independent of the selected mode, the version of the client can always be
    # accessed as follows:
    iota_client = IoTAClient(fiware_header=fiware_header)
    print(f"Iot-Agent Version: {iota_client.get_version()}")
    ql_client = QuantumLeapClient(fiware_header=fiware_header)
    print(f"QuantumLeap Version: {ql_client.get_version()}")

    # # 4 URL
    #
    # Additional to the FiwareHeader each client needs a URL that points
    # to the Fiware-server.
    #
    # ## 4.1 Environment variables
    #
    # As shown above, the client does not need to be given explicitly. If no URL
    # is given to the client, it is extracted from the environment variables
    #
    # ## 4.2 Direct Provision
    #
    # Instead of using an .env.filip or environment variables you can also
    # provide the url directly to the specific clients. It also takes any
    # additional keyword arguments a requests.request would also take,
    # e.g. headers, params etc.

    cb_client = ContextBrokerClient(url=CB_URL, fiware_header=fiware_header)

    # # 5 Combined Client
    #
    # The library also contains a client (HttpClient) that contains all the
    # particular clients as a bundle.
    # It works almost the same as the other agents but takes a config. This
    # can be either a dict or the path to a json file:

    """
    config = {
                "cb_url": "http://<yourHost>:1026",
                "iota_url": "http://<yourHost>:4041",
                "ql_url": "http://<yourHost>:8668"
            }
    from filip.clients.ngsi_v2 import HttpClient
    client = HttpClient(config=config)
    """

    # # 6 Clean up (Optional)
    #
    # Close client
    iota_client.close()
    cb_client.close()
    ql_client.close()
