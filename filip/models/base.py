"""
Shared data models
"""

from aenum import Enum
from pydantic import ConfigDict, BaseModel, Field, field_validator

from filip.utils.validators import (validate_fiware_service_path,
                                    validate_fiware_service)


class NgsiVersion(str, Enum):
    """
    Version of NGSI-Sepcifications that should be used within the target system.
    Note:
        Currently, the library only supports functionality for NGSI-v2
    """

    v2 = "v2"
    ld = "ld"


class DataType(str, Enum):
    """
    When possible reuse schema.org data types
    (Text, Number, DateTime, StructuredValue, etc.).
    Remember that null is not allowed in NGSI-LD and
    therefore should be avoided as a value.

    https://schema.org/DataType
    """

    _init_ = "value __doc__"

    BOOLEAN = "Boolean", "True or False."
    DATE = "Date", "A date value in ISO 8601 date format."
    DATETIME = (
        "DateTime",
        "A combination of date and time of day in the form "
        "[-]CCYY-MM-DDThh:mm:ss[Z|(+|-)hh:mm] "
        "(see Chapter 5.4 of ISO 8601).",
    )
    NUMBER = (
        "Number",
        "Use values from 0123456789 (Unicode 'DIGIT ZERO' "
        "(U+0030) to 'DIGIT NINE' (U+0039)) rather than "
        "superficially similar Unicode symbols. Use '.' "
        "(Unicode 'FULL STOP' (U+002E)) rather than ',' to "
        "indicate a decimal point. Avoid using these symbols "
        "as a readability separator.",
    )
    INTEGER = "Integer", "Integer number"
    FLOAT = "Float", "Floating number. Please check 'DataType.Number'"
    TEXT = "Text", "https://schema.org/Text"
    TIME = (
        "Time",
        "A point in time recurring on multiple days in the form "
        "hh:mm:ss[Z|(+|-)hh:mm] (see XML schema for details).",
    )
    RELATIONSHIP = "Relationship", "Reference to another context entity"
    STRUCTUREDVALUE = "StructuredValue", ("Structured datatype must be "
                                          "serializable")
    ARRAY = "Array", "Array of the types above"
    COMMAND = "command", "A command for IoT Devices"
    COMMAND_RESULT = (
        "commandResult",
        "An entity containing a command, "
        "contains an autogenerated attribute"
        "of this type",
    )
    COMMAND_STATUS = (
        "commandStatus",
        "An entity containing a command, "
        "contains an autogenerated attribute "
        "of this type",
    )


class PaginationMethod(str, Enum):
    """
    Options for the internal pagination methods
    """

    GET = "GET"
    POST = "POST"


class FiwareHeader(BaseModel):
    """
    Define entity service paths which are supported by the NGSI
    Context Brokers to support hierarchical scopes:
    https://fiware-orion.readthedocs.io/en/master/user/service_path/index.html
    """

    model_config = ConfigDict(populate_by_name=True, validate_assignment=True)

    service: str = Field(
        alias="fiware-service",
        default="",
        max_length=50,
        description="Fiware service used for multi-tenancy",
        pattern=r"\w*$",
    )
    service_path: str = Field(
        alias="fiware-servicepath",
        default="",
        description="Fiware service path",
        max_length=51,
    )
    valid_service = field_validator("service")(validate_fiware_service)
    valid_service_path = field_validator("service_path")(validate_fiware_service_path)


class FiwareHeaderSecure(FiwareHeader):
    """
    Defines entity service paths and an authorization via Bearer-Token which are
    supported by the NGSI
    Context Brokers to support hierarchical scopes:
    https://fiware-orion.readthedocs.io/en/master/user/service_path/index.html
    """

    authorization: str = Field(
        alias="authorization",
        default="",
        max_length=3000,
        description="authorization key",
        pattern=r".*"
    )


class LogLevel(str, Enum):
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
    NOTSET = "NOTSET"

    @classmethod
    def _missing_name_(cls, name):
        """
        Class method to realize case-insensitive args

        Args:
            name: missing argument

        Returns:
            valid member of enum
        """
        for member in cls:
            if member.value.casefold() == name.casefold():
                return member
