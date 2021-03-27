from filip.core import Client

if __name__ == '__main__':
    client = Client(config="../config.json")
    client.iota.url = 'https://json.iot.n5geh.eonerc.rwth-aachen.de'
    client.cb.url = 'https://api.n5geh.eonerc.rwth-aachen.de'
    client.headers.update({'FiwareService': 'Test'})
    r=client.session.get(url='https://ts.api.n5geh.eonerc.rwth-aachen.de/version')
    print(f"{r.status_code}")
