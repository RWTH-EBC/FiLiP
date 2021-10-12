from enum import Enum

from . import Entity


class DataFieldType(str, Enum):
    command = "command"
    device_attribute = "device_attribute"
    simple = "simple"


class DataProperty(Entity):
    """
    Representation of OWL:DataProperty
    """

    field_type: DataFieldType = DataFieldType.simple
