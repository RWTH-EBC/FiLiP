import requests
from requests import Response

import filip.test as test
import json
import string
import random
import filip

HEADER_ACCEPT_JSON = {'Accept': 'application/json'}
HEADER_ACCEPT_PLAIN = {'Accept': 'text/plain'}
HEADER_CONTENT_JSON = {'Content-Type': 'application/json'}
HEADER_CONTENT_PLAIN = {'Content-Type': 'text/plain'}
PROTOCOLS = ['IoTA-JSON','IoTA-UL']

AUTH = ('user', 'pass')

class Attribute:
    def __init__(self, name, value, attr_type):
        self.name = name
        self.value = value
        self.type = attr_type

    def get_json(self):
        return {'value': self.value, 'type': '{}'.format(self.type)}

class Command:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.type = "command"

    def get_json(self):
        return {'value': self.value, 'type': '{}'.format(self.type)}

class Device:
    """
    Represents all necessary information for device registration with an Fiware IoT Agent.
    :ivar device_id: Device ID that will be used to identify the device (mandatory).
    :ivar service: Name of the service the device belongs to (will be used in the fiware-service header).
    :ivar service_path: Name of the subservice the device belongs to (used in the fiware-servicepath header).
    :ivar entity_name: Name of the entity representing the device in the Context Broker.
    :ivar timezone: Time zone of the sensor if it has any.
    :ivar endpoint: Endpoint where the device is going to receive commands, if any.
    :ivar protocol: Name of the device protocol, for its use with an IoT Manager.
    :ivar transport: Name of the device transport protocol, for the IoT Agents with multiple transport protocols.
    :ivar attributes: List of active attributes of the device.
    :ivar lazy: List of lazy attributes of the device.
    :ivar commands: List of commands of the device
    :ivar static_attributes: List of static attributes to append to the entity. All the updateContext requests to the CB will have this set of attributes appended.
        """
    def __init__(self, device_id: str, entity_name: str, entity_type: str, **kwargs):
        self.device_id = device_id
        self.entity_name = entity_name
        self.entity_type = entity_type
        self.service = None
        self.service_path = "/"
        self.timezone = kwargs.get("timezone")
        self.endpoint = kwargs.get("endpoint")
        self.protocol = kwargs.get("protocol")
        self.transport = kwargs.get("transport")
        self.attributes = kwargs.get("attributes", [])
        self.lazy = kwargs.get("lazy", [])
        self.commands = kwargs.get("commands", [])
        self.static_attributes = kwargs.get("static_attributes", [])

    def get_json(self):
        dict = {}
        dict['device_id']= self.device_id
        dict['entity_name']= self.entity_name
        dict['entity_type']= self.entity_type
        dict['timezone'] = self.timezone
        dict['endpoint'] = self.endpoint
        dict['protocol'] = self.protocol
        dict['transport'] = self.transport
        dict['attributes'] = self.attributes
        dict['lazy'] = self.lazy
        dict['commands'] = self.commands
        dict['static_attributes'] = self.static_attributes
        return json.dumps(dict, indent=4)

    def add_attribute(self, ):
        """
        :param name: The name of the attribute as submitted to the context broker.
        :param type: The type of the attribute as submitted to the context broker.
        :param object_id: The id of the attribute used from the southbound API.
        :param attr_type: One of \"active\" (default), \"lazy\" or \"static\"
        """
        attr = {
            "name": name,
            "type": type
        }
        if object_id:
            attr["object_id"] = object_id

        if attr_type == "active":
            self.attributes.append(attr)
        elif attr_type == "lazy":
            self.lazy.append(attr)
        elif attr_type == "static":
            self.static_attributes.append(attr)
        else:
            print("[WARN]: Attribute type unknown: \"{}\"".format(attr_type))

    def add_command(self):
        return

    def get_commands(self):
        return

