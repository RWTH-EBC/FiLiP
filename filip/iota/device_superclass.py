"""
This class and module is for easier maintenance of the device.py and device_group.py and includes all shared functions.

"""

import json
import logging
import datetime

log = logging.getLogger("iot")

class Shared:
    """
    Class is implemented for easier maintenance of the IoT Agent Functions. It implements all shared functions and
    attributes of the device and device_group class.
    """
    def __init__(self, **kwargs):
        self.service = kwargs.get("service", None)
        self.service_path = kwargs.get("service_path", "/")
        self.apikey = kwargs.get("apikey")
        self.timestamp = kwargs.get("timestamp", None)
        self.attributes = kwargs.get("attr", [])
        self.lazy_attr = kwargs.get("lazy_attr", [])
        self.internal_attr = kwargs.get("internal_attr", [])
        self.commands = kwargs.get("commands", [])
        self.static_attr = kwargs.get("static_attr", [])

    def __repr__(self):
        """
        Function returns a representation of the object (its data) as a string.
        :return:
        """
        return str((vars(self)))

    def add_lazy(self, attribute):
        self.lazy_attr.append(attribute)

    def add_active(self, attribute):
        self.attributes.append(attribute)

    def add_static(self, attribute):
        self.static_attr.append(attribute)

    def add_command(self, attribute):
        self.commands.append(attribute)

    def add_internal(self, attribute):
        self.internal_attr.append(attribute)

    def get_json(self):
        data_dict = dict()
        if self.apikey:
            data_dict['apikey'] = self.apikey
        if self.timestamp is not None:
            data_dict['timestamp'] = self.timestamp
        if self.service:
            data_dict["service"] = self.service
        if self.service_path:
            data_dict['service_path'] = self.service_path
        data_dict['attributes'] = self.attributes
        data_dict['commands'] = self.commands
        data_dict["lazy"] = self.lazy_attr
        data_dict['static_attributes'] = self.static_attr
        data_dict['internal_attributes'] = self.internal_attr
        return json.dumps(data_dict, indent=4)

    def add_attribute(self, attribute: dict = None, attr_type: str = None,
                      name: str = None, type: str = None,
                      object_id: str = None, value = None):
        """
        :param attribute: {
            "name": "Temp_Sensor",
            "type": "Number",
            "object_id": "T_sen"
            "value": "12"
            }

        :param name: The name of the attribute as submitted to the context
        broker.
        :param attr_type: The type of the attribute as submitted to the context broker.  One of \"active\" (default), \"lazy\" or \"static\"
        :param object_id: The id of the attribute used from the southbound API.
        :param type: The type of the value, e.g. Number, Boolean or String
        :param value: the value of the attribute
        """

        if attribute is None or not isinstance(attribute, dict):
            loc = locals()
            attribute = dict([(i, loc[i]) for i in ('name',
                                                    'type',
                                                    'object_id',
                                                    'value')])
        elif attr_type is None:
            if "attr_type" in attribute.keys():
                attr_type = attribute["attr_type"]
                del attribute["attr_type"]
            else:
                log.error(f"Missing attribute type!")
                return False

        attr_type = attr_type.casefold()
        if attr_type != "static":
            if "value" in attribute.keys():
                if attribute["value"] != None:
                    log.warning(f"Setting attribute: Value only allowed for static "
                                f"attributes! Value will be ignored!")
                del attribute["value"]
        else:
            if "object_id" in attribute.keys():
                if attribute["object_id"] != None:
                    log.warning(f"Setting attribute: Static attribute do not need "
                                f"an object_id! object_id will be ignored!")
                del attribute["object_id"]

        switch_dict = {"active": self.add_active,
                       "lazy": self.add_lazy,
                       "static":  self.add_static,
                       "command": self.add_command,
                       "internal": self.add_internal
                       }.get(attr_type, "not_ok")(attribute)
        if switch_dict == "not_ok":
            log.warning(f"Attribute type unknown: {attr_type}")
            return False
        return True

    def delete_attribute(self, name, attr_type):
        """
        Removing attribute by name and from the list of attributes in the
        local device. You need to execute update device in iot agent in
        order to update the configuration to remote!
        :param name: Name of the attribute to delete
        :param attr_type: Type of the attribute to delete
        :return:
        """
        attr_type=attr_type.casefold()
        try:
            if attr_type == "active":
                self.attributes = [i for i in self.attributes if not (i['name']==name)]
            elif attr_type == "lazy":
                self.lazy_attr = [i for i in self.lazy_attr if not (i['name'] == name)]
            elif attr_type == "static":
                self.static_attr = [i for i in self.static_attr if
                                          not (i['name'] == name)]
            elif attr_type == "command":
                self.commands = [i for i in self.commands if not (i['name'] ==
                                                                   name)]
            elif attr_type == "internal":
                self.internal_attr = [i for i in self.internal_attr if not (i['name'] == name)]
            else:
                log.warning(f"Attribute type unknown: {attr_type}")

            log.info(f"Attribute successfully deleted: {name}")

        except:
            log.warning(f"Attribute could not be deleted: {name}")






