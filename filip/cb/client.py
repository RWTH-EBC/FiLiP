import json
import requests
from typing import Dict
from urllib.parse import urljoin
from core.base_client import _BaseClient
from core.settings import settings
from core.models import FiwareHeader
from cb.models import BaseContextEntity
import math
import logging

logger = logging.getLogger('ocb')


class ContextBrokerClient(_BaseClient):
    """
    Implementation of NGSI Context Broker functionalities, such as creating
    entities and subscriptions; retrieving, updating and deleting data.
    Further documentation:
    https://fiware-orion.readthedocs.io/en/master/

    Api specifications for v2 are located here:
    http://telefonicaid.github.io/fiware-orion/api/v2/stable/
    """
    def __init__(self, session: requests.Session = None,
                 fiware_header: FiwareHeader = None):
        super().__init__(session=session,
                         fiware_header=fiware_header)

    # MANAGEMENT API
    def get_version(self) -> Dict:
        """
        Gets version of IoT Agent
        Returns:
            Dictionary with response
        """
        url = urljoin(settings.CB_URL, '/version')
        try:
            res = self.session.get(url=url, headers=self.headers)
            if res.ok:
                return res.json()
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)

    def get_resources(self) -> Dict:
        """
        Re
        Returns:

        """
        url = urljoin(settings.CB_URL, '/v2')
        try:
            res = self.session.get(url=url, headers=self.headers)
            if res.ok:
                return res.json()
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)

    # STATISTICS API
    def get_statistics(self):
        """
        Gets statistics of context broker
        Returns:
            Dictionary with response
        """
        url = urljoin(settings.CB_URL, 'statistics')
        try:
            res = self.session.get(url=url, headers=self.headers)
            if res.ok:
                return res.json()
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)



    # MANAGEMENT API



    # CONTEXT MANAGEMENT API ENDPOINTS




#    def set_service(self, fiware_service):
#        """Overwrites the fiware_service and service_group path of
        #        config.json"""
#        self.fiware_service.update(fiware_service.name, fiware_service.path)
#
#    def get_service(self):
#        return self.fiware_service
#
#    def get_header(self, additional_headers: dict = None):
#        """combine fiware_service header (if set) and additional headers"""
#        if self.fiware_service == None:
#            return additional_headers
#        elif additional_headers == None:
#            return self.fiware_service.get_header()
#        else:
#            headers = {**self.fiware_service.get_header(),
        #            **additional_headers}
#            return headers
#
#    def log_switch(self, level, response):
#        """
#        Function returns the required log_level with the repsonse
#        :param level: The logging level that should be returned
#        :param response: The message for the logger
#        :return:
#        """
#        switch_dict = {"INFO": logging.info,
#                       "ERROR":  logging.error,
#                       "WARNING": logging.warning
#                       }.get(level, logging.info)(msg=response)
#
#
#    def test_connection(self):
#        """
#        Function utilises the test.test_connection() function to check the
        #        availability of a given url and service_group.
#        :return: Boolean, True if the service_group is reachable, False if not.
#        """
#        boolean = test.test_connection(client=self.session,
#                                       url=self.url+'/version',
#                                       service_name=__name__)
#        return boolean
#
#    def post_entity(self, entity: Entity, force_update: bool = True):
#        """
#        Function registers an Object with the Orion Context Broker,
        #        if it allready exists it can be automatically updated
#        if the overwrite bool is True
#        First a post request with the entity is tried, if the response code
        #        is 422 the entity is
#        uncrossable, as it already exists there are two options, either
        #        overwrite it, if the attribute have changed (e.g. at least one new/
#        new values) (update = True) or leave it the way it is (update=False)
#        :param entity: An entity object
#        :param update: If the response.status_code is 422, whether the old
        #        entity should be updated or not
#        :return:
#        """
#        url = self.url + '/v2/entities'
#        headers = self.get_header(requtils.HEADER_CONTENT_JSON)
#        data = entity.get_json()
#        response = self.session.post(url, headers=headers, data=data)
#        ok, retstr = requtils.response_ok(response)
#        if not ok:
#            if (response.status_code == 422) & (force_update is True):
#                    url += f"{entity.id}/attrs"
#                    response = self.session.post(url, headers=headers,
        #                    data=data)
