"""
Test module for context subscriptions and notifications
"""

import unittest

from pydantic import ValidationError
from filip.clients.ngsi_v2 import ContextBrokerClient
from filip.models.ngsi_v2.base import EntityPattern
from filip.models.base import FiwareHeader
from filip.utils.cleanup import clear_all, clean_test
from tests.config import settings


class TestSubscriptions(unittest.TestCase):
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
            service=settings.FIWARE_SERVICE, service_path=settings.FIWARE_SERVICEPATH
        )
        self.http_url = "https://test.de:80"
        self.mqtt_url = "mqtt://test.de:1883"
        self.mqtt_topic = "/filip/testing"

    def test_entity_pattern(self) -> None:
        """ """
        _id = "urn:ngsi-ld:Test:001"
        _idPattern = ".*"
        _type = "Test"
        _typePattern = "Test"

        # correct usage
        # id + type
        entity_pattern = EntityPattern(id=_id, type=_type)
        # id + type pattern
        entity_pattern = EntityPattern(id=_id, typePattern=_typePattern)
        # id pattern + type
        entity_pattern = EntityPattern(idPattern=_idPattern, type=_type)
        # id pattern + type pattern
        entity_pattern = EntityPattern(idPattern=_idPattern, typePattern=_typePattern)
        # only id
        entity_pattern = EntityPattern(id=_id)
        # only id pattern
        entity_pattern = EntityPattern(idPattern=_idPattern)

        # incorrect usage
        # id & id pattern + type
        with self.assertRaises(ValidationError):
            entity_pattern = EntityPattern(id=_id, idPattern=_idPattern, type=_type)
        # id + type & type pattern
        with self.assertRaises(ValidationError):
            entity_pattern = EntityPattern(id=_id, type=_type, typePattern=_typePattern)
        # only type
        with self.assertRaises(ValidationError):
            entity_pattern = EntityPattern(type=_type)
        # only type pattern
        with self.assertRaises(ValidationError):
            entity_pattern = EntityPattern(typePattern=_typePattern)

    def tearDown(self) -> None:
        """
        Cleanup test server
        """
        clear_all(fiware_header=self.fiware_header, cb_url=settings.CB_URL)
