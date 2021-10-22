"""
Helper functions to prohibit boiler plate code
"""
import logging
from typing import Union, Dict, Any, List
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
    Returns:
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
    Function that checks whether a value does not contain in any of its
    string parts ' or ".
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
        value = [value]

    for v in value:
        if isinstance(v, Dict):
            for key, dict_value in v.items():
                validate_escape_character_free(dict_value)
                # it seems Fiware has no problem if the keys contain ' or "
                # validate_escape_character_free(key)
        elif isinstance(v, List):
            for inner_list in v:
                validate_escape_character_free(inner_list)
        else:
            # if a value here is not a string, it will also not contain ' or "
            v = str(v)
            if '"' in v:
                raise ValueError(f"The value {v} contains "
                                  f"the forbidden char \"")
            if "'" in v:
                raise ValueError(f"The value {v} contains "
                                  f"the forbidden char '")
    return value