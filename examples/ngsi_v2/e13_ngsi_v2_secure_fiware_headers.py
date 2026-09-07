"""
Example e13: Obtain FIWARE tokens via python-keycloak and refresh them per request.
The FiwareHeaderSecureKeycloak class uses a KeycloakTokenManager to fetch and cache tokens, refreshing them before they
expire so every outgoing request receives a fresh Authorization header.
"""

import os
import time
import requests
import urllib3
from filip.clients.ngsi_v2 import ContextBrokerClient
from filip.config import settings
from filip.models.base import KeycloakTokenManager, FiwareHeaderSecureDynamic

urllib3.disable_warnings()
session = requests.Session()
CB_URL = settings.CB_URL
# FIWARE-Service
SERVICE = "securitytest1"
# FIWARE-Servicepath
SERVICE_PATH = "/"
# TODO Provide client credentials from environment (fall back to placeholders for demo purposes)
KEYCLOAK_HOST = os.getenv("KEYCLOAK_HOST", "https://keycloak.example.com")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "example-realm")
CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "demo-client")
CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "demo-secret")
# TODO if username password are not provided, client_credentials will be used
USERNAME = os.getenv("KEYCLOAK_USERNAME", None)
PASSWORD = os.getenv("KEYCLOAK_PASSWORD", None)


def demonstrate_dynamic_requests(
    client: ContextBrokerClient, header: FiwareHeaderSecureDynamic
) -> None:
    """Print successive Authorization headers to show automatic refreshes."""
    print("If everything works, you should see two different access tokens printed\n")
    for attempt in range(2):
        # When model_dump is called, the @computed_field dynamically checks the token cache
        headers = header.model_dump(by_alias=True)
        print(f"[Attempt {attempt + 1}] Authorization: {headers['Authorization']}")
        try:
            client.get_entity_list()
        except Exception as exc:
            print(f"Call #{attempt + 1} failed in demo environment: {exc}")

        if attempt == 0:
            # ---------------------------------------------------------
            # SHOWCASE: Forcing token expiration to prove auto-refresh
            # ---------------------------------------------------------
            print(
                "[Demo] Artificially expiring the token cache to simulate time passing..."
            )
            header.token_manager._expiry_time = time.time() - 100
            print(
                "[Demo] The next loop iteration will automatically fetch a new token without manual intervention."
            )

        time.sleep(2)


if __name__ == "__main__":
    # Initialize the token manager once
    global_token_manager = KeycloakTokenManager(
        server_url=KEYCLOAK_HOST,
        realm_name=KEYCLOAK_REALM,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        username=USERNAME,
        password=PASSWORD,
    )

    # Pass the shared manager to the new header class
    fiware_header = FiwareHeaderSecureDynamic(
        service=SERVICE,
        service_path=SERVICE_PATH,
        token_manager=global_token_manager,
    )

    cb_client = ContextBrokerClient(
        url=CB_URL, fiware_header=fiware_header, session=session
    )

    demonstrate_dynamic_requests(client=cb_client, header=fiware_header)
