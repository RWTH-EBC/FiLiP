"""
Example e13: Obtain FIWARE tokens via python-keycloak and refresh them per request.
The FiwareHeaderSecureKeycloak class uses a KeycloakTokenManager to fetch and cache tokens, refreshing them before they
expire so every outgoing request receives a fresh Authorization header.
"""

import os
import time
from typing import Optional
import requests
import urllib3
from keycloak import KeycloakOpenID
from pydantic import ConfigDict, computed_field, PrivateAttr
from filip.clients.ngsi_v2 import ContextBrokerClient
from filip.config import settings
from filip.models.base import FiwareHeader

urllib3.disable_warnings()
session = requests.Session()
CB_URL = settings.CB_URL
# FIWARE-Service
SERVICE = "filip"
# FIWARE-Servicepath
SERVICE_PATH = "/"
# TODO Provide client credentials from environment (fall back to placeholders for demo purposes)
KEYCLOAK_HOST = os.getenv("KEYCLOAK_HOST", "https://keycloak.example.com")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "example-realm")
CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "demo-client")
CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "demo-secret")


class KeycloakTokenManager:
    """Caches and refreshes client-credential tokens coming from python-keycloak."""

    def __init__(
        self,
        keycloak_host: str,
        realm_name: str,
        client_id: str,
        client_secret: str,
        refresh_margin: int = 10,
    ):
        server_url = keycloak_host.rstrip("/") + "/"
        self._client = KeycloakOpenID(
            server_url=server_url,
            realm_name=realm_name,
            client_id=client_id,
            client_secret_key=client_secret,
        )
        self._token: Optional[str] = None
        self._expires_at: float = 0.0
        self._refresh_margin = refresh_margin

    def get_token(self) -> str:
        now = time.time()
        if not self._token or now >= (self._expires_at - self._refresh_margin):
            token_data = self._client.token(grant_type="client_credentials")
            self._token = token_data["access_token"]
            self._expires_at = now + token_data.get("expires_in", 0)
        return self._token


class FiwareHeaderSecureKeycloak(FiwareHeader):
    """Fiware header that fetches Keycloak authorization on demand."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    _token_manager: KeycloakTokenManager = PrivateAttr(default=None)

    def __init__(self, *, token_manager: KeycloakTokenManager, **data):
        super().__init__(**data)
        self._token_manager = token_manager

    @computed_field(alias="authorization", return_type=str)
    def authorization(self) -> str:
        return f"Bearer {self._token_manager.get_token()}"


def demonstrate_dynamic_requests(
    client: ContextBrokerClient, header: FiwareHeader
) -> None:
    """Print successive Authorization headers to show automatic refreshes."""

    for attempt in range(2):
        headers = header.model_dump(by_alias=True)
        print(f"Attempt {attempt + 1} Authorization: {headers['authorization']}")
        try:
            client.get_entity_list(limit=0)
        except Exception as exc:
            print(f"Call #{attempt + 1} failed in demo environment: {exc}")
        time.sleep(2)


if __name__ == "__main__":
    token_manager = KeycloakTokenManager(
        keycloak_host=KEYCLOAK_HOST,
        realm_name=KEYCLOAK_REALM,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )

    fiware_header = FiwareHeaderSecureKeycloak(
        service=SERVICE,
        service_path=SERVICE_PATH,
        token_manager=token_manager,
    )

    cb_client = ContextBrokerClient(
        url=CB_URL, fiware_header=fiware_header, session=session
    )

    demonstrate_dynamic_requests(client=cb_client, header=fiware_header)
