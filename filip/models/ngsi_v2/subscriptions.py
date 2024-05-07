"""
This module contains NGSIv2 models for context subscription in the context
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


class Message(BaseModel):
    """
    Model for a notification message, when sent to other NGSIv2-APIs
    """
    subscriptionId: Optional[str] = Field(
        default=None,
        description="Id of the subscription the notification comes from",
    )
    data: List[ContextEntity] = Field(
        description="is an array with the notification data itself which "
                    "includes the entity and all concerned attributes. Each "
                    "element in the array corresponds to a different entity. "
                    "By default, the entities are represented in normalized "
                    "mode. However, using the attrsFormat modifier, a "
                    "simplified representation mode can be requested."
    )


class HttpMethods(str, Enum):
    _init_ = 'value __doc__'

    POST = "POST", "Post Method"
    PUT = "PUT", "Put Method"
    PATCH = "PATCH", "Patch Method"


class HttpCustom(Http):
    """
    Model for custom notification patterns sent via HTTP
    """
    headers: Optional[Dict[str, Union[str, Json]]] = Field(
        default=None,
        description="a key-map of HTTP headers that are included in "
                    "notification messages."
    )
    qs: Optional[Dict[str, Union[str, Json]]] = Field(
        default=None,
        description="a key-map of URL query parameters that are included in "
                    "notification messages."
    )
    method: str = Field(
        default=HttpMethods.POST,
        description="the method to use when sending the notification "
                    "(default is POST). Only valid HTTP methods are allowed. "
                    "On specifying an invalid HTTP method, a 400 Bad Request "
                    "error is returned."
    )
    payload: Optional[str] = Field(
        default=None,
        description='the payload to be used in notifications. If omitted, the '
                    'default payload (see "Notification Messages" sections) '
                    'is used.'
    )


class Mqtt(BaseModel):
    """
    Model for notifications sent via MQTT
    https://fiware-orion.readthedocs.io/en/3.2.0/user/mqtt_notifications/index.html
    """
    url: Union[AnyMqttUrl, str] = Field(
        description='to specify the MQTT broker endpoint to use. URL must '
                    'start with mqtt:// and never contains a path (i.e. it '
                    'only includes host and port)')
    topic: str = Field(
        description='to specify the MQTT topic to use',
        )
    valid_type = field_validator("topic")(validate_mqtt_topic)
    qos: Optional[int] = Field(
        default=0,
        description='to specify the MQTT QoS value to use in the '
                    'notifications associated to the subscription (0, 1 or 2). '
                    'This is an optional field, if omitted then QoS 0 is used.',
        ge=0,
        le=2)
    user: Optional[str] = Field(
        default=None,
        description="username if required"
    )
    passwd: Optional[str] = Field(
        default=None,
        description="password if required"
    )

    @field_validator('url')
    @classmethod
    def check_url(cls, value):
        """
        Check if url has a valid structure
        Args:
            value: url to validate
        Returns:
            validated url
        """
        return validate_mqtt_url(url=value)


class MqttCustom(Mqtt):
    """
    Model for custom notification patterns sent via MQTT
    https://fiware-orion.readthedocs.io/en/3.2.0/user/mqtt_notifications/index.html
    """
    payload: Optional[str] = Field(
        default=None,
        description='the payload to be used in notifications. If omitted, the '
                    'default payload (see "Notification Messages" sections) '
                    'is used.'
    )


class Notification(BaseModel):
    """
    If the notification attributes are left empty, all attributes will be
    included in the notifications. Otherwise, only the specified ones will
    be included.
    """
    model_config = ConfigDict(validate_assignment=True)
    timesSent: Optional[Any] = Field(
        default=None,
        description="Not editable, only present in GET operations. "
                    "Number of notifications sent due to this subscription."
    )
    http: Optional[Http] = Field(
        default=None,
        description='It is used to convey parameters for notifications '
                    'delivered through the HTTP protocol. Cannot be used '
                    'together with "httpCustom, mqtt, mqttCustom"'
    )
    httpCustom: Optional[HttpCustom] = Field(
        default=None,
        description='It is used to convey parameters for notifications '
                    'delivered through the HTTP protocol. Cannot be used '
                    'together with "http"'
    )
    mqtt: Optional[Mqtt] = Field(
        default=None,
        description='It is used to convey parameters for notifications '
                    'delivered through the MQTT protocol. Cannot be used '
                    'together with "http, httpCustom, mqttCustom"'
    )
    mqttCustom: Optional[MqttCustom] = Field(
        default=None,
        description='It is used to convey parameters for notifications '
                    'delivered through the MQTT protocol. Cannot be used '
                    'together with "http, httpCustom, mqtt"'
    )
    attrs: Optional[List[str]] = Field(
        default=None,
        description='List of attributes to be included in notification '
                    'messages. It also defines the order in which attributes '
                    'must appear in notifications when attrsFormat value is '
                    'used (see "Notification Messages" section). An empty list '
                    'means that all attributes are to be included in '
                    'notifications. See "Filtering out attributes and '
                    'metadata" section for more detail.'
    )
    exceptAttrs: Optional[List[str]] = Field(
        default=None,
        description='List of attributes to be excluded from the notification '
                    'message, i.e. a notification message includes all entity '
                    'attributes except the ones listed in this field.'
    )
    attrsFormat: Optional[AttrsFormat] = Field(
        default=AttrsFormat.NORMALIZED,
        description='specifies how the entities are represented in '
                    'notifications. Accepted values are normalized (default), '
                    'keyValues or values. If attrsFormat takes any value '
                    'different than those, an error is raised. See detail in '
                    '"Notification Messages" section.'
    )
    metadata: Optional[Any] = Field(
        default=None,
        description='List of metadata to be included in notification messages. '
                    'See "Filtering out attributes and metadata" section for '
                    'more detail.'
    )
    onlyChangedAttrs: Optional[bool] = Field(
        default=False,
        description='Only supported by Orion Context Broker!'
                    'If set to true then notifications associated to the '
                    'subscription include only attributes that changed in the '
                    'triggering update request, in combination with the attrs '
                    'or exceptAttrs field. For instance, if attrs is '
                    '[A=1, B=2, C=3] and A=0 is updated. In case '
                    'onlyChangedAttrs=false, CB notifies [A=0, B=2, C=3].'
                    'In case onlyChangedAttrs=true, CB notifies '
                    '[A=0, B=null, C=null]. This '
    )

    @field_validator('httpCustom')
    def validate_http(cls, http_custom, values):
        if http_custom is not None:
            assert values['http'] is None
        return http_custom

    @field_validator('exceptAttrs')
    def validate_attr(cls, except_attrs, values):
        if except_attrs is not None:
            assert values['attrs'] is None
        return except_attrs

    @model_validator(mode='after')
    def validate_endpoints(self):
        if self.http is not None:
            assert all((v is None for k, v in self.model_dump().items() if k in [
                'httpCustom', 'mqtt', 'mqttCustom']))
        elif self.httpCustom is not None:
            assert all((v is None for k, v in self.model_dump().items() if k in [
                'http', 'mqtt', 'mqttCustom']))
        elif self.mqtt is not None:
            assert all((v is None for k, v in self.model_dump().items() if k in [
                'http', 'httpCustom', 'mqttCustom']))
        else:
            assert all((v is None for k, v in self.model_dump().items() if k in [
                'http', 'httpCustom', 'mqtt']))
        return self


class Response(Notification):
    """
    Server response model for notifications
    """
    timesSent: int = Field(
        description='(not editable, only present in GET operations): '
                    'Number of notifications sent due to this subscription.'
    )
    lastNotification: datetime = Field(
        description='(not editable, only present in GET operations): '
                    'Last notification timestamp in ISO8601 format.'
    )
    lastFailure: Optional[datetime] = Field(
        default = None,
        description='(not editable, only present in GET operations): '
                    'Last failure timestamp in ISO8601 format. Not present if '
                    'subscription has never had a problem with notifications.'
    )
    lastSuccess: Optional[datetime] = Field(
        default=None,
        description='(not editable, only present in GET operations): '
                    'Timestamp in ISO8601 format for last successful '
                    'notification. Not present if subscription has never '
                    'had a successful notification.'
    )


class Condition(BaseModel):
    """
    Notification rules are as follow:
    If attrs and expression are used, a notification is sent whenever one of
    the attributes in the attrs list changes and at the same time expression
    matches.
    If attrs is used and expression is not used, a notification is sent
    whenever any of the attributes in the attrs list changes.
    If attrs is not used and expression is used, a notification is sent
    whenever any of the attributes of the entity changes and at the same time
    expression matches.
    If neither attrs nor expression are used, a notification is sent whenever
    any of the attributes of the entity changes.

    """
    attrs: Optional[Union[str, List[str]]] = Field(
        default=None,
        description='array of attribute names'
    )
    expression: Optional[Union[str, Expression]] = Field(
        default=None,
        description='an expression composed of q, mq, georel, geometry and '
                    'coords (see "List entities" operation above about this '
                    'field).'
    )

    @field_validator('attrs')
    def check_attrs(cls, v):
        if isinstance(v, list):
            return v
        elif isinstance(v, str):
            return [v]
        else:
            raise TypeError()


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
    subject: Subject = Field(
        description="An object that describes the subject of the subscription.",
        example={
            'entities': [{'idPattern': '.*', 'type': 'Room'}],
            'condition': {
                'attrs': ['temperature'],
                'expression': {'q': 'temperature>40'},
            },
        },
    )
    notification: Notification = Field(
        description="An object that describes the notification to send when "
                    "the subscription is triggered.",
        example={
            'http': {'url': 'http://localhost:1234'},
            'attrs': ['temperature', 'humidity'],
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

