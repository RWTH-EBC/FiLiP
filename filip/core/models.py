from aenum import Enum
from pydantic import BaseModel, Field, validator

class DataType(str, Enum):
    """
    When possible reuse schema.org data types
    (Text, Number, DateTime, StructuredValue, etc.).
    Remember that null is not allowed in NGSI-LD and
    therefore should be avoided as a value.

    https://schema.org/DataType
    """
    _init_ = 'value __doc__'

    Boolean = "Boolean", "True or False."
    Date = "Date", "A date value in ISO 8601 date format."
    DateTime = "DateTime", "A combination of date and time of day in the form " \
                           "[-]CCYY-MM-DDThh:mm:ss[Z|(+|-)hh:mm] " \
                           "(see Chapter 5.4 of ISO 8601)."
    Number = "Number", "Use values from 0123456789 (Unicode 'DIGIT ZERO' " \
                       "(U+0030) to 'DIGIT NINE' (U+0039)) rather than " \
                       "superficially similiar Unicode symbols. Use '.' " \
                       "(Unicode 'FULL STOP' (U+002E)) rather than ',' to " \
                       "indicate a decimal point. Avoid using these symbols " \
                       "as a readability separator."
    Text = "Text", "https://schema.org/Text"
    Time = "Time", "A point in time recurring on multiple days in the form " \
                   "hh:mm:ss[Z|(+|-)hh:mm] (see XML schema for details)."

class FiwareHeader(BaseModel):
    service: str = Field(
        alias="Fiware-Service",
        default="",
        max_length=50,
        description="Fiware service used for multitancy"
    )
    path: str = Field(
        alias="Fiware-ServicePath",
        default="/",
        description="Fiware service path",
        max_length = 51,
    )

    @validator('path')
    def validate_service_path(cls, v):
        assert v.startswith('/'), \
            "Service path must have a trailing slash ('/')"
        return v