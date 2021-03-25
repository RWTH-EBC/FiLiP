import unittest
from core.models import FiwareHeader
from timeseries.client import QuantumLeapClient
from cb.models import ContextEntity
from timeseries.models import NotificationMessage


class TestTimeSeries(unittest.TestCase):
    def setUp(self) -> None:
        self.fiware_header = FiwareHeader(service='filip',
                                          service_path='/testing')
        self.client = QuantumLeapClient(fiware_header=self.fiware_header)
        self.attr = {'temperature': {'value': 20,
                                     'type': 'Number'}}
        self.entity_1 = ContextEntity(id='Kitchen', type='Room', **self.attr)
        self.entity_2 = ContextEntity(id='Living', type='Room', **self.attr)

    def test_meta_endpoints(self):
        with QuantumLeapClient(fiware_header=self.fiware_header) as client:
            self.assertIsNotNone(client.get_version())
            self.assertIsNotNone(client.get_health())

    def test_input_endpoints(self):
        with QuantumLeapClient(fiware_header=self.fiware_header) as client:
            data = [self.entity_1, self.entity_2]
            notification_message = NotificationMessage(data=data,
                                                       subscriptionId="test")
            self.assertIsNotNone(client.post_notification(notification_message))
            self.assertIsNotNone(client.post_subscription())

    def test_queries_endpoint(self):
        with QuantumLeapClient(fiware_header=self.fiware_header) as client:
            attrs_id = client.get_entity_attrs_by_id(entity_id=self.entity_2.id)
            attrs_values_id = client.get_entity_attrs_values_by_id(
                entity_id=self.entity_2.id)
            attr_id = client.get_entity_attr_by_id(
                entity_id=self.entity_2.id, attr_name="temperature")
            attr_values_id = client.get_entity_attr_values_by_id(
                entity_id=self.entity_2.id, attr_name="temperature")

            # attrs_type = client.get_entity_attrs_by_type(
            #     entity_type=self.entity_2.type)
            # attrs_values_type = client.get_entity_attrs_values_by_type(
            #     entity_type=self.entity_2.type)
            attr_type = client.get_entity_attr_by_type(
                entity_type=self.entity_1.type, attr_name="temperature")
            attr_values_type = client.get_entity_attr_values_by_type(
                entity_type=self.entity_1.type, attr_name="temperature")

            # TODO:Test for each parameter

            print(attr_id.to_pandas())

    def tearDown(self) -> None:
        try:
            self.client.delete_entity(self.entity_1.id)
            self.client.delete_entity(self.entity_2.id)
        except:
            pass
        self.client.close()

# class TestModels(unittest.TestCase):
#     def setUp(self) -> None:
#         pass
#
#     def test_indexed_values(self):
#         timestamp_str = '2010-10-10T07:09:00.792'
#         timestamp_epoch = datetime.strptime(timestamp_str,
#                                            '%Y-%m-%dT%H:%M:%S.%f')
#         values = IndexedValues(index=[1, 1000], values=['1', '2'])
#         print(values)
#         values = IndexedValues(index=['2010-10-10T07:09:00.792'], values=['1'])
#         print(values)
