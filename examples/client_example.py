from filip.client import Client
import requests
import json
from bs4 import BeautifulSoup
from authlib.integrations.requests_client import OAuth2Session
from authlib.integrations.requests_client import OAuth2Auth


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:68.0) Gecko/20100101 Firefox/68.0',
    'Connection': 'keep-alive',
}

def authworkflow(s, r, data):
    soup = BeautifulSoup(r.content, 'html.parser')
    url = soup.find('form')['action']
    r = s.post(url,
               headers=headers,
               cookies=r.cookies.get_dict(),
               data=data)
    return r

if __name__ == '__main__':
    #client = Client()
    #client.iota.url = 'https://json.iot.n5geh.eonerc.rwth-aachen.de'
    #client.ocb.url = 'https://api.n5geh.eonerc.rwth-aachen.de'
    #client.headers.update({'FiwareService': 'Test'})
    #r=client.session.get(url='https://ts.api.n5geh.eonerc.rwth-aachen.de'
    #                        '/version')
    #print(f"{r.status_code}")
    #client.iota.test_connection()
    #client.ocb.test_connection()
#
#
    #with requests.Session() as s:
    #    r = s.get(url='https://ts.api.n5geh.eonerc.rwth-aachen.de/version')
    #    r = authworkflow(s, r, client.credentials)
    #    print(f"{r.text}")
    #    r = s.get(url='https://json.iot.n5geh.eonerc.rwth-aachen.de/version')
    #    print(r.text)
    #    r = s.get(url='https://api.n5geh.eonerc.rwth-aachen.de/version')
    #    print(r.text)
#
    #print('done')
    path=r'D:\Projects\N5GEH\n5geh.tools.FiLiP\secrets.json'
    with open(path, 'r') as secrets:
        secrets=json.load(secrets)
    client_id = secrets['client_id']
    client_secret = secrets['client_secret']
    scope = 'user:email'
    authorization_endpoint = 'https://github.com/login/oauth/authorize'
    token_endpoint = 'https://github.com/login/oauth/access_token'
    account_url = 'https://api.github.com/user'

    with requests.Session() as client:
        r= client.get(account_url , auth=(secrets['username'],
                                            secrets['password']))
        print(r.text)

    with OAuth2Session(client_id=client_id,
                       client_secret=client_secret,
                       authorization_endpoint=authorization_endpoint,
                       token_endpoint=token_endpoint,
                       scope=scope,
                       ) as client:
        r = client.get(account_url , auth=(secrets['username'],
                                           secrets['password']))
        print(r.text)
        authorization_response='http://127.0.0.1:5000/auth/oauth/github?code=eeebfed12b40189defd1&state=teUSWwiCDzzMnSN63uwmJTs19S5T0G'
        r = client.fetch_token(token_endpoint,
                               authorization_response=authorization_response)
        print(r.text)

        token = client.fetch_token()
        print(token)

    with OAuth2Session(client_id, client_secret) as client:
        client.fetch_token(token=token)
        resp = client.get(account_url)


# TODO: https://stackoverflow.com/questions/38380086/sending-list-of-dicts-as-value-of-dict-with-requests-post-going-wrong