#                    ok, retstr = requtils.response_ok(response)
#            if not ok:
#                level, retstr = requtils.logging_switch(response)
#                self.log_switch(level, response)
#
#    def post_json(self, json=None, entity=None, params=None):
#        """
#        Function registers a JSON with the Orion Context Broker.
#        :param json: A JSON (dictionary)
#        :param entity: An Orion entity, from which the json_data can be
        #        obatained.
#        :param params:
#        :return:
#        """
#        headers = self.get_header(requtils.HEADER_CONTENT_JSON)
#        if json is not None:
#            json_data = json
#        elif (json is None) and (entity is not None):
#            json_data = entity.get_json()
#        else:
#            logger.error(f"Please provide a valid data format.")
#            json_data = ""
#        if params is None:
#            url = self.url + '/v2/entities'
#            response = self.session.post(url, headers=headers, data=json_data)
#        else:
#            url = self.url + "/v2/entities" + "?options=" + params
#            response = self.session.post(url, headers=headers, data=json_data)
#        ok, retstr = requtils.response_ok(response)
#        if not ok:
#            level, retstr = requtils.logging_switch(response)
#            self.log_switch(level, retstr)
#
#    def post_json_key_value(self, json_data=None, params="keyValues"):
#        """
#        :param json_data:
#        :param params:
#        :return:
#        """
#        headers = self.get_header(requtils.HEADER_CONTENT_JSON)
#        url = self.url + "/v2/entities" + "?options=" + params
#        response = self.session.post(url, headers=headers, data=json_data)
#        ok, retstr = requtils.response_ok(response)
#        if not ok:
#            level, retstr = requtils.logging_switch(response)
#            self.log_switch(level, retstr)
#
#    def post_relationship(self, json_data=None):
#        """
#        Function can be used to post a one to many or one to one relationship.
#        :param json_data: Relationship Data obtained from the Relationship
        #        class. e.g. :
#                {"id": "urn:ngsi-ld:Shelf:unit001", "type": "Shelf",
#                "refStore": {"type": "Relationship", "value":
        #                "urn:ngsi-ld:Store:001"}}
#                Can be a one to one or a one to many relationship
#        """
#        url = self.url + '/v2/op/update'
#        headers = self.get_header(requtils.HEADER_CONTENT_JSON)
#        # Action type append required,
#        # Will overwrite existing entities if they exist whereas
#        # the entities attribute holds an array of entities we wish to update.
#        payload = {"actionType": "APPEND",
#                   "entities": [json.loads(json_data)]}
#        data = json.dumps(payload)
#        response = self.session.post(url=url, data=data, headers=headers)
#        ok, retstr = requtils.response_ok(response)
#        if not ok:
#            level, retstr = requtils.logging_switch(response)
#            self.log_switch(level, retstr)
#
#    def get_subjects(self, object_entity_name: str, object_entity_type: str, subject_type=None):
#        """
#        Function gets the JSON for child / subject entities for a parent /
        #        object entity.
#        :param object_entity_name: The parent / object entity name
#        :param object_entity_type: The type of the parent / object entity
#        :param subject_type: optional parameter, if added only those child /
        #        subject entities are returned that match the type
#        :return: JSON containing the child / subject information
#        """
#        url = self.url + '/v2/entities/?q=ref' + object_entity_type + '==' + object_entity_name + '&options=count'
#        if subject_type is not None:
#            url = url + '&attrs=type&type=' + subject_type
#        headers = self.get_header()
#        response = self.session.get(url=url, headers=headers, )
#        ok, retstr = requtils.response_ok(response)
#        if not ok:
#            level, retstr = requtils.logging_switch(response)
#            self.log_switch(level, retstr)
#        else:
#            return response.text
#
#    def get_objects(self, subject_entity_name: str, subject_entity_type:
        #    str, object_type=None):
