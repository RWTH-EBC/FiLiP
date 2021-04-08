import unittest
from cb import ContextBrokerClient
from filip.core.models import FiwareHeader
from filip.cb.models import ContextEntity
from filip.timeseries.client import QuantumLeapClient
from filip.timeseries.models import NotificationMessage


class TestTimeSeries(unittest.TestCase):
    def setUp(self) -> None:
        self.fiware_header = FiwareHeader(service='filip',
                                          service_path='/testing')
        self.client = QuantumLeapClient(fiware_header=self.fiware_header)
        self.attr = {'temperature': {'value': 20,
                                     'type': 'Number'}}
        self.entity_1 = ContextEntity(id='Kitchen_Test', type='Room', **self.attr)
        self.cb_client = ContextBrokerClient(fiware_header=self.fiware_header)

    def test_meta_endpoints(self):
        with QuantumLeapClient(fiware_header=self.fiware_header) as client:
            self.assertIsNotNone(client.get_version())
            self.assertIsNotNone(client.get_health())

    def test_input_endpoints(self):
        with QuantumLeapClient(fiware_header=self.fiware_header) as client:
            data = [self.entity_1]
            notification_message = NotificationMessage(data=data,
                                                       subscriptionId="test")
            self.assertIsNotNone(client.post_subscription(entity_id=self.entity_1.id))
            self.assertIsNotNone(client.post_notification(notification_message))

    def test_queries_endpoint(self):
        with QuantumLeapClient(fiware_header=self.fiware_header) as client:
            try:
                attrs_id = client.get_entity_attrs_by_id(entity_id=self.entity_1.id)
                attrs_values_id = client.get_entity_attrs_values_by_id(
                    entity_id=self.entity_1.id)
                attr_id = client.get_entity_attr_by_id(
                    entity_id=self.entity_1.id, attr_name="temperature")
                attr_values_id = client.get_entity_attr_values_by_id(
                    entity_id=self.entity_1.id, attr_name="temperature")

                # attrs_type = client.get_entity_attrs_by_type(
                #     entity_type=self.entity_2.type)
                # attrs_values_type = client.get_entity_attrs_values_by_type(
                #     entity_type=self.entity_2.type)
                attr_type = client.get_entity_attr_by_type(
                    entity_type=self.entity_1.type, attr_name="temperature")
                attr_values_type = client.get_entity_attr_values_by_type(
                    entity_type=self.entity_1.type, attr_name="temperature")

                print(attrs_id.to_pandas())
                print(attrs_values_id.to_pandas())
                print(attr_id.to_pandas())
                print(attr_values_id.to_pandas())
                print(attr_type.to_pandas())
                print(attr_values_type.to_pandas())
            except:
                print("There is no historical data yet.")

    def tearDown(self) -> None:
        try:
            for sub in self.cb_client.get_subscription_list():
                for entity in sub.subject.entities:
                    if entity.id == self.entity_1.id:
                        if entity.type == self.entity_1.type:
                            self.cb_client.delete_subscription(sub.id)
        except:
            pass
        self.client.close()
        self.cb_client.close()

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
