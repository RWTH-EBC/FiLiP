import json
import requests
from filip import request_utils as requtils

import logging

log = logging.getLogger('orion')


# Class is only implemented for backward compatibility
class Attribute:
    """
    Describes the attribute of an entity.
    """
    def __init__(self, name, value, attr_type):
        self.name = name
        self.value = value
        self.type = attr_type

    def get_json(self):
        return {'value': self.value, 'type': '{}'.format(self.type)}

class Entity:
    def __init__(self, entity_dict: dict):
        """
        :param entity_dict: A dictionarry describing the entity
        Needed Structure: { "id" : "Sensor002",
                            "type": "temperature_Sensor",
                            "Temperature"  : { "value" : 17,
                                                "type" : "Number" },
                            "Status" : {"value": "Ok",
                                        "type": "Text" }
                            }
        """

        self.id = entity_dict["id"]
        self.entity_dict = entity_dict
        self._PROTECTED = ['id', 'type']

    def __repr__(self):
        """
        returns the object-representation
        """
        attrs = self.get_attributes_key_values()
        entity_str = '"enity_id": "{}", "type": "{}", "attributes": "{}" '.format(self.id, self.entity_dict["type"], attrs)
        return entity_str

    def get_json(self):
        """
        Function returns the Entity to be posted as a JSON
        :return: the Entity Json
        """
        json_res = json.dumps(self.entity_dict)
        return json_res

    def add_attribute(self, attr_dict:dict):
        """
        Function adds another Attribute to an existing Entity.
        :param attr_dict: A dictionary describing an Attribute
                        "Temperature"  : { "value" : 17,
                                                "type" : "Number" },
        :return: updated entity dict
        """
        for key in attr_dict.keys():
            self.entity_dict[key] = attr_dict[key]

    def delete_attribute(self, attr_name:str):
        """
        Function deletes an attribute from an existing Entity
        :param attr_name: the name of the attribute to delete
        :return: updated entity_dict
        """
        # ToDo Discuss deep or shallow copy
        del self.entity_dict[attr_name]

    def get_attributes(self):
        """
        Function returns all attributes of an entity
        :return:
        """
        attributes = [key for key in self.entity_dict.keys() if key not in self._PROTECTED]
        return attributes

    def get_attributes_key_values(self):
        """
        Function returns all attributes, their types and values of an entity
        :return:
        """
        attributes_values = {key: value for (key,value) in self.entity_dict.items() if key not in self._PROTECTED}
        return attributes_values

class FiwareService:
    """
    Define entity service paths which are supported by the Orion Context Broker
    to support hierarchical scopes:
    https://fiware-orion.readthedocs.io/en/master/user/service_path/index.html
    """
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path

    def update(self, name: str, path: str):
        """Overwrites the fiware_service and service path of config.json"""
        self.name = name
        self.path = path

    def list(self):
        print

    def get_header(self) -> object:
        return {
            "fiware-service": self.name,
            "fiware-servicepath": self.path
        }

