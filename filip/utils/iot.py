"""
Helper functions to handle the devices related with the IoT Agent
"""
import warnings
from typing import List, Union
from filip.models.ngsi_v2.iot import Device
from filip.utils.filter import filter_device_list as filter_device_list_new

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
    warnings.warn("This function has been moved to 'filip.utils.filter' "
                  "and will be removed from this module in future releases!",
                  DeprecationWarning)

    return filter_device_list_new(devices=devices,
                                  device_ids=device_ids,
                                  entity_names=entity_names,
                                  entity_types=entity_types)