#        """
#        Function returns a List of all objects associated to a subject. If
        #        object type is not None,
#        only those are returned, that match the object type.
#        :param subject_entity_name: The child / subject entity name
#        :param subject_entity_type: The type of the child / subject entity
#        :param object_type:
#        :return: List containing all associated objects
#        """
#        url = self.url + '/v2/entities/' + subject_entity_name + '/?type=' + subject_entity_type + '&options=keyValues'
#        if object_type is not None:
#            url = url + '&attrs=ref' + object_type
#        headers = self.get_header()
#        response = self.session.get(url=url, headers=headers)
#        ok, retstr = requtils.response_ok(response)
#        if not ok:
#            level, retstr = requtils.logging_switch(response)
#            self.log_switch(level, retstr)
#        else:
#            return response.text
#
#    def get_associated(self, name: str, entity_type: str,
        #    associated_type=None):
#        """
#        Function returns all associated data for a given entity name and type
#        :param name: name of the entity
#        :param entity_type: type of the entity
#        :param associated_type: if only associated data of one type should
        #        be returned, this parameter has to be the type
#        :return: A dictionary, containing the data of the entity,
        #        a key "subjects" and "objects" that contain each a list
#                with the reflective data
#        """
#        data_dict = {}
#        associated_objects = self.get_objects(subject_entity_name=name,
        #        subject_entity_type=entity_type,
#                                              object_type=associated_type)
#        associated_subjects = self.get_subjects(object_entity_name=name,
        #        object_entity_type=entity_type,
#                                                subject_type=associated_type)
#        if associated_subjects is not None:
#            data_dict["subjects"] = json.loads(associated_subjects)
#        if associated_objects is not None:
#            object_json = json.loads(associated_objects)
#            data_dict["objects"] = []
#            if isinstance(object_json, list):
#                for associated_object in object_json:
#                    entity_name = associated_object["id"]
#                    object_data = json.loads(self.get_entity(
        #                    entity_name=entity_name))
#                    data_dict["objects"].append(object_data)
#            else:
#                entity_name = object_json["id"]
#                object_data = json.loads(self.get_entity(
        #                entity_name=entity_name))
#                data_dict["objects"].append(object_data)
#
#        entity_dict = json.loads(self.get_entity(entity_name=name))
#
#        whole_dict = {**entity_dict, **data_dict}
#
#        return whole_dict
#
#    def get_entity(self, entity_name,  entity_params=None):
#        url = self.url + '/v2/entities/' + entity_name
#        headers = self.get_header()
#        if entity_params is None:
#            response = self.session.get(url, headers=headers)
#        else:
#            response = self.session.get(url, headers=headers,
#                                    params=entity_params)
#        ok, retstr = requtils.response_ok(response)
#        if not ok:
#            level, retstr = requtils.logging_switch(response)
#            self.log_switch(level, retstr)
#        else:
#            return response.text
#
#    def get_all_entities(self, parameter=None, parameter_value=None,
        #    limit=100):
#        url = self.url + '/v2/entities?options=count'
#        headers = self.get_header()
#        if parameter is None and parameter_value is None:
#            response = self.session.get(url, headers=headers)
#            sub_count = float(response.headers["Fiware-Total-Count"])
#            if sub_count >= limit:
#                response = self.get_pagination(url=url, headers=headers,
#                                               limit=limit, count=sub_count)
#                return response
#        elif parameter is not None and parameter_value is not None:
#            parameters = {'{}'.format(parameter): '{}'.format(parameter_value)}
#            response = self.session.get(url, headers=headers,
        #            params=parameters)
#            sub_count = float(response.headers["Fiware-Total-Count"])
#            if sub_count >= limit:
#                response = self.get_pagination(url=url, headers=headers,
#                                               limit=limit, count=sub_count,
        #                                               params=parameters)
#                return response
#        else:
#            logger.error("Getting all entities: both function parameters
        #            have to be 'not null'")
