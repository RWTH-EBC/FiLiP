import json
import string
import random
import datetime

from filip.iota.device_superclass import Shared

import logging

log = logging.getLogger('iot')


class DeviceGroup(Shared):
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
    :ivar resource: string representing the Soutbound resource that will be used to assign a type to a device
            (e.g. pathname in the soutbound port)
    :ivar apikey: API key string
    :ivar timestamp: Optional flag whether to include TimeInstant wihtin each entity created, as well als
            TimeInstant metadata to each attribute, with the current Timestamp
    :ivar entity_type: Name of the type to assign to the group.
    :ivar trust: Trust token to use for secured access to the Context Broker
    for this type of devices (optional; only needed for secured scenarios).
    :ivar lazy: List of lazy attributes of the device.
    :ivar commands: List of commands of the device
    :ivar attributes: List of active attributes of the device.
    :ivar static_attributes: List of static attributes to append to the entity. All the updateContext requests to the CB will have this set of attributes appended.
    :ivar internal_attributes: Optional section with free format, to allow
    :ivar autoprovsion: (optional, boolean): If true, APPEND is used upon measure arrival (thus effectively allowing autoprovisioned devices). If false, UPDATE is used open measure arrival (thus effectively avoiding autoprovisioned devices). This field is optional, so if it omitted then the global IoTAgent appendModel configuration is used.
    specific IoT Agents to store information along with the devices in the Device Registry.
    """
    def __init__(self, fiware_service ,
                 cb_host: str, **kwargs):
        super(DeviceGroup, self).__init__(service=fiware_service.name,
                                          service_path=fiware_service.path,
                                          **kwargs)
        self.__cbHost = cb_host
        self.__resource = kwargs.get("resource", "/iot/d") #for iot-ul 1.7.0
        # the default must be empty string
        self.autoprovision = kwargs.get("autoprovision", None)
        self.__entity_type = kwargs.get("entity_type", "Thing")
        self.trust = kwargs.get("trust")
        self.devices = []
        self.__agent = kwargs.get("iot-agent", "iota-json")

        # For using the update functionality, the former configuration needs
        # to be stored
        self.__service_last = fiware_service.name
        self.__subservice_last = fiware_service.path
        self.__resource_last = kwargs.get("resource", "/iot/d")
        self.__apikey_last = kwargs.get("apikey", "12345")

    def get_json(self):
        data_dict = json.loads(super().get_json())
        data_dict['cbroker'] = self.__cbHost
        data_dict['entity_type'] = self.__entity_type
        data_dict['resource'] = self.__resource
        if self.autoprovision is not None:
            data_dict['autoprovision'] = self.autoprovision
        return json.dumps(data_dict, indent=4)


    def update(self,**kwargs):
        # For using the update functionality, the former configuration needs
        # to be stored
        # TODO: NOTE: It is not recommenend to change the combination fiware
        #  service structure and apikey --> Delete old and register a new one
        self.__service_last = self.__service
        self.__subservice_last = self.__subservice
        self.__resource_last = self.__resource
        self.__apikey_last = self.__apikey

        # From here on the variables are updated
        self.service = kwargs.get("fiware_service", self.__service)
        self.service_path = kwargs.get("fiware_service_path",
                                       self.__subservice)
        self.__resource = kwargs.get("resource", self.__resource)  # for iot-ul 1.7.0
        # the default must be empty string
        self.apikey = kwargs.get("apikey", self.__apikey)
        self.__entity_type = kwargs.get("entity_type", self.__entity_type)
        # self.trust
        self.__cbHost = kwargs.get("cb_host", self.__cbHost)
        self.__devices = [] # Attribute is not used?
        self.__agent = kwargs.get("iot-agent", self.__agent)

    def get_apikey(self):
        return self.apikey

    def get_resource(self):
        return self.__resource

    def get_apikey_last(self):
        return self.__apikey_last

    def get_resource_last(self):
        return self.__resource_last

    def get_header(self) -> dict:
        return {"fiware-service": self.service,
                "fiware-servicepath": self.service_path
                }

    def get_header_last(self) -> dict:
        return {"fiware-service": self.__service_last,
                "fiware-servicepath": self.__subservice_last
                }

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
                    log.info(f" {datetime.datetime.now()} - Random Key generated: {self.apikey}")
                else:
                    log.info(f" {datetime.datetime.now()} - Default Key will be used: 1234")

            log.info(f" {datetime.datetime.now()} - API-Key check success! {self.apikey}")

        except Exception:
            log.error(f" {datetime.datetime.now()} - API-Key check failed. Please check configuration!")
