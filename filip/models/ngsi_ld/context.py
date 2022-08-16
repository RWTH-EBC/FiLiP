"""
NGSIv2 models for context broker interaction
"""
import json
from typing import Any, Type, List, Dict, Union, Optional, Pattern

from aenum import Enum
from pydantic import BaseModel, Field, validator
from filip.models.ngsi_v2 import ContextEntity
from filip.models.base import FiwareRegex


class DataTypeLD(str, Enum):
    """
    When possible reuse schema.org data types
    (Text, Number, DateTime, StructuredValue, etc.).
    Remember that null is not allowed in NGSI-LD and
    therefore should be avoided as a value.

    https://schema.org/DataType
    """
    _init_ = 'value __doc__'

    PROPERTY = "Property", ""
    RELATIONSHIP = "Relationship", "Reference to another context entity"
    STRUCTUREDVALUE = "StructuredValue", "Structered datatype must be " \
                                         "serializable"


# NGSI-LD entity models
class ContextProperty(BaseModel):
    """
    Model for an attribute is represented by a JSON object with the following
    syntax:

    The attribute value is specified by the value property, whose value may
    be any JSON datatype.

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

        >>> data = {"value": <...>}

        >>> attr = ContextAttribute(**data)

    """
    type: str = DataTypeLD.PROPERTY
    value: Optional[Union[Union[float, int, bool, str, List, Dict[str, Any]],
                          List[Union[float, int, bool, str, List,
                                     Dict[str, Any]]]]] = Field(
        default=None,
        title="Property value",
        description="the actual data"
    )  # todo: Add Property and Relationship

    @validator('value')
    def validate_value_type(cls, value):
        """validator for field 'value'"""
        type_ = type(value)
        if value:
            if type_ == DataTypeLD.STRUCTUREDVALUE:
                value = json.dumps(value)
                return json.loads(value)
            else:
                value = json.dumps(value)
                return json.loads(value)
        return value


class NamedContextProperty(ContextProperty):
    """
    Context attributes are properties of context entities. For example, the
    current speed of a car could be modeled as attribute current_speed of entity
    car-104.

    In the NGSI data model, attributes have an attribute name, an attribute type
    an attribute value and metadata.
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


class ContextRelationship(BaseModel):
    """
    Model for an attribute is represented by a JSON object with the following
    syntax:

    The attribute value is specified by the value property, whose value may
    be any JSON datatype.

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

        >>> data = {"object": <...>}

        >>> attr = ContextRelationship(**data)

    """
    type: str = DataTypeLD.RELATIONSHIP
    object: Optional[Union[Union[float, int, bool, str, List, Dict[str, Any]],
                           List[Union[float, int, bool, str, List,
                                      Dict[str, Any]]]]] = Field(
        default=None,
        title="Realtionship object",
        description="the actual object id"
    )

    @validator('value')
    def validate_value_type(cls, value):
        """validator for field 'value'"""
        type_ = type(value)
        if value:
            if type_ == DataTypeLD.STRUCTUREDVALUE:
                value = json.dumps(value)
                return json.loads(value)
            else:
                value = json.dumps(value)
                return json.loads(value)
        return value


class NamedContextRelationship(ContextRelationship):
    """
    Context attributes are properties of context entities. For example, the
    current speed of a car could be modeled as attribute current_speed of entity
    car-104.

    In the NGSI data model, attributes have an attribute name, an attribute type
    an attribute value and metadata.
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


class ContextLDEntityKeyValues(BaseModel):
    """
    Base Model for an entity is represented by a JSON object with the following
    syntax.

    The entity id is specified by the object's id property, whose value
    is a string containing the entity id.

    The entity type is specified by the object's type property, whose value
    is a string containing the entity's type name.

    """
    id: str = Field(
        ...,
        title="Entity Id",
        description="Id of an entity in an NGSI context broker. Allowed "
                    "characters are the ones in the plain ASCII set, except "
                    "the following ones: control characters, "
                    "whitespace, &, ?, / and #.",
        example='Bcn-Welt',
        max_length=256,
        min_length=1,
        regex=FiwareRegex.standard.value,  # Make it FIWARE-Safe
        allow_mutation=False
    )
    type: str = Field(
        ...,
        title="Entity Type",
        description="Id of an entity in an NGSI context broker. "
                    "Allowed characters are the ones in the plain ASCII set, "
                    "except the following ones: control characters, "
                    "whitespace, &, ?, / and #.",
        example="Room",
        max_length=256,
        min_length=1,
        regex=FiwareRegex.standard.value,  # Make it FIWARE-Safe
        allow_mutation=False
    )

    class Config:
        """
        Pydantic config
        """
        extra = 'allow'
        validate_all = True
        validate_assignment = True