#            return None
#        ok, retstr = requtils.response_ok(response)
#        if not ok:
#            level, retstr = requtils.logging_switch(response)
#            self.log_switch(level, retstr)
#        else:
#            return response.text
#
#    def get_entities_list(self, limit=100) -> list:
#        url = self.url + '/v2/entities?options=count'
#        header = self.get_header(requtils.HEADER_ACCEPT_JSON)
#        response = self.session.get(url, headers=header)
#        sub_count = float(response.headers["Fiware-Total-Count"])
#        if sub_count >= limit:
#            response = self.get_pagination(url=url, headers=header,
#                                           limit=limit, count=sub_count)
#            return response
#        ok, retstr = requtils.response_ok(response)
#        if not ok:
#            level, retstr = requtils.logging_switch(response)
#            self.log_switch(level, retstr)
#            return None
#        else:
#            json_object = json.loads(response.text)
#            entities = []
#            for key in json_object:
#                entities.append(key["id"])
#            return entities
#
#    def get_entity_keyValues(self, entity_name):
#        parameter = {'{}'.format('options'): '{}'.format('keyValues')}
#        return self.get_entity(entity_name, parameter)
#
#    def get_entity_attribute_json(self, entity_name, attr_name):
#        url = self.url + '/v2/entities/' + entity_name + '/attrs/' + attr_name
#        response = self.session.get(url, headers=self.get_header())
#        ok, retstr = requtils.response_ok(response)
#        if not ok:
#            level, retstr = requtils.logging_switch(response)
#            self.log_switch(level, retstr)
#        else:
#            return response.text
#
#    def get_entity_attribute_value(self, entity_name, attr_name):
#        url = self.url + '/v2/entities/' + entity_name + '/attrs/' \
#                       + attr_name + '/value'
#        response = self.session.get(url, headers=self.get_header())
#        ok, retstr = requtils.response_ok(response)
#        if not ok:
#            level, retstr = requtils.logging_switch(response)
#            self.log_switch(level, retstr)
#        else:
#            return response.text
#
#    def get_entity_attribute_list(self, entity_name, attr_name_list):
#        """
#        Function returns all types and values for a list of attributes of an entity,
#        given in attr_name_list
#        :param entity_name: Entity_name - Name of the entity to obtain the
        #        values from
#        :param attr_name_list: List of attributes - e.g. ["Temperature"]
#        :return: List, containin all attribute dictionaries e.g.: [{
        #        "value":33,"type":"Float"}]
#        """
#        attributes = ','.join(attr_name_list)
#        parameters = {'{}'.format('options'): '{}'.format('values'),
#                      '{}'.format('attrs'): attributes}
#        return self.get_entity(entity_name, parameters)
#
#    def update_entity(self, entity):
#        url = self.url + '/v2/entities/' + entity.id + '/attrs'
#        payload = entity.get_attributes_key_values()
#        headers = self.get_header(requtils.HEADER_CONTENT_JSON)
#        data = json.dumps(payload)
#        response = self.session.patch(url, headers=headers, data=data)
#        ok, retstr = requtils.response_ok(response)
#        if not ok:
#            level, retstr = requtils.logging_switch(response)
#            self.log_switch(level, retstr)
#
#    def update_attribute(self, entity_name, attr_name, attr_value):
#        url = self.url + '/v2/entities/' + entity_name + '/attrs/' \
#                       + attr_name + '/value'
#        headers = self.get_header(requtils.HEADER_CONTENT_PLAIN)
#        data = json.dumps(attr_value)
#        response = self.session.put(url, headers=headers, data=data)
#        ok, retstr = requtils.response_ok(response)
#        if not ok:
#            level, retstr = requtils.logging_switch(response)
#            self.log_switch(level, retstr)
#
#    def add_attribute(self, entity: Entity = None, entity_name: str = None,
        #    attr_dict: dict = None):
#        # POST /v2/entities/{id}/attrs?options=append
#        """
#        This function adds attributes to the Entity in the Context Broker.
        #        This can be done in two ways,
#        either by first adding the attribute to the Entity object or by
        #        directly sending it from a dict/JSON
#        The Function first compares it with existing attributes, and only
        #        adds (so updates) the ones not previoulsy existing
