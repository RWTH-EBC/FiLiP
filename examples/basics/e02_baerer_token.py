"""
# Examples for initializing a contextbroker client with authorization via bearer
token.
- The authorization key is provided via the FiwareHeaderSecure class.
- The parameters should be provided via environment variables or a .env file.
"""

from filip.models.base import FiwareHeaderSecure
from filip.clients.ngsi_v2 import ContextBrokerClient

# ## Parameters
# Host address of Context Broker
CB_URL = "https://localhost:1026"
# FIWARE-Service
fiware_service = 'filip'
# FIWARE-Servicepath
fiware_service_path = '/example'
# FIWARE-Bearer token
# TODO it has to be replaced with the token of your protected endpoint
fiware_baerer_token = 'BAERER_TOKEN'

if __name__ == '__main__':
    fiware_header = FiwareHeaderSecure(service=fiware_service,
                                       service_path=fiware_service_path,
                                       authorization=f"""Bearer {
                                       fiware_baerer_token}""")
    cb_client = ContextBrokerClient(url=CB_URL,
                                    fiware_header=fiware_header)
    # query entities from protected orion endpoint
    entity_list = cb_client.get_entity_list()
    print(entity_list)
