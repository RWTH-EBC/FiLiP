from iota import Agent
from config import Config
from cb import Orion
from timeseries import QuantumLeap
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from requests_oauthlib import OAuth1
from requests import Session
from requests_oauthlib import OAuth2Session


class Client(OAuth2Session, Session):
    def __init__(self):
        self.config = Config(
            path=r'D:\Projects\N5GEH\n5geh.tools.FiLiP\config.json')
        self.authtype = 'oauth2'
        self.credentials = {'user': 'tstorek',
                            'password': 'Tpbs286833n5geh!',
                            'client_id': r'testpage',
                            'client_secret':
                                r'683ab7d1-f261-4e83-b5d0-33625359a723',
                            'token_url':
                                'https://auth.n5geh.de/auth/realms/n5geh/protocol/openid-connect/token'}
        self.user = self.credentials['user']
        self.password = self.credentials['password']
        self.auth_types = {'basicauth': HTTPBasicAuth(self.user,
                                                      self.password),
                           'digestauth': HTTPDigestAuth(self.user,
                                                         self.password),
                           'oauth1': OAuth1('YOUR_APP_KEY',
                                            'YOUR_APP_SECRET',
                                            'USER_OAUTH_TOKEN',
                                            'USER_OAUTH_TOKEN_SECRET')}
        #
        from oauthlib.oauth2 import LegacyApplicationClient
        client = LegacyApplicationClient(client_id=self.credentials['client_id'])
        OAuth2Session.__init__(self,
                               client_id=None,
                               client=client,
                               auto_refresh_url=self.credentials['token_url'],
                               auto_refresh_kwargs={
                                          self.credentials['client_id'],
                                          self.credentials['client_secret']})
        self.token=self.fetch_token(
            token_url=self.credentials['token_url'],
            username=self.credentials['user'],
            password=self.credentials['password'],
            client_id=self.credentials['client_id'],
            client_secret=self.credentials['client_secret'])
        if self.authtype.lower() in  self.auth_types.keys():
            Session.__init__(self)
            self.auth = self.auth_types[self.authtype.lower()]

        self.iota=Agent(config=self.config, session=self)
        self.cb=Orion(config=self.config, session=self)
        self.timeseries=QuantumLeap(config=self.config, session=self)

    def oauth2(self):
        from oauthlib.oauth2 import LegacyApplicationClient
        from requests_oauthlib import OAuth2Session
        client = LegacyApplicationClient(client_id=self.credentials['client_id'])
        session=OAuth2Session(
            client_id=None,
            client=client,
            auto_refresh_url=self.credentials['token_url'],
            auto_refresh_kwargs={self.credentials['client_id'],
                                 self.credentials['client_secret']})

        self.token = session.fetch_token(
            token_url=self.credentials['token_url'],
            username=self.credentials['user'],
            password=self.credentials['password'],
            client_id=self.credentials['client_id'],
            client_secret=self.credentials['client_secret'])
        return session

    def token_saver(self, token):
        self.token = token





