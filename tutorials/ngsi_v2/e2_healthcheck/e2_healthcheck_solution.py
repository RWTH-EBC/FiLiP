"""
# # Exercise 2: Service Health Check

# Create one or multiple filip clients and check if the corresponding services
# are up and running by accessing their version information.

# The input sections are marked with 'ToDo'

# #### Steps to complete:
# 1. Set up the missing parameters in the parameter section
# 2. Create filip ngsi_v2 clients for the individual services and check for
#   their version
# 3. Create a config object for the ngsi_v2 multi client (HttpClient),
#   create the multi client and again check for services' versions
"""

# ## Import packages
from filip.clients.ngsi_v2 import \
    HttpClient, \
    HttpClientConfig, \
    ContextBrokerClient, \
    IoTAClient, \
    QuantumLeapClient

# ## Parameters
# ToDo: Enter your context broker url and port, e.g. http://localhost:1026
CB_URL = "http://localhost:1026"
# ToDo: Enter your IoT-Agent url and port, e.g. http://localhost:4041
IOTA_URL = "http://localhost:4041"
# ToDo: Enter your QuantumLeap url and port, e.g. http://localhost:8668
QL_URL = "http://localhost:8668"

# ## Main script
if __name__ == "__main__":
    # ToDo: Create a single client for each service and check the service for
    #  its version
    cbc = ContextBrokerClient(url=CB_URL)
    print(cbc.get_version())

    iotac = IoTAClient(url=IOTA_URL)
    print(iotac.get_version())

    qlc = QuantumLeapClient(url=QL_URL)
    print(qlc.get_version())

    # ToDo: Create a configuration object for a multi client
    config = HttpClientConfig(cb_url=CB_URL, iota_url=IOTA_URL, ql_url=QL_URL)

    # ToDo: Create a multi client check again all services for their version
    multic = HttpClient(config=config)

    print(multic.cb.get_version())
    print(multic.iota.get_version())
    print(multic.timeseries.get_version())
