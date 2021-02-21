import unittest
import json
from pydantic import ValidationError
from core import FiwareHeader


class TestModels(unittest.TestCase):
    def setUp(self) -> None:
        self.fiware_header = {'fiware-service': 'filip',
                              'fiware-servicepath': '/testing'}

    def test_fiware_header(self):
        header = FiwareHeader(service='filip', path='/testing')
        self.assertEqual(header.dict(by_alias=True),
                         self.fiware_header)
        self.assertEqual(header.json(by_alias=True),
                         json.dumps(self.fiware_header))
        self.assertRaises(ValidationError, FiwareHeader,
                          service='filip', path='testing')
