"""
Shared models that are used by multiple submodules
"""
import json

from aenum import Enum
from geojson_pydantic import (
    Point,
    MultiPoint,
    LineString,
    MultiLineString,
    Polygon,
    MultiPolygon,
    Feature,
    FeatureCollection,
)
from pydantic import (
    field_validator,
    model_validator,
    ConfigDict,
    AnyHttpUrl,
    BaseModel,
    Field,
    model_serializer,
    SerializationInfo,
    ValidationInfo,
)

from typing import Union, Optional, Pattern, List, Dict, Any

from filip.models.base import DataType
from filip.models.ngsi_v2.units import validate_unit_data, Unit
from filip.utils.simple_ql import QueryString, QueryStatement
from filip.utils.validators import (
    validate_escape_character_free,
    validate_fiware_datatype_string_protect,
    validate_fiware_datatype_standard,
)


class Http(BaseModel):
    """
    Model for notification and registrations sent or retrieved via HTTP
    """

    url: AnyHttpUrl = Field(
        description="URL referencing the service to be invoked when a "
        "notification is generated. An NGSIv2 compliant server "
        "must support the http URL schema. Other schemas could "
        "also be supported."
    )


class EntityPattern(BaseModel):
    """
    Entity pattern used to create subscriptions or registrations
    """

    id: Optional[str] = Field(default=None, pattern=r"\w")
    idPattern: Optional[Pattern] = None
    type: Optional[str] = Field(default=None, pattern=r"\w")
    typePattern: Optional[Pattern] = None

    @model_validator(mode="after")
    def validate_conditions(self):
        assert (self.id and not self.idPattern) or (not self.id and self.idPattern), (
            "Both cannot be used at the same time, but one of 'id' or "
            "'idPattern must' be present."
        )
        if self.type or self.model_dump().get("typePattern", None):
            assert (self.type and not self.typePattern) or (
                not self.type and self.typePattern
            ), (
                "Type or pattern of the affected entities. "
                "Both cannot be used at the same time."
            )
        return self


class Status(str, Enum):
    """
    Current status of a subscription or registrations
    """

    _init_ = "value __doc__"

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

    model_config = ConfigDict(arbitrary_types_allowed=True)

    q: Optional[Union[str, QueryString]] = Field(
        default=None,
        title="Simple Query Language: filter",
        description="If filtering by attribute value (i.e. the expression is "
        "used in a q query), the rest of tokens (if present) "
        "represent the path to a sub-property of the target NGSI "
        "attribute value (which should be a JSON object). Such "
        "sub-property is defined as the target property.",
    )
    mq: Optional[Union[str, QueryString]] = Field(
        default=None,
        title="Simple Query Language: metadata filters",
        description="If filtering by metadata (i.e. the expression is used in "
        "a mq query), the second token represents a metadata name "
        "associated to the target NGSI attribute, target "
        "metadata, and the rest of tokens (if present) represent "
        "the path to a sub-property of the target metadata value "
        "(which should be a JSON object). Such sub-property is "
        "defined as the target property. ",
    )
    georel: Optional[Union[str, QueryString]] = Field(
        default=None,
        title="Metadata filters",
        description="Any of the geographical relationships as specified by "
        "the Geoqueries section of this specification.",
    )
    geometry: Optional[Union[str, QueryString]] = Field(
        default=None,
        title="Metadata filters",
        description="Any of the supported geometries as specified by the "
        "Geoqueries section of this specification.",
    )
    coords: Optional[Union[str, QueryString]] = Field(
        default=None,
        title="Metadata filters",
        description="String representation of coordinates as specified by the "
        "Geoqueries section of the specification.",
    )

    @field_validator("q", "mq")
    @classmethod
    def validate_expressions(cls, v):
        if isinstance(v, str):
            return QueryString.parse_str(v)

    @model_serializer(mode="wrap")
    def serialize(self, serializer: Any, info: SerializationInfo):
        if isinstance(self.q, (QueryString, QueryStatement)):
            self.q = self.q.to_str()
        if isinstance(self.mq, (QueryString, QueryStatement)):
            self.mq = self.mq.to_str()
        if isinstance(self.coords, (QueryString, QueryStatement)):
            self.coords = self.coords.to_str()
        if isinstance(self.georel, (QueryString, QueryStatement)):
            self.georel = self.georel.to_str()
        if isinstance(self.geometry, (QueryString, QueryStatement)):
            self.geometry = self.geometry.to_str()
        return serializer(self)


class AttrsFormat(str, Enum):
    """
    Allowed options for attribute formats
    """

    _init_ = "value __doc__"

    NORMALIZED = "normalized", "Normalized message representation"
    KEY_VALUES = (
        "keyValues",
        "Key value message representation."
        "This mode represents the entity "
        "attributes by their values only, leaving out "
        "the information about type and metadata. "
        "See example below."
        "Example: "
        "{"
        "  'id': 'R12345',"
        "  'type': 'Room',"
        "  'temperature': 22"
        "}",
    )
    VALUES = (
        "values",
        "Key value message representation. "
        "This mode represents the entity as an array of "
        "attribute values. Information about id and type is "
        "left out. See example below. The order of the "
        "attributes in the array is specified by the attrs "
        "URI param (e.g. attrs=branch,colour,engine). "
        "If attrs is not used, the order is arbitrary. "
        "Example:"
        "[ 'Ford', 'black', 78.3 ]",
    )


