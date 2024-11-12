"""
Test module for context subscriptions and notifications
"""
import json
import unittest

from pydantic import ValidationError
from filip.models.ngsi_ld.base import validate_ngsi_ld_query
from filip.models.ngsi_ld.subscriptions import \
    SubscriptionLD, \
    Endpoint, NotificationParams, EntityInfo, TemporalQuery
from filip.models.base import FiwareHeader
from filip.utils.cleanup import clear_all
from tests.config import settings


class TestLDSubscriptions(unittest.TestCase):
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
        self.http_url = "https://test.de:80"
        self.mqtt_url = "mqtt://test.de:1883"
        self.mqtt_topic = '/filip/testing'
        self.notification = {
                "attributes": ["speed"],
                "format": "keyValues",
                "endpoint": {
                    "uri": "http://my.endpoint.org/notify",
                    "accept": "application/json"
                }
            }
        self.sub_dict = {
            "id": "urn:ngsi-ld:Subscription:mySubscription",
            "type": "Subscription",
            "entities": [
                {
                    "type": "Vehicle"
                }
            ],
            "watchedAttributes": ["speed"],
            "q": "speed>50",
            "geoQ": {
                "georel": "near;maxDistance==2000",
                "geometry": "Point",
                "coordinates": [-1, 100]
                },
            "notification": {
                "attributes": ["speed"],
                "format": "keyValues",
                "endpoint": {
                    "uri": "http://my.endpoint.org/notify",
                    "accept": "application/json"
                }
            },
            "@context": [
                "http://example.org/ngsi-ld/latest/vehicle.jsonld",
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context-v1.3.jsonld"
            ]
            }

    def test_endpoint_models(self):
        """
        According to NGSI-LD Spec section 5.2.15
        Returns:

        """
        endpoint_http = Endpoint(**{
            "uri": "http://my.endpoint.org/notify",
            "accept": "application/json"
        })
        endpoint_mqtt = Endpoint(**{
            "uri": "mqtt://my.host.org:1883/my/test/topic",
            "accept": "application/json",  # TODO check whether it works
            "notifierInfo": [
                {
                    "key": "MQTT-Version",
                    "value": "mqtt5.0"
                }
            ]
        })
        with self.assertRaises(ValidationError):
            endpoint_https = Endpoint(**{
                "uri": "https://my.endpoint.org/notify",
                "accept": "application/json"
            })
        with self.assertRaises(ValidationError):
            endpoint_amqx = Endpoint(**{
                "uri": "amqx://my.endpoint.org/notify",
                "accept": "application/json"
            })

    def test_notification_models(self):
        """
        Test notification models
        According to NGSI-LD Spec section 5.2.14
        """
        # Test validator for conflicting fields
        notification = NotificationParams.model_validate(self.notification)

    def test_entity_selector_models(self):
        """
        According to NGSI-LD Spec section 5.2.33
        Returns:

        """
        entity_info = EntityInfo.model_validate({
                    "type": "Vehicle"
                })
        with self.assertRaises(ValueError):
            entity_info = EntityInfo.model_validate({
                "id": "test:001"
            })
        with self.assertRaises(ValueError):
            entity_info = EntityInfo.model_validate({
                "idPattern": ".*"
            })

    def test_temporal_query_models(self):
        """
        According to NGSI-LD Spec section 5.2.21
        Returns:

        """
        example0_temporalQ = {
            "timerel": "before",
            "timeAt": "2017-12-13T14:20:00Z"
        }
        self.assertEqual(example0_temporalQ,
                         TemporalQuery.model_validate(example0_temporalQ).model_dump(
                             exclude_unset=True)
                         )

        example1_temporalQ = {
            "timerel": "after",
            "timeAt": "2017-12-13T14:20:00Z"
        }
        self.assertEqual(example1_temporalQ,
                         TemporalQuery.model_validate(example1_temporalQ).model_dump(
                             exclude_unset=True)
                         )

        example2_temporalQ = {
            "timerel": "between",
            "timeAt": "2017-12-13T14:20:00Z",
            "endTimeAt": "2017-12-13T14:40:00Z",
            "timeproperty": "modifiedAt"
        }
        self.assertEqual(example2_temporalQ,
                         TemporalQuery.model_validate(example2_temporalQ).model_dump(
                             exclude_unset=True)
                         )

        example3_temporalQ = {
            "timerel": "between",
            "timeAt": "2017-12-13T14:20:00Z"
        }
        with self.assertRaises(ValueError):
            TemporalQuery.model_validate(example3_temporalQ)

        example4_temporalQ = {
            "timerel": "before",
            "timeAt": "14:20:00Z"
        }
        with self.assertRaises(ValueError):
            TemporalQuery.model_validate(example4_temporalQ)

        example5_temporalQ = {
            "timerel": "between",
            "timeAt": "2017-12-13T14:20:00Z",
            "endTimeAt": "14:40:00Z",
            "timeproperty": "modifiedAt"
        }
        with self.assertRaises(ValueError):
            TemporalQuery.model_validate(example5_temporalQ)

    # TODO clean test for NGSI-LD
    def test_subscription_models(self) -> None:
        """
        Test subscription models
        According to NGSI-LD Spec section 5.2.12
        Returns:
            None
        """
        # TODO implement after the client is ready
        pass
        # sub = Subscription.model_validate(self.sub_dict)
        # fiware_header = FiwareHeader(service=settings.FIWARE_SERVICE,
        #                              service_path=settings.FIWARE_SERVICEPATH)
        # with ContextBrokerClient(
        #         url=settings.CB_URL,
        #         fiware_header=fiware_header) as client:
        #     sub_id = client.post_subscription(subscription=sub)
        #     sub_res = client.get_subscription(subscription_id=sub_id)
        #
        #     def compare_dicts(dict1: dict, dict2: dict):
        #         for key, value in dict1.items():
        #             if isinstance(value, dict):
        #                 compare_dicts(value, dict2[key])
        #             else:
        #                 self.assertEqual(str(value), str(dict2[key]))
        #
        #     compare_dicts(sub.model_dump(exclude={'id'}),
        #                   sub_res.model_dump(exclude={'id'}))

        # # test validation of throttling
        # with self.assertRaises(ValidationError):
        #     sub.throttling = -1
        # with self.assertRaises(ValidationError):
        #     sub.throttling = 0.1

    def test_query_string_serialization(self):
        # TODO test query results in client tests
        examples = dict()
        examples[1] = 'temperature==20'
        examples[2] = 'brandName!="Mercedes"'
        examples[3] = 'isParked=="urn:ngsi-ld:OffStreetParking:Downtown1"'
        examples[5] = 'isMonitoredBy'
        examples[6] = '((speed>50|rpm>3000);brandName=="Mercedes")'
        examples[7] = '(temperature>=20;temperature<=25)|capacity<=10'
        examples[8] = 'temperature.observedAt>=2017-12-24T12:00:00Z'
        examples[9] = 'address[city]=="Berlin".'
        examples[10] = 'sensor.rawdata[airquality.particulate]==40'
        for example in examples.values():
            validate_ngsi_ld_query(example)