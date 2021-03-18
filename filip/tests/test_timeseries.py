import unittest
from datetime import datetime
from core.models import FiwareHeader
from timeseries.client import QuantumLeapClient
from cb.models import ContextEntity
from timeseries.models import NotificationMessage, IndexArray


class TestTimeSeries(unittest.TestCase):
    def setUp(self) -> None:
        self.fiware_header = FiwareHeader(service='filip',
                                          service_path='/testing')
        self.client = QuantumLeapClient(fiware_header=self.fiware_header)
        self.attr = {'temperature': {'value': 20,
                                     'type': 'Number'}}
        self.entity_1 = ContextEntity(id='Kitchen', type='Room', **self.attr)
        self.entity_2 = ContextEntity(id='Floor', type='Flat', **self.attr)

    def test_meta_endpoints(self):
        with QuantumLeapClient(fiware_header=self.fiware_header) as client:
            self.assertIsNotNone(client.get_version())
            self.assertIsNotNone(client.get_health())

    def test_input_endpoints(self):
        with QuantumLeapClient(fiware_header=self.fiware_header) as client:
            data = [self.entity_1, self.entity_2]
            notification_message = NotificationMessage(data=data, subscriptionId="test")
            self.assertIsNotNone(client.post_notification(notification_message))
            self.assertEqual(client.delete_entity(self.entity_1.id, self.entity_1.type), self.entity_1.id)
            self.assertEqual(client.delete_entity_type(self.entity_2.type), self.entity_2.type)

    def test_queries_endpoint(self):
        with QuantumLeapClient(fiware_header=self.fiware_header) as client:
            entities_data_all = client.get_entity_data(entity_id=self.entity_1.id)
            self.assertIsInstance(entities_data_all, IndexArray)
            #TODO:Test for each parameter

    def tearDown(self) -> None:
        #TODO:clean up entities
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
