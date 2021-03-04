import logging
import requests
from typing import List, Dict, Set, Union
from urllib.parse import urljoin
from cb import Subscription as sub
from filip.utils import request_utils as requtils
from core import test

from core import settings
from core.base_client import BaseClient
from core.models import FiwareHeader, Notification


logger = logging.getLogger(__name__)


class QuantumLeapClient(BaseClient):
    """
    Implements functions to use the FIWAREs QuantumLeap, which subscribes to an
    Orion Context Broker and stores the subscription data in a timeseries
    database (CrateDB). Further Information:
    https://smartsdk.github.io/ngsi-timeseries-api/#quantumleap
    https://app.swaggerhub.com/apis/heikkilv/quantumleap-api/
    """
    def __init__(self, session: requests.Session = None,
                 fiware_header: FiwareHeader = None):
        super().__init__(session=session,
                         fiware_header=fiware_header)

    # META API ENDPOINTS
    def get_version(self) -> Dict:
        """
        Returns the version of QuantumLeap.
        Returns:
            Dictionary with response
        """
        url = urljoin(settings.QL_URL, '/version')
        try:
            res = self.session.get(url=url, headers=self.headers)
            if res.ok:
                return res.json()
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)

    def get_health(self):
        """
        This endpoint is intended for administrators of QuantumLeap. Using the
        information returned by this endpoint they can diagnose problems in the
        service or its dependencies. This information is also useful for cloud
        tools such as orchestrators and load balancers with rules based on
        health-checks. Due to the lack of a standardized response format, we
        base the implementation on the draft of
        https://inadarei.github.io/rfc-healthcheck/
        Returns:
            Dictionary with response
        """
        url = urljoin(settings.QL_URL, '/health')
        try:
            res = self.session.get(url=url, headers=self.headers)
            if res.ok:
                return res.json()
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)

    def post_config(self):
        """
        (To Be Implemented) Customize your persistance configuration to
        better suit your needs."""
        raise NotImplementedError

    # INPUT API ENDPOINTS
    def post_notification(self, notification: Notification):
        """
        Notify QuantumLeap the arrival of a new NGSI notification.
        Returns:

        """
        pass

    def post_subscription(self):
        pass


    def test_connection(self):
        """
        Function utilises the test.test_connection() function to check the availability of a given url and service_group.
        :return: Boolean, True if the service_group is reachable, False if not.
        """
        pass
        #boolean = test.test_connection(client=self.session,
        #                               url=self.url + '/v2/version',
        #                               service_name=__name__)
#
    #def create_subscription_object(self, entity: Entity, url: str,
    #                               **kwargs) -> object:
    #    """
    #    Creates and returns Subscription object so that it can be edited before
    #    the subscription is actually created.
    #    :param entity: entity to subscribe on
    #    :param url: URL destination for subscription notifications
    #    :return: Subscription object, not yet sent to Orion Context Broker
    #    """
    #    id_pattern = kwargs.get("id_pattern", None)
    #    if id_pattern != None:
    #        subject_entity = Subject_Entity(id_pattern, None, True)
    #    else:
    #        entity_type = json.loads(entity.get_json())["type"]
    #        subject_entity = sub.Subject_Entity(entity.id, entity_type)
    #    subject = sub.Subject([subject_entity])
    #    http_params = sub.HTTP_Params(url)
    #    notification = sub.Notification(http_params)
    #    throttling = kwargs.get("throttling")
    #    expires = kwargs.get("expires")
    #    description = kwargs.get("description")
    #    subscription = sub.Subscription(subject, notification, description,
    #                                    expires, throttling)
    #    return subscription
#
    #def get_header(self, additional_headers: dict = None):
    #    """combine fiware_service header (if set) and additional headers"""
    #    if self.fiware_service == None:
    #        return additional_headers
    #    elif additional_headers == None:
    #        return self.fiware_service.get_header()
    #    else:
    #        headers = {**self.fiware_service.get_header(),
        #        **additional_headers}
    #        return headers
