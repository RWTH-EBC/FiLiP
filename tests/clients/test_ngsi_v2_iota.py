"""
Test for iota http client
"""
import copy
import unittest
import logging
import requests

from uuid import uuid4

from filip.models.base import FiwareHeader
from filip.clients.ngsi_v2 import \
    ContextBrokerClient, \
    IoTAClient
from filip.models.ngsi_v2.iot import \
    ServiceGroup, \
    Device, \
    DeviceAttribute, \
    DeviceCommand, \
    LazyDeviceAttribute, \
    StaticDeviceAttribute
from filip.utils.cleanup import clear_all, clean_test
from tests.config import settings


logger = logging.getLogger(__name__)


class TestAgent(unittest.TestCase):
    def setUp(self) -> None:
        self.fiware_header = FiwareHeader(
            service=settings.FIWARE_SERVICE,
            service_path=settings.FIWARE_SERVICEPATH)
        clear_all(fiware_header=self.fiware_header,
                  cb_url=settings.CB_URL,
                  iota_url=settings.IOTA_URL)
        self.service_group1 = ServiceGroup(entity_type='Thing',
                                           resource='/iot/json',
                                           apikey=str(uuid4()))
        self.service_group2 = ServiceGroup(entity_type='OtherThing',
                                           resource='/iot/json',
                                           apikey=str(uuid4()))
        self.device = {
            "device_id": "test_device",
            "service": self.fiware_header.service,
            "service_path": self.fiware_header.service_path,
            "entity_name": "test_entity",
            "entity_type": "test_entity_type",
            "timezone": 'Europe/Berlin',
            "timestamp": None,
            "apikey": "1234",
            "endpoint": None,
            "transport": 'HTTP',
            "expressionLanguage": None
        }
        self.client = IoTAClient(
            url=settings.IOTA_URL,
            fiware_header=self.fiware_header)

    def test_get_version(self):
        with IoTAClient(
                url=settings.IOTA_URL,
                fiware_header=self.fiware_header) as client:
            self.assertIsNotNone(client.get_version())

    def test_service_group_model(self):
        pass

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                iota_url=settings.IOTA_URL)
    def test_service_group_endpoints(self):
        self.client.post_groups(service_groups=[self.service_group1,
                                                self.service_group2])
        groups = self.client.get_group_list()
        with self.assertRaises(requests.RequestException):
            self.client.post_groups(groups, update=False)

        self.client.get_group(resource=self.service_group1.resource,
                              apikey=self.service_group1.apikey)

        clear_all(fiware_header=self.fiware_header,
                  iota_url=settings.IOTA_URL)

    def test_device_model(self):
        device = Device(**self.device)
        self.assertEqual(self.device,
                         device.dict(exclude_unset=True))

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                cb_url=settings.CB_URL,
                iota_url=settings.IOTA_URL)
    def test_device_endpoints(self):
        """
        Test device creation
        """
        # Clean up Fiware test state, this test can fail if the device was not
        # correctly removed before
        clear_all(fiware_header=self.fiware_header,
                  cb_url=settings.CB_URL,
                  iota_url=settings.IOTA_URL)

        with IoTAClient(
                url=settings.IOTA_URL,
                fiware_header=self.fiware_header) as client:
            client.get_device_list()
            device = Device(**self.device)

            attr = DeviceAttribute(name='temperature',
                                   object_id='t',
                                   type='Number',
                                   entity_name='test')
            attr_command = DeviceCommand(name='open')
            attr_lazy = LazyDeviceAttribute(name='pressure',
                                            object_id='p',
                                            type='Text',
                                            entity_name='pressure')
            attr_static = StaticDeviceAttribute(name='hasRoom',
                                                type='Relationship',
                                                value='my_partner_id')
            device.add_attribute(attr)
            device.add_attribute(attr_command)
            device.add_attribute(attr_lazy)
            device.add_attribute(attr_static)

            client.post_device(device=device)
            device_res = client.get_device(device_id=device.device_id)
            self.assertEqual(device.dict(exclude={'service',
                                                  'service_path',
                                                  'timezone'}),
                             device_res.dict(exclude={'service',
                                                      'service_path',
                                                      'timezone'}))
            self.assertEqual(self.fiware_header.service, device_res.service)
            self.assertEqual(self.fiware_header.service_path,
                             device_res.service_path)

            #cleanup
            clear_all(fiware_header=self.fiware_header,
                      cb_url=settings.CB_URL,
                      iota_url=settings.IOTA_URL)

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                cb_url=settings.CB_URL,
                iota_url=settings.IOTA_URL)
    def test_metadata(self):
        """
        Test for metadata works but the api of iot agent-json seems not
        working correctly
        Returns:
            None
        """
        metadata = {"accuracy": {"type": "Text",
                                 "value": "+-5%"}}
        attr = DeviceAttribute(name="temperature",
                               object_id="temperature",
                               type="Number",
                               metadata=metadata)
        device = Device(**self.device)
        device.device_id = "device_with_meta"
        device.add_attribute(attribute=attr)
        logger.info(device.json(indent=2))

        with IoTAClient(
                url=settings.IOTA_URL,
                fiware_header=self.fiware_header) as client:
            client.post_device(device=device)
            logger.info(client.get_device(device_id=device.device_id).json(
                indent=2, exclude_unset=True))

        with ContextBrokerClient(
                url=settings.CB_URL,
                fiware_header=self.fiware_header) as client:
            logger.info(client.get_entity(entity_id=device.entity_name).json(
                indent=2))

    def test_deletions(self):
        """
        Test the deletion of a context entity/device if the state is always
        correctly cleared
        """
        self.tearDown()

        device_id = 'device_id'
        entity_id = 'entity_id'

        device = Device(device_id=device_id,
                        entity_name=entity_id,
                        entity_type='Thing2',
                        protocol='IoTA-JSON',
                        transport='MQTT',
                        apikey='filip-iot-test-device')

        cb_client = ContextBrokerClient(fiware_header=self.fiware_header)

        # Test 1: Only delete device
        # delete without optional parameter -> entity needs to continue existing
        self.client.post_device(device=device)
        self.client.delete_device(device_id=device_id)
        self.assertTrue(
            len(cb_client.get_entity_list(entity_ids=[entity_id])) == 1)
        cb_client.delete_entity(entity_id=entity_id, entity_type='Thing2')

        # Test 2:Delete device and corresponding entity
        # delete with optional parameter -> entity needs to be deleted
        self.client.post_device(device=device)
        self.client.delete_device(device_id=device_id,
                                  delete_entity=True)
        self.assertTrue(
            len(cb_client.get_entity_list(entity_ids=[entity_id])) == 0)

        # Test 3:Delete device and corresponding entity,
        #        that is linked to multiple devices
        # delete with optional parameter -> entity needs to be deleted
        self.client.post_device(device=device)
        device2 = copy.deepcopy(device)
        device2.device_id = "device_id2"
        self.client.post_device(device=device2)
        self.assertRaises(Exception, self.client.delete_device,
                          device_id=device_id, delete_entity=True)
        self.assertTrue(
            len(cb_client.get_entity_list(entity_ids=[entity_id])) == 1)
        self.client.delete_device(device_id=device2.device_id)

        # Test 4: Only delete entity
        # delete without optional parameter -> device needs to continue existing
        self.client.post_device(device=device)
        cb_client.delete_entity(entity_id=entity_id, entity_type='Thing2')
        self.client.get_device(device_id=device_id)
        self.client.delete_device(device_id=device_id)

        # Test 5: Delete entity, and all devices
        # # delete with optional parameter -> all devices need to be deleted
        self.client.post_device(device=device)
        device2 = copy.deepcopy(device)
        device2.device_id = "device_id2"
        self.client.post_device(device=device2)
        cb_client.delete_entity(entity_id=entity_id, delete_devices=True,
                                entity_type='Thing2')
        self.assertEqual(len(self.client.get_device_list()), 0)

        cb_client.close()
        
        #clean up
        clear_all(fiware_header=self.fiware_header,
                  cb_url=settings.CB_URL,
                  iota_url=settings.IOTA_URL)

    def tearDown(self) -> None:
        """
        Cleanup test server
        """
        self.client.close()
        clear_all(fiware_header=self.fiware_header,
                  cb_url=settings.CB_URL,
                  iota_url=settings.IOTA_URL)