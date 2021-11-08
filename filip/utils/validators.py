"""
Helper functions to prohibit boiler plate code
"""
import logging
from pydantic import AnyHttpUrl, validate_arguments
from filip.types import AnyMqttUrl


logger = logging.getLogger(name=__name__)


@validate_arguments
def validate_http_url(url: AnyHttpUrl) -> str:
    """
    Function checks whether the host has "http" added in case of http as
    protocol.

    Args:
        url (AnyHttpUrl): the url for the host / port

    #Returns:
        validated url
    """
    return url

@validate_arguments
def validate_mqtt_url(url: AnyMqttUrl) -> str:
    """
    Function that checks whether a url is valid mqtt endpoint

    Args:
        url: the url for the target endpoint

    Returns:
       validated url
    """
    return url