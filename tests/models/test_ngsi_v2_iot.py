"""
Test module for context broker models
"""
import time
import unittest
from typing import List
import warnings
from paho.mqtt import client as mqtt_client
from paho.mqtt.client import CallbackAPIVersion
import pyjexl

from filip.models.base import FiwareHeader
from filip.models.ngsi_v2.iot import DeviceCommand, ServiceGroup, \
    Device, TransportProtocol, IoTABaseAttribute, ExpressionLanguage, PayloadProtocol, DeviceAttribute
from filip.clients.ngsi_v2 import ContextBrokerClient, IoTAClient

from filip.utils.cleanup import clear_all, clean_test
from tests.config import settings


class TestContextv2IoTModels(unittest.TestCase):
    """
    Test class for context broker models
    """

    def setUp(self) -> None:
        """
        Setup test data
        Returns:
            None
        """

        self.fiware_header = FiwareHeader(
            service=settings.FIWARE_SERVICE,
            service_path=settings.FIWARE_SERVICEPATH)
        clear_all(fiware_header=self.fiware_header,
                  cb_url=settings.CB_URL,
                  iota_url=settings.IOTA_JSON_URL)
        self.iota_client = IoTAClient(
            url=settings.IOTA_JSON_URL,
            fiware_header=self.fiware_header)
        self.cb_client = ContextBrokerClient(
            url=settings.CB_URL,
            fiware_header=self.fiware_header)

    def test_fiware_safe_fields(self):
        """
        Tests all fields of models/ngsi_v2/iot.py that have a regex to
        be FIWARE safe
        Returns:
            None
        """

        from pydantic import ValidationError

        valid_strings: List[str] = ["name", "test123", "3_:strange-Name!"]
        invalid_strings: List[str] = ["my name", "Test?", "#False", "/notvalid"]

        special_strings: List[str] = ["id", "type", "geo:location"]

        # Test if all needed fields, detect all invalid strings
        for string in invalid_strings:
            self.assertRaises(ValidationError, IoTABaseAttribute,
                              name=string, type="name",
                              entity_name="name", entity_type="name")
            self.assertRaises(ValidationError, IoTABaseAttribute,
                              name="name", type=string,
                              entity_name="name", entity_type="name")
            self.assertRaises(ValidationError, IoTABaseAttribute,
                              name="name", type="name",
                              entity_name=string, entity_type="name")
            self.assertRaises(ValidationError, IoTABaseAttribute,
                              name="name", type="name",
                              entity_name="name", entity_type=string)

            self.assertRaises(ValidationError,
                              DeviceCommand, name=string, type="name")
            self.assertRaises(ValidationError,
                              ServiceGroup, entity_type=string,
                              resource="", apikey="")

            self.assertRaises(ValidationError,
                              Device, device_id="",
                              entity_name=string,
                              entity_type="name",
                              transport=TransportProtocol.HTTP)
            self.assertRaises(ValidationError,
                              Device, device_id="",
                              entity_name="name",
                              entity_type=string,
                              transport=TransportProtocol.HTTP)

        # Test if all needed fields, do not trow wrong errors
        for string in valid_strings:
            IoTABaseAttribute(name=string, type=string,
                              entity_name=string, entity_type=string)
            DeviceCommand(name=string, type="name")
            ServiceGroup(entity_type=string, resource="", apikey="")
            Device(device_id="", entity_name=string, entity_type=string,
                   transport=TransportProtocol.HTTP)

        # Test for the special-string protected field if all strings are blocked
        for string in special_strings:
            with self.assertRaises(ValidationError):
                IoTABaseAttribute(name=string, type="name", entity_name="name",
                                  entity_type="name")
            with self.assertRaises(ValidationError):
                IoTABaseAttribute(name="name", type=string, entity_name="name",
                                  entity_type="name")
            with self.assertRaises(ValidationError):
                DeviceCommand(name=string, type="name")

        # Test for the normal protected field if all strings are allowed
        for string in special_strings:
            IoTABaseAttribute(name="name", type="name",
                              entity_name=string, entity_type=string)
            ServiceGroup(entity_type=string, resource="", apikey="")
            Device(device_id="", entity_name=string, entity_type=string,
                   transport=TransportProtocol.HTTP)

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                cb_url=settings.CB_URL,
                iota_url=settings.IOTA_JSON_URL)
    def test_expression_language(self):
        api_key = settings.FIWARE_SERVICEPATH.strip('/')

        # Test expression language on service group level
        service_group_jexl = ServiceGroup(
            entity_type='Thing',
            apikey=api_key,
            resource='/iot/json',
            expressionLanguage=ExpressionLanguage.JEXL)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            service_group_legacy = ServiceGroup(
                entity_type='Thing',
                apikey=api_key,
                resource='/iot/json',
                expressionLanguage=ExpressionLanguage.LEGACY)

            assert len(w) == 1
            assert issubclass(w[0].category, UserWarning)
            assert "deprecated" in str(w[0].message)

        self.iota_client.post_group(service_group=service_group_jexl)

        # Test jexl expression language on device level
        device1 = Device(device_id="test_device",
                         entity_name="test_entity",
                         entity_type="test_entity_type",
                         transport=TransportProtocol.MQTT,
                         protocol=PayloadProtocol.IOTA_JSON,
                         expressionLanguage=ExpressionLanguage.JEXL,
                         attributes=[DeviceAttribute(name="value", type="Number"),
                                     DeviceAttribute(name="fraction", type="Number",
                                                     expression="(value + 3) / 10"),
                                     DeviceAttribute(name="spaces", type="Text"),
                                     DeviceAttribute(name="trimmed", type="Text",
                                                     expression="spaces|trim"),
                                     ]
                         )
        self.iota_client.post_device(device=device1)

        mqtt_cl = mqtt_client.Client(callback_api_version=CallbackAPIVersion.VERSION2)
        mqtt_cl.connect(settings.MQTT_BROKER_URL.host, settings.MQTT_BROKER_URL.port)
        mqtt_cl.loop_start()

        mqtt_cl.publish(topic=f'/json/{api_key}/{device1.device_id}/attrs',
                        payload='{"value": 12, "spaces": "   foobar   "}')

        time.sleep(2)

        entity1 = self.cb_client.get_entity(entity_id=device1.entity_name)
        self.assertEqual(entity1.get_attribute('fraction').value, 1.5)
        self.assertEqual(entity1.get_attribute('trimmed').value, 'foobar')

        mqtt_cl.loop_stop()
        mqtt_cl.disconnect()

        # Test for wrong jexl expressions
        device2 = Device(device_id="wrong_device",
                         entity_name="test_entity",
                         entity_type="test_entity_type",
                         transport=TransportProtocol.MQTT,
                         protocol=PayloadProtocol.IOTA_JSON)

        attr1 = DeviceAttribute(name="value", type="Number", expression="value ++ 3")
        with self.assertRaises(pyjexl.jexl.ParseError):
            device2.add_attribute(attr1)
        device2.delete_attribute(attr1)

        attr2 = DeviceAttribute(name="spaces", type="Text", expression="spaces | trim")
        with self.assertRaises(pyjexl.jexl.ParseError):
            device2.add_attribute(attr2)
        device2.delete_attribute(attr2)

        attr3 = DeviceAttribute(name="brackets", type="Number", expression="((2 + 3) / 10")
        with self.assertRaises(pyjexl.jexl.ParseError):
            device2.add_attribute(attr3)
        device2.delete_attribute(attr3)

        # Test for legacy expression warning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            device3 = Device(device_id="legacy_device",
                             entity_name="test_entity",
                             entity_type="test_entity_type",
                             transport=TransportProtocol.MQTT,
                             protocol=PayloadProtocol.IOTA_JSON,
                             expressionLanguage=ExpressionLanguage.LEGACY)

            assert len(w) == 2

    def test_add_device_attributes(self):
        """
        Test the device model regarding the behavior with devices attributes.
        According to https://iotagent-node-lib.readthedocs.io/en/latest/api.html and
        based on our best practice, following rules are checked
            - name is required, but not necessarily unique
            - object_id is not required, if given must be unique, i.e. not equal to any
                existing object_id and name
        """
        def initial_device():
            attr = DeviceAttribute(
                name="temperature",
                type="Number"
            )
            return Device(
                device_id="dummy:01",
                entity_name="entity:01",
                entity_type="MyEntity",
                attributes=[attr]
            )

        # fail, because attr1 and attr ara identical
        device_a = initial_device()
        attr1 = DeviceAttribute(
            name="temperature",
            type="Number"
        )
        with self.assertRaises(ValueError):
            device_a.add_attribute(attribute=attr1)

        # fail, because the object_id is duplicated with the name of attr1
        device_b = initial_device()
        attr2 = DeviceAttribute(
            name="temperature",
            type="Number",
            object_id="temperature"
        )
        with self.assertRaises(ValueError):
            device_b.add_attribute(attribute=attr2)

        # success
        device_c = initial_device()
        attr3 = DeviceAttribute(
            name="temperature",
            type="Number",
            object_id="t1"
        )
        device_c.add_attribute(attribute=attr3)
        # success
        attr4 = DeviceAttribute(
            name="temperature",
            type="Number",
            object_id="t2"
        )
        device_c.add_attribute(attribute=attr4)
        # fail, because object id is duplicated
        attr5 = DeviceAttribute(
            name="temperature2",
            type="Number",
            object_id="t2"
        )
        with self.assertRaises(ValueError):
            device_c.add_attribute(attribute=attr5)

    def test_device_creation(self):
        """
        Test the device model regarding the behavior with devices attributes while
        creating the devices.
        According to https://iotagent-node-lib.readthedocs.io/en/latest/api.html and
        based on our best practice, following rules are checked
            - name is required, but not necessarily unique
            - object_id is not required, if given must be unique, i.e. not equal to any
                existing object_id and name
        """

        def create_device(attr1_name, attr2_name,
                          attr1_object_id=None, attr2_object_id=None):
            _attr1 = DeviceAttribute(
                name=attr1_name,
                object_id=attr1_object_id,
                type="Number"
            )
            _attr2 = DeviceAttribute(
                name=attr2_name,
                object_id=attr2_object_id,
                type="Number"
            )
            return Device(
                device_id="dummy:01",
                entity_name="entity:01",
                entity_type="MyEntity",
                attributes=[_attr1, _attr2]
            )

        # fail, because attr1 and attr ara identical
        with self.assertRaises(ValueError):
            create_device(
                attr1_name="temperature",
                attr2_name="temperature",
                attr1_object_id=None,
                attr2_object_id=None
            )

        # fail, because the object_id is duplicated with the name of attr1
        with self.assertRaises(ValueError):
            create_device(
                attr1_name="temperature",
                attr2_name="temperature",
                attr1_object_id=None,
                attr2_object_id="temperature"
            )

        # success
        device = create_device(
            attr1_name="temperature",
            attr2_name="temperature",
            attr1_object_id=None,
            attr2_object_id="t1"
        )
        # success
        attr4 = DeviceAttribute(
            name="temperature",
            type="Number",
            object_id="t2"
        )
        device.add_attribute(attribute=attr4)

        # fail, because object id is duplicated
        with self.assertRaises(ValueError):
            create_device(
                attr1_name="temperature2",
                attr2_name="temperature",
                attr1_object_id="t",
                attr2_object_id="t"
            )

    def tearDown(self) -> None:
        """
        Cleanup test server
        """
        clear_all(fiware_header=self.fiware_header,
                  cb_url=settings.CB_URL,
                  iota_url=settings.IOTA_JSON_URL)
        self.iota_client.close()
        self.cb_client.close()
