"""
Variable types and classes used for better validation
"""
from pydantic import UrlConstraints
from typing_extensions import Annotated
from pydantic_core import Url

AnyMqttUrl = Annotated[Url, UrlConstraints(allowed_schemes=['mqtt'])]
