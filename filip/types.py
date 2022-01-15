"""
Variable types and classes used for better validation
"""
from pydantic import AnyUrl


class AnyMqttUrl(AnyUrl):
    """
    Url used for MQTT communication
    """
    allowed_schemes = {'mqtt'}
