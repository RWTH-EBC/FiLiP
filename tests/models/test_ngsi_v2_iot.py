"""
Test module for context broker models
"""

import unittest
from typing import List

from filip.models.ngsi_v2.iot import DeviceCommand, ServiceGroup, \
    Device, TransportProtocol, IoTABaseAttribute


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

    def test_fiware_safe_fields(self):
        """
        Tests all fields of models/ngsi_v2/iot.py that have a regex to
        be FIWARE safe
        Returns:
            None
        """

        from pydantic.error_wrappers import ValidationError

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