"""
This class and module is for easier maintenance of the device.py and device_group.py and includes all shared functions.

"""

import json

class Shared:
    def __init__(self, service_name, service_path, apikey, timestamp,
                 **kwargs, ):
        self.service = service_name
        self.service_path = service_path
        self.apikey = apikey
        self.timestamp = timestamp
        self.__attr = kwargs.get("attr", [])
        self.__lazy_attr = kwargs.get("lazy_attr", [])
        self.__internal_attr = kwargs.get("internal_attr", [])
        self.__commands = kwargs.get("commands", [])
        self.__static_attr = kwargs.get("static_attr", [])

    def __repr__(self):
        """
        Function returns a representation of the object (its data) as a string.
        :return:
        """
        return str((vars(self)))

    def add_lazy(self, attribute):
        self.__lazy_attr.append(attribute)

    def add_active(self, attribute):
        self.__attr.append(attribute)

    def add_static(self, attribute):
        self.__static_attr.append(attribute)

    def add_command(self, attribute):
        self.__commands.append(attribute)

    def add_internal(self, attribute):
        self.__internal_attr.append(attribute)

    def get_json(self):
        return json.dumps(vars(self), indent=4)

