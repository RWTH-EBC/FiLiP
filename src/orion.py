import config

import requests
import json 


HEADER_ACCEPT = {'Accept': 'application/json'}
HEADER_CONTENT = {'Content-Type': 'application/json'}
AUTH = ('user', 'pass')

CONFIG = config.Config()
URL = CONFIG.orion_host + ':' + CONFIG.orion_port + '/v2'


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


def testConfig():
    c.test_config()

def post(url, head, autho, body):
    res = requests.post(url, headers=head, auth=autho, data = body) 
    print ("post result: " + str(res))
    print (res.content)

def get(url, head, autho, parameters=None):
    res = requests.get(url, headers=head, auth=autho, params=parameters)
    print ("get result: " + str(res))
    print (res.text)


def createEntity(entity):
    e_url = URL + '/entities'
    e_head = HEADER_CONTENT
    post(e_url, e_head, AUTH, entity.getJSON())
   
def queryEntity(e_name, e_params=None):
    e_url = URL + '/entities/' + e_name
    e_head = HEADER_ACCEPT

    if e_params is None:
        get(e_url, e_head, AUTH)
    else:
        get(e_url, e_head, AUTH, e_params)

def getEntityKeyValues(e_name):
    parameter = {'{}'.format('options'): '{}'.format('keyValues')}
    queryEntity(e_name, parameter)

def getEntityAttributes(e_name, attr_name_list):
    attributes = ''.join(attr_name_list)
    parameters = {'{}'.format('options'): '{}'.format('values'), '{}'.format('attrs'): attributes}
    queryEntity(e_name, parameters)


if __name__=="__main__":
    e_a1 = Attribute('temperature', 23, 'Float')
    e_a2 = Attribute('pressure', 514, 'Integer')
    attributes = e_a1, e_a2
    e = Entity('Room3', 'Room', attributes)

#    createEntity(e)
    queryEntity("Room1")
    getEntityKeyValues("Room2")

    attr_list = ["temperature", "pressure"]
    getEntityAttributes("Room3", attr_list)
