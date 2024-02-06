"""
NGSIv2 models for context broker interaction
"""
import logging
from typing import Any, List, Dict, Union, Optional

from aenum import Enum
from pydantic import BaseModel, Field, validator
from filip.models.ngsi_v2 import ContextEntity
from filip.utils.validators import FiwareRegex


class DataTypeLD(str, Enum):
    """
    In NGSI-LD the data types on context entities are only divided into properties and relationships.
    """
    _init_ = 'value __doc__'

    PROPERTY = "Property", "All attributes that do not represent a relationship"
    RELATIONSHIP = "Relationship", "Reference to another context entity, which can be identified with a URN."


# NGSI-LD entity models
class ContextProperty(BaseModel):
    """
    The model for a property is represented by a JSON object with the following syntax:

    The attribute value is specified by the value, whose value can be any data type. This does not need to be
    specified further.

    The NGSI type of the attribute is fixed and does not need to be specified.
    Example:

        >>> data = {"value": <...>}

        >>> attr = ContextProperty(**data)

    """
    type = "Property"
    value: Optional[Union[Union[float, int, bool, str, List, Dict[str, Any]],
                          List[Union[float, int, bool, str, List,
                                     Dict[str, Any]]]]] = Field(
        default=None,
        title="Property value",
        description="the actual data"
    )


class NamedContextProperty(ContextProperty):
    """
    Context properties are properties of context entities. For example, the current speed of a car could be modeled
    as the current_speed property of the car-104 entity.

    In the NGSI-LD data model, properties have a name, the type "property" and a value.
    """
    name: str = Field(
        titel="Property name",
        description="The property name describes what kind of property the "
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
    The model for a relationship is represented by a JSON object with the following syntax:

    The attribute value is specified by the object, whose value can be a reference to another context entity. This
    should be specified as the URN. The existence of this entity is not assumed.

    The NGSI type of the attribute is fixed and does not need to be specified.

    Example:

        >>> data = {"object": <...>}

        >>> attr = ContextRelationship(**data)

    """
    type = "Relationship"
    object: Optional[Union[Union[float, int, bool, str, List, Dict[str, Any]],
                           List[Union[float, int, bool, str, List,
                                      Dict[str, Any]]]]] = Field(
        default=None,
        title="Realtionship object",
        description="the actual object id"
    )


class NamedContextRelationship(ContextRelationship):
    """
    Context Relationship are relations of context entities to each other.
    For example, the current_speed of the entity car-104 could be modeled.
    The location could be modeled as located_in the entity Room-001.

    In the NGSI-LD data model, relationships have a name, the type "relationship" and an object.
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
                    "whitespace, &, ?, / and #."
                    "the id should be structured according to the urn naming scheme.",
        example='urn:ngsi-ld:Room:001',
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
    Context LD entities, or simply entities, are the center of gravity in the
    FIWARE NGSI-LD information model. An entity represents a thing, i.e., any
    physical or logical object (e.g., a sensor, a person, a room, an issue in
    a ticketing system, etc.). Each entity has an entity id.
    Furthermore, the type system of FIWARE NGSI enables entities to have an
    entity type. Entity types are semantic types; they are intended to describe
    the type of thing represented by the entity. For example, a context
    entity #with id sensor-365 could have the type temperatureSensor.

    Each entity is uniquely identified by its id.

    The entity id is specified by the object's id property, whose value
    is a string containing the entity id.

    The entity type is specified by the object's type property, whose value
    is a string containing the entity's type name.

    Entity attributes are specified by additional properties and relationships, whose names are
    the name of the attribute and whose representation is described in the
    "ContextProperty"/"ContextRelationship"-model. Obviously, id and type are
    not allowed to be used as attribute names.

    Example:

        >>> data = {'id': 'MyId',
                    'type': 'MyType',
                    'my_attr': {'value': 20}}

        >>> entity = ContextLDEntity(**data)

    """

    def __init__(self,
                 id: str,
                 type: str,
                 **data):

        super().__init__(id=id, type=type, **data)

    class Config:
        """
        Pydantic config
        """
        extra = 'allow'
        validate_all = True
        validate_assignment = True

    @validator("id")
    def _validate_id(cls, id: str):
        if not id.startswith("urn:ngsi-ld:"):
            raise ValueError('Id has to be an URN and starts with "urn:ngsi-ld:"')
        return id

    @classmethod
    def _validate_properties(cls, data: Dict):
        attrs = {}
        for key, attr in data.items():
            if key not in ContextEntity.__fields__:
                if attr["type"] == DataTypeLD.RELATIONSHIP:
                    attrs[key] = ContextRelationship.parse_obj(attr)
                else:
                    attrs[key] = ContextProperty.parse_obj(attr)
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
                    self.dict().items() if key not in ContextLDEntity.__fields__
                    and value.get('type') != DataTypeLD.RELATIONSHIP}

        return [NamedContextProperty(name=key, **value) for key, value in
                self.dict().items() if key not in
                ContextLDEntity.__fields__ and
                value.get('type') != DataTypeLD.RELATIONSHIP]

    def add_attributes(self, **kwargs):
        """
        Invalid in NGSI-LD
        """
        raise NotImplementedError(
            "This method should not be used in NGSI-LD")

    def get_attribute(self, **kwargs):
        """
        Invalid in NGSI-LD
        """
        raise NotImplementedError(
            "This method should not be used in NGSI-LD")

    def get_attributes(self, **kwargs):
        """
        Invalid in NGSI-LD
        """
        raise NotImplementedError(
            "This method should not be used in NGSI-LD")

    def delete_attributes(self, **kwargs):
        """
        Invalid in NGSI-LD
        """
        raise NotImplementedError(
            "This method should not be used in NGSI-LD")

    def delete_properties(self, props: Union[Dict[str, ContextProperty],
                                             List[NamedContextProperty],
                                             List[str]]):
        """
        Delete the given properties from the entity

        Args:
            props: can be given in multiple forms
                1) Dict: {"<property_name>": ContextProperty, ...}
                2) List: [NamedContextProperty, ...]
                3) List: ["<property_name>", ...]

        Returns:

        """
        names: List[str] = []
        if isinstance(props, list):
            for entry in props:
                if isinstance(entry, str):
                    names.append(entry)
                elif isinstance(entry, NamedContextProperty):
                    names.append(entry.name)
        else:
            names.extend(list(props.keys()))

        # check there are no relationships
        relationship_names = [rel.name for rel in self.get_relationships()]
        for name in names:
            if name in relationship_names:
                raise TypeError(f"{name} is a relationship")

        for name in names:
            delattr(self, name)

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

    def add_relationships(self, attrs: Union[Dict[str, ContextRelationship],
                                             List[NamedContextRelationship]]) -> None:
        """
        Add relationship to entity
        Args:
            attrs:
        Returns:
            None
        """
        if isinstance(attrs, list):
            attrs = {attr.name: ContextRelationship(**attr.dict(exclude={'name'}))
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


class ActionTypeLD(str, Enum):
    """
    Options for queries
    """

    CREATE = "create"
    UPSERT = "upsert"
    UPDATE = "update"
    DELETE = "delete"


class UpdateLD(BaseModel):
    """
    Model for update action
    """
    entities: List[ContextEntity] = Field(
        description="an array of entities, each entity specified using the "
                    "JSON entity representation format "
    )
