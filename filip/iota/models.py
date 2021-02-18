from __future__ import annotations

import pytz
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, validator, AnyHttpUrl
from filip.core.models import DataType


class ExpressionLanguage(str, Enum):
    legacy = "legacy"
    jexl = "jexl"


class NgsiVersion(str, Enum):
    v2 = "v2"
    ld = "ld"


class Protocol(str, Enum):
    IoTA_Json = "IoTA-JSON"
    IoTA_UL = "PDI-IoTA-UltraLight"
    LoRaWAN = "LoRaWAN"


class Transport(str, Enum):
    MQTT = "MQTT"
    AMQP = "AMQP"


class BaseAttribute(BaseModel):
    name: str = Field(
        description="ID of the attribute in the target entity in the "
                    "Context Broker."
    )
    type: DataType = Field(
        description="name of the type of the attribute in the target entity."
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
                    "expressionLanguage/index.html)"
    )
    entity_type: Optional[str] = Field(
        description="configures the type of an alternative entity."
    )
    reverse: Optional[str] = Field(
        description="add bidirectionality expressions to the attribute. See "
                    "the bidirectionality transformation plugin in the "
                    "Data Mapping Plugins section for details. "
                    "(https://iotagent-node-lib.readthedocs.io/en/latest/api/"
                    "index.html#data-mapping-plugins)"
    )


class Attribute(BaseAttribute):
    object_id: Optional[str] = Field(
        description="name of the attribute as coming from the device."
    )


class Command(Attribute):
    pass


class StaticAttribute(BaseAttribute):
    value: DataType = Field(
        description="Constant value for this attribute"
    )


class Service(BaseModel):
    service: str = Field(
        description="Service of the devices of this type"
    )
    subservice: str = Field(
        description="Subservice of the devices of this type."
    )
    resource: str = Field(
        default="/",
        description="string representing the Southbound resource that will be "
                    "used to assign a type to a device  (e.g.: pathname in the "
                    "southbound port)."
    )
    apikey: str = Field(
        default="1234",
        description="API Key string. It is a key used for devices belonging "
                    "to this service. If "", service does not use apikey, but "
                    "it must be specified."
    )
    timestamp: Optional[bool] = Field(
        description="Optional flag about whether or not to add the TimeInstant "
                    "attribute to the device entity created, as well as a "
                    "TimeInstant metadata to each attribute, with the current "
                    "timestamp. With NGSI-LD, the Standard observedAt "
                    "property-of-a-property is created instead."
    )
    entity_type: str = Field(
        description="name of the Entity type to assign to the group."
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
    lazy: Optional[Attribute] = Field(
        desription="list of common lazy attributes of the device. For each "
                   "attribute, its name and type must be provided."
    )
    commands: Optional[Command] = Field(
        desription="list of common commands attributes of the device. For each "
                   "attribute, its name and type must be provided, additional "
                   "metadata is optional"
    )
    attributes: Optional[Attribute] = Field(
        description="list of common commands attributes of the device. For "
                    "each attribute, its name and type must be provided, "
                    "additional metadata is optional."
    )
    static_attributes: Optional[StaticAttribute] = Field(
        description="this attributes will be added to all the entities of this "
                    "group 'as is', additional metadata is optional."
    )
    internal_attributes: Optional[Dict[str, Any]] = Field(
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
        description="Name of the service the device belongs to "
                    "(will be used in the fiware-service header)."
    )
    service_path: Optional[str] = Field(
        default="/",
        description="Name of the subservice the device belongs to "
                    "(used in the fiware-servicepath header).")
    entity_name: str = Field(
        description="Name of the entity representing the device in "
                    "the Context Broker"
    )
    entity_type: str = Field(
        description="Type of the entity in the Context Broker"
    )
    timezone: Optional[str] = Field(
        description="Time zone of the sensor if it has any"
    )
    timestamp: Optional[bool] = Field(
        description="Optional flag about whether or not to add the TimeInstant "
                    "attribute to the device entity created, as well as a "
                    "TimeInstant metadata to each attribute, with the current "
                    "timestamp. With NGSI-LD, the Standard observedAt "
                    "property-of-a-property is created instead."
    )
    apikey: str = Field(
        default="1234",
        description="API Key string. It is a key used for devices belonging "
                    "to this service. If "", service does not use apikey, but "
                    "it must be specified."
    )
    endpoint: Optional[AnyHttpUrl] = Field(
        description="Endpoint where the device is going to receive commands, "
                    "if any."
    )
    protocol: Optional[str] = Field(
        description="Name of the device protocol, for its use with an "
                    "IoT Manager."
    )
    transport: Optional[Transport] = Field(
        description="Name of the device transport protocol, for the IoT Agents "
                    "with multiple transport protocols."
    )
    lazy: Optional[Attribute] = Field(
        desription="List of lazy attributes of the device"
    )
    commands: Optional[Command] = Field(
        desription="List of commands of the device"
    )
    attributes: Optional[Attribute] = Field(
        description="List of active attributes of the device"
    )
    static_attributes: Optional[StaticAttribute] = Field(
        description="List of static attributes to append to the entity. All the"
                    " updateContext requests to the CB will have this set of "
                    "attributes appended."
    )
    internal_attributes: Optional[Dict[str, Any]] = Field(
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
            "Service path must have a trailing slash ('/')"
        return v

    @validator('timezone')
    def validate_timezone(cls, v):
        assert v in pytz.all_timezones
        return v


if __name__ == '__main__':
    device = Device(device_id="saf", entity_name="saf", entity_type="all")
    print(device.json(indent=2, skip_defaults=True))
