"""
Tests for time series api client aka QuantumLeap
"""
import logging
import unittest
from random import random
import requests
import time
from typing import List
from filip.clients.ngsi_v2 import \
    ContextBrokerClient, \
    QuantumLeapClient
from filip.models.base import FiwareHeader
from filip.models.ngsi_v2.context import ContextEntity
from filip.models.ngsi_v2.subscriptions import Message
from filip.utils.cleanup import clean_test, clear_all
from tests.config import settings


logger = logging.getLogger(__name__)


def create_entities() -> List[ContextEntity]:
    """
    Create entities with random values
    Returns:

    """
    def create_attr():
        return {'temperature': {'value': random(),
                                'type': 'Number'},
                'humidity': {'value': random(),
                             'type': 'Number'},
                'co2': {'value': random(),
                        'type': 'Number'}}

    return [ContextEntity(id='Kitchen', type='Room', **create_attr()),
            ContextEntity(id='LivingRoom', type='Room', **create_attr())]


def create_time_series_data(num_records: int = 50000):
    """
    creates large testing data sets that should remain on the server.
    This is mainly to reduce time for testings
    """
    fiware_header = FiwareHeader(service=settings.FIWARE_SERVICE,
                                 service_path="/static")

    with QuantumLeapClient(url=settings.QL_URL, fiware_header=fiware_header) \
            as client:

        for i in range(num_records):
            notification_message = Message(data=create_entities(),
                                           subscriptionId="test")
            client.post_notification(notification_message)


