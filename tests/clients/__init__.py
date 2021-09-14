import unittest

import requests
from filip.models import FiwareHeader

from filip.models.ngsi_v2.context import ContextEntity

from filip.clients.ngsi_v2 import IoTAClient, ContextBrokerClient


def start_test_run(self):
    """
    https://docs.python.org/3/library/unittest.html#unittest.
    TestResult.startTestRun
    Called once before any tests are executed.

    :return:
    """
    # Initialise Test Environment -> clean up all Entities/Devices in testing
    try:
        fiware_header = FiwareHeader(service='filip', service_path='/testing')

        with IoTAClient(fiware_header=fiware_header) as client:
            devices = client.get_device_list()
            for device in devices:
                client.delete_device(device_id=device.device_id)

        with ContextBrokerClient(fiware_header=fiware_header) as client:
            entities = [ContextEntity(id=entity.id, type=entity.type) for
                        entity in client.get_entity_list()]
            client.update(entities=entities, action_type='delete')

    except requests.RequestException:
        pass


setattr(unittest.TestResult, 'startTestRun', start_test_run)


def stop_test_run(self):
    """
    https://docs.python.org/3/library/unittest.html#unittest.
    TestResult.stopTestRun
    Called once after all tests are executed.

    :return:
    """
    pass


setattr(unittest.TestResult, 'stopTestRun', stop_test_run)
