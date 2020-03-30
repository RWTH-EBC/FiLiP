import json
import requests
from filip import request_utils as requtils
from filip import test

import datetime
import math
import logging

log = logging.getLogger('orion')


# ToDo Query params

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
        self.type = entity_dict["type"]
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

    def add_attribute(self, attr_dict: dict):
        """
        Function adds another Attribute to an existing Entity.
        :param attr_dict: A dictionary describing an Attribute
                        "Temperature"  : { "value" : 17,
                                                "type" : "Number" },
        :return: updated entity dict
        """
        for key in attr_dict.keys():
            self.entity_dict[key] = attr_dict[key]

    def delete_attribute(self, attr_name: str):
        """
        Function deletes an attribute from an existing Entity
        :param attr_name: the name of the attribute to delete
        :return: updated entity_dict
        """
        # ToDo Discuss deep or shallow copy
        del self.entity_dict[attr_name]

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

    def __repr__(self):
        fiware_service_str = f'"fiware-service": "{self.name}", "fiware-servicepath": "{self.path}"'
        return fiware_service_str


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
            orion_version = json_obj.get("orion version")
            orion_ld_version = json_obj.get("orionld version")
            if (orion_version == None) or (orion_ld_version == None):
                orion_version = json_obj["orion"]["version"]
                log.info(f"This is the Orion version: {orion_version}")
            else:
                log.info(f"This is the Orion version: {orion_version} ")
                log.info(f"This is the OrionLD version: {orion_ld_version}")

    def test_connection(self):
        """
        Function utilises the test.test_connection() function to check the availability of a given url and service.
        :return: Boolean, True if the service is reachable, False if not.
        """
        boolean = test.test_connection(url=self.url, service_name=self.fiware_service)
        return boolean


    def post_entity(self, entity:object,  update:bool=True):
        """
        Function registers an Object with the Orion Context Broker, if it allready exists it can be automatically updated
        if the overwrite bool is True
        First a post request with the entity is tried, if the response code is 422 the entity is
        uncrossable, as it already exists there are two options, either overwrite it, if the attribute have changed (e.g. at least one new/
        new values) (update = True) or leave it the way it is (update=False)
        :param entity: An entity object
        :param update: If the response.status_code is 422, whether the old entity should be updated or not
        :return:
        """
        url = self.url + '/entities'
        headers=self.get_header(requtils.HEADER_CONTENT_JSON)
        data= entity.get_json()
        response = requests.post(url, headers=headers, data=data)
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            if (response.status_code == 422) & (update == True):
                    url += "/" + entity.id + "/attrs"
                    response = requests.post(url, headers=headers, data=data)
                    ok, retstr = requtils.response_ok(response)
        level, retstr = requtils.logging_switch(response)
        self.log_switch(level, response)


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
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, retstr)


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
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, retstr)


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


        # ToDo test return for multi association
    def get_objects(self, subject_entity_name:str, subject_entity_type:str, object_type=None):
        """
        Function returns a List of all objects associated to a subject. If object type is not None,
        only those are returned, that match the object type.
        :param subject_entity_name: The child / subject entity name
        :param subject_entity_type: The type of the child / subject entity
        :param object_type:
        :return: List containing all associated objects

        """
        url = self.url + '/entities/' + subject_entity_name + '/?type=' + subject_entity_type + '&options=keyValues'
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

    def get_associated(self, name:str, type:str, associated_type=None):
        """
        Function returns all associated data for a given entity name and type
        :param name: name of the entity
        :param type: type of the entity
        :param associated_type: if only associated data of one type should be returned, this parameter has to be the type
        :return: A dictionary, containing the data of the entity, a key "subjects" and "objects" that contain each a list
                with the reflective data
        """
        data_dict = {}
        associated_objects = self.get_objects(subject_entity_name=name, subject_entity_type=type,
                                              object_type=associated_type)
        associated_subjects = self.get_subjects(object_entity_name=name, object_entity_type=type,
                                                subject_type=associated_type)
        if associated_subjects != None:
            data_dict["subjects"] = json.loads(associated_subjects)
        if associated_objects != None:
            object_json = json.loads(associated_objects)
            data_dict["objects"] = []
            if isinstance(object_json, list):
               for associated_object in object_json:
                entity_name = associated_object["id"]
                object_data = json.loads(self.get_entity(entity_name=entity_name))
                data_dict["objects"].append(object_data)
            else:
                entity_name = object_json["id"]
                object_data = json.loads(self.get_entity(entity_name=entity_name))
                data_dict["objects"].append(object_data)

        entity_dict = json.loads(self.get_entity(entity_name=name))

        whole_dict = {**entity_dict, **data_dict}

        return whole_dict








   
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

    def get_all_entities(self, parameter=None, parameter_value=None, limit=100):
        url = self.url + '/entities?options=count'
        headers=self.get_header()
        if parameter is None and parameter_value is None:
            response = requests.get(url, headers=headers)
            sub_count = float(response.headers["Fiware-Total-Count"])
            if sub_count >= limit:
                response = self.get_pagination(url=url, headers=headers,
                                           limit=limit, count=sub_count)
                return response
        elif parameter is not None and parameter_value is not None:
            parameters = {'{}'.format(parameter): '{}'.format(parameter_value)}
            response = requests.get(url, headers=headers, params=parameters)
            sub_count = float(response.headers["Fiware-Total-Count"])
            if sub_count >= limit:
                response = self.get_pagination(url=url, headers=headers,
                                               limit=limit, count=sub_count, params=parameters)
                return response
        else:
            log.error("Getting all entities: both function parameters have to be 'not null'")
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, retstr)
        else:
            return response.text

    def get_entities_list(self, limit=100) -> list:
        url = self.url + '/entities?options=count'
        header = self.get_header(requtils.HEADER_ACCEPT_JSON)
        response = requests.get(url, headers=header)
        sub_count = float(response.headers["Fiware-Total-Count"])
        if sub_count >= limit:
            response = self.get_pagination(url=url, headers=header,
                                           limit=limit, count=sub_count)
            return response
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
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, response)

    def create_subscription(self, subscription_body, check_duplicate:bool=True):
        url = self.url + '/subscriptions'
        headers=self.get_header(requtils.HEADER_CONTENT_JSON)
        if check_duplicate is True:
            exists = self.check_duplicate_subscription(subscription_body)
            if exists is True:
                log.info(f"{datetime.datetime.now()} - A similar subscription already exists.")
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

    def get_subscription_list(self, limit=100):
        url = self.url + '/subscriptions?options=count'
        response = requests.get(url, headers=self.get_header())
        sub_count = float(response.headers["Fiware-Total-Count"])
        if sub_count >= limit:
            response = self.get_pagination(url=url, headers=self.get_header(),
                                           limit=limit, count=sub_count)
            return response
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

    def get_pagination(self, url:str, headers:dict,
                       count:float,  limit:int=20, params=None):
        """
        NGSIv2 implements a pagination mechanism in order to help clients to retrieve large sets of resources.
        This mechanism works for all listing operations in the API (e.g. GET /v2/entities, GET /v2/subscriptions, POST /v2/op/query, etc.).
        This function helps getting datasets that are larger than the limit for the different GET operations.
        :param url: Information about the url, obtained from the orginal function e.g. : http://localhost:1026/v2/subscriptions?limit=20&options=count
        :param headers: The headers from the original function, e.g: {'fiware-service': 'crio', 'fiware-servicepath': '/measurements'}
        :param count: Number of total elements, obtained by adding "&options=count" to the url,
                        included in the response headers
        :param limit: Limit, obtained from the oringal function, default is 20
        :return: A list, containing all objects in a dictionary
        """
        all_data = []
        # due to a math, one of the both numbers has to be a float,
        # otherwise the value is rounded down not up
        no_intervals = int(math.ceil(count / limit))
        for i in range(0, no_intervals):
            offset = str(i * limit)
            if i == 0:
                url = url
            else:
                url = url + '&offset=' + offset
            if params is (not None):
                response = requests.get(url=url, headers=headers, params=params)
            else:
                response = requests.get(url=url, headers=headers)
            ok, retstr = requtils.response_ok(response)
            if (not ok):
                level, retstr = requtils.logging_switch(response)
                self.log_switch(level, retstr)

            else:
                for resp_dict in json.loads(response.text):
                    all_data.append(resp_dict)

        return all_data

    def check_duplicate_subscription(self, subscription_body, limit:int=20):
        """
        Function compares the subject of the subscription body, on whether a subscription
        already exists for a device / entity.
        :param subscription_body: the body of the new subscripton
        :param limit: pagination parameter, to set the number of subscriptions bodies the get request should grab
        :return: exists, boolean -> True, if such a subscription allready exists
        """
        exists = False
        subscription_subject = json.loads(subscription_body)["subject"]
        # Exact keys depend on subscription body
        try:
            subscription_url = json.loads(subscription_body)["notification"]["httpCustom"]["url"]
        except KeyError:
            subscription_url = json.loads(subscription_body)["notification"]["http"]["url"]

        # If the number of subscriptions is larger then the limit, paginations methods have to be used
        url = self.url + '/subscriptions?limit=' + str(limit) + '&options=count'
        response = requests.get(url, headers=self.get_header())

        sub_count = float(response.headers["Fiware-Total-Count"])
        response = json.loads(response.text)
        if sub_count >= limit:
            response = self.get_pagination(url=url, headers=self.get_header(),
                                           limit=limit, count=sub_count)
            print(type(response))

            response = json.loads(response)

            print(type(response))


        for existing_subscription in response:
            # check whether the exact same subscriptions already exists
            if existing_subscription["subject"] == subscription_subject:
                exists = True
                break
            try: existing_url = existing_subscription["notification"]["http"]["url"]
            except KeyError:
                existing_url = existing_subscription["notification"]["httpCustom"]["url"]
            # check whether both subscriptions notify to the same path
            if existing_url != subscription_url:
                continue
            else:
                # iterate over all entities included in the subscription object
                for entity in subscription_subject["entities"]:
                    if 'type' in entity.keys():
                        subscription_type = entity['type']
                    else:
                        subscription_type = entity['typePattern']
                    if 'id' in entity.keys():
                        subscription_id = entity['id']
                    else:
                        subscription_id = entity["idPattern"]
                    # iterate over all entities included in the exisiting subscriptions
                    for existing_entity in existing_subscription["subject"]["entities"]:
                        if "type" in entity.keys():
                            type_existing = entity["type"]
                        else:
                            type_existing = entity["typePattern"]
                        if "id" in entity.keys():
                            id_existing = entity["id"]
                        else:
                            id_existing = entity["idPattern"]
                        # as the ID field is non optional, it has to match
                        # check whether the type match
                        # if the type field is empty, they match all types
                        if (type_existing is subscription_type) or\
                                ('*' in subscription_type) or \
                                ('*' in type_existing)\
                                or (type_existing is "") or (
                                subscription_type is ""):
                            # check if on of the subscriptions is a pattern, or if they both refer to the same id
                            # Get the attrs first, to avoid code duplication
                            # last thing to compare is the attributes
                            # Assumption -> position is the same as the entities list
                            # i == j
                            i = subscription_subject["entities"].index(entity)
                            j = existing_subscription["subject"]["entities"].index(existing_entity)
                            try: subscription_attrs = subscription_subject["condition"]["attrs"][i]
                            except (KeyError, IndexError):
                                subscription_attrs = []
                            try: existing_attrs = existing_subscription["subject"]["condition"]["attrs"][j]
                            except (KeyError, IndexError):
                                existing_attrs = []

                            if (".*" in subscription_id) or ('.*' in id_existing) or (subscription_id == id_existing):
                                # Attributes have to match, or the have to be an empty array
                                if (subscription_attrs == existing_attrs) or (subscription_attrs == []) or (existing_attrs == []):
                                        exists = True
                            # if they do not match completely or subscribe to all ids they have to match up to a certain position
                            elif ("*" in subscription_id) or ('*' in id_existing):
                                    regex_existing = id_existing.find('*')
                                    regex_subscription = subscription_id.find('*')
                                    # slice the strings to compare
                                    if (id_existing[:regex_existing] in subscription_id) or \
                                        (subscription_id[:regex_subscription] in id_existing) or \
                                        (id_existing[regex_existing:] in subscription_id) or \
                                        (subscription_id[regex_subscription:] in id_existing):
                                            if (subscription_attrs == existing_attrs) or (subscription_attrs == []) or (existing_attrs == []):
                                                exists = True
                                            else:
                                                continue
                                    else:
                                        continue
                            else:
                                continue
                        else:
                            continue
                    else:
                        continue
        return exists


    def delete_all_subscriptions(self):
        subscriptions = self.get_subscription_list()
        for sub_id in subscriptions:
            self.delete_subscription(sub_id)

    def post_cmd_v1(self, entity_id: str, entity_type: str,
                    cmd_name: str, cmd_value: str):
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
