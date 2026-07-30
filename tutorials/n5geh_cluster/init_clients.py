"""
Example e13: Obtain FIWARE tokens via python-keycloak and refresh them per request.
The FiwareHeaderSecureKeycloak class uses a KeycloakTokenManager to fetch and cache tokens, refreshing them before they
expire so every outgoing request receives a fresh Authorization header.
"""

import os
import time
import requests
import urllib3
from filip.clients.ngsi_v2 import ContextBrokerClient, IoTAClient, QuantumLeapClient
from filip.config import settings
from filip.models.base import KeycloakTokenManager, FiwareHeaderSecureDynamic

urllib3.disable_warnings()
CB_URL = "https://n5geh.eonerc.rwth-aachen.de/orion/"
IOTA_URL = "https://n5geh.eonerc.rwth-aachen.de/iota/"
QL_URL = "https://n5geh.eonerc.rwth-aachen.de/ql/"

# FIWARE-Service
SERVICE = "ebcdev1"
# FIWARE-Servicepath
SERVICE_PATH = "/"
KEYCLOAK_HOST = "https://sso.eonerc.rwth-aachen.de"
KEYCLOAK_REALM = "EBC-Dev"
# TODO explain the access right
#   read: GET requests
#   write: PUT, PATCH, POST requests
#   admin: DELETE requests
# TODO explain the convention of the client id
CLIENT_ID = f"{SERVICE}-admin"
# TODO get credentials from passbolt
CLIENT_SECRET = "8hCCzHuTxYVcOCZ3NiWPjVJzcI077908"

# Initialize the token manager once
global_token_manager = KeycloakTokenManager(
    server_url=KEYCLOAK_HOST,
    realm_name=KEYCLOAK_REALM,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    # username=USERNAME,
    # password=PASSWORD,
)

# Pass the shared manager to the new header class
fiware_header = FiwareHeaderSecureDynamic(
    service=SERVICE,
    service_path=SERVICE_PATH,
    token_manager=global_token_manager,
)

# Initialize clients
cb_client = ContextBrokerClient(
    url=CB_URL, fiware_header=fiware_header, session=requests.Session()
)
iota_client = IoTAClient(
    url=IOTA_URL, fiware_header=fiware_header, session=requests.Session()
)
ql_client = QuantumLeapClient(
    url=QL_URL, fiware_header=fiware_header, session=requests.Session()
)

if __name__ == "__main__":
    print(f"[success] Check Context Broker version:\n  {cb_client.get_version()}\n")
    print(f"[success] Check IoTagent version:\n  {iota_client.get_version()}\n")
    print(f"[success] Check Quantum Leap version:\n  {ql_client.get_version()}\n")
