import filip.subscription as sub
import filip.orion as orion
import filip.request_utils as requtils
from filip import test
import requests
import json

import logging

log = logging.getLogger('timeseries')


class QuantumLeap():
    """
    Implements functions to use the FIWAREs QuantumLeap, which subscribes to an
    Orion Context Broker and stores the subscription data in a timeseries
    database (CrateDB). Further Information:
    https://smartsdk.github.io/ngsi-timeseries-api/#quantumleap
    """
    def __init__(self, config: object):
        """Initialize with configuration values"""
        self.host = config.data.get("quantum_leap", {}).get("host")
        self.port = config.data.get("quantum_leap", {}).get("port")

        self.crate_host = config.data.get("cratedb", {}).get("host")
        self.crate_port = config.data.get("cratedb", {}).get("port")

        if (self.port == None) or (self.port == ""):
            # if port is None, the full url is given by the  {quantum_leap : { host }} key
            self.url = self.host
        else:
            self.url = self.host + ":" + self.port + '/v2'

        if (self.crate_port == None) or (self.crate_port == ""):
            self.crate_url = self.crate_host
        else:
            self.crate_url = self.crate_host + ":" + self.crate_port

        self.fiware_service = orion.FiwareService(name=config.data['fiware']['service'],
                                                  path=config.data['fiware']['service_path'])

    def create_subscription_object(self, entity: orion.Entity, url: str,
                                   **kwargs) -> object:
        """
        Creates and returns Subscription object so that it can be edited before
        the subscription is actually created.
        :param entity: entity to subscribe on
        :param url: URL destination for subscription notifications
        :return: Subscription object, not yet sent to Orion Context Broker
        """
        id_pattern = kwargs.get("id_pattern", None)
        if id_pattern != None:
            subject_entity = sub.Subject_Entity(id_pattern, None, True)
        else:
            entity_type = json.loads(entity.get_json())["type"]
            subject_entity = sub.Subject_Entity(entity.id, entity_type)
        subject = sub.Subject([subject_entity])
        http_params = sub.HTTP_Params(url)
        notification = sub.Notification(http_params)
        throttling = kwargs.get("throttling")
        expires = kwargs.get("expires")
        description = kwargs.get("description")
        subscription = sub.Subscription(subject, notification, description,
                                        expires, throttling)
        return subscription

    def get_header(self, additional_headers: dict = None):
        """combine fiware_service header (if set) and additional headers"""
        if self.fiware_service == None:
            return additional_headers
        elif additional_headers == None:
            return self.fiware_service.get_header()
        else:
            headers = {**self.fiware_service.get_header(), **additional_headers}
            return headers

    def get_version(self):
        url = self.url + '/version'
        headers=requtils.HEADER_CONTENT_PLAIN
        response = requests.get(url, headers=headers)
        ok, retstr = requtils.response_ok(response)
        if (not ok):
            print(retstr)
            return ""
        else:
            return response.text

    def get_health(self):
        url = self.url + '/health'
        headers = requtils.HEADER_CONTENT_PLAIN
        response = requests.get(url, headers=headers)
        ok, retstr = requtils.response_ok(response)
        if not ok:
            print(retstr)
            return ""
        else:
            return response.text

    def delete_entity(self, entity_name: str):
        url = self.url + '/entities/' + entity_name
        headers = self.get_header(requtils.HEADER_CONTENT_PLAIN)
        response = requests.delete(url, headers=headers)
        ok, retstr = requtils.response_ok(response)
        if not ok:
            print(retstr)

    def delete_entities_of_type(self, entity_type):
        url = self.url + '/types/' + entity_type
        headers = self.get_header(requtils.HEADER_CONTENT_PLAIN)
        response = requests.delete(url, headers=headers)
        ok, retstr = requtils.response_ok(response)
        if not ok:
            print(retstr)

    def get_entity_data(self, entity_id: str, attr_name: str = None, 
                        valuesonly: bool = False, **kwargs):
        url = self.url + '/entities/' + entity_id
        params = kwargs.get("params")
        headers = self.get_header(requtils.HEADER_CONTENT_PLAIN)
        if attr_name != None:
            url += '/attrs/' + attr_name
        if valuesonly:
            url += '/value'
        response = requests.get(url, headers=headers, params=params)
        ok, retstr = requtils.response_ok(response)
        if not ok:
            print(retstr)
            return ""
        else:
            return response.text

    def get_entity_type_data(self, entity_type: str, attr_name: str = None,
                             valuesonly: bool = False):
        url = self.url + '/types/' + entity_type
        headers = self.get_header(requtils.HEADER_CONTENT_PLAIN)
        if attr_name != None:
            url += '/attrs/' + attr_name
        if valuesonly:
            url += '/value'
        response = requests.get(url, headers=headers)
        ok, retstr = requtils.response_ok(response)
        if not ok:
            print(retstr)
            return ""
        else:
            return response.text

    def get_attributes(self, attr_name: str = None, valuesonly: bool = False):
        url = self.url + '/attrs'
        headers = self.get_header(requtils.HEADER_CONTENT_PLAIN)
        if attr_name != None:
            url += '/' + attr_name
        if valuesonly:
            url += '/value'
        response = requests.get(url, headers=headers)
        ok, retstr = requtils.response_ok(response)
        if not ok:
            print(retstr)
            return ""
        else:
            return response.text

    def get_timeseries(self, entity_name: str = None, attr_name: str = None,
                       valuesonly: bool = True, limit: str = "10000"):
        """

        :param entity_name: Name of the entity where the timeseries data should be retrieved
        :param attr_name: Name of the attribute where the timeseries data should be retrieved, if none given, all attribute are retrieved
        :param valuesonly: Return has values only
        :param limit: maximum number of values that should be retrieved
        :return: A dictionary, where the key is the time and the value the respective value e.g. '2020-02-11T13:45:23.000': 6
        """
        url = self.url +"/entities/"+ entity_name
        headers = self.get_header(requtils.HEADER_CONTENT_PLAIN)
        res = dict()
        if attr_name != None:
            url += '/attrs/' + attr_name
        if valuesonly:
            url += '/value'
        url += '?limit=' + limit
        response = requests.get(url, headers=headers)
        ok, retstr = requtils.response_ok(response)
        if not ok:
            print(retstr)
            return None
        else:
            response_json = json.loads(response.text)
            for attr in response_json["attributes"]:
                attr_name = attr["attrName"]
                res[attr_name] = dict(zip(response_json["index"], attr["values"]))
            return res





