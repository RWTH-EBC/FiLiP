import json
import string
import random
import datetime

from filip import config


import logging

log = logging.getLogger('iot')


PROTOCOLS = ['IoTA-JSON','IoTA-UL']


class Device:
    """
    Represents all necessary information for device registration with an Fiware IoT Agent.
    :ivar device_id: Device ID that will be used to identify the device (mandatory).
    :ivar service: Name of the service the device belongs to (will be used in the fiware-service header).
    :ivar service_path: Name of the subservice the device belongs to (used in the fiware-servicepath header).
    :ivar entity_name: Name of the entity representing the device in the Context Broker.
    :ivar timezone: Time zone of the sensor if it has any. Default ist UTC/Zulu.
    :ivar timestamp: (optional, boolean): This field indicates if an attribute 'TimeInstant' will be added (true) or not (false). If this field is omitted, the global IotAgent configuration timestamp will be used.
    :ivar apikey: Optional Apikey string to use instead of group apikey
    :ivar endpoint: Endpoint where the device is going to receive commands, if any.
    :ivar protocol: Name of the device protocol, for its use with an IoT Manager.
    :ivar transport: Name of the device transport protocol, for the IoT Agents with multiple transport protocols.
    :ivar attributes: List of active attributes of the device.
    :ivar lazy: List of lazy attributes of the device.
    :ivar commands: List of commands of the device
    :ivar static_attributes: List of static attributes to append to the entity. All the updateContext requests to the CB will have this set of attributes appended.
    :ivar internal_attributes: List of internal attributes with free format for specific IoT Agent configuration.
                                Note: They are only stored in the device registry.
    :ivar autoprovision: (optional, boolean): If true, APPEND is used upon
    measure arrival (thus effectively allowing autoprovisioned devices). If false, UPDATE is used open measure arrival (thus effectively avoiding autoprovisioned devices). This field is optional, so if it omitted then the global IoTAgent appendModel configuration is used.
        """


    def __init__(self, device_id: str, entity_name: str, entity_type: str, **kwargs):
        self.device_id = device_id
        self.entity_name = entity_name
        self.entity_type = entity_type
        self.service = kwargs.get("service", None)
        self.service_path = kwargs.get("service_path", "/")
        self.timezone = config.TIMEZONE
        #self.timezone = kwargs.get("timezone", "UTC/Zulu")
        self.timestamp = kwargs.get("timestamp", None)
        self.autoprovision = kwargs.get("autoprovision", None)
        self.apikey = kwargs.get("apikey")
        self.endpoint = kwargs.get("endpoint") # necessary for HTTP
        self.protocol = kwargs.get("protocol")
        self.transport = kwargs.get("transport")
        self.attributes = kwargs.get("attributes", [])
        self.lazy = kwargs.get("lazy", [])
        self.commands = kwargs.get("commands", [])
        self.static_attributes = kwargs.get("static_attributes", [])
        self.internal_attributes = kwargs.get("internal_attributes", [])


    def __repr__(self):
        """
        Function returns a representation of the object (its data) as a string.
        :return:
        """
        return str((vars(self)))

    def get_json(self):
        data_dict = dict()
        data_dict['device_id']= self.device_id
        data_dict['entity_name']= self.entity_name
        data_dict['entity_type']= self.entity_type
        data_dict['timezone'] = self.timezone
        if self.endpoint:
            data_dict['endpoint'] = self.endpoint
        if self.apikey:
            data_dict['apikey'] = self.apikey
        if self.timestamp!=None:
            data_dict['timestamp'] = self.timestamp
        if self.service:
            data_dict["service"] = self.service
        if self.service_path:
            data_dict['service_path'] = self.service_path
        data_dict['protocol'] = self.protocol
        data_dict['transport'] = self.transport
        data_dict['attributes'] = self.attributes
        data_dict['lazy'] = self.lazy
        data_dict['commands'] = self.commands
        data_dict['static_attributes'] = self.static_attributes
        data_dict['internal_attributes'] = self.internal_attributes
        if self.autoprovision!=None:
            data_dict['autoprovision'] = self.autoprovision
        return json.dumps(data_dict, indent=4)

    def add_lazy(self, attribute):
        self.lazy.append(attribute)

    def add_active(self, attribute):
        self.attributes.append(attribute)

    def add_static(self, attribute):
        self.static_attributes.append(attribute)

    def add_command(self, attribute):
        self.commands.append(attribute)

    def add_internal(self, attribute):
        self.internal_attributes.append(attribute)


    # Function beneath is only for backwards compatibility


    def add_attribute(self, attribute:dict):
        """
        :param attribute: {
            "name": "Temp_Sensor",
            "value_type": "Number",
            "attr_type": "Static",
            "attr_value": "12",
            }

        :param name: The name of the attribute as submitted to the context broker.
        :param type: The type of the attribute as submitted to the context broker.

        :param object_id: The id of the attribute used from the southbound API.
        :param attr_type: One of \"active\" (default), \"lazy\" or \"static\"
        """
        """
        :param attr_name: The name of the attribute as submitted to the context broker.
        :param attr_type: The type of the attribute as submitted to the context broker.
        :param value_type: One of \"active\" (default), \"lazy\" or \"static\"
        :param object_id: The id of the attribute used from the southbound API.
        :param attr_value: the value of the attribute
        """

        attr_type = attribute["attr_type"]
        if "attr_value" in attribute:
            if attribute["attr_type"] != "static":# & attribute["attr_value"] != None:
                log.warning(f" {datetime.datetime.now()} - Setting attribute value only allowed for static attributes! Value will be ignored!")
                del attribute["attr_value"]

        attr = {"name": attribute["name"],
                "type": attribute["value_type"]
                }
        # static attribute do not need an object id
        if attr_type != "static":
            attr["object_id"] = attribute["object_id"]


        # attr["value"] = Attribute.value NOT Supported by agent-lib
        switch_dict = {"active": self.add_active,
                       "lazy": self.add_lazy,
                       "static":  self.add_static,
                       "command": self.add_command,
                       "internal": self.add_internal
                }.get(attr_type, "not_ok")(attr)
        if switch_dict == "not_ok":
            log.warning(f" {datetime.datetime.now()} - Attribute type unknown: {attr_type}")


    def delete_attribute(self, attr_name, attr_type):
        '''
        Removing attribute by name and from the list of attributes in the
        local device. You need to execute update device in iot agent in
        order to update the configuration to remote!
        :param attr_name: Name of the attribute to delete
        :param attr_type: Type of the attribute to delete
        :return:
        '''
        try:
            if attr_type == "active":
                self.attributes = [i for i in self.attributes if not (i['name']==attr_name)]
            elif attr_type == "lazy":
                self.lazy = [i for i in self.lazy if not (i['name'] == attr_name)]
            elif attr_type == "static":
                self.static_attributes = [i for i in self.static_attributes if
                                          not (i['name'] == attr_name)]
            elif attr_type == "command":
                self.commands = [i for i in self.commands if not (i['name'] ==
                                                                   attr_name)]
            elif attr_type == "internal":
                self.internal_attributes = [i for i in self.internal_attributes if not (i['name'] == attr_name)]
            else:
                log.warning(f" {datetime.datetime.now()} - Attribute type unknown: {attr_type}")

            log.info(f" {datetime.datetime.now()} -Attribute successfully deleted: {attr_name}")
        except:
            log.warning(f" {datetime.datetime.now()} -Attribute could not be deleted: {attr_name}")


