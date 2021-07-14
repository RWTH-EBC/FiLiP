"""
Helper functions to prohibit boiler plate code
"""
from typing import Union
from pydantic import AnyHttpUrl, validate_arguments


@validate_arguments
def validate_url(url: Union[AnyHttpUrl, str]) -> str:
    """
    Function checks whether the host has "http" added in case of http as
    protocol.
    Args:
        url (Union[AnyHttpUrl, str]): the url for the host / port
    Returns:
        None
    """
    return url
