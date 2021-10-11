"""
Functions to clean up a tenant within a fiware based platform.

created Oct 08, 2021

@author Thomas Storek
"""
from requests import RequestException
from typing import Callable
from filip.models import FiwareHeader
from filip.clients.ngsi_v2 import \
    ContextBrokerClient, \
    IoTAClient, \
    QuantumLeapClient


def clear_cb(url: str, fiware_header: FiwareHeader):
    """
    Function deletes all entities, registrations and subscriptions for a
    given fiware header

    Note:
        Always clear the devices first because the IoT-Agent will otherwise
        through errors if it cannot find its registration anymore.

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
    for entity in client.get_entities():
        try:
            client.delete_entity(entity_id=entity.entityId,
                                 entity_type=entity.entityType)
        except RequestException as err:
            if err.response.status_code == 404:
                try:
                    if not err.response.json()['error'] == 'Not Found':
                        raise
                except KeyError:
                    raise
            else:
                raise


def clear_all(*,
              fiware_header: FiwareHeader,
              cb_url: str = None,
              iota_url: str = None,
              ql_url: str = None):
    """
    Clears all services that a url is provided for

    Args:
        fiware_header:
        cb_url: url of the context broker service
        iota_url: url of the IoT-Agent service
        ql_url: url of the QuantumLeap service

    Returns:
        None
    """
    if iota_url is not None:
        clear_iota(url=iota_url, fiware_header=fiware_header)
    if cb_url is not None:
        clear_cb(url=cb_url, fiware_header=fiware_header)
    if ql_url is not None:
        clear_ql(url=ql_url, fiware_header=fiware_header)


def clean_test(*,
               fiware_service: str,
               fiware_servicepath: str,
               cb_url: str = None,
               iota_url: str = None,
               ql_url: str = None) -> Callable:
    """
    Decorator to clean up the server before and after the test

    Note:
        This does not substitute a proper TearDown method, because a failing
        test will not execute the clean up after the error. Since this would
        mean an unnecessary error handling. We actually want a test to fail
        with proper messages.

    Args:
        fiware_service: tenant
        fiware_servicepath: tenant path
        cb_url: url of context broker service
        iota_url: url of IoT-Agent service
        ql_url: url of quantumleap service

    Returns:
        Decorator for clean tests
    """
    fiware_header = FiwareHeader(service=fiware_service,
                                 service_path=fiware_servicepath)
    clear_all(fiware_header=fiware_header,
              cb_url=cb_url,
              iota_url=iota_url,
              ql_url=ql_url)

    def decorator(func):
        """
        Inner decorator function

        Args:
            func: func to be wrapped

        Returns:
            Wrapper with wrapped function
        """
        def wrapper(*args, **kwargs):
            """
            Wrapper function for the decorated function

            Args:
                *args: any args of the wrapped function
                **kwargs: any kwrags of the wrapped function

            Returns:
                Wrapped function
            """

            return func(*args, **kwargs)
        return wrapper

    clear_all(fiware_header=fiware_header,
              cb_url=cb_url,
              iota_url=iota_url,
              ql_url=ql_url)

    return decorator
