"""
Tests filter functions in filip.utils.filter
"""
import unittest
from datetime import datetime

from filip.clients.ngsi_v2 import ContextBrokerClient
from filip.models.base import FiwareHeader
from filip.models.ngsi_v2.base import EntityPattern
from filip.models.ngsi_v2.iot import Device
from filip.models.ngsi_v2.subscriptions import Subscription
from filip.utils import filter
from filip.utils.cleanup import clear_all
from tests.config import settings


class TestFilterFunctions(unittest.TestCase):

    def setUp(self) -> None:
        """
        Setup test data and client

        Returns:
            None
        """
        self.fiware_header = FiwareHeader(
            service=settings.FIWARE_SERVICE,
            service_path=settings.FIWARE_SERVICEPATH)
        self.url = settings.CB_URL
        self.client = ContextBrokerClient(url=self.url,
                                          fiware_header=self.fiware_header)
        clear_all(fiware_header=self.fiware_header,
                  cb_url=self.url)
        self.subscription = Subscription.parse_obj({
            "description": "One subscription to rule them all",
            "subject": {
                "entities": [
                    {
                        "idPattern": ".*",
                        "type": "Room"
                    }
                ],
                "condition": {
                    "attrs": [
                        "temperature"
                    ],
                    "expression": {
                        "q": "temperature>40"
                    }
                }
            },
            "notification": {
                "http": {
                    "url": "http://localhost:1234"
                },
                "attrs": [
                    "temperature",
                    "humidity"
                ]
            },
            "expires": datetime.now(),
            "throttling": 0
        })
        self.subscription.subject.entities[0] = EntityPattern(idPattern=".*",
                                                              type="Room")

    def test_filter_subscriptions_by_entity(self):
        subscription_1 = self.subscription.copy()
        self.client.post_subscription(subscription=subscription_1)

        subscription_2 = self.subscription.copy()
        subscription_2.subject.entities[0] = EntityPattern(idPattern=".*",
                                                           type="Building")
        self.client.post_subscription(subscription=subscription_2)

        filtered_sub = filter.filter_subscriptions_by_entity("test",
                                                             "Building",
                                                             self.url,
                                                             self.fiware_header)
        self.assertGreater(len(filtered_sub), 0)

    def test_filter_device_list(self) -> None:
        """
        Test the function filter_device_list
        """
        # create devices
        base_device_id = "device:"

        base_entity_id_1 = "urn:ngsi-ld:TemperatureSensor:"
        entity_type_1 = "TemperatureSensor"

        base_entity_id_2 = "urn:ngsi-ld:HumiditySensor:"
        entity_type_2 = "HumiditySensor"

        devices = []

        for i in range(20):
            base_entity_id = base_entity_id_1 if i < 10 else base_entity_id_2
            entity_type = entity_type_1 if i < 10 else entity_type_2

            device_id = base_device_id + str(i)
            entity_id = base_entity_id + str(i)
            device = Device(
                service=settings.FIWARE_SERVICE,
                service_path=settings.FIWARE_SERVICEPATH,
                device_id=device_id,
                entity_type=entity_type,
                entity_name=entity_id
            )
            devices.append(device)

        entity_id_list = [device.entity_name for device in devices]
        device_id_list = [device.device_id for device in devices]

        # test with no inputs
        self.assertEqual(len(filter.filter_device_list(devices)), len(devices))

        # test with entity type
        self.assertEqual(len(filter.filter_device_list(
            devices,
            entity_types=[entity_type_1])),
            10)
        self.assertEqual(len(filter.filter_device_list(
            devices,
            entity_types=[entity_type_1, entity_type_2])),
            20)

        # test with entity id
        self.assertEqual(len(filter.filter_device_list(
            devices,
            entity_names=entity_id_list[5:])),
            len(entity_id_list[5:]))

        # test with entity type and entity id
        self.assertEqual(len(filter.filter_device_list(
            devices,
            entity_names=entity_id_list,
            entity_types=[entity_type_1])),
            10)

        # test with device id
        self.assertEqual(len(filter.filter_device_list(
            devices, device_ids=device_id_list[5:])),
            len(device_id_list[5:]))

        # test with single args
        self.assertEqual(len(filter.filter_device_list(
            devices,
            device_ids=devices[0].device_id)), 1)

        self.assertEqual(len(filter.filter_device_list(
            devices,
            entity_names=devices[0].entity_name)), 1)

        self.assertNotEqual(len(filter.filter_device_list(
            devices,
            entity_types=devices[0].entity_type)), 1)

        self.assertEqual(len(filter.filter_device_list(
            devices,
            device_ids=devices[0].device_id,
            entity_names=devices[0].entity_name,
            entity_types=devices[0].entity_type)), 1)

        # test for errors
        with self.assertRaises(TypeError):
            filter.filter_device_list(devices, device_ids={'1234'})
        with self.assertRaises(TypeError):
            filter.filter_device_list(devices, entity_names={'1234'})
        with self.assertRaises(TypeError):
            filter.filter_device_list(devices, entity_types={'1234'})


    def tearDown(self) -> None:
        """
        Cleanup test server
        """
        self.client.close()
        clear_all(fiware_header=self.fiware_header,
                  cb_url=self.url)