class PropertyFormat(str, Enum):
    """
    Format to decide if properties of ContextEntity class are returned as
    List of NamedContextAttributes or as Dict of ContextAttributes.
    """
    LIST = 'list'
    DICT = 'dict'


class ContextLDEntity(ContextLDEntityKeyValues, ContextEntity):
    """
    Context entities, or simply entities, are the center of gravity in the
    FIWARE NGSI information model. An entity represents a thing, i.e., any
    physical or logical object (e.g., a sensor, a person, a room, an issue in
    a ticketing system, etc.). Each entity has an entity id.
    Furthermore, the type system of FIWARE NGSI enables entities to have an
    entity type. Entity types are semantic types; they are intended to describe
    the type of thing represented by the entity. For example, a context
    entity #with id sensor-365 could have the type temperatureSensor.

    Each entity is uniquely identified by the combination of its id and type.

    The entity id is specified by the object's id property, whose value
    is a string containing the entity id.

    The entity type is specified by the object's type property, whose value
    is a string containing the entity's type name.

    Entity attributes are specified by additional properties, whose names are
    the name of the attribute and whose representation is described in the
    "ContextAttribute"-model. Obviously, id and type are
    not allowed to be used as attribute names.

    Example:

        >>> data = {'id': 'MyId',
                    'type': 'MyType',
                    'my_attr': {'value': 20, 'type': 'Number'}}

        >>> entity = ContextLDEntity(**data)

    """

    def __init__(self,
                 id: str,
                 type: str,
                 **data):

        # There is currently no validation for extra fields
        data.update(self._validate_properties(data))
        super().__init__(id=id, type=type, **data)

    class Config:
        """
        Pydantic config
        """
        extra = 'allow'
        validate_all = True
        validate_assignment = True

    @classmethod
    def _validate_properties(cls, data: Dict):
        attrs = {key: ContextProperty.parse_obj(attr) for key, attr in
                 data.items() if key not in ContextLDEntity.__fields__}
        return attrs

    def get_properties(self,
                       response_format: Union[str, PropertyFormat] =
                       PropertyFormat.LIST) -> \
            Union[List[NamedContextProperty],
                  Dict[str, ContextProperty]]:
        """
        Args:
            response_format:

        Returns:

        """
        response_format = PropertyFormat(response_format)
        if response_format == PropertyFormat.DICT:
            return {key: ContextProperty(**value) for key, value in
                    self.dict().items() if key not in ContextLDEntity.__fields__}

        return [NamedContextProperty(name=key, **value) for key, value in
                self.dict().items() if key not in
                ContextLDEntity.__fields__ ]

    def add_properties(self, attrs: Union[Dict[str, ContextProperty],
                                          List[NamedContextProperty]]) -> None:
        """
        Add property to entity
        Args:
            attrs:
        Returns:
            None
        """
        if isinstance(attrs, list):
            attrs = {attr.name: ContextProperty(**attr.dict(exclude={'name'}))
                     for attr in attrs}
        for key, attr in attrs.items():
            self.__setattr__(name=key, value=attr)

    def get_relationships(self,
                          response_format: Union[str, PropertyFormat] =
                          PropertyFormat.LIST) \
            -> Union[List[NamedContextRelationship],
                     Dict[str, ContextRelationship]]:
        """
        Get all relationships of the context entity

        Args:
            response_format:

        Returns:

        """
        response_format = PropertyFormat(response_format)
        if response_format == PropertyFormat.DICT:
            return {key: ContextRelationship(**value) for key, value in
                    self.dict().items() if key not in ContextLDEntity.__fields__
                    and value.get('type') == DataTypeLD.RELATIONSHIP}
        return [NamedContextRelationship(name=key, **value) for key, value in
                self.dict().items() if key not in
                ContextLDEntity.__fields__ and
                value.get('type') == DataTypeLD.RELATIONSHIP]
