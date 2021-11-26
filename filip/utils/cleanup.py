"""
Functions to clean up a tenant within a fiware based platform.

created Oct 08, 2021

@author Thomas Storek
"""
import time

from requests import RequestException
from typing import Callable, List, Union
from filip.models import FiwareHeader
from filip.clients.ngsi_v2 import \
    ContextBrokerClient, \
    IoTAClient, \
    QuantumLeapClient


def clear_context_broker(url: str, fiware_header: FiwareHeader):
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
    # clean entities
    client.delete_entities(entities=client.get_entity_list())

    # clear subscriptions
    for sub in client.get_subscription_list():
        client.delete_subscription(subscription_id=sub.id)
    assert len(client.get_subscription_list()) == 0

    # clear registrations
    for reg in client.get_registration_list():
        client.delete_registration(registration_id=reg.id)
    assert len(client.get_registration_list()) == 0


def clear_iot_agent(url: str, fiware_header: FiwareHeader):
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

    # clear registrations
    for device in client.get_device_list():
        client.delete_device(device_id=device.device_id)
    assert len(client.get_device_list()) == 0

    # clear groups
    for group in client.get_group_list():
        client.delete_group(resource=group.resource,
                            apikey=group.apikey)
    assert len(client.get_group_list()) == 0


def clear_quantumleap(url: str, fiware_header: FiwareHeader):
    """
    Function deletes all data for a given fiware header
    Args:
        url: Url of the quantumleap service
        fiware_header: header of the tenant

    Returns:
        None
    """
    def handle_emtpy_db_exception(err: RequestException) -> None:
        """
        When the database is empty for request quantumleap returns a 404
        error with a error message. This will be handled here
        evaluating the empty database error as 'OK'

        Args:
            err: exception raised by delete function
        """
        if err.response.status_code == 404 \
                and err.response.json().get('error', None) == 'Not Found':
            pass
        else:
            raise
    # create client
    client = QuantumLeapClient(url=url, fiware_header=fiware_header)

    # clear data
    # entities = []
    # try:
    #     entities = client.get_entities()
    # except RequestException as err:
    #     handle_emtpy_db_exception(err)
    #
    # # will be executed for all found entities
    # for entity in entities:
    #     try:
    #         client.delete_entity(entity_id=entity.entityId,
    #                              entity_type=entity.entityType)
    #     except RequestException as err:
    #         handle_emtpy_db_exception(err)

    # test if all entities are deleted. If the client is not empty the assert
    # will fail. Else the request will throw an error, the error handler
    # checks if the error, is due to an empty list else it will raise an
    # error itself

    counter = 0
    try:
        entities = client.get_entities()
        while len(entities) > 0 and counter < 10:
            print(f"-----{counter}----------{len(client.get_entities())}")
            print(len(client.get_entities()))
            for entity in entities:
                try:
                    client.delete_entity(entity_id=entity.entityId,
                                         entity_type=entity.entityType)
                except RequestException as err:
                    handle_emtpy_db_exception(err)
            entities = client.get_entities()
            counter += 1
            time.sleep(counter/10)
    except RequestException as err:
        handle_emtpy_db_exception(err)


    try:
        assert len(client.get_entities()) == 0
    except RequestException as err:
        handle_emtpy_db_exception(err)


def clear_all(*,
              fiware_header: FiwareHeader,
              cb_url: str = None,
              iota_url: Union[str, List[str]] = None,
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
        if isinstance(iota_url, str):
            iota_url = [iota_url]
        for url in iota_url:
            clear_iot_agent(url=url, fiware_header=fiware_header)
    if cb_url is not None:
        clear_context_broker(url=cb_url, fiware_header=fiware_header)
    if ql_url is not None:
        clear_quantumleap(url=ql_url, fiware_header=fiware_header)

def clean_test(*,
               fiware_service: str,
               fiware_servicepath: str,
               cb_url: str = None,
               iota_url: Union[str, List[str]] = None,
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
    # Inner decorator function
    def decorator(func):
        #  Wrapper function for the decorated function
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    clear_all(fiware_header=fiware_header,
              cb_url=cb_url,
              iota_url=iota_url,
              ql_url=ql_url)

    return decorator
