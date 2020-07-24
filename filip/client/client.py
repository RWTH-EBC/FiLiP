from config import Config
from iota import Agent
from ocb import Orion
from timeseries import QuantumLeap
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from requests import Session
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import LegacyApplicationClient, \
    MobileApplicationClient, \
    BackendApplicationClient
import logging
import json
import errno

logger = logging.getLogger('client')

auth = {'type': 'oauth2',
        'workflow': 'resource_owner_password_credentials_grant',
        'secret': r'D:\Projects\N5GEH\n5geh.tools.FiLiP\secrets.json', }

class Client:
    def __init__(self):
        auth_types = {'basicauth': self.__http_basic_auth,
                      'digestauth': self.__http_digest_auth,
                      'oauth2': self.__oauth2}

        self.config = Config(
            path=r'D:\Projects\N5GEH\n5geh.tools.FiLiP\config.json')

        self.config['auth'] = auth
        self.__credentials = {}
        if self.config['auth']:
            assert self.config['auth']['type'].lower() in auth_types.keys()
            self.__get_secrets(path=self.config['auth']['secret'])
            auth_types[self.config['auth']['type']]()
        else:
            self.session = Session()
        self.iota = Agent(config=self.config, session=self.session)
        self.ocb = Orion(config=self.config, session=self.session)
        self.timeseries = QuantumLeap(config=self.config, session=self.session)

    @property
    def headers(self):
        return self.session.headers

    @property
    def cert(self):
        return self.session.cert

    @property
    def credentials(self):
        return self.__credentials

    @credentials.setter
    def credentials(self, data: dict):
        for key in data.keys():
            self.__credentials[key] = data[key]

    @credentials.deleter
    def credentials(self):
        self.__credentials = {}

    def __get_secrets(self, path=None):
        """
        Reads credentials form secret file the path variable is pointing to.
        :param path: location of secrets-file
        :return: None
        """
        try:
            with open(path, 'r') as filename:
                logger.info(f"Reading credentials from: {path}")
                self.__credentials = json.load(filename)

        except IOError as err:
            if err.errno == errno.ENOENT:
                logger.error(f"{path} - does not exist")
            elif err.errno == errno.EACCES:
                logger.error(f"{path} - cannot be read")
            else:
                logger.error(f"{path} - some other error")

    def __http_basic_auth(self):
        """
        Initiates a client using the basic authorization mechanism provided by
        the requests package. The documentation of the package is located here:
        https://requests.readthedocs.io/en/master/user/authentication/
        The credentials must be provided via secret-file.
        """
        try:
            self.session = Session()
            self.session.auth = HTTPBasicAuth(self.__credentials['username'],
                                              self.__credentials['password'])
        except KeyError:
            pass

    def __http_digest_auth(self):
        """
        Initiates a client using the digest authorization mechanism provided by
        the requests package. The documentation of the package is located here:
        https://requests.readthedocs.io/en/master/user/authentication/
        The credentials must be provided via secret-file.
        """
        try:
            self.session = Session()
            self.session.auth = HTTPDigestAuth(self.__credentials['username'],
                                               self.__credentials['password'])
        except KeyError:
            pass

    def __oauth2(self):
        """
        Initiates a oauthclient according to the workflows defined by OAuth2.0.
        We use requests-oauthlib for this implementation. The documentation
        of the package is located here:
        https://requests-oauthlib.readthedocs.io/en/latest/index.html
        The information for workflow selection must be provided via
        filip-config. The credentials must be provided via secrets-file.
        :return: None
        """
        oauth2clients = {'authorization_code_grant': None,
                         'implicit_grant': MobileApplicationClient,
                         'resource_owner_password_credentials_grant':
                             LegacyApplicationClient,
                         'client_credentials_grant': BackendApplicationClient, }
        try:
            workflow = self.config['auth']['workflow']
        except KeyError:
            logger.warning(f"No workflow for OAuth2 defined! Default "
                           f"workflow will used: Authorization Code Grant."
                           f"Other oauth2-workflows available are: "
                           f"{oauth2clients.keys()}")
            workflow = 'authorization_code_grant'

        oauthclient = oauth2clients[workflow](client_id=self.__credentials[
            'client_id'])
        self.session = OAuth2Session(client_id=None,
                                     client=oauthclient,
                                     auto_refresh_url=self.__credentials[
                                         'token_url'],
                                     auto_refresh_kwargs={
                                         self.__credentials['client_id'],
                                         self.__credentials['client_secret']})

        self.__token = self.session.fetch_token(
            token_url=self.__credentials['token_url'],
            username=self.__credentials['username'],
            password=self.__credentials['password'],
            client_id=self.__credentials['client_id'],
            client_secret=self.__credentials['client_secret'])

    def __token_saver(self, token):
        self.__token = token

