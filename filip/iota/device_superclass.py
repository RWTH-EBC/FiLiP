"""
This class and module is for easier maintenance of the device.py and device_group.py and includes all shared functions.

"""

import json

class Shared:
    """
    Class
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
        self.__lazy_attr.append(attribute)

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