#        :param entity: The updated Entity Instance
#        :param entity_name: The Entity name which should be updated
#        :param attribute_dict: A JSON/Dict containing the attributes
#        :return: -
#        """
#        if isinstance(entity, Entity):
#            attributes = entity.get_attributes()
#            entity_name = entity.id
#        else:
#            attributes = attr_dict
#            entity_name = entity_name
#        existing_attributes = self.get_attributes(entity_name)
#        new_attributes = {k: v for (k, v) in attributes.items() if k not in
        #        existing_attributes}
#        url = self.url + '/v2/entities/' + entity_name +
        #        '/attrs?options=append'
#        headers = self.get_header(requtils.HEADER_CONTENT_JSON)
#        data = json.dumps(new_attributes)
#        response = self.session.post(url, data=data, headers=headers)
#        ok, retstr = requtils.response_ok(response)
#        if not ok:
#            level, retstr = requtils.logging_switch(response)
#            self.log_switch(level, retstr)
#
#    def get_attributes(self, entity_name: str):
#        """
#        For a given entity this function returns all attribute names
#        :param entity_name: the name of the entity
#        :return: attributes - list of attributes
#        """
#        entity_json = json.loads(self.get_entity(entity_name))
#        attributes = [k for k in entity_json.keys() if k not in ["id", "type"]]
#        return attributes
#
#    def remove_attributes(self, entity_name):
#        url = self.url + '/v2/entities/' + entity_name + '/attrs'
#        response = self.session.put(url)
#        ok, retstr = requtils.response_ok(response)
#        if not ok:
#            level, retstr = requtils.logging_switch(response)
#            self.log_switch(level, response)
#
#    def create_subscription(self, subscription_body, check_duplicate: bool = True):
#        url = self.url + '/v2/subscriptions'
#        headers = self.get_header(requtils.HEADER_CONTENT_JSON)
#        if check_duplicate is True:
#            exists = self.check_duplicate_subscription(subscription_body)
#            if exists is True:
#                logger.info(f"A similar subscription already exists.")
#        response = self.session.post(url, headers=headers,
        #        data=subscription_body)
#        if response.headers is None:
#            return
#        ok, retstr = requtils.response_ok(response)
#        if not ok:
#            level, retstr = requtils.logging_switch(response)
#            self.log_switch(level, retstr)
#            return None
#        else:
#            location = response.headers.get('Location')
#            addr_parts = location.split('/')
#            subscription_id = addr_parts.pop()
#            return subscription_id
#
#    def get_subscription_list(self, limit=100):
#        url = self.url + '/v2/subscriptions?options=count'
#        response = self.session.get(url, headers=self.get_header())
#        sub_count = float(response.headers["Fiware-Total-Count"])
#        if sub_count >= limit:
#            response = self.get_pagination(url=url, headers=self.get_header(),
#                                           limit=limit, count=sub_count)
#            return response
#        ok, retstr = requtils.response_ok(response)
#        if not ok:
#            level, retstr = requtils.logging_switch(response)
#            self.log_switch(level, retstr)
#            return None
#        json_object = json.loads(response.text)
#        subscriptions = []
#        for key in json_object:
#            subscriptions.append(key["id"])
#        return subscriptions
#
#    def get_subscription(self, subscription_id: str):
#        url = self.url + '/v2/subscriptions/' + subscription_id
#        response = self.session.get(url, headers=self.get_header())
#        ok, retstr = requtils.response_ok(response)
#        if not ok:
#            level, retstr = requtils.logging_switch(response)
#            self.log_switch(level, retstr)
#
#    def delete_subscription(self, subscription_id: str):
#        url = self.url + '/v2/subscriptions/' + subscription_id
#        response = self.session.delete(url, headers=self.get_header())
#        ok, retstr = requtils.response_ok(response)
#        if not ok:
#            level, retstr = requtils.logging_switch(response)
#            self.log_switch(level, retstr)
#
#    def get_pagination(self, url: str, headers: dict,
#                       count: float,  limit: int = 20, params=None):
#        """
#        NGSIv2 implements a pagination mechanism in order to help clients to retrieve large sets of resources.
#        This mechanism works for all listing operations in the API (e.g. GET /v2/entities, GET /v2/subscriptions, POST /v2/op/query, etc.).
#        This function helps getting datasets that are larger than the limit
        #        for the different GET operations.
