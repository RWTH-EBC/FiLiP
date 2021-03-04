import unittest
from datetime import datetime
from core.models import FiwareHeader
from pydantic import BaseModel
from timeseries.client import QuantumLeap
from timeseries.models import IndexedValues

class TestTimeseries(unittest.TestCase):
    def setUp(self) -> None:
        self.fiware_header = FiwareHeader(service='filip',
                                          service_path='/testing')
        self.client = QuantumLeap(fiware_header=self.fiware_header)

    def test_meta_endpoints(self):
        with QuantumLeap(fiware_header=self.fiware_header) as client:
            self.assertIsNotNone(client.get_version())
            self.assertIsNotNone(client.get_health())

    def test_input_endpoints(self):
        pass

    def tearDown(self) -> None:
        self.client.close()

class TestModels(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_indexed_values(self):
        timestamp_str = '2010-10-10T07:09:00.792'
        timestamp_epoch = datetime.strptime(timestamp_str,
                                           '%Y-%m-%dT%H:%M:%S.%f')
        values = IndexedValues(index=[1, 1000], values=['1', '2'])
        print(values)
        values = IndexedValues(index=['2010-10-10T07:09:00.792'], values=['1'])
        print(values)