class DeviceGroup:
    """
    For every Device Group, the pair (resource, apikey) must be unique
    (as it is used to identify which group to assign to which device).
    Those operations of the API targeting specific resources will need
    the use of the resource and apikey parameters to select the
    apropriate instance.

    :param name:    Service of the devices of this type
    :param path:    Subservice of the devices of this type.
    :param cbHost: Context Broker connection information. This options
    can be used to override the global ones for specific types of devices.
    :param kwargs:
    :ivar entity_type: Name of the type to assign to the group.
    :ivar trust: Trust token to use for secured access to the Context Broker
    for this type of devices (optional; only needed for secured scenarios).
    :ivar lazy: List of lazy attributes of the device.
    :ivar commands: List of commands of the device
    :ivar attributes: List of active attributes of the device.
    :ivar static_attributes: List of static attributes to append to the entity. All the updateContext requests to the CB will have this set of attributes appended.
    :ivar internal_attributes: Optional section with free format, to allow
    specific IoT Agents to store information along with the devices in the Device Registry.
    """
    def __init__(self, fiware_service: str, fiware_servicepath: str, cb_host:
    str,
                           **kwargs):

        self.service = fiware_service
        self.subservice = fiware_servicepath
        self.resource = kwargs.get("resource", "")
        self.apikey = kwargs.get("apikey", "12345")
        self.entity_type = kwargs.get("entity_type", "Thing")
        #self.trust
        self.cbHost = cb_host
        #self.lazy
        #self.commands
        #self.attributes
        #self.static_attributes
        #self.internal_attributes

        self.devices = []
        self.agent = kwargs.get("iot-agent", "iota-json")


    def get_header(self) -> dict:
        return {
            "fiware-service": self.service,
            "fiware-servicepath": self.subservice
        }


    def get_json(self):
        dict = {}
        dict['apikey']= self.apikey
        dict['cbroker'] = self.cbHost
        dict['entity_type']= self.entity_type
        dict['resource'] = self.resource
        return json.dumps(dict, indent=4)

    def generate_apikey(self, length: int = 10):
        """
        This function generates a random key from lowercase letter and
        digit characters
        :ivar length: Number of characters in the key string
        """
        return ''.join(random.choice(
            string.ascii_lowercase + string.digits) for _ in range(
            length))

    def test_apikey(self):
        """
        This function tests if an apikey is defined in the configfile.
        Otherwise it will ask the user to generate one and saves it to the
        configfile in the given sections.
        """
        try:
            if self.apikey == "":
                res = input("[INFO]: No API-Key defined. Do you want to "
                            "generate one? "
                            "y/Y ")
                if res == "y" or res == "Y":
                    res = input("Please specify number of key (default is "
                                "10)? ")
                    if res != 10:
                        self.apikey = self.generate_apikey(int(res))
                    else:
                        self.apikey = self.generate_apikey()
                    #with open(self.path, 'w') as configfile:
                    #    self.config.write(configfile)
                    print("[INFO]: Random Key generated: '" + self.apikey + "'")
                else:
                    print("[INFO]: Default Key will be used: '1234'!")
            print("[INFO]: API-Key check success! " + self.apikey)
        except Exception:
            print("[ERROR]: API-Key check failed. Please check configuration!")


