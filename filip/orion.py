import json
import requests
import filip.request_utils as requtils

import logging

log = logging.getLogger('orion')


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
        self.type = entity_dict["type"]
        self.entity_dict = entity_dict
        self._PROTECTED = ['id', 'type']

    def get_json(self):
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


    def get_attributes(self):
        """
        Function returns list of attribute names.
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



class Relationship:
    """
    Class implements the concept of FIWARE Entity Relationships.

    """

    def __init__(self, ref_object:Entity, subject:Entity, predicate:str = None ):
        """
        :param ref_object:  The parent / object of the relationship
        :param subject: The child / subject of the relationship
        :param predicate: currently not supported -> describes the relationship between object and subject
        """
        self.object = ref_object
        self.subject = subject
        self.predicate = predicate
        self.add_ref()

    def add_ref(self):
        """
        Function updates the subject Attribute with the relationship attribute
        :return:
        """
        ref_attr = json.loads(self.get_ref())
        self.subject.add_attribute(ref_attr)


    def get_ref(self):
        """
        Function creates the NGSI Ref schema in a ref_dict, needed for the subject
        :return: ref_dict
        """
        ref_type = self.object.type
        ref_key = "ref" + str(ref_type)
        ref_dict = {}
        ref_dict[ref_key] = {"type" : "Relationship",
                             "value" : self.object.id}

        return json.dumps(ref_dict)

    def get_json(self):
        """
        Function returns a JSON to describe the Relationship,
        which then can be pushed to orion
        :return: whole_dict
        """
        temp_dict = {}
        temp_dict["id"] = self.subject.id
        temp_dict["type"] = self.subject.type
        ref_dict = json.loads(self.get_ref())
        whole_dict = {**temp_dict, **ref_dict}
        return json.dumps(whole_dict)


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

    def log_switch(self, level, response):
        """
        Function returns the required log_level with the repsonse
        :param level: The logging level that should be returned
        :param response: The message for the logger
        :return:
        """
        switch_dict={
                "INFO": logging.info,
                "ERROR":  logging.error,
                "WARNING": logging.warning
                }.get(level, logging.info)(msg=response)



    def sanity_check(self):
        url = self.url[:-3] + '/version'
        headers=self.get_header(requtils.HEADER_ACCEPT_JSON)
        response = requests.get(url, headers=headers)
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, retstr)
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
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, response)
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

    def post_relationship(self, json_data=None):
        """
        Function can be used to post a one to many or one to one relationship.
        :param json_data: Relationship Data obtained from the Relationship class. e.g. :
                {"id": "urn:ngsi-ld:Shelf:unit001", "type": "Shelf",
                "refStore": {"type": "Relationship", "value": "urn:ngsi-ld:Store:001"}}
                Can be a one to one or a one to many relationship
        """
        url = self.url + '/op/update'
        headers = self.get_header(requtils.HEADER_CONTENT_JSON)
        # Action type append required,
        # Will overwrite existing entities if they exist whereas
        # the entities attribute holds an array of entities we wish to update.
        payload = {"actionType": "APPEND",
                   "entities": [json.loads(json_data)]}
        data = json.dumps(payload)
        response = requests.post(url=url, data=data, headers=headers)
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, retstr)

    def get_subjects(self, object_entity_name:str, object_entity_type:str, subject_type=None):
        """
        Function gets the JSON for child / subject entities for a parent / object entity.
        :param object_entity_name: The parent / object entity name
        :param object_entity_type: The type of the parent / object entity
        :param subject_type: optional parameter, if added only those child / subject entities are returned that match the type
        :return: JSON containing the child / subject information
        """

        url = self.url + '/entities/?q=ref' + object_entity_type + '=='  + object_entity_name + '&options=count'
        if subject_type != None:
             url = url + '&attrs=type&type=' + subject_type
        headers = self.get_header()
        response = requests.get(url=url, headers=headers)
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, retstr)
        else:
            return response.text

    def get_objects(self, subject_entity_name:str, subject_entity_type:str, object_type=None):
        """
        Function returns a List of all objects associated to a subject. If object type is not None,
        only those are returned, that match the object type.
        :param subject_entity_name: The child / subject entity name
        :param subject_entity_type: The type of the child / subject entity
        :param object_type:
        :return: List containing all associated objects
        """
        url = self.url + '/entities/' + subject_entity_name + '/?type=' + subject_entity_type + '&options=values'
        if object_type != None:
            url = url + '&attrs=ref' + object_type
        headers = self.get_header()
        response = requests.get(url=url, headers=headers)
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, retstr)
        else:
            return response.text
   
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
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, retstr)
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
            log.error("Getting all entities: both function parameters have to be 'not null'")
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, retstr)
        else:
            return response.text

    def get_entities_list(self) -> list:
        url = self.url + '/entities'
        header = self.get_header(requtils.HEADER_ACCEPT_JSON)
        response = requests.get(url, headers=header)
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, retstr)
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
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, retstr)
        else:
            return response.text

    def get_entity_attribute_value(self, entity_name, attribute_name):
        url = self.url + '/entities/' + entity_name + '/attrs/' \
                       + attribute_name + '/value'
        response = requests.get(url, headers=self.get_header())
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, retstr)
        else:
            return response.text

    def get_entity_attribute_list(self, entity_name, attr_name_list):
        attributes = ','.join(attr_name_list)
        parameters = {'{}'.format('options'): '{}'.format('values'),
                      '{}'.format('attrs'): attributes}
        return self.get_entity(entity_name, parameters)

    def update_entity(self, entity):
        url = self.url + '/entities/' + entity.id + '/attrs'
        payload = entity.get_attributes_key_values()
        headers=self.get_header(requtils.HEADER_CONTENT_JSON)
        data=json.dumps(payload)
        response = requests.patch(url, headers=headers, data=data)
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, retstr)

    def update_attribute(self, entity_name, attr_name, attr_value):
        url = self.url + '/entities/' + entity_name + '/attrs/' \
                       + attr_name + '/value'
        headers=self.get_header(requtils.HEADER_CONTENT_PLAIN)
        data=json.dumps(attr_value)
        response = requests.put(url, headers=headers, data=data)
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, retstr)

    def remove_attributes(self, entity_name):
        url = self.url + '/entities/' + entity_name + '/attrs'
        response = requests.put(url)
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, response)

    def create_subscription(self, subscription_body):
        url = self.url + '/subscriptions'
        headers=self.get_header(requtils.HEADER_CONTENT_JSON)
        response = requests.post(url, headers=headers, data=subscription_body)
        if response.headers==None:
            return
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, retstr)
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
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, retstr)
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
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, retstr)

    def delete_subscription(self, subscription_id):
        url = self.url + '/subscriptions/' + subscription_id
        response = requests.delete(url, headers=self.get_header())
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, retstr)

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
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, retstr)

    def delete(self, entity_id: str, attr: str = None):
        url = self.url + '/entities/' + entity_id
        response = requests.delete(url, headers=self.get_header())
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, retstr)

    def delete_all_entities(self):
        entities = self.get_entities_list()
        for entity_id in entities:
            self.delete(entity_id)
