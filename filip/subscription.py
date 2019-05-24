import json 
from enum import Enum

# Subscription according to NGSI v2 specification

class Subject_Entity:
    def __init__(self, _id, _type=None):
        self.id = _id           # id XOR idPattern; required
        self.type = _type       # type OR typePattern; if omitted -> "any entity type"
    
    def get_json_dict(self):
        json_dict = {"id": "{}".format(self.id)}
        if self.type is not None:
            json_dict["type"] = self.type
        return json_dict

class Subject_Expression:
    def __init__(self):
        self.q = None
        self.mq = None
        self.georel = None
        self.geometry = None
        self.coords = None

    def get_json_dict(self):
        json_dict = {}
        if self.q is not None:
            json_dict["q"] = self.q
        if self.mq is not None:
            json_dict["mq"] = self.mq
        if self.georel is not None:
            json_dict["georel"] = self.georel
        if self.geometry is not None:
            json_dict["geometry"] = self.geometry
        if self.coords is not None:
            json_dict["coords"] = self.coords
        return json_dict

class Subject_Condition:
    def __init__(self, attributes=None, expression=None):
        self.attributes = attributes    # list of attribute names; optional
        self.expression = expression    # TODO: description; optional

    def get_json_dict(self):
        json_dict = {}
        if self.attributes is None and self.expression is None:
            return None

        if self.attributes is not None:
            json_dict["attrs"] = self.attributes
        if self.expression is not None:
            json_dict["expression"] = self.expression.get_json_dict()
        return json_dict

class Subject:
    def __init__(self, entities, condition=None):
        self.entities = entities    # list of Subject_Entity objects, required
        self.condition = condition  # optional Subject_Condition object; if left empty -> notification will be triggered for any entity attribute change

    def get_json_dict(self):
        json_dict = {}
        entity_list = []
        for entity in self.entities:
            entity_list.append(entity.get_json_dict())

        json_dict["entities"] = entity_list

        if self.condition is not None:
            json_dict["condition"] = self.condition.get_json_dict()

        return json_dict

# attribute_type can be either "attrs" or "exceptAttrs"
# if left empty, all attributes are included in notifications
class Notification_Attributes:
    def __init__(self, attribute_type=None, _list=None, specified=False):
        if attribute_type is not None and _list is not None:
            self.attribute_type = attribute_type    # string value which is either 'attrs' or 'exceptAttrs'
            self.attr_list = _list      # list of either 'attrs' or 'exceptAttr'
            self.specified = True
        else: 
            self.specified = False

    def get_json_dict(self):
        if not self.specified:
            return None

        json_dict = {}
        json_dict[self.attribute_type] = self.attr_list
        return json_dict

    def is_specified(self):
        return self.specified
        

class HTTP_Params:
    def __init__(self, url):
        self.url = url          # URL referencing the service to be invoked by a notification
        self.headers = None     # key-map (dict) of HTTP headers; optional
        self.qs = None          # key-map (dict) of URL query parameters                
        self.method = None      # HTTP method to use for notification (default: POST)
        self.payload = None     # payload to be used in notifications

    def is_custom_http(self):
        if self.headers is not None \
        or self.qs is not None \
        or self.method is not None \
        or self.payload is not None:
            return True
        else:
            return False

    def get_json_dict(self):
        json_dict = {"url": self.url}
        if not self.is_custom_http():
            return json_dict

        if self.headers is not None:
            json_dict["headers"] = self.headers #TODO: this is wrong, headers is a key-map
        if self.qs is not None:
            json_dict["qs"] = self.qs # TODO (See headers)
        if self.method is not None:
            json_dict["method"] = self.method
        if self.payload is not None:
            json_dict["payload"] = self.payload

        return json_dict

class Notification:
    def __init__(self, http, attr=None):
        self.http = http    # object of class 'HTTP_Params'
        self.attr = attr    # Notification_Attributes object
        self.attrsFormat = None     # optional, specifies how entites are represented in notifications
        self.metadata = None        # list of metadata to be included in notifications

    def get_json_dict(self):
        json_dict = {}
        if self.http.is_custom_http():
            json_dict["httpCustom"] = self.http.get_json_dict()
        else:
            json_dict["http"] = self.http.get_json_dict()

        if self.attrsFormat is not None:
            json_dict["attrsFormat"] = self.attrsFormat

        if self.metadata is not None:
            json_dict["metadata"] = self.metadata

        if self.attr is not None and self.attr.is_specified():
            json_dict.update(self.attr.get_json_dict())
        return json_dict


class Subscription:
    def __init__(self, subject, notification, description=None, expires=None, throttling=None):
        self.subject = subject              # Subject of the subscription
        self.notification = notification    # Notification of the subscription
        self.description = description      # string, optional
        self.expires = expires              # date in ISO 8601 format, optional (if omitted -> permanent subscription) 
        self.throttling = throttling        # min. period (in seconds) between two notifications; optional
        self.subscription_id = None         # subscription unique identifier, created by Orion Context Broker at creation time

    def get_json(self):
        json_dict = {}
        if self.description is not None:
            json_dict["description"] = self.description
        if self.expires is not None:
            json_dict["expires"] = self.expires
        if self.throttling is not None:
            json_dict["throttling"] = self.throttling

        json_dict["notification"] = self.notification.get_json_dict()
        json_dict["subject"] = self.subject.get_json_dict()

        return json.dumps(json_dict)
    
