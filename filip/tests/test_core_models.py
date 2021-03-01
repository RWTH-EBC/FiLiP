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



if __name__ == '__main__':
    data = {'id': 'str',
            'type': 'myType',
            'temperature': {'value': '20', 'type': 'Number'},
            'relation': {'value': 'OtherEntity', 'type': 'Relationship'}}
    base_model = ContextEntity(**data)
    print(base_model.json(indent=2))

    model = ContextEntity(**data)
    model2 = ContextEntity.parse_obj(data)
    print(model == model2)
    print(model.json(indent=2))
    print(model.get_properties())
    print(model.get_relationships())
    GeneratedModel = create_context_entity_model(data=data)

    data = {'id': 'str',
            'type': 'myType',
            'temperature': {'value': 20, 'type': 'Number'},
            'relation': {'value': 'OtherEntity', 'type': 'Relationship'}}

    model3 = GeneratedModel(**data)
    model4 = GeneratedModel.parse_obj(data)
    print(model.get_properties())
    print(model3.json(indent=2))
    print(model3.__fields__)