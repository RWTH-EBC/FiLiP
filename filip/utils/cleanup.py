"""
Functions to clean up a tenant within a fiware based platform.

created Oct 08, 2021

@author Thomas Storek
"""

from requests import RequestException
from filip.models import FiwareHeader
from filip.clients.ngsi_v2 import ContextBrokerClient, IoTAClient, QuantumLeapClient


def clear_cb(url: str, fiware_header: FiwareHeader):
    """
    Function deletes all entities, registrations and subscriptions for a
    given fiware header

    Args:
        url: Url of the context broker service
        fiware_header: header of the tenant

    Returns:
        None
    """
    # create client
    client = ContextBrokerClient(url=url, fiware_header=fiware_header)

    # clear entities
    entities = client.get_entity_list()
    if entities:
        client.update(entities=entities, action_type='delete')

    # clear subscriptions
    for sub in client.get_subscription_list():
        client.delete_subscription(subscription_id=sub.id)

    # clear registrations
    for reg in client.get_registration_list():
        client.delete_registration(registration_id=reg.id)


def clear_iota(url: str, fiware_header: FiwareHeader):
    """
    Function deletes all device groups and devices for a
    given fiware header

    Args:
        url: Url of the context broker service
        fiware_header: header of the tenant

    Returns:
        None
    """
    # create client
    client = IoTAClient(url=url, fiware_header=fiware_header)

    # clear groups
    for group in client.get_group_list():
        client.delete_group(resource=group.resource,
                            apikey=group.apikey)

    # clear registrations
    for device in client.get_device_list():
        client.delete_device(device_id=device.device_id)


def clear_ql(url: str, fiware_header: FiwareHeader):
    """
    Function deletes all data for a given fiware header
    Args:
        url: Url of the quantumleap service
        fiware_header: header of the tenant

    Returns:
        None
    """
    # create client
    client = QuantumLeapClient(url=url, fiware_header=fiware_header)

    # clear data
    try:
        entities = client.get_entities()
        for entity in client.get_entities():
            client.delete_entity(entity_id=entity.entityId,
                                 entity_type=entity.entityType)
    except RequestException as err:
        if err.response.status_code == 404:
            try:
                err.response.json()['error'] == 'Not Found'
            except KeyError:
                raise
        else:
            raise



def clear_all(*,
              fiware_header: FiwareHeader,
              cb_url: str = None,
              iota_url: str = None,
              ql_url: str =  None):
    """
    Clears all services that a url is provided for
    Args:
        fiware_header:
        cb_url: url of the context broker service
        iota_url: url of the IoT-Agent service
        ql_url: url of the QuantumLeap service

    Returns:

    """
    if cb_url is not None:
        clear_cb(url=cb_url, fiware_header=fiware_header)
    if iota_url is not None:
        clear_iota(url=iota_url, fiware_header=fiware_header)
    if ql_url is not None:
        clear_ql(url=ql_url, fiware_header=fiware_header)
