"""
Helper functions to prohibit boiler plate code
"""
import logging
from typing import Dict, Any, List
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


def validate_escape_character_free(value: Any) -> Any:
    """
    Function that checks whether a value contains a string part that starts
    or end with ' or ".
    the function iterates to break down each complex data-structure to its
    fundamental string parts.
    Each value of a list is examined
    Of dictionaries each value is examined, keys are skipped, as they are ok
    for Fiware
    Args:
        value: the string to check

    Returns:
       validated string
    """

    if not isinstance(value, List):
        values = [value]
    else:
        values = value

    for value in values:
        if isinstance(value, Dict):
            for key, dict_value in value.items():
                validate_escape_character_free(dict_value)
                # it seems Fiware has no problem if the keys contain ' or "
                # validate_escape_character_free(key)
        elif isinstance(value, List):
            for inner_list in value:
                validate_escape_character_free(inner_list)
        else:
            # if a value here is not a string, it will also not contain ' or "
            value = str(value)
            if '"' == value[-1:] or '"' == value[0:1]:
                raise ValueError(f"The value {value} contains "
                                 f"the forbidden char \"")
            if "'" == value[-1:] or "'" == value[0:1]:
                raise ValueError(f"The value {value} contains "
                                 f"the forbidden char '")
    return values
