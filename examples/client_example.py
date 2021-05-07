import logging
from filip.cb import ContextBrokerClient
from filip.core.models import FiwareHeader
from filip.timeseries import QuantumLeapClient

logger = logging.getLogger(__name__)

if __name__ == '__main__':

    logger.info("------Setting up clients------")
    with QuantumLeapClient(fiware_header=FiwareHeader(service='filip',
                                                      service_path='/testing')) as \
            ql_client:
        print("Quantum Leap " + ql_client.get_version().__str__() + " at url " +
              ql_client.base_url)

    with ContextBrokerClient(fiware_header=FiwareHeader(service='filip',
                                                        service_path='/testing')) as \
            cb_client:
        for key, value in cb_client.get_version().items():
            print("Context broker version " + value["version"] + " at url " +
                  cb_client.base_url)
