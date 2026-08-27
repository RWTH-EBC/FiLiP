"""
Example e13: Obtain FIWARE tokens via python-keycloak and refresh them per request.
The FiwareHeaderSecureKeycloak class uses a KeycloakTokenManager to fetch and cache tokens, refreshing them before they
expire so every outgoing request receives a fresh Authorization header.
"""

import json
import os
import time
from pathlib import Path

import requests
import urllib3
from filip.clients.ngsi_v2 import ContextBrokerClient, IoTAClient, QuantumLeapClient
from filip.config import settings
from filip.models.base import KeycloakTokenManager, FiwareHeaderSecureDynamic

urllib3.disable_warnings()
CB_URL = "https://n5geh.eonerc.rwth-aachen.de/orion/"
IOTA_URL = "https://n5geh.eonerc.rwth-aachen.de/iota/"
QL_URL = "https://n5geh.eonerc.rwth-aachen.de/ql/"
QL_URL_INTERNAL = "http://quantumleap-quantumleap.timeseries.svc.cluster.local:8668"
# MQTT settings
MQTT_BROKER_URL = "mqtt://mqtt.n5geh.eonerc.rwth-aachen.de:8883"
MQTT_USER = "ebcdev"
MQTT_PW = "ebcdev"
MQTT_INTERNAL_URL = "mqtt://emqx-listeners.emqx.svc.cluster.local:1883"

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

with open(Path("credential.json"), "r") as f:
    # read credential
    creds = json.load(f)
    service = creds["service"]
    assert service == SERVICE
    secret = creds.get("secret")
CLIENT_ID = f"{SERVICE}-admin"
CLIENT_SECRET = secret

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
