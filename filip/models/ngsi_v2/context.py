"""
NGSIv2 models for context broker interaction
"""
import json
from typing import Any, List, Dict, Union, Optional, Set, Tuple

from aenum import Enum
from pydantic import field_validator, ConfigDict, BaseModel, Field, \
    model_validator
from pydantic_core.core_schema import ValidationInfo

from filip.models.ngsi_v2.base import (
    EntityPattern,
    Expression,
    BaseAttribute,
    BaseValueAttribute,
    BaseNameAttribute,
)
from filip.models.base import DataType
from filip.utils.validators import (
    validate_fiware_datatype_standard,
    validate_fiware_datatype_string_protect,
)


class GetEntitiesOptions(str, Enum):
    """Options for queries"""

    _init_ = "value __doc__"

    NORMALIZED = "normalized", "Normalized message representation"
    KEY_VALUES = (
        "keyValues",
        "Key value message representation."
        "This mode represents the entity "
        "attributes by their values only, leaving out "
        "the information about type and metadata. "
        "See example "
        "below."
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
    UNIQUE = (
        "unique",
        "unique mode. This mode is just like values mode, "
        "except that values are not repeated",
    )


class PropertyFormat(str, Enum):
    """
    Format to decide if properties of ContextEntity class are returned as
    List of NamedContextAttributes or as Dict of ContextAttributes.
    """

    LIST = "list"
    DICT = "dict"


class ContextAttribute(BaseAttribute, BaseValueAttribute):
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

        >>> data = {"value": <...>,
                    "type": <...>,
                    "metadata": <...>}
        >>> attr = ContextAttribute(**data)

    """
    # although `type` is a required field in the NGSIv2 specification, it is
    # set to optional here to allow for the possibility of setting
    # default-types in child classes. Pydantic will raise the correct error
    # and also exports the correct json-schema.
    def __init__(self, type: str = None, **data):
        if type is None and self.model_fields["type"].default:
            type = self.model_fields["type"].default
        super().__init__(type=type, **data)


class NamedContextAttribute(ContextAttribute, BaseNameAttribute):
    """
    Context attributes are properties of context entities. For example, the
    current speed of a car could be modeled as attribute current_speed of entity
    car-104.

    In the NGSI data model, attributes have an attribute name, an attribute type
    an attribute value and metadata.
    """

    pass


class ContextEntityKeyValues(BaseModel):
    """
    Base Model for an entity is represented by a JSON object with the following
    syntax.

    The entity id is specified by the object's id property, whose value
    is a string containing the entity id.

    The entity type is specified by the object's type property, whose value
    is a string containing the entity's type name.

    """

    model_config = ConfigDict(
        extra="allow", validate_default=True, validate_assignment=True
    )
    id: str = Field(
        ...,
        title="Entity Id",
        description="Id of an entity in an NGSI context broker. Allowed "
        "characters are the ones in the plain ASCII set, except "
        "the following ones: control characters, "
        "whitespace, &, ?, / and #.",
        example="Bcn-Welt",
        max_length=256,
        min_length=1,
        frozen=True,
    )
    valid_id = field_validator("id")(validate_fiware_datatype_standard)
    type: Union[str, Enum] = Field(
        ...,
        title="Entity Type",
        description="Id of an entity in an NGSI context broker. "
        "Allowed characters are the ones in the plain ASCII set, "
        "except the following ones: control characters, "
        "whitespace, &, ?, / and #.",
        example="Room",
        max_length=256,
        min_length=1,
        frozen=True,
    )
    valid_type = field_validator("type")(validate_fiware_datatype_standard)

    # although `type` is a required field in the NGSIv2 specification, it is
    # set to optional here to allow for the possibility of setting
    # default-types in child classes. Pydantic will raise the correct error
    # and also exports the correct json-schema.
    def __init__(self, id: str, type: Union[str, Enum] = None, **data):
        # this allows to set the type of the entity in child classes
        if type is None:
            if isinstance(self.model_fields["type"].default, str):
                type = self.model_fields["type"].default
            else:
                # if this statement is reached not proper default-value for
                # `type` was found and pydantic will raise the correct error
                super().__init__(id=id, **data)
        # This will result in usual behavior
        super().__init__(id=id, type=type, **data)

    def get_attributes(self) -> dict:
        """
        Get the attribute of the entity with the given name in
        dict format

        Returns:
            dict
        """
        return self.model_dump(exclude={"id", "type"})


class ContextEntity(ContextEntityKeyValues):
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
    the name of the attribute and whose representation is described by the
    "ContextAttribute"-model. Obviously, `id` and `type` are
    not allowed as attribute names.

    Example::

        >>> data = {'id': 'MyId',
                    'type': 'MyType',
                    'my_attr': {'value': 20, 'type': 'Number'}}

        >>> entity = ContextEntity(**data)

    """

    model_config = ConfigDict(
        extra="allow", validate_default=True, validate_assignment=True
    )
    # although `type` is a required field in the NGSIv2 specification, it is
    # set to optional here to allow for the possibility of setting
    # default-types in child classes. Pydantic will raise the correct error
    # and also exports the correct json-schema.
    def __init__(self, id: str, type: str = None, **data):
        # There is currently no validation for extra fields
        data.update(self._validate_attributes(data))
        # case where type is None to raise correct error message
        if type is None:
            super().__init__(id=id, **data)
        else:
            super().__init__(id=id, type=type, **data)

    # Validation of attributes
    @classmethod
    def _validate_attributes(cls, data: dict):
        """
        Validate attributes of the entity if the attribute is not a model
        field and the type is not already a subtype of ContextAttribute
        """
        attrs = {
            key: ContextAttribute.model_validate(attr)
            for key, attr in data.items()
            if (key not in cls.model_fields and not isinstance(attr, ContextAttribute))
        }

        return attrs

    @field_validator('*')
    @classmethod
    def check_attributes(cls, value, info: ValidationInfo):
        """
        Check whether all model fields are of subtype of ContextAttribute to
        ensure full functionality.
        """
        if info.field_name in ["id", "type"]:
             return value

        if info.field_name in cls.model_fields:
            if not (isinstance(value, ContextAttribute)
                    or value == cls.model_fields[info.field_name].default):
                raise ValueError(f"Attribute {info.field_name} must be a of "
                                 f"type or subtype ContextAttribute")
        return value

    @model_validator(mode="after")
    @classmethod
    def check_attributes_after(cls, values):
        try:
            for attr in values.model_extra:
                if not isinstance(values.__getattr__(attr), ContextAttribute):
                    raise ValueError(f"Attribute {attr} must be a of type or "
                                     f"subtype ContextAttribute. You most "
                                     f"likely tried to directly assign an "
                                     f"attribute without converting it to a "
                                     f"proper Attribute-Type!")
        except TypeError:
            pass
        return values

    # API for attributes and commands
    def add_attributes(
        self, attrs: Union[Dict[str, ContextAttribute], List[NamedContextAttribute]]
    ) -> None:
        """
        Add attributes (properties, relationships) to entity

        Args:
            attrs: Dict[str, ContextAttribute]: {NAME for attr : Attribute} or
                   List[NamedContextAttribute]

        Returns:
            None
        """
        if isinstance(attrs, list):
            attrs = {
                attr.name: ContextAttribute(**attr.model_dump(exclude={"name"}))
                for attr in attrs
            }
        for key, attr in attrs.items():
            self.__setattr__(name=key, value=attr)

    def get_attributes(
        self,
        whitelisted_attribute_types: Optional[List[DataType]] = None,
        blacklisted_attribute_types: Optional[List[DataType]] = None,
        response_format: Union[str, PropertyFormat] = PropertyFormat.LIST,
        strict_data_type: bool = True,
    ) -> Union[List[NamedContextAttribute], Dict[str, ContextAttribute]]:
        """
        Get attributes or a subset from the entity.

        Args:
            whitelisted_attribute_types: Optional list, if given only
                attributes matching one of the types are returned
            blacklisted_attribute_types: Optional list, if given all
                attributes are returned that do not match a list entry
            response_format: Wanted result format,
                                List -> list of NamedContextAttributes
                                Dict -> dict of {name: ContextAttribute}
            strict_data_type: whether to restrict the data type to pre-defined
                types, True by default.
                True  -> Only return the attributes with pre-defined types,
                False -> Do not restrict the data type.
        Raises:
            AssertionError, if both a white and a black list is given
        Returns:
            List[NamedContextAttribute] or Dict[str, ContextAttribute]
        """

        response_format = PropertyFormat(response_format)

        assert (
            whitelisted_attribute_types is None or blacklisted_attribute_types is None
        ), "Only whitelist or blacklist is allowed"

        if whitelisted_attribute_types is not None:
            attribute_types = whitelisted_attribute_types
        elif blacklisted_attribute_types is not None:
            attribute_types = [
                att_type
                for att_type in list(DataType)
                if att_type not in blacklisted_attribute_types
            ]
        else:
            attribute_types = [att_type for att_type in list(DataType)]

        if response_format == PropertyFormat.DICT:
            if strict_data_type:
                return {
                    key: ContextAttribute(**value)
                    for key, value in self.model_dump().items()
                    if key not in ContextEntity.model_fields
                    and value.get("type") in [att.value for att in attribute_types]
                }
            else:
                return {
                    key: ContextAttribute(**value)
                    for key, value in self.model_dump().items()
                    if key not in ContextEntity.model_fields
                }
        else:
            if strict_data_type:
                return [
                    NamedContextAttribute(name=key, **value)
                    for key, value in self.model_dump().items()
                    if key not in ContextEntity.model_fields
                    and value.get("type") in [att.value for att in attribute_types]
                ]
            else:
                return [
                    NamedContextAttribute(name=key, **value)
                    for key, value in self.model_dump().items()
                    if key not in ContextEntity.model_fields
                ]

    def update_attribute(
        self, attrs: Union[Dict[str, ContextAttribute], List[NamedContextAttribute]]
    ) -> None:
        """
        Update attributes of an entity. Overwrite the current held value
        for the attribute with the value contained in the corresponding given
        attribute

        Args:
            attrs: List of NamedContextAttributes,
                   Dict of {attribute_name: ContextAttribute}
        Raises:
            NameError, if the attribute does not currently exist in the entity
        Returns:
            None
        """
        if isinstance(attrs, list):
            attrs = {
                attr.name: ContextAttribute(**attr.model_dump(exclude={"name"}))
                for attr in attrs
            }

        existing_attribute_names = self.get_attribute_names()
        for key, attr in attrs.items():
            if key not in existing_attribute_names:
                raise NameError
            self.__setattr__(name=key, value=attr)

    def get_attribute_names(self) -> Set[str]:
        """
        Returns a set with all attribute names of this entity

        Returns:
            Set[str]
        """

        return {
            key for key in self.model_dump() if key not in ContextEntity.model_fields
        }

    def delete_attributes(
        self,
        attrs: Union[
            Dict[str, ContextAttribute], List[NamedContextAttribute], List[str]
        ],
    ):
        """
        Delete the given attributes from the entity

        Args:
            attrs:  - Dict {name: ContextAttribute}
                    - List[NamedContextAttribute]
                    - List[str] -> names of attributes
        Raises:
            Exception: if one of the given attrs does not represent an
                       existing argument
        """

        names: List[str] = []
        if isinstance(attrs, list):
            for entry in attrs:
                if isinstance(entry, str):
                    names.append(entry)
                elif isinstance(entry, NamedContextAttribute):
                    names.append(entry.name)
        else:
            names.extend(list(attrs.keys()))
        for name in names:
            delattr(self, name)

    def get_attribute(self, attribute_name: str) -> NamedContextAttribute:
        """
        Get the attribute of the entity with the given name

        Args:
            attribute_name (str): Name of attribute

        Raises:
            KeyError, if no attribute with given name exists

        Returns:
            NamedContextAttribute
        """
        for attr in self.get_attributes():
            if attr.name == attribute_name:
                return attr
        raise KeyError(f"Attribute '{attribute_name}' not in entity")

    def get_properties(
        self, response_format: Union[str, PropertyFormat] = PropertyFormat.LIST
    ) -> Union[List[NamedContextAttribute], Dict[str, ContextAttribute]]:
        """
        Returns all attributes of the entity that are not of type Relationship,
        and are not auto generated command attributes

        Args:
            response_format: Wanted result format,
                                List -> list of NamedContextAttributes
                                Dict -> dict of {name: ContextAttribute}

        Returns:
            [NamedContextAttribute] or {name: ContextAttribute}
        """
        pre_filtered_attrs = self.get_attributes(
            blacklisted_attribute_types=[DataType.RELATIONSHIP],
            response_format=PropertyFormat.LIST,
        )

        all_command_attributes_names = set()
        for command in self.get_commands():
            (c, c_status, c_info) = self.get_command_triple(command.name)
            all_command_attributes_names.update([c.name, c_status.name, c_info.name])

        property_attributes = []
        for attr in pre_filtered_attrs:
            if attr.name not in all_command_attributes_names:
                property_attributes.append(attr)

        if response_format == PropertyFormat.LIST:
            return property_attributes
        else:
            return {
                p.name: ContextAttribute(**p.model_dump(exclude={"name"}))
                for p in property_attributes
            }

    def get_relationships(
        self, response_format: Union[str, PropertyFormat] = PropertyFormat.LIST
    ) -> Union[List[NamedContextAttribute], Dict[str, ContextAttribute]]:
        """
        Get all relationships of the context entity

        Args:
            response_format: Wanted result format,
                                List -> list of NamedContextAttributes
                                Dict -> dict of {name: ContextAttribute}

        Returns:
            [NamedContextAttribute] or {name: ContextAttribute}

        """
        return self.get_attributes(
            whitelisted_attribute_types=[DataType.RELATIONSHIP],
            response_format=response_format,
        )

    def get_commands(
        self, response_format: Union[str, PropertyFormat] = PropertyFormat.LIST
    ) -> Union[List[NamedContextAttribute], Dict[str, ContextAttribute]]:
        """
        Get all commands of the context entity. Only works if the commands
        were autogenerated by Fiware from an Device.

        Args:
            response_format: Wanted result format,
                                List -> list of NamedContextAttributes
                                Dict -> dict of {name: ContextAttribute}

        Returns:
            [NamedContextAttribute] or {name: ContextAttribute}
        """

        # if an attribute with name n is a command, its type does not need to
        # be COMMAND.
        # But the attributes name_info (type: commandResult) and
        # name_status(type: commandStatus) need to exist. (Autogenerated)

        # Search all attributes of type commandStatus, check for each if a
        # corresponding _info exists and if also a fitting attribute exists
        # we know: that is a command.

        commands = []
        for status_attribute in self.get_attributes(
            whitelisted_attribute_types=[DataType.COMMAND_STATUS]
        ):
            if not status_attribute.name.split("_")[-1] == "status":
                continue
            base_name = status_attribute.name[:-7]

            try:
                info_attribute = self.get_attribute(f"{base_name}_info")
                if not info_attribute.type == DataType.COMMAND_RESULT:
                    continue

                attribute = self.get_attribute(base_name)
                commands.append(attribute)
            except KeyError:
                continue

        if response_format == PropertyFormat.LIST:
            return commands
        else:
            return {
                cmd.name: ContextAttribute(**cmd.model_dump(exclude={"name"}))
                for cmd in commands
            }

    def get_command_triple(
        self, command_attribute_name: str
    ) -> Tuple[NamedContextAttribute, NamedContextAttribute, NamedContextAttribute]:
        """
        Returns for a given command attribute name all three corresponding
        attributes as triple

        Args:
            command_attribute_name: Name of the command attribute

        Raises:
            KeyError, if the given name does not belong to a command attribute

        Returns:
            (Command, Command_status, Command_info)
        """

        commands = self.get_commands(response_format=PropertyFormat.DICT)

        if command_attribute_name not in commands:
            raise KeyError(f"Command '{command_attribute_name}' not in commands")

        command = self.get_attribute(command_attribute_name)

        # as the given name was found as a valid command, we know that the
        # status and info attributes exist correctly
        command_status = self.get_attribute(f"{command_attribute_name}_status")
        command_info = self.get_attribute(f"{command_attribute_name}_info")

        return command, command_status, command_info


class Query(BaseModel):
    """
    Model for queries
    """

    entities: List[EntityPattern] = Field(
        description="a list of entities to search for. Each element is "
        "represented by a JSON object"
    )
    attrs: Optional[List[str]] = Field(
        default=None,
        description="List of attributes to be provided "
        "(if not specified, all attributes).",
    )
    expression: Optional[Expression] = Field(
        default=None,
        description="An expression composed of q, mq, georel, geometry and "
                    "coords",
    )
    metadata: Optional[List[str]] = Field(
        default=None,
        description="a list of metadata names to include in the response. "
        'See "Filtering out attributes and metadata" section for '
        "more detail.",
    )


class ActionType(str, Enum):
    """
    Options for queries
    """

    _init_ = "value __doc__"
    APPEND = (
        "append",
        "maps to POST /v2/entities (if the entity does not "
        "already exist) or POST /v2/entities/<id>/attrs (if "
        "the entity already exists). ",
    )
    APPEND_STRICT = (
        "appendStrict",
        "maps to POST /v2/entities (if the "
        "entity does not already exist) or POST "
        "/v2/entities/<id>/attrs?options=append "
        "(if the entity already exists).",
    )
    UPDATE = "update", "maps to PATCH /v2/entities/<id>/attrs."
    DELETE = (
        "delete",
        "maps to DELETE /v2/entities/<id>/attrs/<attrName> on "
        "every attribute included in the entity or to DELETE "
        "/v2/entities/<id> if no attribute were included in "
        "the entity.",
    )
    REPLACE = "replace", "maps to PUT /v2/entities/<id>/attrs"


class Update(BaseModel):
    """
    Model for update action
    """

    action_type: Union[ActionType, str] = Field(
        alias="actionType",
        description="actionType, to specify the kind of update action to do: "
        "either append, appendStrict, update, delete, or replace. ",
    )
    entities: List[Union[ContextEntity, ContextEntityKeyValues]] = Field(
        description="an array of entities, each entity specified using the "
        "JSON entity representation format "
    )

    @field_validator("action_type")
    @classmethod
    def check_action_type(cls, action):
        """
        validates action_type
        Args:
            action: field action_type
        Returns:
            action_type
        """
        return ActionType(action)


class Command(BaseModel):
    """
    Class for sending commands to IoT Devices.
    Note that the command must be registered via an IoT-Agent. Internally
    FIWARE uses its registration mechanism in order to connect the command
    with an IoT-Device
    """

    type: DataType = Field(
        default=DataType.COMMAND,
        description="Command must have the type command",
        # const=True
    )
    value: Any = Field(
        description="Any json serializable command that will "
        "be forwarded to the connected IoT device"
    )

    @field_validator("value")
    @classmethod
    def check_value(cls, value):
        """
        Check if value is json serializable
        Args:
            value: value field
        Returns:
            value
        """
        try:
            json.dumps(value)
        except:
            raise ValueError(f"Command value {value} " f"is not serializable")
        return value


class NamedCommand(Command):
    """
    Class for sending command to IoT-Device.
    Extend :class: Command with command Name
    """

    name: str = Field(
        description="Name of the command",
        max_length=256,
        min_length=1,
    )
    valid_name = field_validator("name")(validate_fiware_datatype_string_protect)
