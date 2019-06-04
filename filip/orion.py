import json 
import filip.cb_request as cb

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
    """
    Describes an entity which can be saved in the Orion Context Broker.
    """
    def __init__(self, entity_id: str, entity_type: str, attributes: list):
        """
        :param entity_id: ID of the entity
        :param entity_type: type of the entity
        :param attributes: list of Attribute objects
        """
        self.id = entity_id
        self.type = entity_type
        self.attributes = attributes

    def get_attributes_json_dict(self):
        json_dict = {}
        for attr in self.attributes:
            json_dict[attr.name] = attr.get_json()
        return json_dict

    def get_json(self):
        json_dict = self.get_attributes_json_dict()
        json_dict['id'] = self.id
        json_dict['type'] = self.type
        json_res = json.dumps(json_dict)
        return json_res

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

    def get_header(self) -> object:
        return {
            "fiware-service": self.name,
            "fiware-servicepath": self.path
        }

class Orion:
    """
    Implementation of Orion Context Broker functionalities, such as creating entities
    and subscriptions; retrieving, updating and deleting data. Further documentation:
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

    def post_entity(self, entity):
        url = self.url + '/entities'
        cb.post(url, self.get_header(cb.HEADER_CONTENT_JSON), entity.get_json())
   
    def get_entity(self, entity_name,  entity_params=None):
        url = self.url + '/entities/' + entity_name

        if entity_params is None:
            return cb.get(url, self.get_header())
        else:
            return cb.get(url, self.get_header(), entity_params)

    def get_all_entities(self, parameter=None, parameter_value=None):
        url = self.url + '/entities'

        if parameter is None and parameter_value is None:
            return cb.get(url, self.get_header())
        elif parameter is not None and parameter_value is not None:
            parameters = {'{}'.format(parameter): '{}'.format(parameter_value)}
            return cb.get(url, self.get_header(), parameters)
        else:
            print ("ERROR getting all entities: both function parameters have to be 'not null'")

    def get_entity_keyValues(self, entity_name):
        parameter = {'{}'.format('options'): '{}'.format('keyValues')}
        return self.get_entity(entity_name, parameter)

    def get_entity_attribute_json(self, entity_name,
                                  attribute_name):
        url = self.url + '/entities/' + entity_name + '/attrs/' + attribute_name
        return cb.get(url, self.get_header())

    def get_entity_attribute_value(self, entity_name, attribute_name):
        url = self.url + '/entities/' + entity_name + '/attrs/' + attribute_name + '/value'
        return cb.get(url, self.get_header())

    def get_entity_attribute_list(self, entity_name, attr_name_list):
        attributes = ','.join(attr_name_list)
        parameters = {'{}'.format('options'): '{}'.format('values'), '{}'.format('attrs'): attributes}
        return self.get_entity(entity_name, parameters)

    def update_entity(self, entity):
        url = self.url + '/entities/' + entity.name + '/attrs'
        payload = entity.get_attributes_json_dict()
        cb.patch(url, self.get_header(cb.HEADER_CONTENT_JSON), json.dumps(payload))
        # TODO: query entity operation to check that entity was actually updated
        # if ok, should return 204

    def update_attribute(self, entity_name, attr_name, attr_value):
        url = self.url + '/entities/' + entity_name + '/attrs/' + attr_name + '/value'
        cb.put(url, self.get_header(cb.HEADER_CONTENT_PLAIN), json.dumps(attr_value))

    def remove_attributes(self, entity_name):
        url = self.url + '/entities/' + entity_name + '/attrs'
        cb.put(url)

    def create_subscription(self, subscription_body):
        url = self.url + '/subscriptions'
        ret = cb.post(url, self.get_header(cb.HEADER_CONTENT_JSON), 
                        subscription_body, None, True)
        if ret==None:
            return

        location = ret.get('Location')
        addr_parts = location.split('/')
        subscription_id = addr_parts.pop()
        return subscription_id

    def get_subscription_list(self):
        url = self.url + '/subscriptions'
        data = cb.get(url, self.get_header())
        json_object = json.loads(data)

        subscriptions = []
        for key in json_object:
            subscriptions.append(key["id"])

        return subscriptions

    def get_subscription(self, subscription_id):
        url = self.url + '/subscriptions/' + subscription_id
        return cb.get(url, self.get_header())

    def delete_subscription(self, subscription_id):
        url = self.url + '/subscriptions/' + subscription_id
        cb.delete(url, self.get_header())

    def delete_all_subscriptions(self):
        subscriptions = self.get_subscription_list()
        for sub_id in subscriptions:
            self.delete_subscription(sub_id)

    def post_cmd_v1(self, entity_id: str, entity_type: str, cmd_name: str, cmd_value: str):
        url = self.url_v1 + '/updateContext'
        payload = {"updateAction": "UPDATE",
                   "contextElements": [
                           {"id": entity_id, "type" : entity_type, "isPattern": "false", 
                                "attributes": [{"name": cmd_name, 
                                                "type": "command", "value": cmd_value }]}
                    
                        ]
                    }
        cb.post(url, self.get_header(cb.HEADER_CONTENT_JSON), json.dumps(payload))

    def delete(self, entity_id: str, attr: str = None):
        url = self.url + '/entities/' + entity_id
        cb.delete(url, self.get_header())
