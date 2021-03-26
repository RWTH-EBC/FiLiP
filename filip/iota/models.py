from __future__ import annotations
import logging
import pytz
import itertools
import json
from enum import Enum
from typing import Any, Dict, Optional, List, Union
from pydantic import BaseModel, Field, validator, AnyHttpUrl
from filip.core.models import NgsiVersion, DataType, UnitCode


logger = logging.getLogger()

class ExpressionLanguage(str, Enum):
    LEGACY = "legacy"
    JEXL = "jexl"


class PayloadProtocol(str, Enum):
    IOTA_JSON = "IoTA-JSON"
    IOTA_UL = "PDI-IoTA-UltraLight"
    LORAWAN = "LoRaWAN"


class TransportProtocol(str, Enum):
    MQTT = "MQTT"
    AMQP = "AMQP"
    HTTP = "HTTP"


class BaseAttribute(BaseModel):
    name: str = Field(
        description="ID of the attribute in the target entity in the "
                    "Context Broker. Allowed characters "
                    "are the ones in the plain ASCII set, except the following "
                    "ones: control characters, whitespace, &, ?, / and #.",
        max_length = 256,
        min_length = 1,
        regex = "(^((?![?&#/])[\x00-\x7F])*$)(?!(id|type|geo:distance|\*))"
    )
    type: DataType = Field(
        description="name of the type of the attribute in the target entity. "
    )
    metadata: Optional[Dict[str, Any]] = Field(
        description="additional static metadata for the attribute "
                    "in the target entity. (e.g. unitCode)"
    )
    expression: Optional[str] = Field(
        description="indicates that the value of the target attribute will "
                    "not be the plain value or the measurement, but an "
                    "expression based on a combination of the reported values. "
                    "See the Expression Language definition for details "
                    "(https://iotagent-node-lib.readthedocs.io/en/latest/"
                    "expressionLanguage/index.html)"
    )
    entity_name: Optional[str] = Field(
        description="entity_name: the presence of this attribute indicates "
                    "that the value will not be stored in the original device "
                    "entity but in a new entity with an ID given by this "
                    "attribute. The type of this additional entity can be "
                    "configured with the entity_type attribute. If no type is "
                    "configured, the device entity type is used instead. "
                    "Entity names can be defined as expressions, using the "
                    "Expression Language definition. "
                    "(https://iotagent-node-lib.readthedocs.io/en/latest/"
                    "expressionLanguage/index.html) Allowed characters "
                    "are the ones in the plain ASCII set, except the following "
                    "ones: control characters, whitespace, &, ?, / and #.",
        max_length=256,
        min_length=1,
        regex="^((?![?&#/])[\x00-\x7F])*$" # Make it FIWARE-Safe"
    )
    entity_type: Optional[str] = Field(
        description="configures the type of an alternative entity. "
                    "Allowed characters "
                    "are the ones in the plain ASCII set, except the following "
                    "ones: control characters, whitespace, &, ?, / and #.",
        max_length=256,
        min_length=1,
        regex="^((?![?&#/])[\x00-\x7F])*$" # Make it FIWARE-Safe"
    )
    reverse: Optional[str] = Field(
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
            return self.dict == other


class DeviceAttribute(BaseAttribute):
    object_id: Optional[str] = Field(
        description="name of the attribute as coming from the device."
    )
    metadata: Optional[Dict[str, Dict]] = Field(
        description="Additional meta information for the attribute, "
                    "e.g. 'unitcode'"
    )

    @validator('metadata')
    def check_metadata(cls, v):
        assert json.dumps(v), "metadata not serializable"
        if v.get('unitcode', False):
            UnitCode(**v['unitcode'])

        return v


class LazyDeviceAttribute(DeviceAttribute):
    pass


class DeviceCommand(BaseAttribute):
    pass


class StaticDeviceAttribute(BaseAttribute):
    value: Union[Dict, List, str, float] = Field(
        description="Constant value for this attribute"
    )
    metadata: Optional[Dict[str, Dict]] = Field(
        description="Additional meta information for the attribute, "
                    "e.g. 'unitcode'"
    )





class ServiceGroup(BaseModel):
    service: Optional[str] = Field(
        description="ServiceGroup of the devices of this type"
    )
    subservice: Optional[str] = Field(
        description="Subservice of the devices of this type."
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
        description="Optional flag about whether or not to add the TimeInstant "
                    "attribute to the device entity created, as well as a "
                    "TimeInstant metadata to each attribute, with the current "
                    "timestamp. With NGSI-LD, the Standard observedAt "
                    "property-of-a-property is created instead."
    )
    entity_type: str = Field(
        description="name of the Entity type to assign to the group. "
                    "Allowed characters "
                    "are the ones in the plain ASCII set, except the following "
                    "ones: control characters, whitespace, &, ?, / and #.",
        max_length=256,
        min_length=1,
        regex="^((?![?&#/])[\x00-\x7F])*$" # Make it FIWARE-Safe
    )
    trust: Optional[str] = Field(
        description="trust token to use for secured access to the "
                    "Context Broker for this type of devices (optional; only "
                    "needed for secured scenarios)."
    )
    cbHost: Optional[AnyHttpUrl] = Field(
        description="Context Broker connection information. This options can "
                    "be used to override the global ones for specific types of "
                    "devices."
    )
    lazy: Optional[List[LazyDeviceAttribute]] = Field(
        desription="list of common lazy attributes of the device. For each "
                   "attribute, its name and type must be provided."
    )
    commands: Optional[List[DeviceCommand]] = Field(
        desription="list of common commands attributes of the device. For each "
                   "attribute, its name and type must be provided, additional "
                   "metadata is optional"
    )
    attributes: Optional[List[DeviceAttribute]] = Field(
        description="list of common commands attributes of the device. For "
                    "each attribute, its name and type must be provided, "
                    "additional metadata is optional."
    )
    static_attributes: Optional[List[StaticDeviceAttribute]] = Field(
        description="this attributes will be added to all the entities of this "
                    "group 'as is', additional metadata is optional."
    )
    internal_attributes: Optional[List[Dict[str, Any]]] = Field(
        description="optional section with free format, to allow specific "
                    "IoT Agents to store information along with the devices "
                    "in the Device Registry."
    )
    expressionLanguage: Optional[ExpressionLanguage] = Field(
        description="optional boolean value, to set expression language used "
                    "to compute expressions, possible values are: "
                    "legacy or jexl. When not set or wrongly set, legacy "
                    "is used as default value."
    )
    explicitAttrs: Optional[bool] = Field(
        description="optional boolean value, to support selective ignore "
                    "of measures so that IOTA doesn’t progress. If not "
                    "specified default is false."
    )
    ngsiVersion: Optional[NgsiVersion] = Field(
        description="optional string value used in mixed mode to switch between"
                    " NGSI-v2 and NGSI-LD payloads. Possible values are: "
                    "v2 or ld. The default is v2. When not running in mixed "
                    "mode, this field is ignored.")
    defaultEntityNameConjunction: Optional[str] = Field(
        description="optional string value to set default conjunction string "
                    "used to compose a default entity_name when is not "
                    "provided at device provisioning time."
    )

    @validator('subservice')
    def validate_service_path(cls, v):
        assert v.startswith('/'), \
            "Subservice must have a trailing slash ('/')"
        return v


class Device(BaseModel):
    device_id: str = Field(
        description="Device ID that will be used to identify the device"
    )
    service: Optional[str] = Field(
        description="Name of the service_group the device belongs to "
                    "(will be used in the fiware-service_group header).",
        max_length=50
    )
    service_path: Optional[str] = Field(
        default="/",
        description="Name of the subservice the device belongs to "
                    "(used in the fiware-servicepath header).",
        max_length=51
    )
    entity_name: str = Field(
        description="Name of the entity representing the device in "
                    "the Context Broker Allowed characters "
                    "are the ones in the plain ASCII set, except the following "
                    "ones: control characters, whitespace, &, ?, / and #.",
        max_length=256,
        min_length=1,
        regex="^((?![?&#/])[\x00-\x7F])*$" # Make it FIWARE-Safe"
    )
    entity_type: str = Field(
        description="Type of the entity in the Context Broker. "
                    "Allowed characters "
                    "are the ones in the plain ASCII set, except the following "
                    "ones: control characters, whitespace, &, ?, / and #.",
        max_length=256,
        min_length=1,
        regex="^((?![?&#/])[\x00-\x7F])*$" # Make it FIWARE-Safe"
    )
    timezone: Optional[str] = Field(
        default='Europe/London',
        description="Time zone of the sensor if it has any"
    )
    timestamp: Optional[bool] = Field(
        description="Optional flag about whether or not to add the TimeInstant "
                    "attribute to the device entity created, as well as a "
                    "TimeInstant metadata to each attribute, with the current "
                    "timestamp. With NGSI-LD, the Standard observedAt "
                    "property-of-a-property is created instead."
    )
    apikey: Optional[str] = Field(
        description="Optional Apikey key string to use instead of group apikey"
    )
    endpoint: Optional[AnyHttpUrl] = Field(
        description="Endpoint where the device is going to receive commands, "
                    "if any."
    )
    protocol: Optional[str] = Field(
        description="Name of the device protocol, for its use with an "
                    "IoT Manager."
    )
    transport: Optional[TransportProtocol] = Field(
        description="Name of the device transport protocol, for the IoT Agents "
                    "with multiple transport protocols."
    )
    lazy: Optional[List[DeviceAttribute]] = Field(
        desription="List of lazy attributes of the device"
    )
    commands: Optional[List[DeviceCommand]] = Field(
        desription="List of commands of the device"
    )
    attributes: Optional[List[DeviceAttribute]] = Field(
        description="List of active attributes of the device"
    )
    static_attributes: Optional[List[StaticDeviceAttribute]] = Field(
        description="List of static attributes to append to the entity. All the"
                    " updateContext requests to the CB will have this set of "
                    "attributes appended."
    )
    internal_attributes: Optional[List[Dict[str, Any]]] = Field(
        description="List of internal attributes with free format for specific "
                    "IoT Agent configuration"
    )
    expressionLanguage: Optional[ExpressionLanguage] = Field(
        description="optional boolean value, to set expression language used "
                    "to compute expressions, possible values are: "
                    "legacy or jexl. When not set or wrongly set, legacy "
                    "is used as default value."
    )
    explicitAttrs: Optional[bool] = Field(
        description="optional boolean value, to support selective ignore "
                    "of measures so that IOTA doesn’t progress. If not "
                    "specified default is false."
    )
    ngsiVersion: Optional[NgsiVersion] = Field(
        description="optional string value used in mixed mode to switch between"
                    " NGSI-v2 and NGSI-LD payloads. Possible values are: "
                    "v2 or ld. The default is v2. When not running in "
                    "mixed mode, this field is ignored.")

    @validator('service_path')
    def validate_service_path(cls, v):
        assert v.startswith('/'), \
            "ServiceGroup path must have a trailing slash ('/')"
        return v

    @validator('timezone')
    def validate_timezone(cls, v):
        assert v in pytz.all_timezones
        return v

    def get_attribute(self, attribute_name: str) -> Union[DeviceAttribute,
        LazyDeviceAttribute, StaticDeviceAttribute]:
        """

        Args:
            attribute_name:

        Returns:

        """
        for attribute in itertools.chain(self.attributes,
                                         self.lazy,
                                         self.static_attributes,
                                         self.internal_attributes):
            if attribute.name == attribute_name:
                return attribute
        logger.error(f"Device: {self.device_id}: Could not find "
                     f"attribute with name {attribute_name}")
        raise KeyError


    def add_attribute(self,
                      attribute: Union[DeviceAttribute,
                                       LazyDeviceAttribute,
                                       StaticDeviceAttribute],
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
            if isinstance(attribute, DeviceAttribute):
                if attribute in self.attributes:
                    raise ValueError
                else:
                    self.attributes.append(attribute)
            elif isinstance(attribute, LazyDeviceAttribute):
                if attribute in self.lazy:
                    raise ValueError
                else:
                    self.lazy.append(attribute)
            elif isinstance(attribute, StaticDeviceAttribute):
                if attribute in self.static_attributes:
                    raise ValueError
                else:
                    self.static_attributes.append(attribute)
        except ValueError:
            if update:
                self.update_attribute(attribute, add=False)
                logger.warning(f"Device: {self.device_id}: Attribute already "
                               f"exists. Will update: \n"
                               f" {attribute.json(indent=2)}")
            else:
                logger.error(f"Device: {self.device_id}: Attribute already "
                             f"exists: \n {attribute.json(indent=2)}")
                raise ValueError


    def update_attribute(self, attribute: Union[DeviceAttribute,
                                                LazyDeviceAttribute,
                                                StaticDeviceAttribute],
                         add: bool = False) -> None:
        """
        Updates existing device attribute
        Args:
            attribute: Attribute to add to device configuration
            add (bool): Adds attribute if not exist

        Returns:
            None
        """
        try:
            if isinstance(attribute, DeviceAttribute):
                idx = self.attributes.index(attribute)
                self.attributes[idx].dict().update(attribute.dict())
            elif isinstance(attribute, LazyDeviceAttribute):
                idx = self.lazy.index(attribute)
                self.lazy[idx].dict().update(attribute.dict())
            elif isinstance(attribute, StaticDeviceAttribute):
                idx = self.static_attributes.index(attribute)
                self.static_attributes[idx].dict().update(attribute.dict())
        except ValueError:
            if add:
                logger.warning(f"Device: {self.device_id}: Could not find "
                               f"attribute: \n {attribute.json(indent=2)}")
                self.add_attribute(attribute=attribute)

            else:
                logger.error(f"Device: {self.device_id}: Could not find "
                             f"attribute: \n {attribute.json(indent=2)}")
                raise KeyError

    def delete_attribute(self, attribute: Union[DeviceAttribute,
                                                LazyDeviceAttribute,
                                                StaticDeviceAttribute]):
        """
        Deletes attribute from device
        Args:
            attribute: ()

        Returns:

        """
        try:
            if isinstance(attribute, DeviceAttribute):
                self.attributes.remove(attribute)
            elif isinstance(attribute, LazyDeviceAttribute):
                self.lazy.remove(attribute)
            elif isinstance(attribute, StaticDeviceAttribute):
                self.static_attributes.remove(attribute)
        except ValueError:
            logger.warning(f"Device: {self.device_id}: Could not delete "
                           f"attribute: \n {attribute.json(indent=2)}")
        logger.info(f"Device: {self.device_id}: Attribute deleted! \n"
                    f"{attribute.json(indent=2)}")