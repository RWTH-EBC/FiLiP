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
        json_dict = {'value': self.value, 'type': '{}'.format(self.type)}
        return json_dict

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

class Orion:
    def __init__(self, Config):
        self.url = Config.data["orion"]["host"] + ':' + Config.data["orion"]["port"] + '/v2'

    def post_entity(self, entity):
        url = self.url + '/entities'
        head = HEADER_CONTENT_JSON
        cb.post(url, head, entity.get_json())
   
    def get_entity(self, entity_name, entity_params=None):
        url = self.url + '/entities/' + entity_name
        head = HEADER_ACCEPT_JSON

        if entity_params is None:
            return cb.get(url, head)
        else:
            return cb.get(url, head, entity_params)

    def get_all_entities(self, parameter=None, parameter_value=None):
        url = self.url + '/entities'
        head = HEADER_ACCEPT_JSON

        if parameter is None and parameter_value is None:
            return cb.get(url, head)
        elif parameter is not None and parameter_value is not None:
            parameters = {'{}'.format(parameter): '{}'.format(parameter_value)}
            return cb.get(url, head, parameters)
        else:
            print ("ERROR getting all entities: both function parameters have to be 'not null'")

    def get_entity_keyValues(self, entity_name):
        parameter = {'{}'.format('options'): '{}'.format('keyValues')}
        return self.get_entity(entity_name, parameter)

    def get_entity_attribute_json(self, entity_name, attribute_name):
        url = self.url + '/entities/' + entity_name + '/attrs/' + attribute_name
        head = HEADER_ACCEPT_JSON
        return cb.get(url, head)

    def get_entity_attribute_value(self, entity_name, attribute_name):
        url = self.url + '/entities/' + entity_name + '/attrs/' + attribute_name + '/value'
        head = HEADER_ACCEPT_PLAIN
        return cb.get(url, head)

    def get_entity_attribute_list(self, entity_name, attr_name_list):
        attributes = ','.join(attr_name_list)
        parameters = {'{}'.format('options'): '{}'.format('values'), '{}'.format('attrs'): attributes}
        return self.get_entity(entity_name, parameters)

    def update_entity(self, entity):
        url = self.url + '/entities/' + entity.name + '/attrs'
        head = HEADER_CONTENT_JSON
        json_dict = entity.get_attributes_json_dict()
        cb.patch(url, head, json.dumps(json_dict))
        # TODO: query entity operation to check that entity was actually updated
        # if ok, should return 204

    def update_attribute(self, entity_name, attr_name, attr_value):
        url = self.url + '/entities/' + entity_name + '/attrs/' + attr_name + '/value'
        head = HEADER_CONTENT_PLAIN
        cb.put(url, head, attr_value)

    def remove_attributes(self, entity_name):
        url = self.url + '/entities/' + entity_name + '/attrs'
        cb.put(url)

    def create_subscription(self, subscription_body):
        url = self.url + '/subscriptions'
        head = HEADER_CONTENT_JSON

        headers = cb.post(url, head, subscription_body, None, True)

        location = headers.get('Location')
        addr_parts = location.split('/')
        subscription_id = addr_parts.pop()
        return subscription_id

