from filip.client import Client

if __name__ == '__main__':
    client = Client()
    client.iota.url='https://json.iot.n5geh.eonerc.rwth-aachen.de'
    client.iota.test_connection()
    client.cb.url='https://api.n5geh.eonerc.rwth-aachen.de'
    client.cb.test_connection()
    client.timeseries.url='https://ts.api.n5geh.eonerc.rwth-aachen.de'
    client.timeseries.test_connection()
