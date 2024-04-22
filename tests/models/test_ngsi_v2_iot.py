"""
Test module for context broker models
"""

import unittest
from typing import List
import warnings

from filip.models.base import FiwareHeader
from filip.models.ngsi_v2.iot import DeviceCommand, ServiceGroup, \
    Device, TransportProtocol, IoTABaseAttribute, ExpressionLanguage
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
        self.iotac = IoTAClient(
            url=settings.IOTA_JSON_URL,
            fiware_header=self.fiware_header)
        self.client = ContextBrokerClient(
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
        service_group_jexl = ServiceGroup(
            service=self.fiware_header.service,
            subservice=self.fiware_header.service_path,
            apikey=settings.FIWARE_SERVICEPATH.strip('/'),
            resource='/iot/json',
            expressionLanguage=ExpressionLanguage.JEXL)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            service_group_legacy = ServiceGroup(
                service=self.fiware_header.service,
                subservice=self.fiware_header.service_path,
                apikey=settings.FIWARE_SERVICEPATH.strip('/'),
                resource='/iot/json',
                expressionLanguage=ExpressionLanguage.LEGACY)

            assert len(w) == 1
            assert issubclass(w[0].category, UserWarning)
            assert "deprecated" in str(w[0].message)

        self.iotac.post_group(service_group=service_group_jexl)