#
#
    #def get_health(self):
    #    url = self.url + '/v2/health'
    #    headers = requtils.HEADER_CONTENT_PLAIN
    #    response = self.session.get(url, headers=headers)
    #    ok, retstr = requtils.response_ok(response)
    #    if not ok:
    #        print(retstr)
    #        return ""
    #    else:
    #        return response.text
#
    #def delete_entity(self, entity_name: str):
    #    url = self.url + '/v2/entities/' + entity_name
    #    headers = self.get_header(requtils.HEADER_CONTENT_PLAIN)
    #    response = self.session.delete(url, headers=headers)
    #    ok, retstr = requtils.response_ok(response)
    #    if not ok:
    #        print(retstr)
#
    #def delete_entities_of_type(self, entity_type):
    #    url = self.url + '/v2/types/' + entity_type
    #    headers = self.get_header(requtils.HEADER_CONTENT_PLAIN)
    #    response = self.session.delete(url, headers=headers)
    #    ok, retstr = requtils.response_ok(response)
    #    if not ok:
    #        print(retstr)
#
    #def get_entity_data(self, entity_id: str, attr_name: str = None,
    #                    valuesonly: bool = False, **kwargs):
    #    url = self.url + '/v2/entities/' + entity_id
    #    params = kwargs.get("params")
    #    headers = self.get_header(requtils.HEADER_CONTENT_PLAIN)
    #    if attr_name != None:
    #        url += '/attrs/' + attr_name
    #    if valuesonly:
    #        url += '/value'
    #    response = self.session.get(url, headers=headers, params=params)
    #    ok, retstr = requtils.response_ok(response)
    #    if not ok:
    #        print(retstr)
    #        return ""
    #    else:
    #        return response.text
#
    #def get_entity_type_data(self, entity_type: str, attr_name: str = None,
    #                         valuesonly: bool = False):
    #    url = self.url + '/v2/types/' + entity_type
    #    headers = self.get_header(requtils.HEADER_CONTENT_PLAIN)
    #    if attr_name != None:
    #        url += '/attrs/' + attr_name
    #    if valuesonly:
    #        url += '/value'
    #    response = self.session.get(url, headers=headers)
    #    ok, retstr = requtils.response_ok(response)
    #    if not ok:
    #        print(retstr)
    #        return ""
    #    else:
    #        return response.text
#
    #def get_attributes(self, attr_name: str = None, valuesonly: bool = False):
    #    url = self.url + '/v2/attrs'
    #    headers = self.get_header(requtils.HEADER_CONTENT_PLAIN)
    #    if attr_name != None:
    #        url += '/' + attr_name
    #    if valuesonly:
    #        url += '/value'
    #    response = self.session.get(url, headers=headers)
    #    ok, retstr = requtils.response_ok(response)
    #    if not ok:
    #        print(retstr)
    #        return ""
    #    else:
    #        return response.text
#
    #def get_timeseries(self, entity_name: str = None, attr_name: str = None,
    #                   valuesonly: bool = True, limit: str = "10000"):
    #    """
#
    #    :param entity_name: Name of the entity where the timeseries data
        #    should be retrieved
    #    :param attr_name: Name of the attribute where the timeseries data
        #    should be retrieved, if none given, all attribute are retrieved
    #    :param valuesonly: Return has values only
    #    :param limit: maximum number of values that should be retrieved
    #    :return: A dictionary, where the key is the time and the value the
        #    respective value e.g. '2020-02-11T13:45:23.000': 6
    #    """
    #    url = self.url +"/v2/entities/"+ entity_name
    #    headers = self.get_header(requtils.HEADER_CONTENT_PLAIN)
    #    res = dict()
    #    if attr_name != None:
    #        url += '/attrs/' + attr_name
    #    if valuesonly:
    #        url += '/value'
    #    url += '?limit=' + limit
    #    response = self.session.get(url, headers=headers)
    #    ok, retstr = requtils.response_ok(response)
    #    if not ok:
    #        print(retstr)
    #        return None
    #    else:
    #        response_json = json.loads(response.text)
    #        for attr in response_json["attributes"]:
    #            attr_name = attr["attrName"]
    #            res[attr_name] = dict(zip(response_json["index"],
            #            attr["values"]))
    #        return res





