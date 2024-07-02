"""
Test module for NGSI-LD query language based on NGSI-LD Spec section 4.9
"""
import json
import unittest

from pydantic import ValidationError
from filip.clients.ngsi_v2 import ContextBrokerClient
from filip.models.ngsi_v2.subscriptions import \
    Http, \
    HttpCustom, \
    Mqtt, \
    MqttCustom, \
    Notification, \
    Subscription
from filip.models.base import FiwareHeader
from filip.utils.cleanup import clear_all, clean_test
from tests.config import settings


class TestLDQuery(unittest.TestCase):
    """
    Test class for context broker models
    """
    # TODO the specs have to be read carefully

    def setUp(self) -> None:
        """
        Setup test data
        Returns:
            None
        """
        self.fiware_header = FiwareHeader(
            service=settings.FIWARE_SERVICE,
            service_path=settings.FIWARE_SERVICEPATH)
        # self.http_url = "https://test.de:80"
        # self.mqtt_url = "mqtt://test.de:1883"
        # self.mqtt_topic = '/filip/testing'


    def tearDown(self) -> None:
        """
        Cleanup test server
        """
        clear_all(fiware_header=self.fiware_header,
                  cb_url=settings.CB_URL)