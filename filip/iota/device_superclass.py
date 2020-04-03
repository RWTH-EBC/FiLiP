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

    def add_attribute(self, attribute: dict = None, attr_name: str = None,
                      attr_type: str = None, value_type: str = None,
                      object_id: str = None, attr_value=None):
        """
        :param attribute: {
            "name": "Temp_Sensor",
            "value_type": "Number",
            "object_id": "T_sen"
            "attr_type": "Static",
            "attr_value": "12",
            }

        :param attr_name: The name of the attribute as submitted to the context broker.
        :param attr_type: The type of the attribute as submitted to the context broker.  One of \"active\" (default), \"lazy\" or \"static\"
        :param object_id: The id of the attribute used from the southbound API.
        :param value_type: The type of the value, e.g. Number, Boolean or String
        :param attr_value: the value of the attribute
        """
        if isinstance(attribute, dict):
            if "attr_value" in attribute:
                if attribute["attr_type"] is not "static":
                    log.warning(f" {datetime.datetime.now()} - Setting attribute "
                                f"value only allowed for static attributes! Value will be ignored!")

        if attribute is None or not isinstance(attribute, dict):
            loc = locals()
            attribute = dict([(i, loc[i]) for i in ('attr_name',
                                                    'attr_type',
                                                    'value_type',
                                                    'object_id',
                                                    'attr_value')])

        attr_type = attribute["attr_type"]
        if "attribute_value" in attribute.keys():
            if attr_type is not "static":
                del attribute["attr_value"]

        attr = {"name": attribute["attr_name"],
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
        """
        Removing attribute by name and from the list of attributes in the
        local device. You need to execute update device in iot agent in
        order to update the configuration to remote!
        :param attr_name: Name of the attribute to delete
        :param attr_type: Type of the attribute to delete
        :return:
        """
        try:
            if attr_type == "active":
                self.attributes = [i for i in self.attributes if not (i['name']==attr_name)]
            elif attr_type == "lazy":
                self.lazy_attr = [i for i in self.lazy_attr if not (i['name'] == attr_name)]
            elif attr_type == "static":
                self.static_attr = [i for i in self.static_attr if
                                          not (i['name'] == attr_name)]
            elif attr_type == "command":
                self.commands = [i for i in self.commands if not (i['name'] ==
                                                                   attr_name)]
            elif attr_type == "internal":
                self.internal_attr = [i for i in self.internal_attr if not (i['name'] == attr_name)]
            else:
                log.warning(f" {datetime.datetime.now()} - Attribute type unknown: {attr_type}")

            log.info(f" {datetime.datetime.now()} -Attribute successfully deleted: {attr_name}")

        except:
            log.warning(f" {datetime.datetime.now()} -Attribute could not be deleted: {attr_name}")






