import json 
from enum import Enum

class Subject_Entity:
    def __init__(self, _id, _type=None, use_id_pattern=False, use_type_pattern=False):
        """
        :param _id: id XOR idPattern, required
        :param _type: type OR typePattern; if omitted: any entity type
        :param use_id_pattern: use idPattern instead of id
        :param use_type_pattern: use typePattern instead of type
        """
        self.id = _id
        self.type = _type
        self.use_id_pattern = use_id_pattern
        self.use_type_pattern = use_type_pattern
    
    def get_json_dict(self):
        json_dict = {}
        if self.use_id_pattern:
            json_dict["idPattern"] = self.id
        else:
            json_dict["id"] = self.id
        if self.type is not None:
            if self.use_type_pattern:
                json_dict["typePattern"] = self.type
            else:
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
    def __init__(self, attributes: list = None, expression:object = None):
        """
        :param attributes: list of attribute names, optional
        :param expression: Subject_Expression object, optional
        """
        self.attributes = attributes
        self.expression = expression

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
    def __init__(self, entities: list, condition: object = None):
        """
        :param entities: list of Subject_Entity objects, required
        :param condition: Subject_Condition object; if left empty,
        a notification will be triggered for any attribute change
        """
        self.entities = entities
        self.condition = condition

    def get_json_dict(self):
        json_dict = {}
        entity_list = []
        for entity in self.entities:
            entity_list.append(entity.get_json_dict())
        json_dict["entities"] = entity_list
        if self.condition is not None:
            json_dict["condition"] = self.condition.get_json_dict()
        return json_dict

class Notification_Attributes:
    def __init__(self, attribute_type: str = None, _list=None, specified=False):
        """
        If the notification attributes are left empty, all attributes will be
        included in the notifications. Otherwise, only the specified ones will
        be included.
        :param attribute_type: either 'attrs' or 'exceptAttrs'
        :param _list: list of either 'attrs' or 'exceptAttrs' attributes
        """
        if attribute_type is not None and _list is not None:
            self.attribute_type = attribute_type
            self.attr_list = _list
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
    def __init__(self, url, headers: dict = None, qs: dict = None,
                 method: str = None, payload = None):
        """
        :param url: URL referencing the service to be invoked by a notification
        :param headers: key-map (dict) of HTTP headers; optional
        :param qs: key-map (dict) of URL query parameters
        :param method: HTTP method to use for notification (default: POST)
        :param payload: payload to be used in notifications
        """
        self.url = url
        self.headers = headers
        self.qs = qs
        self.method = method
        self.payload = payload

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
    def __init__(self, http, attr: object = None, attrsFormat: str = None,
                                                   metadata: list = None):
        """
        :param http: object of class 'HTTP_Params', required
        :param attr: object of class 'Notification_Attribute', optional
        :param attrsFormat: specifies entity representation, optional
        :param metadata: list of metadata to be included in notifications,
        optional
        """
        self.http = http
        self.attr = attr
        self.attrsFormat = attrsFormat
        self.metadata  = metadata

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
    """
    Orion Context Broker Subscription according to NGSI v2 specification.
    Further information:
    http://telefonicaid.github.io/fiware-orion/api/v2/stable/
    """
    def __init__(self, subject, notification, description=None, expires=None,
                                                            throttling=None):
        """
        :param subject: Subject of the subscription, required
        :param notification: Notification of the subscription, required
        :param description: description string, optional
        :param expires: date in ISO 8601 format, optional
        :param throttling: min. period (seconds) between two notifications,
        optional
        """
        self.subject = subject
        self.notification = notification
        self.description = description
        self.expires = expires
        self.throttling = throttling
        self.subscription_id = None
        """subscription unique identifier, created by Orion Context Broker at creation time"""

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
