"""
# This example shows how to generate an access token from an authnetication srever in order to access Fiware services
# which are protected behind an authentication/authorisation layer.
"""
import os

import requests
import urllib3

from filip.clients.ngsi_v2 import ContextBrokerClient
from filip.config import settings
from filip.models.base import FiwareHeaderSecure

urllib3.disable_warnings()
session = requests.Session()
CB_URL = settings.CB_URL
# FIWARE-Service
SERVICE = 'filip'
# FIWARE-Servicepath
SERVICE_PATH = '/'
# Provide client credentials which are used when generating access token from authentication server
CLIENT_ID = 'client_id'
CLIENT_SECRET = 'client_secret'
# TODO: Please adapt it according to your authentication server which is generating access token for the service
KEYCLOAK_HOST = 'https://keycloak.example.com'


class KeycloakPython:
    def __init__(self, keycloak_host=None, client_id=None, client_secret=None):
        """
        - Initialze the Keycloak Host , Client ID and Client secret.
        - If no parameters are passed .env file is used
        - Priority : function parameters > Class Instatiation > .env file
        """
        # if keycloak_host == None:
        #     self.keycloak_host = os.getenv('KEYCLOAK_HOST')
        # else:
        #     self.keycloak_host = keycloak_host
        self.keycloak_host = os.getenv('KEYCLOAK_HOST') if keycloak_host == None else keycloak_host
        self.client_id = os.getenv('CLIENT_ID') if client_id == None else client_id
        self.client_secret = os.getenv('CLIENT_SECRET') if client_secret == None else client_secret

    def get_access_token(self, keycloak_host=None, client_id=None, client_secret=None):
        """
        - Get access token for a given client id and client secret.
        """
        self.keycloak_host = keycloak_host if keycloak_host != None else self.keycloak_host
        self.client_id = client_id if client_id != None else self.client_id
        self.client_secret = client_secret if client_secret != None else self.client_secret
        self.data = {'client_id': self.client_id,
                     'client_secret': self.client_secret,
                     'scope': 'email',
                     'grant_type': 'client_credentials',
                     }
        try:
            headers = {"content-type": "application/x-www-form-urlencoded"}
            access_data = requests.post(self.keycloak_host, data=self.data, headers=headers)
            expires_in = access_data.json()['expires_in']
            access_token = access_data.json()['access_token']
            return access_token, expires_in
        except requests.exceptions.RequestException as err:
            raise KeycloakPythonException(err.args[0])

    def get_data(self, client_host, headers={}, keycloak_host=None, client_id=None, client_secret=None):
        """
        - Get data for a given api.
        - Mandatory input - Target api, fiware-service and fiware-servicepath headers
        - Optional Inmput - Keycloak host, Client ID, Client Secret
        """
        access_token, expires_in = self.get_access_token(keycloak_host=keycloak_host, client_id=client_id,
                                                         client_secret=client_secret)
        headers['Authorization'] = 'Bearer %s' % (access_token)
        response = requests.get(client_host, headers=headers)
        return response.text

    def post_data(self, client_host, data, headers={}, keycloak_host=None, client_id=None, client_secret=None):
        """
        - Post data for a given api.
        - Mandatory input - Target api, headers, request body.
        - Optional Inmput - Keycloak host, Client ID, Client Secret.
        """
        access_token, expires_in = self.get_access_token(keycloak_host=keycloak_host, client_id=client_id,
                                                         client_secret=client_secret)
        headers['Content-Type'] = 'application/json'
        headers['Authorization'] = 'Bearer %s' % (access_token)
        response = requests.post(client_host, data=data, headers=headers)
        return response

    def patch_data(self, client_host, json, headers={}, keycloak_host=None, client_id=None, client_secret=None):
        """
        - Patch data for a given api.
        - Mandatory input - Target api, headers, request body.
        - Optional Inmput - Keycloak host, Client ID, Client Secret.
        """
        access_token, expires_in = self.get_access_token(keycloak_host=keycloak_host, client_id=client_id,
                                                         client_secret=client_secret)
        headers['Content-Type'] = 'application/json'
        headers['Authorization'] = 'Bearer %s' % (access_token)
        response = requests.patch(url=client_host, json=json, headers=headers)
        return response


class KeycloakPythonException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


if __name__ == "__main__":
    # get token from keycloak
    token, in_sec = KeycloakPython(KEYCLOAK_HOST, CLIENT_ID, CLIENT_SECRET).get_access_token()

    # create secure fiware header with authorisation token
    fiware_header = FiwareHeaderSecure(service=SERVICE,
                                       service_path=SERVICE_PATH,
                                       authorization='Bearer %s' % token)

    # create a context broker client
    cb_client = ContextBrokerClient(url=CB_URL, fiware_header=fiware_header, session=session)
    # you don't need to set any extra parameter for requesting the service besides setting session in the client object
    entity_list = cb_client.get_entity_list()
