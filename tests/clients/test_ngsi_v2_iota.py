"""
Test for iota http client
"""
import copy
import unittest
import logging
import requests

from uuid import uuid4

from filip.models.base import FiwareHeader, DataType
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
from filip.utils.cleanup import \
    clear_all, \
    clean_test, \
    clear_context_broker, \
    clear_iot_agent 
from tests.config import settings

logger = logging.getLogger(__name__)


class TestAgent(unittest.TestCase):

    def setUp(self) -> None:
        self.fiware_header = FiwareHeader(
            service=settings.FIWARE_SERVICE,
            service_path=settings.FIWARE_SERVICEPATH)
        clear_all(fiware_header=self.fiware_header,
                  cb_url=settings.CB_URL,
                  iota_url=settings.IOTA_JSON_URL)
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
            url=settings.IOTA_JSON_URL,
            fiware_header=self.fiware_header)

    def test_get_version(self):
        with IoTAClient(
                url=settings.IOTA_JSON_URL,
                fiware_header=self.fiware_header) as client:
            self.assertIsNotNone(client.get_version())

    def test_service_group_model(self):
        pass

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                iota_url=settings.IOTA_JSON_URL)
    def test_service_group_endpoints(self):
        self.client.post_groups(service_groups=[self.service_group1,
                                                self.service_group2])
        groups = self.client.get_group_list()
        with self.assertRaises(requests.RequestException):
            self.client.post_groups(groups, update=False)

        self.client.get_group(resource=self.service_group1.resource,
                              apikey=self.service_group1.apikey)

    def test_device_model(self):
        device = Device(**self.device)
        self.assertEqual(self.device,
                         device.model_dump(exclude_unset=True))

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                cb_url=settings.CB_URL,
                iota_url=settings.IOTA_JSON_URL)
    def test_device_endpoints(self):
        """
        Test device creation
        """
        with IoTAClient(
                url=settings.IOTA_JSON_URL,
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
            self.assertEqual(device.model_dump(exclude={'service',
                                                        'service_path',
                                                        'timezone'}),
                             device_res.model_dump(exclude={'service',
                                                            'service_path',
                                                            'timezone'}))
            self.assertEqual(self.fiware_header.service, device_res.service)
            self.assertEqual(self.fiware_header.service_path,
                             device_res.service_path)

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                cb_url=settings.CB_URL,
                iota_url=settings.IOTA_JSON_URL)
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
        logger.info(device.model_dump_json(indent=2))

        with IoTAClient(
                url=settings.IOTA_JSON_URL,
                fiware_header=self.fiware_header) as client:
            client.post_device(device=device)
            logger.info(client.get_device(device_id=device.device_id).model_dump_json(
                indent=2, exclude_unset=True))

        with ContextBrokerClient(
                url=settings.CB_URL,
                fiware_header=self.fiware_header) as client:
            logger.info(client.get_entity(entity_id=device.entity_name).model_dump_json(
                indent=2))

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                cb_url=settings.CB_URL,
                iota_url=settings.IOTA_JSON_URL)
    def test_deletions(self):
        """
        Test the deletion of a context entity/device if the state is always
        correctly cleared
        """

        device_id = 'device_id'
        entity_id = 'entity_id'

        device = Device(device_id=device_id,
                        entity_name=entity_id,
                        entity_type='Thing2',
                        protocol='IoTA-JSON',
                        transport='HTTP',
                        apikey='filip-iot-test-device')

        cb_client = ContextBrokerClient(url=settings.CB_URL,
                                        fiware_header=self.fiware_header)

        # Test 1: Only delete device
        # delete without optional parameter -> entity needs to continue existing
        self.client.post_device(device=device)
        self.client.delete_device(device_id=device_id, cb_url=settings.CB_URL)
        self.assertTrue(
            len(cb_client.get_entity_list(entity_ids=[entity_id])) == 1)
        cb_client.delete_entity(entity_id=entity_id, entity_type='Thing2')

        # Test 2:Delete device and corresponding entity
        # delete with optional parameter -> entity needs to be deleted
        self.client.post_device(device=device)
        self.client.delete_device(device_id=device_id,
                                  cb_url=settings.CB_URL,
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
        with self.assertRaises(Exception):
            self.client.delete_device(device_id=device_id,
                                      delete_entity=True,
                                      cb_url=settings.CB_URL)
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
                                entity_type='Thing2',
                                iota_url=settings.IOTA_JSON_URL)
        self.assertEqual(len(self.client.get_device_list()), 0)

    def test_update_device(self):
        """
        Test the methode: update_device of the iota client
        """

        device = Device(**self.device)
        device.endpoint = "http://test.com"
        device.transport = "MQTT"

        device.add_attribute(DeviceAttribute(
            name="Att1", object_id="o1", type=DataType.STRUCTUREDVALUE))
        device.add_attribute(StaticDeviceAttribute(
            name="Stat1", value="test", type=DataType.TEXT))
        device.add_attribute(StaticDeviceAttribute(
            name="Stat2", value="test", type=DataType.TEXT))
        device.add_command(DeviceCommand(name="Com1"))

        # use update_device to post
        self.client.update_device(device=device, add=True)

        cb_client = ContextBrokerClient(url=settings.CB_URL,
                                        fiware_header=self.fiware_header)

        # test if attributes exists correctly
        live_entity = cb_client.get_entity(entity_id=device.entity_name)
        live_entity.get_attribute("Att1")
        live_entity.get_attribute("Com1")
        live_entity.get_attribute("Com1_info")
        live_entity.get_attribute("Com1_status")
        self.assertEqual(live_entity.get_attribute("Stat1").value, "test")

        # change device attributes and update
        device.get_attribute("Stat1").value = "new_test"
        device.delete_attribute(device.get_attribute("Stat2"))
        device.delete_attribute(device.get_attribute("Att1"))
        device.delete_attribute(device.get_attribute("Com1"))
        device.add_attribute(DeviceAttribute(
            name="Att2", object_id="o1", type=DataType.STRUCTUREDVALUE))
        device.add_attribute(StaticDeviceAttribute(
            name="Stat3", value="test3", type=DataType.TEXT))
        device.add_command(DeviceCommand(name="Com2"))

        # device.endpoint = "http://localhost:8080"
        self.client.update_device(device=device)

        # test if update does what it should, for the device. It does not
        # change the entity completely:

        live_device = self.client.get_device(device_id=device.device_id)

        with self.assertRaises(KeyError):
            live_device.get_attribute("Att1")
        with self.assertRaises(KeyError):
            live_device.get_attribute("Com1_info")
        with self.assertRaises(KeyError):
            live_device.get_attribute("Stat2")
        self.assertEqual(live_device.get_attribute("Stat1").value, "new_test")
        live_device.get_attribute("Stat3")
        live_device.get_command("Com2")
        live_device.get_attribute("Att2")

        cb_client.close()

    def test_patch_device(self):
        """
            Test the methode: patch_device of the iota client
        """

        device = Device(**self.device)
        device.endpoint = "http://test.com"
        device.transport = "MQTT"

        device.add_attribute(DeviceAttribute(
            name="Att1", object_id="o1", type=DataType.STRUCTUREDVALUE))
        device.add_attribute(StaticDeviceAttribute(
            name="Stat1", value="test", type=DataType.TEXT))
        device.add_attribute(StaticDeviceAttribute(
            name="Stat2", value="test", type=DataType.TEXT))
        device.add_command(DeviceCommand(name="Com1"))

        # use patch_device to post
        self.client.patch_device(device=device)

        cb_client = ContextBrokerClient(url=settings.CB_URL,
                                        fiware_header=self.fiware_header)

        # test if attributes exists correctly
        live_entity = cb_client.get_entity(entity_id=device.entity_name)
        live_entity.get_attribute("Att1")
        live_entity.get_attribute("Com1")
        live_entity.get_attribute("Com1_info")
        live_entity.get_attribute("Com1_status")
        self.assertEqual(live_entity.get_attribute("Stat1").value, "test")

        # change device attributes and update
        device.get_attribute("Stat1").value = "new_test"
        device.delete_attribute(device.get_attribute("Stat2"))
        device.delete_attribute(device.get_attribute("Att1"))
        device.delete_attribute(device.get_attribute("Com1"))
        device.add_attribute(DeviceAttribute(
            name="Att2", object_id="o1", type=DataType.STRUCTUREDVALUE))
        device.add_attribute(StaticDeviceAttribute(
            name="Stat3", value="test3", type=DataType.TEXT))
        device.add_command(DeviceCommand(name="Com2"))

        self.client.patch_device(device=device, cb_url=settings.CB_URL)

        # test if update does what it should, for the device. It does not
        # change the entity completely:
        live_entity = cb_client.get_entity(entity_id=device.entity_name)
        with self.assertRaises(KeyError):
            live_entity.get_attribute("Att1")
        with self.assertRaises(KeyError):
            live_entity.get_attribute("Com1_info")
        with self.assertRaises(KeyError):
            live_entity.get_attribute("Stat2")
        self.assertEqual(live_entity.get_attribute("Stat1").value, "new_test")
        live_entity.get_attribute("Stat3")
        live_entity.get_attribute("Com2_info")
        live_entity.get_attribute("Att2")

        # test update where device information were changed
        new_device_dict = {"endpoint": "http://localhost:7071/",
                           "device_id": "new_id",
                           "entity_name": "new_name",
                           "entity_type": "new_type",
                           "timestamp": False,
                           "apikey": "zuiop",
                           "protocol": "HTTP",
                           "transport": "HTTP"}
        new_device = Device(**new_device_dict)

        for key, value in new_device_dict.items():
            device.__setattr__(key, value)
            self.client.patch_device(device=device)
            live_device = self.client.get_device(device_id=device.device_id)
            self.assertEqual(live_device.__getattribute__(key),
                             new_device.__getattribute__(key))
            cb_client.close()

    def test_service_group(self):
        """
        Test of querying service group based on apikey and resource.
        """
        # Create dummy service groups
        group_base = ServiceGroup(service=settings.FIWARE_SERVICE,
                                  subservice=settings.FIWARE_SERVICEPATH,
                                  resource="/iot/json", apikey="base")
        group1 = ServiceGroup(service=settings.FIWARE_SERVICE,
                              subservice=settings.FIWARE_SERVICEPATH,
                              resource="/iot/json", apikey="test1")
        group2 = ServiceGroup(service=settings.FIWARE_SERVICE,
                              subservice=settings.FIWARE_SERVICEPATH,
                              resource="/iot/json", apikey="test2")
        self.client.post_groups([group_base, group1, group2], update=True)

        # get service group
        self.assertEqual(group_base, self.client.get_group(resource="/iot/json", apikey="base"))
        self.assertEqual(group1, self.client.get_group(resource="/iot/json", apikey="test1"))
        self.assertEqual(group2, self.client.get_group(resource="/iot/json", apikey="test2"))
        with self.assertRaises(KeyError):
            self.client.get_group(resource="/iot/json", apikey="not_exist")

        #self.tearDown()

    def test_update_service_group(self):
        """
        Test for updating service group
        """
        attributes = [DeviceAttribute(name="temperature", type="Number")]
        group_base = ServiceGroup(service=settings.FIWARE_SERVICE, subservice=settings.FIWARE_SERVICEPATH,
                                  resource="/iot/json", apikey="base",
                                  entity_type="Sensor",
                                  attributes=attributes)

        self.client.post_group(service_group=group_base)
        self.assertEqual(group_base, self.client.get_group(resource="/iot/json", apikey="base"))

        # # boolean attribute
        group_base.autoprovision = False
        self.client.update_group(service_group=group_base)
        self.assertEqual(group_base, self.client.get_group(resource="/iot/json", apikey="base"))

        # entity type
        group_base.entity_type = "TemperatureSensor"
        self.client.update_group(service_group=group_base)
        self.assertEqual(group_base, self.client.get_group(resource="/iot/json", apikey="base"))

        # attributes
        humidity = DeviceAttribute(name="humidity", type="Number")
        group_base.attributes.append(humidity)
        self.client.update_group(service_group=group_base)
        self.assertEqual(group_base, self.client.get_group(resource="/iot/json", apikey="base"))

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                iota_url=settings.IOTA_JSON_URL,
                cb_url=settings.CB_URL)
    def test_clear_iot_agent(self):
        """
        Test for clearing iot agent AFTER clearing context broker
        while having a device with a command

        Returns:
            None
        """
        cb_client = ContextBrokerClient(url=settings.CB_URL,
                                        fiware_header=self.fiware_header)
        device = Device(**self.device)
        device.add_command(DeviceCommand(name="dummy_cmd"))
        self.client.post_device(device=device)
        clear_context_broker(settings.CB_URL,
                             self.fiware_header)
        self.assertEqual(len(cb_client.get_registration_list()), 1)

        clear_iot_agent(settings.IOTA_JSON_URL, self.fiware_header)
        self.assertCountEqual(cb_client.get_registration_list(), [])

    def tearDown(self) -> None:
        """
        Cleanup test server

        """
        cb_client = ContextBrokerClient(url=settings.CB_URL,
                                        fiware_header=self.fiware_header)
        devs_with_cmds = [dev.commands for dev in self.client.get_device_list()
                          if dev.commands !=[]]
        if devs_with_cmds != [] and cb_client.get_registration_list() == []:
            print("Dangling device with command and no registration found")
            clear_context_broker(url=settings.CB_URL,
                                 fiware_header=self.fiware_header)
        else:
            self.client.close()
            clear_all(fiware_header=self.fiware_header,
                cb_url=settings.CB_URL,
                iota_url=settings.IOTA_JSON_URL)

