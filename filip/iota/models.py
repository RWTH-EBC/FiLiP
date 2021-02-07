from __future__ import annotations

from enum import Enum
from typing import Any, List, Dict, Optional
from pydantic import BaseModel, Field, validator, AnyHttpUrl












class DataType(Enum, str):
    """
    When possible reuse schema.org data types
    (Text, Number, DateTime, StructuredValue, etc.).
    Remember that null is not allowed in NGSI-LD and
    therefore should be avoided as a value.

    https://schema.org/DataType
    """
    Boolean = "Boolean"
    Date = "Date"
    DateTime = "DateTime"
    Number = "Number"
    Text = "Text"
    Time = "Time"


class Attribute(BaseModel):
    object_id: Optional[str] = Field(
        description="name of the attribute as coming from the device."
    )
    name: str = Field(
        description="ID of the attribute in the target entity in the "
                    "Context Broker."
    )
    type: DataType = Field(
        description="name of the type of the attribute in the target entity."
    )
    metadata: Dict[Any] = Field(
        description="additional static metadata for the attribute "
                    "in the target entity. (e.g. unitCode)"
    )
    expression: Optional[str] = Field(
        description="indicates that the value of the target attribute will "
                    "not be the plain value or the measurement, but an "
                    "expression based on a combination of the reported values. "
                    "See the Expression Language definition for details "
                    "(https://iotagent-node-lib.readthedocs.io/en/latest/expressionLanguage/index.html)"
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
                    "(https://iotagent-node-lib.readthedocs.io/en/latest/expressionLanguage/index.html)"
    )
    entity_type: Optional[str] = Field(
        description="configures the type of an alternative entity."
    )
    reverse: Optional[str] = Field(
        description="add bidirectionality expressions to the attribute. See "
                    "the bidirectionality transformation plugin in the "
                    "Data Mapping Plugins section for details. "
                    "(https://iotagent-node-lib.readthedocs.io/en/latest/api/index.html#data-mapping-plugins)"
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
        description="API Key string"
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
    lazy: Optional[Attribute]


class Device(BaseModel):
    device_id: str = Field(
        description="Device ID that will be used to identify the device")
    service: str = Field(
        description="Name of the service the device belongs to "
                    "(will be used in the fiware-service header).")
    service_path: str = Field(
        default="/",
        description="Name of the subservice the device belongs to "
                    "(used in the fiware-servicepath header).")
    entity_name: str = Field()
    entity_type: str
    protocol: str
    timezone: str
    attributes: List[Dict[str, Any]]
    static_attributes: List[Dict[str, Any]]

    @validator('service_path')
    def test_service_path(cls, v):
        assert v.startswith('/'), \
            "Service path must have a trailing slash ('/')"
        return v
