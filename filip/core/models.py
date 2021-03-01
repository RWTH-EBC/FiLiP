from aenum import Enum
from typing import ClassVar
from pydantic import BaseModel, Field, validator, BaseConfig
#from utils.unitcodes import units


class NgsiVersion(str, Enum):
    v2 = "v2"
    ld = "ld"


class DataTypes(str, Enum):
    """
    When possible reuse schema.org data types
    (Text, Number, DateTime, StructuredValue, etc.).
    Remember that null is not allowed in NGSI-LD and
    therefore should be avoided as a value.

    https://schema.org/DataType
    """
    _init_ = 'value __doc__'

    BOOLEAN = "Boolean", "True or False."
    DATE = "Date", "A date value in ISO 8601 date format."
    DATETIME = "DateTime", "A combination of date and time of day in the form " \
                           "[-]CCYY-MM-DDThh:mm:ss[Z|(+|-)hh:mm] " \
                           "(see Chapter 5.4 of ISO 8601)."
    NUMBER = "Number", "Use values from 0123456789 (Unicode 'DIGIT ZERO' " \
                       "(U+0030) to 'DIGIT NINE' (U+0039)) rather than " \
                       "superficially similiar Unicode symbols. Use '.' " \
                       "(Unicode 'FULL STOP' (U+002E)) rather than ',' to " \
                       "indicate a decimal point. Avoid using these symbols " \
                       "as a readability separator."
    TEXT = "Text", "https://schema.org/Text"
    TIME = "Time", "A point in time recurring on multiple days in the form " \
                   "hh:mm:ss[Z|(+|-)hh:mm] (see XML schema for details)."
    RELATIONSHIP = "Relationship", "Reference to another context entity"


class FiwareHeader(BaseModel):
    """
    Define entity service paths which are supported by the NGSI
    Context Brokers to support hierarchical scopes:
    https://fiware-orion.readthedocs.io/en/master/user/service_path/index.html
    """
    service: str = Field(
        alias="fiware-service",
        default="",
        max_length=50,
        description="Fiware service_group used for multitancy",
        regex="\w*$"
    )
    service_path: str = Field(
        alias="fiware-servicepath",
        default="/",
        description="Fiware service_group path",
        max_length = 51,
        regex="^\/+[\w\/]*$"
    )

    class Config(BaseConfig):
        allow_population_by_field_name = True


#class UnitCode(BaseModel):
#    """
#    Fiware recommends unit codes for meta data. This class helps to validate
#    the codes.
#    """
#    type:   ClassVar[str] = "Text"
#    value:  str = Field(
#        title="unit code",
#        description="Code of the measured quantity")
#
#    @validator('value')
#    def validate_code(cls, v):
#        units.get_unit(code=v)
#        return v


