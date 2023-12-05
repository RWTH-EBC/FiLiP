"""
# Examples for initializing a contextbroker client with authorization via baerer token.
- The authorization key is provided via the FiwareHeaderSecure class.
- The parameters should be provided via environment variables or a .env file.
"""

from filip.models.base import FiwareHeader
from filip.clients.ngsi_v2 import ContextBrokerClient
from pydantic import Field
 
class FiwareHeaderSecure(FiwareHeader):
    """
    Define service paths whith authorization
    """
    authorization: str = Field(
        alias="authorization",
        default="",
        max_length=3000,
        description="authorization key",
        regex=r".*"
    )
    

# ## Parameters
# Host address of Context Broker
CB_URL = "http://localhost:1026"
# FIWARE-Service
fiware_service = 'filip'
# FIWARE-Servicepath
fiware_service_path = '/example'
# FIWARE-Bearer token
fiware_baerer_token = 'BAERER_TOKEN'
    
if __name__ == '__main__':
    fiware_header = FiwareHeaderSecure(service= fiware_service,
                                       service_path= fiware_service_path,
                                       authorization= f"""Bearer {fiware_baerer_token}""")
    
    cb_client = ContextBrokerClient(url = CB_URL,
                                    fiware_header=fiware_header)