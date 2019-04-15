import requests
import filip.test as test
import string

import filip

HEADER_JSON = {'Accept': 'application/json'}
HEADER_PLAIN = {'Accept': 'text/plain'}
HEADER_CONTENT = {'Content-Type': 'application/json'}
PROTOCOLS = ['IoTA-JSON','IoTA-UL']

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
        self.service_path = None
        self.timezone = kwargs.get("timezone")
        #self.endpoint = kwargs.get("endpoint")
        self.protocol = kwargs.get("protocol")
        self.transport = kwargs.get("transport")
        self.attributes = kwargs.get("attributes", [])
        self.lazy = kwargs.get("lazy", [])
        self.commands = kwargs.get("commands", [])
        self.static_attributes = kwargs.get("static_attributes", [])

    def add_attribute(self):
        return

    def add_command(self):
        return

    def get_commands(self):
        return



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

    def get_service(self):
        return



    def add_service(self, service_name: str, service_path: str,
                           **kwargs):
        iot_service={'service': service_name,
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







