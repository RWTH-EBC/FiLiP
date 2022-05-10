"""
Helper functions to handle the devices related with the IoT Agent
"""
from typing import List
from filip.models.ngsi_v2.iot import Device


def filter_device_list(devices: List[Device],
                       entity_name: List[str] = None,
                       entity_type: List[str] = None,
                       device_id: List[str] =None) -> List[Device]:
    """
    Filter the given device list based on conditions

    Args:
        devices: device list that need to be filtered
        entity_name: A list of entity_name (e.g. entity_id) as filter condition
        entity_type: A list of entity_type as filter condition
        device_id: A list of device_id as filter condition

    Returns:

    """
    if entity_name:
        devices = [device for device in devices if device.entity_name in entity_name]
    if entity_type:
        devices = [device for device in devices if device.entity_type in entity_type]
    if device_id:
        devices = [device for device in devices if device.device_id in device_id]
    return devices
