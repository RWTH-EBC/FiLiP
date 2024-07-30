"""
Module contains models for accessing and interaction with FIWARE's IoT-Agents.
"""
from __future__ import annotations
import logging
import itertools
import warnings
from enum import Enum
from typing import Any, Dict, Optional, List, Union
import pytz
from pydantic import field_validator, model_validator, ConfigDict, BaseModel, Field, AnyHttpUrl
from filip.models.base import NgsiVersion, DataType
from filip.models.ngsi_v2.base import \
    BaseAttribute, \
    BaseValueAttribute, \
    BaseNameAttribute
from filip.utils.validators import (validate_fiware_datatype_string_protect,
                                    validate_fiware_datatype_standard,
                                    validate_jexl_expression,
                                    validate_expression_language)

logger = logging.getLogger()


class ExpressionLanguage(str, Enum):
    """
    Options for expression language
    """
    LEGACY = "legacy"
    JEXL = "jexl"


class PayloadProtocol(str, Enum):
    """
    Options for payload protocols
    """
    IOTA_JSON = "IoTA-JSON"
    IOTA_UL = "PDI-IoTA-UltraLight"
    LORAWAN = "LoRaWAN"


class TransportProtocol(str, Enum):
    """
    Options for transport protocols
    """
    MQTT = "MQTT"
    AMQP = "AMQP"
    HTTP = "HTTP"


class IoTABaseAttribute(BaseAttribute, BaseNameAttribute):
    """
    Base model for device attributes
    """

    expression: Optional[str] = Field(
        default=None,
        description="indicates that the value of the target attribute will "
                    "not be the plain value or the measurement, but an "
                    "expression based on a combination of the reported values. "
                    "See the Expression Language definition for details "
                    "(https://iotagent-node-lib.readthedocs.io/en/latest/"
                    "api.html#expression-language-support)"
    )
    entity_name: Optional[str] = Field(
        default=None,
        description="entity_name: the presence of this attribute indicates "
                    "that the value will not be stored in the original device "
                    "entity but in a new entity with an ID given by this "
                    "attribute. The type of this additional entity can be "
                    "configured with the entity_type attribute. If no type is "
                    "configured, the device entity type is used instead. "
                    "Entity names can be defined as expressions, using the "
                    "Expression Language definition "
                    "(https://iotagent-node-lib.readthedocs.io/en/latest/"
                    "api.html#expression-language-support). Allowed characters are"
                    " the ones in the plain ASCII set, except the following "
                    "ones: control characters, whitespace, &, ?, / and #.",
        max_length=256,
        min_length=1,
    )
    valid_entity_name = field_validator("entity_name")(validate_fiware_datatype_standard)
    entity_type: Optional[str] = Field(
        default=None,
        description="configures the type of an alternative entity. "
                    "Allowed characters "
                    "are the ones in the plain ASCII set, except the following "
                    "ones: control characters, whitespace, &, ?, / and #.",
        max_length=256,
        min_length=1,
    )
    valid_entity_type = field_validator("entity_type")(validate_fiware_datatype_standard)
    reverse: Optional[str] = Field(
        default=None,
        description="add bidirectionality expressions to the attribute. See "
                    "the bidirectionality transformation plugin in the "
                    "Data Mapping Plugins section for details. "
                    "(https://iotagent-node-lib.readthedocs.io/en/latest/api/"
                    "index.html#data-mapping-plugins)"
    )

    def __eq__(self, other):
        if isinstance(other, BaseAttribute):
            return self.name == other.name
        else:
            return self.model_dump() == other


class DeviceAttribute(IoTABaseAttribute):
    """
    Model for active device attributes
    """
    object_id: Optional[str] = Field(
        default=None,
        description="name of the attribute as coming from the device."
    )


