"""
Helper functions for HTTP requests
"""
import logging
from pydantic import BaseModel, AnyHttpUrl


log = logging.getLogger(__name__)

class UrlValidator(BaseModel):
    """
    Validator model for URLs
    """
    url: AnyHttpUrl


def validate_url(url):
    """
    Function checks whether the host has "http" added in case of http as protocol.
    :param url: the url for the host / port
    :return: url - if necessary updated
    """
    UrlValidator(url=url)
