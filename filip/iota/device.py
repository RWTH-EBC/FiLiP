import json

from filip import config
from filip.iota.device_superclass import Shared

import logging

log = logging.getLogger('iot')


PROTOCOLS = ['IoTA-JSON', 'IoTA-UL']


class Device(Shared):
    """
    Represents all necessary information for device registration with an Fiware IoT Agent.
    :ivar device_id: Device ID that will be used to identify the device (mandatory).
    :ivar service_group: Name of the service_group the device belongs to (will be used in the fiware-service_group header).
    :ivar service_path: Name of the subservice the device belongs to (used in the fiware-servicepath header).
    :ivar entity_name: Name of the entity representing the device in the Context Broker.
    :ivar timezone: Time zone of the sensor if it has any. Default ist UTC/Zulu.
    :ivar timestamp: (optional, boolean): This field indicates if an attribute 'TimeInstant' will be added (true) or not (false).
                    If this field is omitted, the global IotAgent configuration timestamp will be used.
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
    :ivar autoprovision: (optional, boolean): If true, APPEND is used upon measure arrival
        (thus effectively allowing autoprovisioned devices). If false, UPDATE is used open measure arrival (thus effectively avoiding autoprovisioned devices).
        This field is optional, so if it omitted then the global IoTAgent appendModel configuration is used.
        """


    def __init__(self, device_id: str, entity_name: str, entity_type: str, **kwargs):
        super(Device, self).__init__(**kwargs)
        self.device_id = device_id
        self.entity_name = entity_name
        self.entity_type = entity_type
        self.timezone = config.TIMEZONE
        # self.timezone = kwargs.get("timezone", "UTC/Zulu")
        self.timestamp = kwargs.get("timestamp", None)
        self.autoprovision = kwargs.get("autoprovision", None)
        self.endpoint = kwargs.get("endpoint") # necessary for HTTP
        self.protocol = kwargs.get("protocol")
        self.transport = kwargs.get("transport")

    def get_json(self):
        data_dict = json.loads(super().get_json())
        data_dict['device_id'] = self.device_id
        data_dict['entity_name'] = self.entity_name
        data_dict['entity_type'] = self.entity_type
        data_dict['timezone'] = self.timezone
        if self.endpoint:
            data_dict['endpoint'] = self.endpoint
        data_dict['protocol'] = self.protocol
        data_dict['transport'] = self.transport
        if self.autoprovision is not None:
            data_dict['autoprovision'] = self.autoprovision
        return json.dumps(data_dict, indent=4)
