"""
Filter functions to keep client code clean and easy to use.
"""
from typing import List, Union
from filip.clients.ngsi_v2 import ContextBrokerClient
from filip.models import FiwareHeader
from filip.models.ngsi_v2.iot import Device
from filip.models.ngsi_v2.subscriptions import Subscription


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


def filter_subscriptions_by_entity(entity_id: str,
                                   entity_type: str,
                                   url: str = None,
                                   fiware_header: FiwareHeader = None,
                                   subscriptions: List[Subscription] = None,
                                   ) -> List[Subscription]:
    """
    Function that filters subscriptions based on the entity id or id pattern
    and entity type or type pattern. The function can be used in two ways,
    wither pass list of subscriptions to filter based on entity or directly pass
    client information to filter subscriptions in a single request.

    Args:
        entity_id: Id of the entity to be matched
        entity_type: Type of the entity to be matched
        url: Url of the context broker service
        fiware_header: Fiware header of the tenant
        subscriptions: List of subscriptions to filter
    Returns:
        list of subscriptions by entity
    """
    if not subscriptions:
        client = ContextBrokerClient(url=url, fiware_header=fiware_header)
        subscriptions = client.get_subscription_list()
    filtered_subscriptions = []
    for subscription in subscriptions:
        for entity in subscription.subject.entities:
            if entity.id == entity_id or (
                    entity.idPattern is not None
                    and entity.idPattern.match(entity_id)):
                if entity.type == entity_type or \
                        (entity.typePattern is not None and
                         entity.typePattern.match(entity_type)):
                    filtered_subscriptions.append(subscription)
    return filtered_subscriptions