#        :param url: Information about the url, obtained from the orginal
        #        function e.g. : http://localhost:1026/v2/subscriptions?limit=20&options=count
#        :param headers: The headers from the original function,
        #        e.g: {'fiware-service_group': 'crio', 'fiware-servicepath': '/measurements'}
#        :param count: Number of total elements, obtained by adding
        #        "&options=count" to the url,
#                        included in the response headers
#        :param limit: Limit, obtained from the oringal function, default is 20
#        :return: A list, containing all objects in a dictionary
#        """
#        all_data = []
#        # due to a math, one of the both numbers has to be a float,
#        # otherwise the value is rounded down not up
#        no_intervals = int(math.ceil(count / limit))
#        for i in range(0, no_intervals):
#            offset = str(i * limit)
#            if i == 0:
#                url = url
#            else:
#                url = url + '&offset=' + offset
#            if params == (not None):
#                response = self.session.get(url=url, headers=headers,
        #                params=params)
#            else:
#                response = self.session.get(url=url, headers=headers)
#            ok, retstr = requtils.response_ok(response)
#            if not ok:
#                level, retstr = requtils.logging_switch(response)
#                self.log_switch(level, retstr)
#            else:
#                for resp_dict in json.loads(response.text):
#                    all_data.append(resp_dict)
#
#        return all_data
#
#    def check_duplicate_subscription(self, subscription_body, limit: int = 20):
#        """
#        Function compares the subject of the subscription body, on whether a subscription
#        already exists for a device / entity.
#        :param subscription_body: the body of the new subscripton
#        :param limit: pagination parameter, to set the number of
        #        subscriptions bodies the get request should grab
#        :return: exists, boolean -> True, if such a subscription allready
        #        exists
#        """
#        exists = False
#        subscription_subject = json.loads(subscription_body)["subject"]
#        # Exact keys depend on subscription body
#        try:
#            subscription_url = json.loads(subscription_body)[
        #            "notification"]["httpCustom"]["url"]
#        except KeyError:
#            subscription_url = json.loads(subscription_body)[
        #            "notification"]["http"]["url"]
#
#        # If the number of subscriptions is larger then the limit,
        #        paginations methods have to be used
#        url = self.url + '/v2/subscriptions?limit=' + str(limit) +
        #        '&options=count'
#        response = self.session.get(url, headers=self.get_header())
#
#        sub_count = float(response.headers["Fiware-Total-Count"])
#        response = json.loads(response.text)
#        if sub_count >= limit:
#            response = self.get_pagination(url=url, headers=self.get_header(),
#                                           limit=limit, count=sub_count)
#            response = json.loads(response)
#
#        for existing_subscription in response:
#            # check whether the exact same subscriptions already exists
#            if existing_subscription["subject"] == subscription_subject:
#                exists = True
#                break
#            try:
#                existing_url = existing_subscription["notification"][
        #                "http"]["url"]
#            except KeyError:
#                existing_url = existing_subscription["notification"][
        #                "httpCustom"]["url"]
#            # check whether both subscriptions notify to the same path
#            if existing_url != subscription_url:
#                continue
#            else:
#                # iterate over all entities included in the subscription object
#                for entity in subscription_subject["entities"]:
#                    if 'type' in entity.keys():
#                        subscription_type = entity['type']
#                    else:
#                        subscription_type = entity['typePattern']
#                    if 'id' in entity.keys():
#                        subscription_id = entity['id']
#                    else:
#                        subscription_id = entity["idPattern"]
#                    # iterate over all entities included in the exisiting
        #                    subscriptions
#                    for existing_entity in existing_subscription["subject"][
        #                    "entities"]:
