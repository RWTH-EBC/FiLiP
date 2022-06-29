"""
Helper functions to handle the devices related with the IoT Agent
"""
from typing import List, Union
from filip.models.ngsi_v2.iot import Device


def filter_device_list(devices: List[Device],
                       device_ids: Union[str, List[str]] = None,
                       entity_names: Union[str, List[str]] = None,
                       entity_types: Union[str, List[str]] = None) -> List[Device]:
    """
    Filter the given device list based on conditions

    Args:
        devices: device list that need to be filtered
        device_ids: A list of device_id as filter condition
        entity_names: A list of entity_name (e.g. entity_id) as filter condition.
        entity_types: A list of entity_type as filter condition

    Returns:
        List of matching devices
    """
    if device_ids:
        if isinstance(device_ids, (list, str)):
            if isinstance(device_ids, str):
                device_ids = [device_ids]
            devices = [device for device in devices if device.device_id in device_ids]
        else:
            raise TypeError('device_ids must be a string or a list of strings!')

    if entity_names:
        if isinstance(entity_names, (list, str)):
            if isinstance(entity_names, str):
                entity_names = [entity_names]
            devices = [device for device in devices if device.entity_name in entity_names]
        else:
            raise TypeError('entity_names must be a string or a list of strings!')

    if entity_types:
        if isinstance(entity_types, (list, str)):
            if isinstance(entity_types, str):
                entity_types = [entity_types]
            devices = [device for device in devices if device.entity_type in entity_types]
        else:
            raise TypeError('entity_types must be a string or a list of strings!')

    return devices
