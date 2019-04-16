import json 
from enum import Enum

# Subscription according to NGSI v2 specification

AUTH = ('user', 'pass')


class Subject_Entity:
    def __init__(self, _id, _type):
        self.id = _id           # id XOR idPattern; required
        self.type = _type       # type OR typePattern; if omitted -> "any entity type"
    
    def get_json_dict(self):
        return None

class Subject_Condition:
    def __init__(self, attributes, expression=None):
        self.attributes = attributes    # list of attribute names; optional
        self.expression = expression    # TODO: description; optionala

   

# subscription subject
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
        return json_dict
#        if self.condition is not None:
#            entity_list = []
#            for entity in self.entities:
#                entity_list.append(entity.get_json_dict())
#
#            json_dict["condition"] = entity_list


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
    def __init__(self, url, only_url_given=True, headers=None, qs=None, method=None, payload=None):
        self.url = url              # URL referencing the service to be invoked by a notification
        self.only_url = only_url_given  # 'http' for True; 'httpCustom' for False
        self.headers = headers      # key-map of HTTP headers; optional
        self.qs = qs                # key-map of URL query parameters                
        self.method = method        # HTTP method to use for notification (default: POST)
        self.payload = payload      # payload to be used in notifications

    def is_custom_http(self):
        return (not self.only_url)

    def get_json_dict(self):
        json_dict = {"url": self.url}
        if not self.is_custom_http():
            return json_dict

        if self.headers is not None:
            json_dict["headers"] = self.headers #TODO: this is wrong, headers is a key-map
        if self.qs is not None:
            json_dict["qs"] = self.qs # TODO (See headers)

        #set_attr = filter(lambda attr: not attr.startswith('__') and not None, dir(obj))
        #print(set_attr)

        return json_dict

class Notification:
    def __init__(self, http, attr):
        self.http = http    # object of class 'HTTP_Params'
        self.attr = attr    # Notification_Attributes object

    def get_json_dict(self):
        json_dict = {}
        if self.http.is_custom_http():
            json_dict["httpCustom"] = self.http.get_json_dict()
        else:
            json_dict["http"] = self.http.get_json_dict()

        if self.attr.is_specified():
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


        # get all not-null attributes (filter out methods as well)
        #set_attr = 
        #filter(lambda attr: not attr.startswith('__') and not None, dir(self));
        #print(set_attr)

#        for attr in dir(self) if 
#        json_dict = {'description': '{}'.format(self.description)




    def list_registrations(self, host, port, **kwargs):
        url = "http://" + host + ":" + port + "/v2/registrations"
        head = HEADER_CONTENT_JSON

        if kwargs is not None:
            parameters = {}
            for key, value in kwargs.iteritems():
                if key in ("limit", "offset", "options"): #TODO: options contains several options
                    parameters[key] = value
            cb.get(url, head, AUTH, json.dumps(parameters))
        else:
            cb.get(url, head, AUTH)
        


#ORION
    def create_subscription(self, subscription):
        url = self.url + '/subscriptions'
        head = HEADER_ACCEPT_JSON

        post(url, head, AUTH, subscription_get_json)

        subscription.subscription_id = ...
