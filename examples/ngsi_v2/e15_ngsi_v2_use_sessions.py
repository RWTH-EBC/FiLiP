"""
# This example shows how to manipulate settings like retry strategy and certificate verification on requests by
including session object with the client request.
"""

import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3 import Retry

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

if __name__ == "__main__":

    # 1. Create fiware header
    fiware_header = FiwareHeader(service=SERVICE, service_path=SERVICE_PATH)

    # (Optional) 2. Set retry strategy in the session
    retry_strategy = Retry(
        total=5,  # Maximum number of retries
        backoff_factor=1,  # Exponential backoff (1, 2, 4, 8, etc.)
        status_forcelist=[
            429,
            500,
            502,
            503,
            504,
        ],  # Retry on these HTTP status codes
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    # (Optional) 3. Disable certificate verification for the request
    session.verify = False

    # 4. Create a context broker client including the session object
    cb_client = ContextBrokerClient(
        url=CB_URL, fiware_header=fiware_header, session=session
    )

    # (Optional) 5. Make desired requests using the client
    entity_list = cb_client.get_entity_list()