class Orion:
    """
    Implementation of Orion Context Broker functionalities, such as creating
    entities and subscriptions; retrieving, updating and deleting data.
    Further documentation:
    https://fiware-orion.readthedocs.io/en/master/
    """
    def __init__(self, Config):
        self.url = Config.data["orion"]["host"] + ':' \
                   + Config.data["orion"]["port"] + '/v2'
        self.fiware_service = FiwareService(name=Config.data['fiware']['service'],
                                       path=Config.data['fiware']['service_path'])
        self.url_v1 = Config.data["orion"]["host"] + ':' \
                      + Config.data["orion"]["port"] + '/v1'

    def set_service(self, fiware_service):
        """Overwrites the fiware_service and service path of config.json"""
        self.fiware_service.update(fiware_service.name, fiware_service.path)
 
    def get_header(self, additional_headers: dict = None):
        """combine fiware_service header (if set) and additional headers"""
        if self.fiware_service == None:
            return additional_headers
        elif additional_headers == None:
            return self.fiware_service.get_header()
        else:
            headers = {**self.fiware_service.get_header(), **additional_headers}
            return headers

    def sanity_check(self):
        url = self.url[:-3] + '/version'
        headers=self.get_header(requtils.HEADER_ACCEPT_JSON)
        response = requests.get(url, headers=headers)
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            print(retstr)
            requtils.pretty_print_request(response.request)
        else:
            json_obj = json.loads(response.text)
            version = json_obj["orion"]["version"]
            print(version)

    def post_entity(self, entity):
        url = self.url + '/entities'
        headers=self.get_header(requtils.HEADER_CONTENT_JSON)
        data=entity.get_json()
        response = requests.post(url, headers=headers, data=data)
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            print(retstr)
            requtils.pretty_print_request(response.request)

    def post_json(self, json=None, entity=None, params=None):
        """

        :param json:
        :param entity:
        :param params:
        :return:
        """
        headers=self.get_header(requtils.HEADER_CONTENT_JSON)
        if json is not None:
            json_data = json
        elif (json is None) and (entity is not None):
            json_data = entity.get_json()
        if params == None:
            url = self.url + '/entities'
            response = requests.post(url, headers=headers, data=json_data)
        else:
            url = self.url + "/entities" + "?options=" + params
            response = requests.post(url, headers=headers, data=json_data)
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            print(retstr)
            requtils.pretty_print_request(response.request)
            print(url, headers)

    def post_json_key_value(self, json_data=None, params="keyValues"):
        """

        :param json_data:
        :param params:
        :return:
        """
        headers=self.get_header(requtils.HEADER_CONTENT_JSON)
        url = self.url + "/entities" + "?options=" + params
        response = requests.post(url, headers=headers, data=json_data)
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            print(retstr)
            requtils.pretty_print_request(response.request)
            print(url, headers)
   
    def get_entity(self, entity_name,  entity_params=None):
        url = self.url + '/entities/' + entity_name
        headers=self.get_header()
        if entity_params is None:
            response = requests.get(url, headers=headers)
        else:
            response = requests.get(url, headers=headers,
                                    params=entity_params)
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            print(retstr)
        else:
            return response.text

    def get_all_entities(self, parameter=None, parameter_value=None):
        url = self.url + '/entities'
        headers=self.get_header()
        if parameter is None and parameter_value is None:
            response = requests.get(url, headers=headers)
        elif parameter is not None and parameter_value is not None:
            parameters = {'{}'.format(parameter): '{}'.format(parameter_value)}
            response = requests.get(url, headers=headers, params=parameters)
        else:
            log.error("ERROR getting all entities: both function parameters have to be 'not null'")
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            print(retstr)
        else:
            return response.text

    def get_entities_list(self) -> list:
        url = self.url + '/entities'
        header = self.get_header(requtils.HEADER_ACCEPT_JSON)
        response = requests.get(url, headers=header)
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            print(retstr)
            return None
        json_object = json.loads(response.text)
        entities = []
        for key in json_object:
            entities.append(key["id"])
        return entities

    def get_entity_keyValues(self, entity_name):
        parameter = {'{}'.format('options'): '{}'.format('keyValues')}
        return self.get_entity(entity_name, parameter)

    def get_entity_attribute_json(self, entity_name, attribute_name):
        url = self.url + '/entities/' + entity_name + '/attrs/' + attribute_name
        response = requests.get(url, headers=self.get_header())
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            print(retstr)
        else:
            return response.text

    def get_entity_attribute_value(self, entity_name, attribute_name):
        url = self.url + '/entities/' + entity_name + '/attrs/' \
                       + attribute_name + '/value'
        response = requests.get(url, headers=self.get_header())
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            print(retstr)
        else:
            return response.text

    def get_entity_attribute_list(self, entity_name, attr_name_list):
        """
        Function returns all types and values for a list of attributes of an entity,
        given in attr_name_list
        :param entity_name: Entity_name - Name of the entity to obtain the values from
        :param attr_name_list: List of attributes - e.g. ["Temperature"]
        :return: List, containin all attribute dictionaries e.g.: [{"value":33,"type":"Float"}]
        """
        attributes = ','.join(attr_name_list)
        parameters = {'{}'.format('options'): '{}'.format('values'),
                      '{}'.format('attrs'): attributes}
        return self.get_entity(entity_name, parameters)

    def update_entity(self, entity):
        url = self.url + '/entities/' + entity.name + '/attrs'
        payload = entity.get_attributes_json_dict()
        headers=self.get_header(requtils.HEADER_CONTENT_JSON)
        data=json.dumps(payload)
        response = requests.patch(url, headers=headers, data=data)
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            print(retstr)

    def update_attribute(self, entity_name, attr_name, attr_value):
        url = self.url + '/entities/' + entity_name + '/attrs/' \
                       + attr_name + '/value'
        headers=self.get_header(requtils.HEADER_CONTENT_PLAIN)
        data=json.dumps(attr_value)
        response = requests.put(url, headers=headers, data=data)
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            print(retstr)

    def add_attribute(self, entity:object=None , entity_name:str=None, attribute_dict:dict=None):
        # POST /v2/entities/{id}/attrs?options=append
        """
        This function adds attributes to the Entity in the Context Broker. This can be done in two ways,
        either by first adding the attribute to the Entity object or by directly sending it from a dict/JSON
        The Function first compares it with existing attributes, and only adds (so updates) the ones not previoulsy existing
        :param entity: The updated Entity Instance
        :param entity_name: The Entity name which should be updated
        :param attribute_dict: A JSON/Dict containing the attributes
        :return: -
        """
        if isinstance(entity, Entity):
            attributes = entity.get_attributes()
            entity_name = Entity.id
        else:
            attributes = attribute_dict
            entity_name = entity_name
        existing_attributes = self.get_attributes(entity_name)
        new_attributes = {k: v for (k, v) in attributes.items() if k not in existing_attributes}
        url = self.url + '/entities/' + entity_name + '/attrs?options=append'
        headers=self.get_header(requtils.HEADER_CONTENT_JSON)
        data = json.dumps(new_attributes)
        response = requests.post(url, data=data, headers=headers)
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            print(retstr)




    def get_attributes(self, entity_name:str):
        """
        For a given entity this function returns all attribute names
        :param entity_name: the name of the entity
        :return: attributes - list of attributes
        """
        entity_json = json.loads(self.get_entity(entity_name))
        attributes = [k for k in entity_json.keys() if k not in ["id", "type"]]
        return attributes



    def remove_attributes(self, entity_name):
        url = self.url + '/entities/' + entity_name + '/attrs'
        response = requests.put(url)
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            print(retstr)

    def create_subscription(self, subscription_body):
        url = self.url + '/subscriptions'
        headers=self.get_header(requtils.HEADER_CONTENT_JSON)
        response = requests.post(url, headers=headers, data=subscription_body)
        if response.headers==None:
            return
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            print(retstr)
            return ""
        else:
            location = response.headers.get('Location')
            addr_parts = location.split('/')
            subscription_id = addr_parts.pop()
            return subscription_id

    def get_subscription_list(self):
        url = self.url + '/subscriptions'
        response = requests.get(url, headers=self.get_header())
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            print(retstr)
            return
        json_object = json.loads(response.text)
        subscriptions = []
        for key in json_object:
            subscriptions.append(key["id"])
        return subscriptions

    def get_subscription(self, subscription_id):
        url = self.url + '/subscriptions/' + subscription_id
        response = requests.get(url, headers=self.get_header())
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            print(retstr)

    def delete_subscription(self, subscription_id):
        url = self.url + '/subscriptions/' + subscription_id
        response = requests.delete(url, headers=self.get_header())
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            print(retstr)

    def delete_all_subscriptions(self):
        subscriptions = self.get_subscription_list()
        for sub_id in subscriptions:
            self.delete_subscription(sub_id)

    def post_cmd_v1(self, entity_id: str, entity_type: str, cmd_name: str, cmd_value: str):
        url = self.url_v1 + '/updateContext'
        payload = {"updateAction": "UPDATE",
                   "contextElements": [
                        {"id": entity_id,
                         "type" : entity_type,
                         "isPattern": "false",
                         "attributes": [
                            {"name": cmd_name,
                             "type": "command",
                             "value": cmd_value
                            }]
                        }]
                   }
        headers=self.get_header(requtils.HEADER_CONTENT_JSON)
        data=json.dumps(payload)
        response = requests.post(url, headers=headers, data=data)
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            print(retstr)

    def delete(self, entity_id: str, attr: str = None):
        url = self.url + '/entities/' + entity_id
        response = requests.delete(url, headers=self.get_header())
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            print(retstr)

    def delete_all_entities(self):
        entities = self.get_entities_list()
        for entity_id in entities:
            self.delete(entity_id)
