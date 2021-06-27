"""
Helper functions to prohibit boiler plate code
"""
from typing import Dict, Union
from pydantic import BaseModel, AnyHttpUrl


class UrlValidator(BaseModel):
    """
    Validator model for URLs
    """
    url: AnyHttpUrl


def validate_url(url: Union[AnyHttpUrl, str]) -> None:
    """
    Function checks whether the host has "http" added in case of http as
    protocol.
    Args:
        url (Union[AnyHttpUrl, str]): the url for the host / port

    Returns:
        None
    """
    UrlValidator(url=url)
