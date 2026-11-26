"""Smoke tests for FiLiP issue #506, model deprecations (FutureWarning)."""

import unittest
import warnings

from filip.models.ngsi_v2.context import Command, NamedCommand
from filip.models.ngsi_v2.iot import Device, DeviceCommand, ServiceGroup


class TestLegacyCommandDeprecation(unittest.TestCase):
    @staticmethod
    def get_future_warnings(factory):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", FutureWarning)
            result = factory()
        messages = [
            str(item.message)
            for item in caught
            if issubclass(item.category, FutureWarning)
        ]
        return result, messages

    def test_command_warns(self):
        cmd, messages = self.get_future_warnings(lambda: Command(value="ON"))
        self.assertEqual(cmd.value, "ON")
        self.assertEqual(len(messages), 1)
        self.assertIn("Command is deprecated", messages[0])

    def test_named_command_warns_once(self):
        cmd, messages = self.get_future_warnings(
            lambda: NamedCommand(name="set_mode", value="ON")
        )
        self.assertEqual(cmd.name, "set_mode")
        self.assertEqual(len(messages), 1)
        self.assertIn("NamedCommand is deprecated", messages[0])

    def test_device_command_warns(self):
        cmd, messages = self.get_future_warnings(lambda: DeviceCommand(name="set_mode"))
        self.assertEqual(cmd.name, "set_mode")
        self.assertEqual(len(messages), 1)
        self.assertIn("DeviceCommand is deprecated", messages[0])

    def test_nested_device_command_warns(self):
        _, messages = self.get_future_warnings(
            lambda: Device(
                device_id="device1",
                entity_name="entity1",
                entity_type="TestDevice",
                commands=[{"name": "set_mode"}],
            )
        )
        self.assertEqual(len(messages), 1)
        self.assertIn("DeviceCommand is deprecated", messages[0])

    def test_nested_service_group_command_warns(self):
        _, messages = self.get_future_warnings(
            lambda: ServiceGroup(
                resource="/iot/json",
                apikey="test-key",
                commands=[{"name": "set_mode"}],
            )
        )
        self.assertEqual(len(messages), 1)
        self.assertIn("DeviceCommand is deprecated", messages[0])

    def test_device_without_commands_does_not_warn(self):
        _, messages = self.get_future_warnings(
            lambda: Device(
                device_id="device1",
                entity_name="entity1",
                entity_type="TestDevice",
            )
        )
        self.assertEqual(messages, [])

    def test_field_descriptions(self):
        for model in (Device, ServiceGroup):
            with self.subTest(model=model.__name__):
                description = model.model_fields["commands"].description
                self.assertIn("DEPRECATED", description)
                self.assertIn("notifications", description.lower())
