"""
This module contains NGSI-LD models for context subscription in the context
broker.
"""
from typing import Any, List, Dict, Union, Optional
from datetime import datetime
from aenum import Enum
from pydantic import \
    field_validator, model_validator, ConfigDict, BaseModel, \
    conint, \
    Field, \
    Json
from .base import AttrsFormat, EntityPattern, Http, Status, Expression
from filip.utils.validators import validate_mqtt_url, validate_mqtt_topic
from filip.models.ngsi_v2.context import ContextEntity
from filip.custom_types import AnyMqttUrl



class Subject(BaseModel):
    """
    Model for subscription subject
    """
    entities: List[EntityPattern] = Field(
        description="A list of objects, each one composed of by an Entity "
                    "Object:"
    )
    condition: Optional[Condition] = Field(
        default=None,
    )

class Subscription(BaseModel):
    """
    Subscription payload validations
    https://fiware-orion.readthedocs.io/en/master/user/ngsiv2_implementation_notes/index.html#subscription-payload-validations
    """
    model_config = ConfigDict(validate_assignment=True)

    id: Optional[str] = Field(
        default=None,
        description="Subscription unique identifier. Automatically created at "
                    "creation time."
    )
    description: Optional[str] = Field(
        default=None,
        description="A free text used by the client to describe the "
                    "subscription."
    )
    status: Optional[Status] = Field(
        default=Status.ACTIVE,
        description="Either active (for active subscriptions) or inactive "
                    "(for inactive subscriptions). If this field is not "
                    "provided at subscription creation time, new subscriptions "
                    "are created with the active status, which can be changed"
                    " by clients afterwards. For expired subscriptions, this "
                    "attribute is set to expired (no matter if the client "
                    "updates it to active/inactive). Also, for subscriptions "
                    "experiencing problems with notifications, the status is "
                    "set to failed. As soon as the notifications start working "
                    "again, the status is changed back to active."
    )
    data: Data = Field(
        description="An object that describes the subject of the subscription.",
        example={
            'entities': [{'type': 'FillingLevelSensor'}],
            'condition': {
                'watchedAttributes': ['filling'],
                'q': {'q': 'filling>0.4'},
            },
        },
    )

    notification: Notification = Field(
        description="An object that describes the notification to send when "
                    "the subscription is triggered.",
        example={
            'attributes': ["filling", "controlledAsset"],
            'format': 'normalized',
            'endpoint':{
                'uri': 'http://tutorial:3000/subscription/low-stock-farm001-ngsild',
                'accept': 'application/json'
            }
        },
    )
    
    expires: Optional[datetime] = Field(
        default=None,
        description="Subscription expiration date in ISO8601 format. "
                    "Permanent subscriptions must omit this field."
    )

    throttling: Optional[conint(strict=True, ge=0,)] = Field(
        default=None,
        strict=True,
        description="Minimal period of time in seconds which "
                    "must elapse between two consecutive notifications. "
                    "It is optional."
    )
