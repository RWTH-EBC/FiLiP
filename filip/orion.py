import requests
import json 


HEADER_ACCEPT_JSON = {'Accept': 'application/json'}
HEADER_ACCEPT_PLAIN = {'Accept': 'text/plain'}
HEADER_CONTENT_JSON = {'Content-Type': 'application/json'}
HEADER_CONTENT_PLAIN = {'Content-Type': 'text/plain'}

AUTH = ('user', 'pass')

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

def pretty_print_request(req):
    print('{}\n{}\n{}\n\nBODY:{}\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
        '---------------------------'
    ))

def post(url, head, autho, body):
    response = requests.post(url, headers=head, auth=autho, data=body)

    if not response.ok:
        print ("POST request with following content returned error status '" + str(response.status_code) + " (" + str(response.reason) + ")'")
        pretty_print_request(response.request)
    else:
        print ("POST ok")

def put(url, head=None, autho=None, data=None):
    response = requests.put(url, headers=head,auth=autho, data=data)

    if not response.ok:
        print ("PUT request with following content returned error status '" + str(response.status_code) + " (" + str(response.reason) + ")'")
        pretty_print_request(response.request)
    else:
        print ("PUT ok")

def get(url, head, autho, parameters=None):
    response  = requests.get(url, headers=head, auth=autho, params=parameters)

    if not response.ok:
        print ("GET request with following content returned error status '" + str(response.status_code) + " (" + str(response.reason) + ")'")
        pretty_print_request(response.request)
        print ("Response of failed GET request: " + response.text)
    else:
        return response.text

def patch(url, head, autho, body):
    response = requests.patch(url, data=body, headers=head, auth=autho)  # TODO: check if 'data' should be replaced with 'json'

    if not response.ok:
        print ("PATCH request with following content returned error status '" + str(response.status_code) + " (" + str(response.reason) + ")'")
        pretty_print_request(response.request)
    else:
        print ("PATCH ok")
        # TODO: check success
            # response should be 204 (No Content)
            # query entity operation to check that entity was actually updated

class Orion:
    def __init__(self, Config):
        self.url = Config.data["orion"]["host"] + ':' + Config.data["orion"]["port"] + '/v2'

<<<<<<< HEAD
    def postEntity(self, entity):
        url = self.url + 'v2/entities'
        head = HEADER_CONTENT
        post(url, head, AUTH, entity.getJSON())
=======
    def post_entity(self, entity):
        url = self.url + '/entities'
        head = HEADER_CONTENT_JSON
        post(url, head, AUTH, entity.get_json())
>>>>>>> remotes/origin/development
   
    def get_entity(self, entity_name, entity_params=None):
        url = self.url + '/entities/' + entity_name
        head = HEADER_ACCEPT_JSON

        if entity_params is None:
            return get(url, head, AUTH)
        else:
            return get(url, head, AUTH, entity_params)

    def get_all_entities(self, parameter=None, parameter_value=None):
        url = self.url + '/entities'
        head = HEADER_ACCEPT_JSON

        if parameter is None and parameter_value is None:
            return get (url, head, AUTH)
        elif parameter is not None and parameter_value is not None:
            parameters = {'{}'.format(parameter): '{}'.format(parameter_value)}
            return get (url, head, AUTH, parameters)
        else:
            print ("ERROR getting all entities: both function parameters have to be 'not null'")

    def get_entity_keyValues(self, entity_name):
        parameter = {'{}'.format('options'): '{}'.format('keyValues')}
        return self.get_entity(entity_name, parameter)

    def get_entity_attribute_json(self, entity_name, attribute_name):
        url = self.url + '/entities/' + entity_name + '/attrs/' + attribute_name
        head = HEADER_ACCEPT_JSON
        return get(url, head, AUTH)

    def get_entity_attribute_value(self, entity_name, attribute_name):
        url = self.url + '/entities/' + entity_name + '/attrs/' + attribute_name + '/value'
        head = HEADER_ACCEPT_PLAIN
        return get(url, head, AUTH)

    def get_entity_attribute_list(self, entity_name, attr_name_list):
        attributes = ','.join(attr_name_list)
        parameters = {'{}'.format('options'): '{}'.format('values'), '{}'.format('attrs'): attributes}
        return self.get_entity(entity_name, parameters)

    def update_entity(self, entity):
        url = self.url + '/entities/' + entity.name + '/attrs'
        head = HEADER_CONTENT_JSON
        json_dict = entity.get_attributes_json_dict()
        patch(url, head, AUTH, json.dumps(json_dict))
        # TODO: see patch function

    def update_attribute(self, entity_name, attr_name, attr_value):
        url = self.url + '/entities/' + entity_name + '/attrs/' + attr_name + '/value'
        head = HEADER_CONTENT_PLAIN
        put(url, head, AUTH, attr_value)

    def remove_attributes(self, entity_name):
        url = self.url + '/entities/' + entity_name + '/attrs'
        put(url)
