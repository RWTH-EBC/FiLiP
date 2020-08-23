from filip.client import Client

if __name__ == '__main__':
    client = Client(config_file="../config.json")
    client.iota.url = 'https://json.iot.n5geh.eonerc.rwth-aachen.de'
    client.ocb.url = 'https://api.n5geh.eonerc.rwth-aachen.de'
    client.headers.update({'FiwareService': 'Test'})
    r=client.session.get(url='https://ts.api.n5geh.eonerc.rwth-aachen.de'
                            '/version')
    print(f"{r.status_code}")
    client.iota.test_connection()
    client.ocb.test_connection()

# TODO: https://stackoverflow.com/questions/38380086/sending-list-of-dicts-as-value-of-dict-with-requests-post-going-wrong





