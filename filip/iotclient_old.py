import csv
import json
import os
import random
import string

import requests

ORION_URL = os.getenv("ORION_URL", "http://localhost:1026/")
IOTA_URL = os.getenv("IOTA_URL", "http://localhost:4041/")
FIWARE_SERVICE = os.getenv("FIWARE_SERVICE", "default")
FIWARE_SERVICE_PATH = os.getenv("FIWARE_SERVICE_PATH", "/")


class Device:
    """
    Represents all necessary information for device registration with an
    Fiware IoT Agent.

    :ivar device_id: Device ID that will be used to identify the device (mandatory).
    :ivar service: Name of the service the device belongs to (will be used in the filip-service header).
    :ivar service_path: Name of the subservice the device belongs to (used in the filip-servicepath header).
    :ivar entity_name: Name of the entity representing the device in the Context Broker.
    :ivar timezone: Time zone of the sensor if it has any.
    :ivar endpoint: Endpoint where the device is going to receive commands, if any.
    :ivar protocol: Name of the device protocol, for its use with an IoT Manager.
    :ivar transport: Name of the device transport protocol, for the IoT Agents with multiple transport protocols.
    :ivar attributes: List of active attributes of the device.
    :ivar lazy: List of lazy attributes of the device.
    :ivar commands: List of commands of the device
    :ivar static_attributes: List of static attributes to append to the entity.
    All the updateContext requests to the CB will have this set of attributes appended.
    """
    def __init__(self, device_id: str, entity_name: str, entity_type: str,
                 **kwargs):
        self.device_id = device_id
        self.service = kwargs.get("service", FIWARE_SERVICE)
        self.service_path = kwargs.get("service_path", FIWARE_SERVICE_PATH)
        self.entity_name = entity_name
        self.entity_type = entity_type
        self.timezone = kwargs.get("timezone")
        self.endpoint = kwargs.get("endpoint")
        self.protocol = kwargs.get("protocol")
        self.transport = kwargs.get("transport")
        self.attributes = kwargs.get("attributes", [])
        self.lazy = kwargs.get("lazy", [])
        self.commands = kwargs.get("commands", [])
        self.static_attributes = kwargs.get("static_attributes", [])

    def add_attribute(self, name, type, object_id: str = None, attr_type='active'):
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
            print("[WARN] Attribute type unknown: \"{}\"".format(attr_type))

def provision_devices(devices: [Device]):
    """
    Register a list of devices with the IoTA.
    :param devices: List of devices
    """
    # Sort based on service and servicepath
    devices_per_service = {}
    for device in devices:
        devices_per_service.setdefault(device.service, {})\
            .setdefault(device.service_path, []).append(device)

    for service, service_paths in devices_per_service.items():
        for service_path, device_list in service_paths.items():
            provision_req = requests.post(IOTA_URL+"iot/devices",
                                          headers=_get_header(service, service_path),
                                          data=json.dumps([d.__dict__ for d in device_list]))
            if provision_req.status_code != 200:
                print("[WARN] Provision request failed. Service: {}, Service-Path: {}, devices: {}"
                      .format(service, service_path, len(device_list)))
            else:
                print("[INFO] Provisioned {} devices under service \"{}\" and service-path \"{}\""
                      .format(len(device_list), service, service_path))