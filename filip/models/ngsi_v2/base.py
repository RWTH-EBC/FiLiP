"""
created Sep 21 2021

@author Thomas Storek

Shared models that are used by multiple submodules
"""
import copy
import json

from aenum import Enum
from pydantic import AnyHttpUrl, BaseModel, Field, validator, root_validator
from typing import Union, Optional, Pattern, List, Dict, Any, TYPE_CHECKING

from filip.models.base import DataType, FiwareRegex
from filip.models.ngsi_v2.units import validate_unit_data
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


# NGSIv2 entity models
class ContextMetadata(BaseModel):
    """
    Context metadata is used in FIWARE NGSI in several places, one of them being
    an optional part of the attribute value as described above. Similar to
    attributes, each piece of metadata has.

    Note:
         In NGSI it is not foreseen that metadata may contain nested metadata.
    """
    type: Optional[Union[DataType, str]] = Field(
        title="metadata type",
        description="a metadata type, describing the NGSI value type of the "
                    "metadata value Allowed characters "
                    "are the ones in the plain ASCII set, except the following "
                    "ones: control characters, whitespace, &, ?, / and #.",
        max_length=256,
        min_length=1,
        regex=FiwareRegex.standard.value  # Make it FIWARE-Safe
    )
    value: Optional[Any] = Field(
        title="metadata value",
        description="a metadata value containing the actual metadata"
    )

    @validator('value', allow_reuse=True)
    def validate_value(cls, value):
        assert json.dumps(value), "metadata not serializable"
        return value


class NamedContextMetadata(ContextMetadata):
    """
    Model for metadata including a name
    """
    name: str = Field(
        titel="metadata name",
        description="a metadata name, describing the role of the metadata in "
                    "the place where it occurs; for example, the metadata name "
                    "accuracy indicates that the metadata value describes how "
                    "accurate a given attribute value is. Allowed characters "
                    "are the ones in the plain ASCII set, except the following "
                    "ones: control characters, whitespace, &, ?, / and #.",
        max_length=256,
        min_length=1,
        regex=FiwareRegex.standard.value  # Make it FIWARE-Safe
    )

    @root_validator
    def validate_data(cls, values):
        if values.get("name", "").casefold() in ["unit",
                                                 "unittext",
                                                 "unitcode"]:
            values.update(validate_unit_data(values))
        return values

    def to_context_metadata(self):
        return {self.name: ContextMetadata(**self.dict())}


class BaseAttribute(BaseModel):
    """
    Model for an attribute is represented by a JSON object with the following
    syntax:

    The attribute NGSI type is specified by the type property, whose value
    is a string containing the NGSI type.

    The attribute metadata is specified by the metadata property. Its value
    is another JSON object which contains a property per metadata element
    defined (the name of the property is the name of the metadata element).
    Each metadata element, in turn, is represented by a JSON object
    containing the following properties:

    Values of entity attributes. For adding it you need to nest it into a
    dict in order to give it a name.

    Example:

        >>> data = {"type": <...>,
                    "metadata": <...>}
        >>> attr = BaseAttribute(**data)

    """

    type: Union[DataType, str] = Field(
        default=DataType.TEXT,
        description="The attribute type represents the NGSI value type of the "
                    "attribute value. Note that FIWARE NGSI has its own type "
                    "system for attribute values, so NGSI value types are not "
                    "the same as JSON types. Allowed characters "
                    "are the ones in the plain ASCII set, except the following "
                    "ones: control characters, whitespace, &, ?, / and #.",
        max_length=256,
        min_length=1,
        regex=FiwareRegex.string_protect.value,  # Make it FIWARE-Safe
    )
    metadata: Optional[Union[Dict[str, ContextMetadata],
                             NamedContextMetadata,
                             List[NamedContextMetadata]]] = Field(
        default={},
        title="Metadata",
        description="optional metadata describing properties of the attribute "
                    "value like e.g. accuracy, provider, or a timestamp")

    @validator('metadata')
    def validate_metadata_type(cls, value):
        """validator for field 'metadata'"""
        if isinstance(value, NamedContextMetadata):
            value = [value]
        elif isinstance(value, dict):
            if all(isinstance(item, ContextMetadata)
                   for item in value.values()):
                return value
            json.dumps(value)
            return {key: ContextMetadata(**item) for key, item in value.items()}
        if isinstance(value, list):
            if all(isinstance(item, NamedContextMetadata) for item in value):
                return {item.name: ContextMetadata(**item.dict(exclude={
                    'name'})) for item in value}
            if all(isinstance(item, Dict) for item in value):
                return {key: ContextMetadata(**item) for key, item in value}
        raise TypeError(f"Invalid type {type(value)}")


class BaseNameAttribute(BaseModel):
    """
    Model to add the name property to an BaseAttribute Model.
    The attribute name describes what kind of property the
    attribute value represents of the entity
    """
    name: str = Field(
        titel="Attribute name",
        description="The attribute name describes what kind of property the "
                    "attribute value represents of the entity, for example "
                    "current_speed. Allowed characters "
                    "are the ones in the plain ASCII set, except the following "
                    "ones: control characters, whitespace, &, ?, / and #.",
        max_length=256,
        min_length=1,
        regex=FiwareRegex.string_protect.value,
        # Make it FIWARE-Safe
    )


class BaseValueAttribute(BaseModel):
    """
    Model to add the value property to an BaseAttribute Model. The Model
    is represented by a JSON object with the following syntax:


    The attribute value is specified by the value property, whose value may
    be any JSON datatype.
    """
    type: Union[DataType, str] = Field(
        default=DataType.TEXT,
        description="The attribute type represents the NGSI value type of the "
                    "attribute value. Note that FIWARE NGSI has its own type "
                    "system for attribute values, so NGSI value types are not "
                    "the same as JSON types. Allowed characters "
                    "are the ones in the plain ASCII set, except the following "
                    "ones: control characters, whitespace, &, ?, / and #.",
        max_length=256,
        min_length=1,
        regex=FiwareRegex.string_protect.value,  # Make it FIWARE-Safe
    )
    value: Optional[Union[Union[float, int, bool, str, List, Dict[str, Any]],
                          List[Union[float, int, bool, str, List,
                                     Dict[str, Any]]]]] = Field(
        default=None,
        title="Attribute value",
        description="the actual data"
    )

    @validator('value')
    def validate_value_type(cls, value, values):
        """validator for field 'value'"""

        type_ = values['type']
        if value:
            if type_ == DataType.TEXT:
                if isinstance(value, list):
                    return [str(item) for item in value]
                return str(value)
            if type_ == DataType.BOOLEAN:
                if isinstance(value, list):
                    return [bool(item) for item in value]
                return bool(value)
            if type_ in (DataType.NUMBER, DataType.FLOAT):
                if isinstance(value, list):
                    return [float(item) for item in value]
                return float(value)
            if type_ == DataType.INTEGER:
                if isinstance(value, list):
                    return [int(item) for item in value]
                return int(value)
            if type_ == DataType.DATETIME:
                return value
            if type_ == DataType.ARRAY:
                if isinstance(value, list):
                    return value
                raise TypeError(f"{type(value)} does not match "
                                f"{DataType.ARRAY}")
            if type_ == DataType.STRUCTUREDVALUE:
                value = json.dumps(value)
                return json.loads(value)
            else:
                value = json.dumps(value)
                return json.loads(value)
        return value
