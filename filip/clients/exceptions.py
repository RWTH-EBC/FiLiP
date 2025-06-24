"""
Module for client specific exceptions
"""
import requests.models
from requests import RequestException


class BaseHttpClientException(RequestException):
    """
    Base exception class for all HTTP clients. The response of a request will be available in the exception.

    Args:
        message (str): Error message
        response (Response): Response object
    """
    def __init__(self, message: str, response: requests.models.Response):
        super().__init__(message)
        self.response = response