class LazyDeviceAttribute(BaseNameAttribute):
    """
    Model for lazy device attributes
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


class DeviceCommand(BaseModel):
    """
    Model for commands
    """
    name: str = Field(
        description="ID of the attribute in the target entity in the "
                    "Context Broker. Allowed characters "
                    "are the ones in the plain ASCII set, except the following "
                    "ones: control characters, whitespace, &, ?, / and #.",
        max_length=256,
        min_length=1,
    )
    valid_name = field_validator("name")(validate_fiware_datatype_string_protect)
    type: Union[DataType, str] = Field(
        description="name of the type of the attribute in the target entity. ",
        default=DataType.COMMAND
    )


class StaticDeviceAttribute(IoTABaseAttribute, BaseValueAttribute):
    """
    Model for static device attributes
    """
    pass


class ServiceGroup(BaseModel):
    """
    Model for device service group.
    https://iotagent-node-lib.readthedocs.io/en/latest/api/index.html#service-group-api
    """
    service: Optional[str] = Field(
        default=None,
        description="ServiceGroup of the devices of this type"
    )
    subservice: Optional[str] = Field(
        default=None,
        description="Subservice of the devices of this type.",
        pattern="^/"
    )
    resource: str = Field(
        description="string representing the Southbound resource that will be "
                    "used to assign a type to a device  (e.g.: pathname in the "
                    "southbound port)."
    )
    apikey: str = Field(
        description="API Key string. It is a key used for devices belonging "
                    "to this service_group. If "", service_group does not use "
                    "apikey, but it must be specified."
    )
    timestamp: Optional[bool] = Field(
        default=None,
        description="Optional flag about whether or not to add the TimeInstant "
                    "attribute to the device entity created, as well as a "
                    "TimeInstant metadata to each attribute, with the current "
                    "timestamp. With NGSI-LD, the Standard observedAt "
                    "property-of-a-property is created instead."
    )
    entity_type: Optional[str] = Field(
        default=None,
        description="name of the Entity type to assign to the group. "
                    "Allowed characters "
                    "are the ones in the plain ASCII set, except the following "
                    "ones: control characters, whitespace, &, ?, / and #.",
        max_length=256,
        min_length=1,
    )
    valid_entity_type = field_validator("entity_type")(validate_fiware_datatype_standard)
    trust: Optional[str] = Field(
        default=None,
        description="trust token to use for secured access to the "
                    "Context Broker for this type of devices (optional; only "
                    "needed for secured scenarios)."
    )
    cbHost: Optional[AnyHttpUrl] = Field(
        default=None,
        description="Context Broker connection information. This options can "
                    "be used to override the global ones for specific types of "
                    "devices."
    )
    @field_validator('cbHost')
    @classmethod
    def validate_cbHost(cls, value):
        """
        convert cbHost to str
        Returns:
            timezone
        """
        return str(value) if value else value
    lazy: Optional[List[LazyDeviceAttribute]] = Field(
        default=[],
        desription="list of common lazy attributes of the device. For each "
                   "attribute, its name and type must be provided."
    )
    commands: Optional[List[DeviceCommand]] = Field(
        default=[],
        desription="list of common commands attributes of the device. For each "
                   "attribute, its name and type must be provided, additional "
                   "metadata is optional"
    )
    attributes: Optional[List[DeviceAttribute]] = Field(
        default=[],
        description="list of common commands attributes of the device. For "
                    "each attribute, its name and type must be provided, "
                    "additional metadata is optional."
    )
    static_attributes: Optional[List[StaticDeviceAttribute]] = Field(
        default=[],
        description="this attributes will be added to all the entities of this "
                    "group 'as is', additional metadata is optional."
    )
    internal_attributes: Optional[List[Dict[str, Any]]] = Field(
        default=[],
        description="optional section with free format, to allow specific "
                    "IoT Agents to store information along with the devices "
                    "in the Device Registry."
    )
    expressionLanguage: Optional[ExpressionLanguage] = Field(
        default=ExpressionLanguage.JEXL,
        description="optional boolean value, to set expression language used "
                    "to compute expressions, possible values are: "
                    "legacy or jexl, but legacy is deprecated. If it is set None, jexl is used."
    )
    valid_expressionLanguage = field_validator("expressionLanguage")(validate_expression_language)
    explicitAttrs: Optional[bool] = Field(
        default=False,
        description="optional boolean value, to support selective ignore "
                    "of measures so that IOTA does not progress. If not "
                    "specified default is false."
    )
    autoprovision: Optional[bool] = Field(
        default=True,
        description="optional boolean: If false, autoprovisioned devices "
                    "(i.e. devices that are not created with an explicit "
                    "provision operation but when the first measure arrives) "
                    "are not allowed in this group. "
                    "Default (in the case of omitting the field) is true."
    )
    ngsiVersion: Optional[NgsiVersion] = Field(
        default="v2",
        description="optional string value used in mixed mode to switch between"
                    " NGSI-v2 and NGSI-LD payloads. Possible values are: "
                    "v2 or ld. The default is v2. When not running in mixed "
                    "mode, this field is ignored.")
    defaultEntityNameConjunction: Optional[str] = Field(
        default=None,
        description="optional string value to set default conjunction string "
                    "used to compose a default entity_name when is not "
                    "provided at device provisioning time."
    )


class DeviceSettings(BaseModel):
    """
    Model for iot device settings
    """
    model_config = ConfigDict(validate_assignment=True)
    timezone: Optional[str] = Field(
        default='Europe/London',
        description="Time zone of the sensor if it has any"
    )
    timestamp: Optional[bool] = Field(
        default=None,
        description="Optional flag about whether or not to add the TimeInstant "
                    "attribute to the device entity created, as well as a "
                    "TimeInstant metadata to each attribute, with the current "
                    "timestamp. With NGSI-LD, the Standard observedAt "
                    "property-of-a-property is created instead."
    )
    apikey: Optional[str] = Field(
        default=None,
        description="Optional Apikey key string to use instead of group apikey"
    )
    endpoint: Optional[AnyHttpUrl] = Field(
        default=None,
        description="Endpoint where the device is going to receive commands, "
                    "if any."
    )
    protocol: Optional[Union[PayloadProtocol, str]] = Field(
        default=None,
        description="Name of the device protocol, for its use with an "
                    "IoT Manager."
    )
    transport: Optional[Union[TransportProtocol, str]] = Field(
        default=None,
        description="Name of the device transport protocol, for the IoT Agents "
                    "with multiple transport protocols."
    )
    expressionLanguage: Optional[ExpressionLanguage] = Field(
        default=ExpressionLanguage.JEXL,
        description="optional boolean value, to set expression language used "
                    "to compute expressions, possible values are: "
                    "legacy or jexl, but legacy is deprecated. If it is set None, jexl is used."
    )
    valid_expressionLanguage = field_validator("expressionLanguage")(validate_expression_language)
    explicitAttrs: Optional[bool] = Field(
        default=False,
        description="optional boolean value, to support selective ignore "
                    "of measures so that IOTA does not progress. If not "
                    "specified default is false."
    )


class Device(DeviceSettings):
    """
    Model for iot devices.
    https://iotagent-node-lib.readthedocs.io/en/latest/api/index.html#device-api
    """
    model_config = ConfigDict(validate_default=True, validate_assignment=True)
    device_id: str = Field(
        description="Device ID that will be used to identify the device"
    )
    service: Optional[str] = Field(
        default=None,
        description="Name of the service the device belongs to "
                    "(will be used in the fiware-service header).",
        max_length=50
    )
    service_path: Optional[str] = Field(
        default="/",
        description="Name of the subservice the device belongs to "
                    "(used in the fiware-servicepath header).",
        max_length=51,
        pattern="^/"
    )
    entity_name: str = Field(
        description="Name of the entity representing the device in "
                    "the Context Broker Allowed characters "
                    "are the ones in the plain ASCII set, except the following "
                    "ones: control characters, whitespace, &, ?, / and #.",
        max_length=256,
        min_length=1,
    )
    valid_entity_name = field_validator("entity_name")(validate_fiware_datatype_standard)
    entity_type: str = Field(
        description="Type of the entity in the Context Broker. "
                    "Allowed characters "
                    "are the ones in the plain ASCII set, except the following "
                    "ones: control characters, whitespace, &, ?, / and #.",
        max_length=256,
        min_length=1,
    )
    valid_entity_type = field_validator("entity_type")(validate_fiware_datatype_standard)
    lazy: List[LazyDeviceAttribute] = Field(
        default=[],
        description="List of lazy attributes of the device"
    )
    commands: List[DeviceCommand] = Field(
        default=[],
        desription="List of commands of the device"
    )
    attributes: List[DeviceAttribute] = Field(
        default=[],
        description="List of active attributes of the device"
    )
    static_attributes: Optional[List[StaticDeviceAttribute]] = Field(
        default=[],
        description="List of static attributes to append to the entity. All the"
                    " updateContext requests to the CB will have this set of "
                    "attributes appended."
    )
    internal_attributes: Optional[List[Dict[str, Any]]] = Field(
        default=[],
        description="List of internal attributes with free format for specific "
                    "IoT Agent configuration"
    )
    ngsiVersion: NgsiVersion = Field(
        default=NgsiVersion.v2,
        description="optional string value used in mixed mode to switch between"
                    " NGSI-v2 and NGSI-LD payloads. Possible values are: "
                    "v2 or ld. The default is v2. When not running in "
                    "mixed mode, this field is ignored.")

    @field_validator('timezone')
    @classmethod
    def validate_timezone(cls, value):
        """
        validate timezone
        Returns:
            timezone
        """
        assert value in pytz.all_timezones
        return value

    @model_validator(mode='after')
    def validate_device_attributes_expression(self):
        """
        Validates device attributes expressions based on the expression language (JEXL or Legacy, where Legacy is
        deprecated).

        Args:
            self: The Device instance.

        Returns:
            The Device instance after validation.
        """
        if self.expressionLanguage == ExpressionLanguage.JEXL:
            for attribute in self.attributes:
                if attribute.expression:
                    validate_jexl_expression(attribute.expression, attribute.name, self.device_id)
        elif self.expressionLanguage == ExpressionLanguage.LEGACY:
            warnings.warn(f"No validation for legacy expression language of Device {self.device_id}.")

        return self

    @model_validator(mode='after')
    def validate_duplicated_device_attributes(self):
        """
        Check whether device has identical attributes
        Args:
            self: dict of Device instance.

        Returns:
            The dict of Device instance after validation.
        """
        for i, attr in enumerate(self.attributes):
            for other_attr in self.attributes[:i] + self.attributes[i + 1:]:
                if attr.model_dump() == other_attr.model_dump():
                    raise ValueError(f"Duplicated attributes found: {attr.name}")
        return self

    @model_validator(mode='after')
    def validate_device_attributes_name_object_id(self):
        """
        Validate the device regarding the behavior with devices attributes.
        According to https://iotagent-node-lib.readthedocs.io/en/latest/api.html and
        based on our best practice, following rules are checked
            - name is required, but not necessarily unique
            - object_id is not required, if given must be unique, i.e. not equal to any
                existing object_id and name
        Args:
            self: dict of Device instance.

        Returns:
            The dict of Device instance after validation.
        """
        for i, attr in enumerate(self.attributes):
            for other_attr in self.attributes[:i] + self.attributes[i + 1:]:
                if attr.object_id and other_attr.object_id and \
                        attr.object_id == other_attr.object_id:
                    raise ValueError(f"object_id {attr.object_id} is not unique")
                if attr.object_id and attr.object_id == other_attr.name:
                    raise ValueError(f"object_id {attr.object_id} is not unique")
        return self

    def get_attribute(self, attribute_name: str) -> Union[DeviceAttribute,
                                                          LazyDeviceAttribute,
                                                          StaticDeviceAttribute,
                                                          DeviceCommand]:
        """

        Args:
            attribute_name:

        Returns:

        """
        for attribute in itertools.chain(self.attributes,
                                         self.lazy,
                                         self.static_attributes,
                                         self.internal_attributes,
                                         self.commands):
            if attribute.name == attribute_name:
                return attribute
        msg = f"Device: {self.device_id}: Could not " \
              f"find attribute with name {attribute_name}"
        logger.error(msg)
        raise KeyError(msg)

    def add_attribute(self,
                      attribute: Union[DeviceAttribute,
                                       LazyDeviceAttribute,
                                       StaticDeviceAttribute,
                                       DeviceCommand],
                      update: bool = False) -> None:
        """

        Args:
            attribute:
            update (bool): If 'True' and attribute does already exists tries
                to  update the attribute if not
        Returns:
            None
        """
        try:
            if type(attribute) == DeviceAttribute:
                if attribute.model_dump(exclude_none=True) in \
                        [attr.model_dump(exclude_none=True) for attr in self.attributes]:
                    raise ValueError

                self.attributes.append(attribute)
                self.__setattr__(name='attributes',
                                 value=self.attributes)
            elif type(attribute) == LazyDeviceAttribute:
                if attribute in self.lazy:
                    raise ValueError

                self.lazy.append(attribute)
                self.__setattr__(name='lazy',
                                 value=self.lazy)
            elif type(attribute) == StaticDeviceAttribute:
                if attribute in self.static_attributes:
                    raise ValueError

                self.static_attributes.append(attribute)
                self.__setattr__(name='static_attributes',
                                 value=self.static_attributes)
            elif type(attribute) == DeviceCommand:
                if attribute in self.commands:
                    raise ValueError

                self.commands.append(attribute)
                self.__setattr__(name='commands',
                                 value=self.commands)
            else:
                raise ValueError
        except ValueError:
            if update:
                self.update_attribute(attribute, append=False)
                logger.warning("Device: %s: Attribute already "
                               "exists. Will update: \n %s",
                               self.device_id, attribute.model_dump_json(indent=2))
            else:
                logger.error("Device: %s: Attribute already "
                             "exists: \n %s", self.device_id,
                             attribute.model_dump_json(indent=2))
                raise

    def update_attribute(self,
                         attribute: Union[DeviceAttribute,
                                          LazyDeviceAttribute,
                                          StaticDeviceAttribute,
                                          DeviceCommand],
                         append: bool = False) -> None:
        """
        Updates existing device attribute

        Args:
            attribute: Attribute to add to device configuration
            append (bool): Adds attribute if not exist

        Returns:
            None
        """
        try:
            if type(attribute) == DeviceAttribute:
                idx = self.attributes.index(attribute)
                self.attributes[idx].model_dump().update(attribute.model_dump())
            elif type(attribute) == LazyDeviceAttribute:
                idx = self.lazy.index(attribute)
                self.lazy[idx].model_dump().update(attribute.model_dump())
            elif type(attribute) == StaticDeviceAttribute:
                idx = self.static_attributes.index(attribute)
                self.static_attributes[idx].model_dump().update(attribute.model_dump())
            elif type(attribute) == DeviceCommand:
                idx = self.commands.index(attribute)
                self.commands[idx].model_dump().update(attribute.model_dump())
        except ValueError:
            if append:
                logger.warning("Device: %s: Could not find "
                               "attribute: \n %s",
                               self.device_id, attribute.model_dump_json(indent=2))
                self.add_attribute(attribute=attribute)
            else:
                msg = f"Device: {self.device_id}: Could not find "\
                      f"attribute: \n {attribute.model_dump_json(indent=2)}"
                raise KeyError(msg)

    def delete_attribute(self, attribute: Union[DeviceAttribute,
                                                LazyDeviceAttribute,
                                                StaticDeviceAttribute,
                                                DeviceCommand]):
        """
        Deletes attribute from device
        Args:
            attribute: ()

        Returns:

        """
        try:
            if type(attribute) == DeviceAttribute:
                self.attributes.remove(attribute)
            elif type(attribute) == LazyDeviceAttribute:
                self.lazy.remove(attribute)
            elif type(attribute) == StaticDeviceAttribute:
                self.static_attributes.remove(attribute)
            elif type(attribute) == DeviceCommand:
                self.commands.remove(attribute)
            else:
                raise ValueError
        except ValueError:
            logger.warning("Device: %s: Could not delete "
                           "attribute: \n %s",
                           self.device_id, attribute.model_dump_json(indent=2))
            raise

        logger.info("Device: %s: Attribute deleted! \n %s",
                    self.device_id, attribute.model_dump_json(indent=2))

    def get_command(self, command_name: str):
        """
        Short for self.get_attributes
        Args:
            command_name (str):
        Returns:

        """
        return self.get_attribute(attribute_name=command_name)

    def add_command(self, command: DeviceCommand, update: bool = False):
        """
        Short for self.add_attribute
        Args:
            command (DeviceCommand):
            update (bool): Update command if it already exists
        Returns:
        """
        self.add_attribute(attribute=command, update=update)

    def update_command(self, command: DeviceCommand, append: bool = False):
        """
        Short for self.update_attribute
        Args:
            command:
            append:
        Returns:
        """
        self.update_attribute(attribute=command, append=append)

    def delete_command(self, command: DeviceCommand):
        """
        Short for self.delete_attribute
        Args:
            command:

        Returns:
            None
        """
        self.delete_attribute(attribute=command)
