import requests
import json 


HEADER_JSON = {'Accept': 'application/json'}
HEADER_PLAIN = {'Accept': 'text/plain'}
HEADER_CONTENT = {'Content-Type': 'application/json'}

AUTH = ('user', 'pass')

class Attribute:
    def __init__(self, name, value, attr_type):
        self.name = name
        self.value = value
        self.type = attr_type

    def getJSON(self):
        json_dict = {'value': self.value, 'type': '{}'.format(self.type)}
        return json_dict

class Entity:
    def __init__(self, entity_id, entity_type, attributes):
        self.id = entity_id
        self.type = entity_type
        self.attributes = attributes

    def getJSON(self):
        json_dict = {'id': '{}'.format(self.id), 'type': '{}'.format(self.type)}
        for attr in self.attributes:
            json_dict[attr.name] = attr.getJSON()

        json_res = json.dumps(json_dict)
        print(json.dumps(json_dict))
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
    response = requests.post(url, headers=head, auth=autho, data = body)

    if not response.ok:
        print ("POST request with following content returned error status '" + str(response.status_code) + " (" + str(response.reason) + ")'")
        pretty_print_request(response.request)
    else:
        print ("POST ok")

def get(url, head, autho, parameters=None):
    response  = requests.get(url, headers=head, auth=autho, params=parameters)

    if not response.ok:
        print ("GET request with following content returned error status '" + str(response.status_code) + " (" + str(response.reason) + ")'")
        pretty_print_request(response.request)
        print ("Response of failed GET request: " + response.text)
    else:
        return response.text

class Orion:
    def __init__(self, Config):
        self.url = Config.data["orion"]["host"] + ':' + Config.data["orion"]["port"] + '/v2'

    def postEntity(self, entity):
        url = self.url + '/entities'
        head = HEADER_CONTENT
        post(url, head, AUTH, entity.getJSON())
   
    def getEntity(self, entity_name, entity_params=None):
        url = self.url + '/entities/' + entity_name
        head = HEADER_JSON

        if entity_params is None:
            return get(url, head, AUTH)
        else:
            return get(url, head, AUTH, entity_params)

    def getAllEntities(self, parameter=None, parameter_value=None):
        url = self.url + '/entities'
        head = HEADER_JSON

        if parameter is None and parameter_value is None:
            return get (url, head, AUTH)
        elif parameter is not None and parameter_value is not None:
            parameters = {'{}'.format(parameter): '{}'.format(parameter_value)}
            return get (url, head, AUTH, parameters)
        else:
            print ("ERROR getting all entities: both function parameters have to be 'not null'")

    def getEntityKeyValues(self, entity_name):
        parameter = {'{}'.format('options'): '{}'.format('keyValues')}
        return self.getEntity(entity_name, parameter)

    def getEntityAttribute_JSON(self, entity_name, attribute_name):
        url = self.url + '/entities/' + entity_name + '/attrs/' + attribute_name
        head = HEADER_JSON
        return get(url, head, AUTH)

    def getEntityAttributeValue(self, entity_name, attribute_name):
        url = self.url + '/entities/' + entity_name + '/attrs/' + attribute_name + '/value'
        head = HEADER_PLAIN
        return get(url, head, AUTH)

    def getEntityAttributeList(self, entity_name, attr_name_list):
        attributes = ','.join(attr_name_list)
        parameters = {'{}'.format('options'): '{}'.format('values'), '{}'.format('attrs'): attributes}
        return self.getEntity(entity_name, parameters)

