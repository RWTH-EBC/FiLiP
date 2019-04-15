import json 
from enum import Enum

# Subscription according to NGSI v2 specification

AUTH = ('user', 'pass')


class Subject_Entity:
    def __init__(self, _id, _type):
        self.id = _id           # id XOR idPattern; required
        self.type = _type       # type OR typePattern; if omitted -> "any entity type"

class Subject_Condition:
    def __init__(self, attributes, expression):
        self.attributes = attributes    # list of attribute names; optional
        self.expression = expression    # TODO: description; optional

# subscription subject
class Subject:
    def __init__(self):
        self.entities = None    # list of Subject_Entity objects 
        self.condition = None   # optional Subject_Condition object; if left empty -> notification will be triggered for any entity attribute change



class Attribute_Type(Enum):
    ATTRS = 1   # attributes are included in notification message
    EXCEPT = 2  # attributes which will NOT be in the notification message are defined
    ALL = 3    # all attributes are included in notifications

class Notification_Attribute:
    def __init__(self, attr_type=Attribute_Type.ALL, _list=None):
        self.attr_type = attr_type
        self.attr_list = _list      # list of either 'attrs' or 'exceptAttr'
        

class HTTP_Type(Enum):
    HTTP = 1            # only URL is given for the Notification
    HTTP_CUSTOM = 2     # URL plus custom parameters (headers, qs, method, payload)

class HTTP_Params:
    def __init__(self, url, _type=HTTP_Type.HTTP, headers=None, qs=None, method=None, payload=None):
        self.url = url              # URL referencing the service to be invoked by a notification
        self.type = _type           # 'http' or 'httpCustom'
        self.headers = headers      # key-map of HTTP headers; optional
        self.qs = qs                # key-map of URL query parameters                
        self.method = method        # HTTP method to use for notification (default: POST)
        self.payload = payload      # payload to be used in notifications

    def get_json(self):
        # TODO

class Notification:
    def __init__(self, http, attr):
        self.http = http    # object of class 'HTTP_Params'
        self.attr = attr    # Notification_Attribute object

class Subscription:
    def __init__(self, subject, notification):
        self.subject = subject              # Subject of the subscription
        self.notification = notification    # Notification of the subscription
        self.description = None         # string, optional
        self.expires = None             # date in ISO 8601 format, optional (if omitted -> permanent subscription) 
        self.throttling = None          # min. period (in seconds) between two notifications; optional
        self.subscription_id = None     # subscription unique identifier, created by Orion Context Broker at creation time

    def get_json(self):
        json_dict = {'description': '{}'.format(self.description)




#ORION
    def create_subscription(self, subscription):
        url = self.url + '/subscriptions'
        head = HEADER_ACCEPT_JSON

        post(url, head, AUTH, subscription_get_json)

        subscription.subscription_id = ...