class TestTimeSeries(unittest.TestCase):
    """
    Test class for time series api client
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
        self.ql_client = QuantumLeapClient(
            url=settings.QL_URL,
            fiware_header=self.fiware_header)

        self.cb_client = ContextBrokerClient(
            url=settings.CB_URL,
            fiware_header=self.fiware_header)

    def test_meta_endpoints(self) -> None:
        """
        Test meta data endpoints
        Returns:
            None
        """
        with QuantumLeapClient(
                url=settings.QL_URL,
                fiware_header=self.fiware_header) \
                as client:
            self.assertIsNotNone(client.get_version())
            self.assertIsNotNone(client.get_health())

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                cb_url=settings.CB_URL,
                ql_url=settings.QL_URL)
    def test_input_endpoints(self) -> None:
        """
        Test input endpoint
        Returns:
            None
        """
        entities = create_entities()
        for entity in entities:
            self.cb_client.post_entity(entity)

        with QuantumLeapClient(
                url=settings.QL_URL,
                fiware_header=self.fiware_header) \
                as client:
            notification_message = Message(data=entities,
                                           subscriptionId="test")
            client.post_subscription(cb_url=settings.CB_URL,
                                     ql_url=settings.QL_URL,
                                     entity_id=entities[0].id)
            client.post_notification(notification_message)
        time.sleep(1)

    @clean_test(fiware_service=settings.FIWARE_SERVICE,
                fiware_servicepath=settings.FIWARE_SERVICEPATH,
                ql_url=settings.QL_URL)
    def test_entity_context(self) -> None:
        """
        Test entities endpoint
        Returns:
            None
        """
        entities = create_entities()
        with QuantumLeapClient(
                url=settings.QL_URL,
                fiware_header=self.fiware_header) \
                as client:
            notification_message = Message(data=entities,
                                           subscriptionId="test")
            client.post_notification(notification_message)

            time.sleep(1)
            entities = client.get_entities(entity_type=entities[0].type)
            for entity in entities:
                logger.debug(entity.json(indent=2))

    def test_query_endpoints_by_id(self) -> None:
        """
        Test queries with default values

        Returns:
            None
        """
        with QuantumLeapClient(
                url=settings.QL_URL,
                fiware_header=self.fiware_header.copy(
                    update={'service_path': '/static'})) \
                as client:

            entities = create_entities()

            with self.assertRaises(requests.RequestException):
                client.get_entity_by_id(entity_id=entities[0].id,
                                        entity_type='MyType')
            for entity in entities:
                # get by id
                attrs_id = client.get_entity_by_id(entity_id=entity.id,
                                                   aggr_period='minute',
                                                   aggr_method='avg',
                                                   attrs='temperature,co2')
                logger.debug(attrs_id.json(indent=2))
                logger.debug(attrs_id.to_pandas())

                attrs_values_id = client.get_entity_values_by_id(
                    entity_id=entity.id)
                logger.debug(attrs_values_id.to_pandas())
                self.assertEqual(len(attrs_values_id.index), 10000)

                attr_id = client.get_entity_attr_by_id(
                    entity_id=entity.id, attr_name="temperature")
                logger.debug(attr_id.to_pandas())
                self.assertEqual(len(attr_id.index), 10000)

                attr_values_id = client.get_entity_attr_values_by_id(
                    entity_id=entity.id, attr_name="temperature")
                logger.debug(attr_values_id.to_pandas())
                self.assertEqual(len(attrs_values_id.index), 10000)

    def test_query_endpoints_by_type(self) -> None:
        """
        Test queries by type with default values

        Returns:
            None
        """
        with QuantumLeapClient(
                url=settings.QL_URL,
                fiware_header=self.fiware_header.copy(
                    update={'service_path': '/static'})) \
                as client:

            entities = create_entities()

            for entity in entities:
                # get by type
                attrs_type = client.get_entity_by_type(
                    entity_type=entity.type)
                for entity_id in attrs_type:
                    logger.debug(entity_id.to_pandas())

                self.assertEqual(sum([len(entity_id.index) for
                                      entity_id in attrs_type]),
                                 10000)

                attrs_values_type = client.get_entity_values_by_type(
                    entity_type=entity.type, )
                for entity_id in attrs_values_type:
                    logger.debug(entity_id.to_pandas())
                self.assertEqual(sum([len(entity_id.index) for
                                      entity_id in attrs_values_type]),
                                 10000)

                attr_type = client.get_entity_attr_by_type(
                    entity_type=entity.type, attr_name="temperature")
                for entity_id in attr_type:
                    logger.debug(entity_id.to_pandas())
                self.assertEqual(sum([len(entity_id.index) for
                                      entity_id in attr_type]),
                                 10000)

                attr_values_type = client.get_entity_attr_values_by_type(
                    entity_type=entity.type, attr_name="temperature")
                for entity_id in attr_values_type:
                    logger.debug(entity_id.to_pandas())
                self.assertEqual(sum([len(entity_id.index) for
                                      entity_id in attr_values_type]),
                                 10000)

    def test_test_query_endpoints_with_args(self) -> None:
        """
        Test arguments for queries

        Returns:
            None
        """
        with QuantumLeapClient(
                url=settings.QL_URL,
                fiware_header=self.fiware_header.copy(
                    update={'service_path': '/static'})) \
                as client:

            for entity in create_entities():
                # test limit
                for limit in range(5000, 25000, 5000):
                    records = client.get_entity_by_id(
                        entity_id=entity.id,
                        attrs='temperature,co2',
                        limit=limit)

                    logger.debug(records.json(indent=2))
                    logger.debug(records.to_pandas())
                    self.assertEqual(len(records.index), limit)

                # test last_n
                for last_n in range(5000, 25000, 5000):
                    limit = 15000
                    last_n_records = client.get_entity_by_id(
                        entity_id=entity.id,
                        attrs='temperature,co2',
                        limit=limit,
                        last_n=last_n)
                    self.assertGreater(last_n_records.index[0],
                                       records.index[0])
                    self.assertEqual(len(last_n_records.index),
                                     min(last_n, limit))

                # test offset
                old_records = None
                for offset in range(5000, 25000, 5000):
                    # with limit
                    records = client.get_entity_by_id(
                        entity_id=entity.id,
                        attrs='temperature,co2',
                        offset=offset)

                    if old_records:
                        self.assertLess(old_records.index[0],
                                        records.index[0])
                    old_records = records

                old_records = None
                for offset in range(5000, 25000, 5000):
                    # test with last_n
                    records = client.get_entity_by_id(
                        entity_id=entity.id,
                        attrs='temperature,co2',
                        offset=offset,
                        last_n=5)
                    if old_records:
                        self.assertGreater(old_records.index[0],
                                           records.index[0])
                    old_records = records

    def tearDown(self) -> None:
        """
        Clean up server
        Returns:
            None
        """
        clear_all(fiware_header=self.fiware_header,
                  cb_url=settings.CB_URL,
                  ql_url=settings.QL_URL)

        self.ql_client.close()
        self.cb_client.close()