#                        if "type" in entity.keys():
#                            type_existing = entity["type"]
#                        else:
#                            type_existing = entity["typePattern"]
#                        if "id" in entity.keys():
#                            id_existing = entity["id"]
#                        else:
#                            id_existing = entity["idPattern"]
#                        # as the ID field is non optional, it has to match
#                        # check whether the type match
#                        # if the type field is empty, they match all types
#                        if (type_existing == subscription_type) or\
#                                ('*' in subscription_type) or \
#                                ('*' in type_existing)\
#                                or (type_existing == "") or (
#                                subscription_type == ""):
#                            # check if on of the subscriptions is a pattern,
        #                            or if they both refer to the same id
#                            # Get the attrs first, to avoid code duplication
#                            # last thing to compare is the attributes
#                            # Assumption -> position is the same as the
        #                            entities list
#                            # i == j
#                            i = subscription_subject["entities"].index(entity)
#                            j = existing_subscription["subject"][
        #                            "entities"].index(existing_entity)
#                            try:
#                                subscription_attrs = subscription_subject[
        #                                "condition"]["attrs"][i]
#                            except (KeyError, IndexError):
#                                subscription_attrs = []
#                            try:
#                                existing_attrs = existing_subscription[
        #                                "subject"]["condition"]["attrs"][j]
#                            except (KeyError, IndexError):
#                                existing_attrs = []
#
#                            if (".*" in subscription_id) or ('.*' in
        #                            id_existing) or (subscription_id == id_existing):
#                                # Attributes have to match, or the have to
        #                                be an empty array
#                                if (subscription_attrs == existing_attrs) or
        #                                (subscription_attrs == []) or (existing_attrs == []):
#                                        exists = True
#                            # if they do not match completely or subscribe
        #                            to all ids they have to match up to a certain position
#                            elif ("*" in subscription_id) or ('*' in
        #                            id_existing):
#                                    regex_existing = id_existing.find('*')
#                                    regex_subscription =
        #                                    subscription_id.find('*')
#                                    # slice the strings to compare
#                                    if (id_existing[:regex_existing] in
        #                                    subscription_id) or (subscription_id[:regex_subscription] in id_existing) or \
#                                            (id_existing[regex_existing:] in
        #                                            subscription_id) or (subscription_id[regex_subscription:] in id_existing):
#                                            if (subscription_attrs ==
        #                                            existing_attrs) or (subscription_attrs == []) or (existing_attrs == []):
#                                                exists = True
#                                            else:
#                                                continue
#                                    else:
#                                        continue
#                            else:
#                                continue
#                        else:
#                            continue
#                    else:
#                        continue
#        return exists
#
#    def delete_all_subscriptions(self):
#        subscriptions = self.get_subscription_list()
#        for sub_id in subscriptions:
#            self.delete_subscription(sub_id)
#
#    def post_cmd_v1(self, entity_id: str, entity_type: str,
#                    cmd_name: str, cmd_value: str):
#        url = self.url + '/v1/updateContext'
#        payload = {"updateAction": "UPDATE",
#                   "contextElements": [
#                        {"id": entity_id,
#                         "type": entity_type,
#                         "isPattern": "false",
#                         "attributes": [
#                            {"name": cmd_name,
#                             "type": "command",
#                             "value": cmd_value
#                             }]
#                         }]
#                   }
#        headers = self.get_header(requtils.HEADER_CONTENT_JSON)
#        data = json.dumps(payload)
#        response = self.session.post(url, headers=headers, data=data)
#        ok, retstr = requtils.response_ok(response)
#        if not ok:
#            level, retstr = requtils.logging_switch(response)
#            self.log_switch(level, retstr)
#
#    def delete(self, entity_id: str):
#        url = self.url + '/v2/entities/' + entity_id
#        response = self.session.delete(url, headers=self.get_header())
#        ok, retstr = requtils.response_ok(response)
#        if not ok:
#            level, retstr = requtils.logging_switch(response)
#            self.log_switch(level, retstr)
#
#    def delete_all_entities(self):
#        entities = self.get_entities_list()
#        for entity_id in entities:
#            self.delete(entity_id)
#