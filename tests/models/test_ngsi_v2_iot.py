"""
Test module for context broker models
"""
import time
import unittest
from typing import List
import warnings
from paho.mqtt import client as mqtt_client
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

        mqtt_cl = mqtt_client.Client()
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

    def tearDown(self) -> None:
        """
        Cleanup test server
        """
        clear_all(fiware_header=self.fiware_header,
                  cb_url=settings.CB_URL,
                  iota_url=settings.IOTA_JSON_URL)
        self.iota_client.close()
        self.cb_client.close()
