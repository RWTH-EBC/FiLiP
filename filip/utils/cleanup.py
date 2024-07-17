"""
Functions to clean up a tenant within a fiware based platform.
"""
import warnings
from functools import wraps

from pydantic import AnyHttpUrl, AnyUrl
from requests import RequestException
from typing import Callable, List, Union
from filip.models import FiwareHeader
from filip.clients.ngsi_v2 import \
    ContextBrokerClient, \
    IoTAClient, \
    QuantumLeapClient


def clear_context_broker(url: str,
                         fiware_header: FiwareHeader,
                         clear_registrations: bool = False,
                         cb_client: ContextBrokerClient = None
                         ):
    """
    Function deletes all entities, registrations and subscriptions for a
    given fiware header. To use TLS connection you need to provide the cb_client parameter
    as an argument with the Session object including the certificate and private key.

    Note:
        Always clear the devices first because the IoT-Agent will otherwise
        through errors if it cannot find its registration anymore.

    Args:
        url: Url of the context broker service
        fiware_header: header of the tenant
        cb_client: enables TLS communication if created with Session object, only needed
                    for self-signed certificates
        clear_registrations: Determines whether registrations should be deleted.
                             If registrations are deleted while devices with commands
                             still exist, these devices become unreachable.
                             Only set to true once such devices are cleared.
    Returns:
        None
    """
    assert url or cb_client, "Either url or client object must be given"
    # create client
    if cb_client is None:
        client = ContextBrokerClient(url=url, fiware_header=fiware_header)
    else:
        client = cb_client

    # clean entities
    client.delete_entities(entities=client.get_entity_list())

    # clear subscriptions
    for sub in client.get_subscription_list():
        client.delete_subscription(subscription_id=sub.id)
    assert len(client.get_subscription_list()) == 0

    # clear registrations
    if clear_registrations:
        for reg in client.get_registration_list():
            client.delete_registration(registration_id=reg.id)
        assert len(client.get_registration_list()) == 0


def clear_iot_agent(url: Union[str, AnyHttpUrl] = None,
                    fiware_header: FiwareHeader = None,
                    iota_client: IoTAClient = None):
    """
    Function deletes all device groups and devices for a
    given fiware header. To use TLS connection you need to provide the iota_client parameter
    as an argument with the Session object including the certificate and private key.

    Args:
        url: Url of the iot agent service
        fiware_header: header of the tenant
        iota_client: enables TLS communication if created with Session object, only needed for self-signed certificates

    Returns:
        None
    """
    assert url or iota_client, "Either url or client object must be given"
    # create client
    if iota_client is None:
        client = IoTAClient(url=url, fiware_header=fiware_header)
    else:
        client = iota_client

    # clear registrations
    for device in client.get_device_list():
        client.delete_device(device_id=device.device_id)
    assert len(client.get_device_list()) == 0

    # clear groups
    for group in client.get_group_list():
        client.delete_group(resource=group.resource,
                            apikey=group.apikey)
    assert len(client.get_group_list()) == 0


def clear_quantumleap(url: str = None,
                      fiware_header: FiwareHeader = None,
                      ql_client: QuantumLeapClient = None):
    """
    Function deletes all data for a given fiware header. To use TLS connection you need to provide the ql_client parameter
    as an argument with the Session object including the certificate and private key.
    Args:
        url: Url of the quantumleap service
        fiware_header: header of the tenant
        ql_client: enables TLS communication if created with Session object, only needed for self-signed certificates

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
    assert url or ql_client, "Either url or client object must be given"
    # create client
    if ql_client is None:
        client = QuantumLeapClient(url=url, fiware_header=fiware_header)
    else:
        client = ql_client

    # clear data
    entities = []
    try:
        entities = client.get_entities()
    except RequestException as err:
        handle_emtpy_db_exception(err)

    # will be executed for all found entities
    for entity in entities:
        client.delete_entity(entity_id=entity.entityId,
                             entity_type=entity.entityType)


def clear_all(*,
              fiware_header: FiwareHeader = None,
              cb_url: str = None,
              iota_url: Union[str, List[str]] = None,
              ql_url: str = None,
              cb_client: ContextBrokerClient = None,
              iota_client: IoTAClient = None,
              ql_client: QuantumLeapClient = None):
    """
    Clears all services that a url is provided for

    Args:
        fiware_header:
        cb_url: url of the context broker service
        iota_url: url of the IoT-Agent service
        ql_url: url of the QuantumLeap service
        cb_client: enables TLS communication if created with Session object, only needed
         for self-signed certificates
        iota_client: enables TLS communication if created with Session object, only needed
         for self-signed certificates
        ql_client: enables TLS communication if created with Session object, only needed
         for self-signed certificates

    Returns:
        None
    """
    if iota_url is not None or iota_client is not None:
        if iota_url is None:
            # loop client
            if isinstance(iota_client, IoTAClient):
                iota_client = [iota_client]
            for client in iota_client:
                clear_iot_agent(fiware_header=fiware_header, iota_client=client)
        else:
            if isinstance(iota_url, (str, AnyUrl)):
                iota_url = [iota_url]
            for url in iota_url:
                clear_iot_agent(url=url, fiware_header=fiware_header)

    if cb_url is not None or cb_client is not None:
        clear_context_broker(url=cb_url, fiware_header=fiware_header, cb_client=cb_client)

    if ql_url is not None or ql_client is not None:
        clear_quantumleap(url=ql_url, fiware_header=fiware_header, ql_client=ql_client)


def clean_test(*,
               fiware_service: str,
               fiware_servicepath: str,
               cb_url: str = None,
               iota_url: Union[str, List[str]] = None,
               ql_url: str = None,
               cb_client: ContextBrokerClient = None,
               iota_client: IoTAClient = None,
               ql_client: QuantumLeapClient = None) -> Callable:
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
        cb_client: enables TLS communication if created with Session object, only needed for self-signed certificates
        iota_client: enables TLS communication if created with Session object, only needed for self-signed certificates
        ql_client: enables TLS communication if created with Session object, only needed for self-signed certificates

    Returns:
        Decorator for clean tests
    """
    fiware_header = FiwareHeader(service=fiware_service,
                                 service_path=fiware_servicepath)
    clear_all(fiware_header=fiware_header,
              cb_url=cb_url,
              iota_url=iota_url,
              ql_url=ql_url,
              cb_client=cb_client,
              iota_client=iota_client,
              ql_client=ql_client)
    # Inner decorator function
    def decorator(func):
        #  Wrapper function for the decorated function
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    clear_all(fiware_header=fiware_header,
              cb_url=cb_url,
              iota_url=iota_url,
              ql_url=ql_url,
              cb_client=cb_client,
              iota_client=iota_client,
              ql_client=ql_client)

    return decorator