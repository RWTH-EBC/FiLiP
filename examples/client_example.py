from filip.client import Client
import requests
from bs4 import BeautifulSoup

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
    client = Client()
    client.iota.url = 'https://json.iot.n5geh.eonerc.rwth-aachen.de'
    client.ocb.url = 'https://api.n5geh.eonerc.rwth-aachen.de'
    client.headers.update({'FiwareService': 'Test'})
    client.iota.test_connection()
    client.ocb.test_connection()

    with requests.Session() as s:
        r = s.get(url='https://ts.api.n5geh.eonerc.rwth-aachen.de/version')
        r = authworkflow(s, r, client.credentials)
        print(f"{r.text}")
        r = s.get(url='https://json.iot.n5geh.eonerc.rwth-aachen.de/version')
        print(r.text)
        r = s.get(url='https://api.n5geh.eonerc.rwth-aachen.de/version')
        print(r.text)






