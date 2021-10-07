"""
created Sep 21 2021

@author Thomas Storek

Shared models that are used by multiple submodules
"""
from aenum import Enum
from pydantic import AnyHttpUrl, BaseModel, Field, validator, root_validator
from typing import Union, Optional, Pattern

from filip.utils.simple_ql import QueryString, QueryStatement
from filip.utils.validators import validate_http_url


class Http(BaseModel):
    """
    Model for notification and registrations sent or retrieved via HTTP
    """
    url: Union[AnyHttpUrl, str] = Field(
        description="URL referencing the service to be invoked when a "
                    "notification is generated. An NGSIv2 compliant server "
                    "must support the http URL schema. Other schemas could "
                    "also be supported."
    )

    @validator('url', allow_reuse=True)
    def check_url(cls, value):
        return validate_http_url(url=value)


class EntityPattern(BaseModel):
    """
    Entity pattern used to create subscriptions or registrations
    """
    id: Optional[str] = Field(regex=r"\w")
    idPattern: Optional[Pattern]
    type: Optional[str] = Field(regex=r'\w')
    typePattern: Optional[Pattern]

    @root_validator()
    def validate_conditions(cls, values):
        assert ((values['id'] and not values['idPattern']) or
                (not values['id'] and values['idPattern'])), \
            "Both cannot be used at the same time, but one of 'id' or " \
            "'idPattern must' be present."
        if values['type'] or values.get('typePattern', None):
            assert ((values['type'] and not values['typePattern']) or
                    (not values['id'] and values['typePattern'])), \
                "Type or pattern of the affected entities. " \
                "Both cannot be used at the same time."
        return values


class Status(str, Enum):
    """
    Current status of a subscription or registrations
    """
    _init_ = 'value __doc__'

    ACTIVE = "active", "for active subscriptions"
    INACTIVE = "inactive", "for inactive subscriptions"
    FAILED = "failed", "for failed subscription"
    EXPIRED = "expired", "for expired subscription"


class Expression(BaseModel):
    """
    By means of a filtering expression, allows to express what is the scope
    of the data provided.
    https://telefonicaid.github.io/fiware-orion/api/v2/stable
    """
    q: Optional[Union[str, QueryString]] = Field(
        default=None,
        title='Simple Query Language: filter',
        description='If filtering by attribute value (i.e. the expression is '
                    'used in a q query), the rest of tokens (if present) '
                    'represent the path to a sub-property of the target NGSI '
                    'attribute value (which should be a JSON object). Such '
                    'sub-property is defined as the target property.'
    )
    mq: Optional[Union[str, QueryString]] = Field(
        default=None,
        title='Simple Query Language: metadata filters',
        description='If filtering by metadata (i.e. the expression is used in '
                    'a mq query), the second token represents a metadata name '
                    'associated to the target NGSI attribute, target '
                    'metadata, and the rest of tokens (if present) represent '
                    'the path to a sub-property of the target metadata value '
                    '(which should be a JSON object). Such sub-property is '
                    'defined as the target property. '
    )
    georel: Optional[Union[str, QueryString]] = Field(
        default=None,
        title='Metadata filters',
        description='Any of the geographical relationships as specified by '
                    'the Geoqueries section of this specification.'
    )
    geometry: Optional[Union[str, QueryString]] = Field(
        default=None,
        title='Metadata filters',
        description='Any of the supported geometries as specified by the '
                    'Geoqueries section of this specification.'
    )
    coords: Optional[Union[str, QueryString]] = Field(
        default=None,
        title='Metadata filters',
        description='String representation of coordinates as specified by the '
                    'Geoqueries section of the specification.'
    )

    @validator('q', 'mq')
    def validate_expressions(cls, v):
        if isinstance(v, str):
            return QueryString.parse_str(v)

    class Config:
        """
        Pydantic config
        """
        json_encoders = {QueryString: lambda v: v.to_str(),
                         QueryStatement: lambda v: v.to_str()}


class AttrsFormat(str, Enum):
    """
    Allowed options for attribute formats
    """
    _init_ = 'value __doc__'

    NORMALIZED = "normalized", "Normalized message representation"
    KEY_VALUES = "keyValues", "Key value message representation." \
                              "This mode represents the entity " \
                              "attributes by their values only, leaving out " \
                              "the information about type and metadata. " \
                              "See example below." \
                              "Example: " \
                              "{" \
                              "  'id': 'R12345'," \
                              "  'type': 'Room'," \
                              "  'temperature': 22" \
                              "}"
    VALUES = "values", "Key value message representation. " \
                       "This mode represents the entity as an array of " \
                       "attribute values. Information about id and type is " \
                       "left out. See example below. The order of the " \
                       "attributes in the array is specified by the attrs " \
                       "URI param (e.g. attrs=branch,colour,engine). " \
                       "If attrs is not used, the order is arbitrary. " \
                       "Example:" \
                       "[ 'Ford', 'black', 78.3 ]"