class Agent:
    def __init__(self, agent_name: str, config):
        self.name = agent_name
        self.test_configuration(config)
        self.host = config.data[self.name]['host']
        self.port = config.data[self.name]['port']
        self.url = self.host + ":" + self.port
        self.protocol = config.data[self.name]['protocol']
        #TODO: Figuring our how to register the service and conncet with devices
        self.services = []

    def test_configuration(self, config):
        if test.test_config(self.name, config.data):
            test.test_connection(self.name , config.data[self.name]['host']
                                 +":" +config.data[self.name]['port']+
                                 '/iot/about')

    def get_groups(self, device_group):
        url = self.url + '/iot/services'
        headers = DeviceGroup.get_header(device_group)
        response = requests.request("GET", url, headers=headers)
        print(response.text)

    def delete_group(self, device_group):
        url = self.url + '/iot/services'
        headers = DeviceGroup.get_header(device_group)
        querystring ={"resource":device_group.resource,"apikey": device_group.apikey}
        response = requests.request("DELETE", url,
                                    headers=headers, params=querystring)
        if response.status_code==204:
            print("[INFO]: Device group successfully deleted!")
        else:
            print(response.text)

    def post_group(self, device_group):
        url = self.url + '/iot/services'
        headers = {**HEADER_CONTENT_JSON, **device_group.get_header()}
        payload={}
        payload['services'] = [json.loads(device_group.get_json())]
        payload = json.dumps(payload, indent=4)
        print(payload)
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response.text)
        #filip.orion.post(url, head, AUTH, json_dict)

    def post_device(self, device, device_group):
        url = self.url + '/iot/devices'
        headers = {**HEADER_CONTENT_JSON, **device_group.get_header()}
        payload={}
        payload['devices'] = [json.loads(device.get_json())]
        payload = json.dumps(payload, indent=4)
        print(payload)
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response.text)

    def delete_device(self, device, device_group):
        url = self.url + '/iot/devices/'+ device.device_id
        headers = {**HEADER_CONTENT_JSON, **device_group.get_header()}
        payload= ""
        response = requests.request("DELETE", url, data=payload,
                                    headers=headers)
        if response.status_code == 204:
            print("[INFO]: Device successfully deleted!")
        else:
            print(response.text)

    def get_device(self, device, device_group):
        url = self.url + '/iot/devices/' + device.device_id
        headers = {**HEADER_CONTENT_JSON, **device_group.get_header()}
        payload = ""
        response = requests.request("GET", url, data=payload,
                                    headers=headers)
        print(response.text)

    def update_device(self, device, device_group, payload: json):
        url = self.url + '/iot/devices/' + device.device_id
        headers = {**HEADER_CONTENT_JSON, **device_group.get_header()}
        response = requests.request("GET", url, data=payload,
                                    headers=headers)
        print(response.text)

    def add_attribute(self, name, type, value, object_id: str = None,
                      attr_type='active'):
        """
        :param name: The name of the attribute as submitted to the context broker.
        :param type: The type of the attribute as submitted to the context broker.
        :param object_id: The id of the attribute used from the southbound API.
        :param attr_type: One of \"active\" (default), \"lazy\" or \"static\"
        """
        attr = {
            "name": name,
            "type": type,
            "value": value
        }
        if object_id:
            attr["object_id"] = object_id

        if attr_type == "active":
            self.attributes.append(attr)
        elif attr_type == "lazy":
            self.lazy.append(attr)
        elif attr_type == "static":
            self.static_attributes.append(attr)
        else:
            print("[WARN] Attribute type unknown: \"{}\"".format(attr_type))



### END of valid Code################

    def add_service(self, service_name: str, service_path: str,
                           **kwargs):
        device_group={'service': service_name,
                'service_path': service_path,
                'data':{
                    "entity_type": "Thing",
                    "protocol": kwargs.get("protocol", self.protocol),
                    "transport": kwargs.get("transport", "MQTT"),
                    "apikey": kwargs.get("apikey", "1234"),
                    "attributes": [],
                    "lazy": [],
                    "commands": [],
                    "static_attributes": []
                 }
             }

    def register_service(self, service: str, service_path: str,
                           **kwargs):
        """
        Register the default configuration that is used to set up new devices
        :param service: Fiware service (header)
        :param service_path: Fiware servic path (header)
        :param kwargs:
        :return: configuration data on success
        """
        data = {
            "services": [
                {
                    "entity_type": "Thing",
                    "protocol": kwargs.get("protocol", "IoTA-JSON"),
                    "transport": kwargs.get("transport", "MQTT"),
                    "apikey": kwargs.get("apikey", "1234"),
                    "attributes": [],
                    "lazy": [],
                    "commands": [],
                    "static_attributes": []
                }
            ]
        }

        req = requests.post(self.url + "/iot/services",
                            headers=self._get_header(service, service_path),
                            data=data)



        if req.status_code != 200:
            print("[WARN] Unable to register default configuration for service \"{}\", path \"{}\": {}"
                  .format(service, service_path, req.text))
            return None
        return data

    def _get_header(self, service: str, path: str) -> dict:
        return {
            "fiware_service": service,
            "fiware_servicepath": path
        }

    def fetch_service(self, service: str, service_path: str) -> [dict]:
        resp = requests.get(self.url + "/iot/services",
                            headers=self._get_header(
            service, service_path))

        if resp.status_code == 200:
            return resp.json()["services"]
        else:
            print("[WARN] Unable to fetch configuration for service "
                  "\"{}\", path \"{}\": {}"
                  .format(service, service_path, resp.text))