# NGSIv2 entity models
class Metadata(BaseModel):
    """
    Context metadata is used in FIWARE NGSI in several places, one of them being
    an optional part of the attribute value as described above. Similar to
    attributes, each piece of metadata has.

    Note:
         In NGSI it is not foreseen that metadata may contain nested metadata.
    """

    type: Optional[Union[DataType, str]] = Field(
        default=None,
        title="metadata type",
        description="a metadata type, describing the NGSI value type of the "
        "metadata value Allowed characters "
        "are the ones in the plain ASCII set, except the following "
        "ones: control characters, whitespace, &, ?, / and #.",
        max_length=256,
        min_length=1,
    )
    valid_type = field_validator("type")(validate_fiware_datatype_standard)
    value: Optional[Any] = Field(
        default=None,
        title="metadata value",
        description="a metadata value containing the actual metadata",
    )

    @field_validator("value")
    def validate_value(cls, value, info: ValidationInfo):
        assert json.dumps(value), "metadata not serializable"

        if info.data.get("type").casefold() == "unit":
            value = Unit.model_validate(value)
        return value


class NamedMetadata(Metadata):
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
    )
    valid_name = field_validator("name")(validate_fiware_datatype_standard)

    @model_validator(mode="after")
    def validate_data(self):
        if self.model_dump().get("name", "").casefold() in [
            "unit",
            "unittext",
            "unitcode",
        ]:
            valide_dict = self.model_dump()
            valide_dict.update(validate_unit_data(self.model_dump()))
            return self
        return self

    def to_context_metadata(self):
        return {self.name: Metadata(**self.model_dump())}


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

    model_config = ConfigDict(validate_assignment=True)
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
    )
    valid_type = field_validator("type")(validate_fiware_datatype_string_protect)
    metadata: Optional[
        Union[
            Dict[str, Metadata],
            NamedMetadata,
            List[NamedMetadata],
            Dict[str, Dict[str, str]],
        ]
    ] = Field(
        default={},
        title="Metadata",
        description="optional metadata describing properties of the attribute "
        "value like e.g. accuracy, provider, or a timestamp",
    )

    @field_validator("metadata")
    @classmethod
    def validate_metadata_type(cls, value):
        """validator for field 'metadata'"""
        if type(value) == NamedMetadata:
            value = [value]
        elif isinstance(value, dict):
            if all(isinstance(item, Metadata) for item in value.values()):
                value = [
                    NamedMetadata(name=key, **item.model_dump())
                    for key, item in value.items()
                ]
            else:
                json.dumps(value)
                value = [NamedMetadata(name=key, **item) for key, item in value.items()]

        if isinstance(value, list):
            if all(isinstance(item, dict) for item in value):
                value = [NamedMetadata(**item) for item in value]
            if all(isinstance(item, NamedMetadata) for item in value):
                return {
                    item.name: Metadata(**item.model_dump(exclude={"name"}))
                    for item in value
                }

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
        # Make it FIWARE-Safe
    )
    valid_name = field_validator("name")(validate_fiware_datatype_string_protect)


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
    )
    valid_type = field_validator("type")(validate_fiware_datatype_string_protect)
    value: Optional[Any] = Field(
        default=None, title="Attribute value", description="the actual data"
    )

    @field_validator("value")
    def validate_value_type(cls, value, info: ValidationInfo):
        """
        Validator for field 'value'
        The validator will try autocast the value based on the given type.
        If `DataType.STRUCTUREDVALUE` is used for type it will also serialize
        pydantic models. With latter operation all additional features of the
        original pydantic model will be dumped.
        If the type is unknown it will check json-serializable.
        """

        type_ = info.data.get("type")
        value_ = value
        if isinstance(value, BaseModel):
            value_ = value.model_dump()
        validate_escape_character_free(value_)

        if value not in (None, "", " "):
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
            # allows list
            if type_ == DataType.ARRAY:
                if isinstance(value, list):
                    return value
                raise TypeError(f"{type(value)} does not match " f"{DataType.ARRAY}")
            # allows dict and BaseModel as object
            if type_ == DataType.OBJECT:
                if isinstance(value, dict):
                    value = json.dumps(value)
                    return json.loads(value)
                elif isinstance(value, BaseModel):
                    value.model_dump_json()
                    return value
                raise TypeError(
                    f"{type(value)} does not match " f"{DataType.OBJECT}"
                )

            # allows geojson as structured value
            if type_ == DataType.GEOJSON:
                if isinstance(
                    value,
                    (
                        Point,
                        MultiPoint,
                        LineString,
                        MultiLineString,
                        Polygon,
                        MultiPolygon,
                        Feature,
                        FeatureCollection,
                    ),
                ):
                    return value
                if isinstance(value, dict):
                    _geo_json_type = value.get("type", None)
                    if _geo_json_type == "Point":
                        return Point(**value)
                    elif _geo_json_type == "MultiPoint":
                        return MultiPoint(**value)
                    elif _geo_json_type == "LineString":
                        return LineString(**value)
                    elif _geo_json_type == "MultiLineString":
                        return MultiLineString(**value)
                    elif _geo_json_type == "Polygon":
                        return Polygon(**value)
                    elif _geo_json_type == "MultiPolygon":
                        return MultiPolygon(**value)
                    elif _geo_json_type == "Feature":
                        return Feature(**value)
                    elif _geo_json_type == "FeatureCollection":
                        return FeatureCollection(**value)
                raise TypeError(f"{type(value)} does not match "
                                f"{DataType.GEOJSON}")

            # allows list, dict and BaseModel as structured value
            if type_ == DataType.STRUCTUREDVALUE:
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                    return json.loads(value)
                elif isinstance(value, BaseModel):
                    value.model_dump_json()
                    return value
                raise TypeError(
                    f"{type(value)} does not match " f"{DataType.STRUCTUREDVALUE}"
                )

            # if none of the above, check if it is a pydantic model
            if isinstance(value, BaseModel):
                value.model_dump_json()
                return value

            # if none of the above, check if serializable. Hence, no further
            # type check is performed
            value = json.dumps(value)
            return json.loads(value)

        return value
