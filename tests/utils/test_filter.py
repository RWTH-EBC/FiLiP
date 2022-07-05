"""
Tests filter functions in filip.utils.filter
"""
import unittest
from datetime import datetime

from filip.clients.ngsi_v2 import ContextBrokerClient
from filip.models.base import FiwareHeader
from filip.models.ngsi_v2.base import EntityPattern
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

    def tearDown(self) -> None:
        """
        Cleanup test server
        """
        self.client.close()
        clear_all(fiware_header=self.fiware_header,
                  cb_url=self.url)
