"""
Module for FIWARE api client
"""
import logging
import json
import errno
from typing import Optional, Union, Dict
from pathlib import Path
from pydantic import BaseModel, AnyHttpUrl
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from requests import Session
from filip.clients.base_http_client import BaseHttpClient
from filip.config import settings
from filip.models.base import FiwareHeader
from filip.clients.ngsi_v2 import \
    ContextBrokerClient, \
    IoTAClient, \
    QuantumLeapClient


logger = logging.getLogger('client')


class HttpClientConfig(BaseModel):
    """
    Config class for http client
    """
    cb_url: Optional[AnyHttpUrl] = settings.CB_URL
    iota_url: Optional[AnyHttpUrl] = settings.IOTA_URL
    ql_url: Optional[AnyHttpUrl] = settings.QL_URL
    auth: Optional[Dict] = None


class HttpClient(BaseHttpClient):
    """
    Master client. This client contains all implemented sub clients based on
    the principal of composition. Hence, each sub client is accessible from
    this client, but they share a general config and if provided a session.
    """
    def __init__(self,
                 config: Union[str, Path, HttpClientConfig, Dict] = None,
                 session: Session = None,
                 fiware_header: FiwareHeader = None,
                 **kwargs):
        """
        Constructor for master client
        Args:
            config (Union[str, Path, Dict]): Configuration object
            session (request.Session): Session object
            fiware_header (FiwareHeader): Fiware header
            **kwargs: Optional arguments that ``request`` takes.
        """
        if config:
            self.config = config
        else:
            self.config = HttpClientConfig()

        super().__init__(session=session,
                         fiware_header=fiware_header,
                         **kwargs)

        # initialize sub clients
        self.cb = ContextBrokerClient(url=self.config.cb_url,
                                      session=self.session,
                                      fiware_header=self.fiware_headers,
                                      **self.kwargs)

        self.iota = IoTAClient(url=self.config.iota_url,
                               session=self.session,
                               fiware_header=self.fiware_headers,
                               **self.kwargs)

        self.timeseries = QuantumLeapClient(url=self.config.ql_url,
                                            session=self.session,
                                            fiware_header=self.fiware_headers,
                                            **self.kwargs)

        # from here on deprecated?
        auth_types = {'basicauth': self.__http_basic_auth,
                      'digestauth': self.__http_digest_auth}
        # 'oauth2': self.__oauth2}

        if self.config.auth:
            assert self.config.auth['type'].lower() in auth_types.keys()
            self.__get_secrets_file(path=self.config.auth['secret'])
            auth_types[self.config.auth['type']]()

        self.__secrets = {"username": None,
                          "password": None,
                          "client_id": None,
                          "client_secret": None}

    @property
    def config(self):
        """Return current config"""
        return self._config

    @config.setter
    def config(self, config: HttpClientConfig):
        """Set a new config"""
        if isinstance(config, HttpClientConfig):
            self._config = config
        elif isinstance(config, (str, Path)):
            with open(config) as f:
                config_json = f.read()
                self._config = HttpClientConfig.model_validate_json(config_json)
        else:
            self._config = HttpClientConfig.model_validate(config)

    @property
    def cert(self):
        """Return session certificate"""
        return self.session.cert

    @property
    def secrets(self):
        """Returns secrets"""
        return self.__secrets

    @secrets.setter
    def secrets(self, data: dict):
        """Set new secrets"""
        self.__secrets.update(data)

    @secrets.deleter
    def secrets(self):
        """Delete secrets"""
        self.__secrets = {}

    def __get_secrets_file(self, path=None):
        """
        Reads credentials form secret file the path variable is pointing to.

        Args:
            path: location of secrets-file
        Returns:
             None
        """
        try:
            with open(path, 'r') as filename:
                logger.info("Reading credentials from: %s", path)
                self.__secrets.update(json.load(filename))

        except IOError as err:
            if err.errno == errno.ENOENT:
                logger.error("%s - does not exist", path)
            elif err.errno == errno.EACCES:
                logger.error("%s - cannot be read", path)
            else:
                logger.error("%s - some other error", path)

    def __http_basic_auth(self):
        """
        Initiates a client using the basic authorization mechanism provided by
        the requests package. The documentation of the package is located here:
        https://requests.readthedocs.io/en/master/user/authentication/
        The credentials must be provided via secret-file.
        """
        try:
            self.session = Session()
            self.session.auth = HTTPBasicAuth(self.__secrets['username'],
                                              self.__secrets['password'])
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
            self.session.auth = HTTPDigestAuth(self.__secrets['username'],
                                               self.__secrets['password'])
        except KeyError:
            pass

    # def __oauth2(self):
    #    """
    #    Initiates a oauthclient according to the workflows defined by OAuth2.0.
    #    We use requests-oauthlib for this implementation. The documentation
    #    of the package is located here:
    #    https://requests-oauthlib.readthedocs.io/en/latest/index.html
    #    The information for workflow selection must be provided via
    #    filip-config. The credentials must be provided via secrets-file.
    #    :return: None
    #    """
    #    oauth2clients = {'authorization_code': None,
    #                     'implicit': MobileApplicationClient,
    #                     'resource_owner_password_credentials':
    #                         LegacyApplicationClient,
    #                     'client_credentials': BackendApplicationClient, }
    #    try:
    #        workflow = self.config['auth']['workflow']
    #    except KeyError:
    #        logger.warning(f"No workflow for OAuth2 defined! Default "
    #                       f"workflow will used: Authorization Code Grant."
    #                       f"Other oauth2-workflows available are: "
    #                       f"{oauth2clients.keys()}")
    #        workflow = 'authorization_code_grant'
#
    #    oauthclient = oauth2clients[workflow](client_id=self.__secrets[
    #        'client_id'])
    #    self.session = OAuth2Session(client_id=None,
    #                                 client=oauthclient,
    #                                 auto_refresh_url=self.__secrets[
    #                                     'token_url'],
    #                                 auto_refresh_kwargs={
    #                                     self.__secrets['client_id'],
    #                                     self.__secrets['client_secret']})
#
    #    self.__token = self.session.fetch_token(
    #        token_url=self.__secrets['token_url'],
    #        username=self.__secrets['username'],
    #        password=self.__secrets['password'],
    #        client_id=self.__secrets['client_id'],
    #        client_secret=self.__secrets['client_secret'])

    def __token_saver(self, token):
        self.__token = token
