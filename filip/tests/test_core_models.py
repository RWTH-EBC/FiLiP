import unittest
import json
from pydantic import ValidationError
from core.models import FiwareHeader


class TestModels(unittest.TestCase):
    def setUp(self) -> None:
        self.fiware_header = {'fiware-service': 'filip',
                              'fiware-servicepath': '/testing'}

    def test_fiware_header(self):
        header = FiwareHeader(service='filip', service_path='/testing')
        self.assertEqual(header.dict(by_alias=True),
                         self.fiware_header)
        self.assertEqual(header.json(by_alias=True),
                         json.dumps(self.fiware_header))
        self.assertRaises(ValidationError, FiwareHeader,
                          service='jkgsadh ', service_path='/testing')
        self.assertRaises(ValidationError, FiwareHeader,
                          service='%', service_path='/testing')
        self.assertRaises(ValidationError, FiwareHeader,
                          service='filip', service_path='testing/')
        self.assertRaises(ValidationError, FiwareHeader,
                          service='filip', service_path='/$testing')
        self.assertRaises(ValidationError, FiwareHeader,
                          service='filip', service_path='/testing ')
