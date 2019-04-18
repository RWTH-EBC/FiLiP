import requests
import json 
import filip.cb_request as cb


HEADER_ACCEPT_JSON = {'Accept': 'application/json'}
HEADER_ACCEPT_PLAIN = {'Accept': 'text/plain'}
HEADER_CONTENT_JSON = {'Content-Type': 'application/json'}
HEADER_CONTENT_PLAIN = {'Content-Type': 'text/plain'}


class Attribute:
    def __init__(self, name, value, attr_type):
        self.name = name
        self.value = value
        self.type = attr_type

    def get_json(self):
        return {'value': self.value, 'type': '{}'.format(self.type)}

class Entity:
    def __init__(self, entity_id, entity_type, attributes):
        self.id = entity_id
        self.type = entity_type
        self.attributes = attributes

    def get_attributes_json_dict(self):
        json_dict = {}
        for attr in self.attributes:
            json_dict[attr.name] = attr.get_json()
        return json_dict

    def get_json(self):
        json_dict = self.get_attributes_json_dict()
        json_dict['id'] = self.id
        json_dict['type'] = self.type
        json_res = json.dumps(json_dict)
        return json_res


class FiwareService:
    def __init__(self, name: str, path: str, **kwargs):
        self.name = name
        self.path = path


    def get_header(self) -> object:
        return {
            "fiware-service": self.name,
            "fiware-servicepath": self.path
        }


class Orion:
    def __init__(self, Config):
        self.url = Config.data["orion"]["host"] + ':' + Config.data["orion"]["port"] + '/v2'

    def post_entity(self, fiware_service, entity):
        url = self.url + '/entities'
        headers = {**HEADER_CONTENT_JSON, **fiware_service.get_header()}
        cb.post(url, headers, entity.get_json())
   
    def get_entity(self, fiware_service, entity_name,  entity_params=None):
        url = self.url + '/entities/' + entity_name
        headers = fiware_service.get_header()

        if entity_params is None:
            return cb.get(url, headers)
        else:
            return cb.get(url, headers, entity_params)

    def get_all_entities(self, fiware_service, parameter=None,
                         parameter_value=None):
        url = self.url + '/entities'
        headers = fiware_service.get_header()

        if parameter is None and parameter_value is None:
            return cb.get(url, headers)
        elif parameter is not None and parameter_value is not None:
            parameters = {'{}'.format(parameter): '{}'.format(parameter_value)}
            return cb.get(url, headers, parameters)
        else:
            print ("ERROR getting all entities: both function parameters have to be 'not null'")

    def get_entity_keyValues(self, entity_name):
        parameter = {'{}'.format('options'): '{}'.format('keyValues')}
        return self.get_entity(entity_name, parameter)

    def get_entity_attribute_json(self, fiware_service, entity_name,
                                  attribute_name):
        url = self.url + '/entities/' + entity_name + '/attrs/' + attribute_name
        headers = fiware_service.get_header()
        return cb.get(url, headers)

    def get_entity_attribute_value(self, entity_name, attribute_name):
        url = self.url + '/entities/' + entity_name + '/attrs/' + attribute_name + '/value'
        head = HEADER_ACCEPT_PLAIN
        return cb.get(url, head)

    def get_entity_attribute_list(self, entity_name, attr_name_list):
        attributes = ','.join(attr_name_list)
        parameters = {'{}'.format('options'): '{}'.format('values'), '{}'.format('attrs'): attributes}
        return self.get_entity(entity_name, parameters)

    def update_entity(self, fiware_service, entity):
        url = self.url + '/entities/' + entity.name + '/attrs'
        headers = {**HEADER_CONTENT_JSON, **fiware_service.get_header()}
        payload = entity.get_attributes_json_dict()
        cb.patch(url, headers, json.dumps(payload))
        # TODO: query entity operation to check that entity was actually updated
        # if ok, should return 204

    def update_attribute(self, entity_name, attr_name, attr_value):
        url = self.url + '/entities/' + entity_name + '/attrs/' + attr_name + '/value'
        head = HEADER_CONTENT_PLAIN
        cb.put(url, head, json.dumps(attr_value))

    def remove_attributes(self, entity_name):
        url = self.url + '/entities/' + entity_name + '/attrs'
        cb.put(url)

    def create_subscription(self, subscription_body):
        url = self.url + '/subscriptions'
        head = HEADER_CONTENT_JSON

        headers = cb.post(url, head, subscription_body, None, True)
        if headers==None:
            return
        location = headers.get('Location')
        addr_parts = location.split('/')
        subscription_id = addr_parts.pop()
        return subscription_id

