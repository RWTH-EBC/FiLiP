from typing import List, Optional, Union
from pydantic import BaseModel, Field, HttpUrl


class EntityInfo(BaseModel):
    """
    In v1.3.1 it is specified as EntityInfo
    In v1.6.1 it is specified in a new data type, namely EntitySelector
    """
    id: Optional[HttpUrl] = Field(
        default=None,
        description="Entity identifier (valid URI)"
    )
    idPattern: Optional[str] = Field(
        default=None,
        description="Regular expression as per IEEE POSIX 1003.2™ [11]"
    )
    type: str = Field(
        ...,
        description="Fully Qualified Name of an Entity Type or the Entity Type Name as a short-hand string. See clause 4.6.2"
    )

    class Config:
        allow_population_by_field_name = True


class GeoQuery(BaseModel):
    geometry: str = Field(
        description="A valid GeoJSON [8] geometry, type excepting GeometryCollection"
    )
    coordinates: Union[list, str] = Field(
        description="A JSON Array coherent with the geometry type as per IETF RFC 7946 [8]"
    )
    georel: str = Field(
        description="A valid geo-relationship as defined by clause 4.10 (near, within, etc.)"
    )
    geoproperty: Optional[str] = Field(
        default=None,
        description="Attribute Name as a short-hand string"
    )

    class Config:
        allow_population_by_field_name = True


class KeyValuePair(BaseModel):
    key: str
    value: str


class Endpoint(BaseModel):
    """
    Example of "receiverInfo"
        "receiverInfo": [
            {
              "key": "H1",
              "value": "123"
            },
            {
              "key": "H2",
              "value": "456"
            }
          ]
    Example of "notifierInfo"
        "notifierInfo": [
            {
              "key": "MQTT-Version",
              "value": "mqtt5.0"
            }
          ]
    """
    uri: HttpUrl = Field(
        ...,
        description="Dereferenceable URI"
    )
    accept: Optional[str] = Field(
        default=None,
        description="MIME type for the notification payload body (application/json, application/ld+json, application/geo+json)"
    )
    receiverInfo: Optional[List[KeyValuePair]] = Field(
        default=None,
        description="Generic {key, value} array to convey optional information to the receiver"
    )
    notifierInfo: Optional[List[KeyValuePair]] = Field(
        default=None,
        description="Generic {key, value} array to set up the communication channel"
    )

    class Config:
        allow_population_by_field_name = True


class NotificationParams(BaseModel):
    attributes: Optional[List[str]] = Field(
        default=None,
        description="Entity Attribute Names (Properties or Relationships) to be included in the notification payload body. If undefined, it will mean all Attributes"
    )
    format: Optional[str] = Field(
        default="normalized",
        description="Conveys the representation format of the entities delivered at notification time. By default, it will be in normalized format"
    )
    endpoint: Endpoint = Field(
        ...,
        description="Notification endpoint details"
    )
    status: Optional[str] = Field(
        default=None,
        description="Status of the Notification. It shall be 'ok' if the last attempt to notify the subscriber succeeded. It shall be 'failed' if the last attempt to notify the subscriber failed"
    )

    # Additional members
    timesSent: Optional[int] = Field(
        default=None,
        description="Number of times that the notification was sent. Provided by the system when querying the details of a subscription"
    )
    lastNotification: Optional[str] = Field(
        default=None,
        description="Timestamp corresponding to the instant when the last notification was sent. Provided by the system when querying the details of a subscription"
    )
    lastFailure: Optional[str] = Field(
        default=None,
        description="Timestamp corresponding to the instant when the last notification resulting in failure was sent. Provided by the system when querying the details of a subscription"
    )
    lastSuccess: Optional[str] = Field(
        default=None,
        description="Timestamp corresponding to the instant when the last successful notification was sent. Provided by the system when querying the details of a subscription"
    )

    class Config:
        allow_population_by_field_name = True


class TemporalQuery(BaseModel):
    timerel: str = Field(
        ...,
        description="String representing the temporal relationship as defined by clause 4.11 (Allowed values: 'before', 'after', and 'between')"
    )
    timeAt: str = Field(
        ...,
        description="String representing the timeAt parameter as defined by clause 4.11. It shall be a DateTime"
    )
    endTimeAt: Optional[str] = Field(
        default=None,
        description="String representing the endTimeAt parameter as defined by clause 4.11. It shall be a DateTime. Cardinality shall be 1 if timerel is equal to 'between'"
    )
    timeproperty: Optional[str] = Field(
        default=None,
        description="String representing a Property name. The name of the Property that contains the temporal data that will be used to resolve the temporal query. If not specified,"
    )

    class Config:
        allow_population_by_field_name = True


class Subscription(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="Subscription identifier (JSON-LD @id)"
    )
    type: str = Field(
        default="Subscription",
        description="JSON-LD @type"
    )
    subscriptionName: Optional[str] = Field(
        default=None

        ,
        description="A (short) name given to this Subscription"
    )
    description: Optional[str] = Field(
        default=None,
        description="Subscription description"
    )
    entities: Optional[List[EntityInfo]] = Field(
        default=None,
        description="Entities subscribed"
    )
    watchedAttributes: Optional[List[str]] = Field(
        default=None,
        description="Watched Attributes (Properties or Relationships)"
    )
    notificationTrigger: Optional[List[str]] = Field(
        default=None,
        description="Notification triggers"
    )
    timeInterval: Optional[int] = Field(
        default=None,
        description="Time interval in seconds"
    )
    q: Optional[str] = Field(
        default=None,
        description="Query met by subscribed entities to trigger the notification"
    )
    geoQ: Optional[GeoQuery] = Field(
        default=None,
        description="Geoquery met by subscribed entities to trigger the notification"
    )
    csf: Optional[str] = Field(
        default=None,
        description="Context source filter"
    )
    isActive: bool = Field(
        default=True,
        description="Indicates if the Subscription is under operation (True) or paused (False)"
    )
    notification: NotificationParams = Field(
        ...,
        description="Notification details"
    )
    expiresAt: Optional[str] = Field(
        default=None,
        description="Expiration date for the subscription"
    )
    throttling: Optional[int] = Field(
        default=None,
        description="Minimal period of time in seconds between two consecutive notifications"
    )
    temporalQ: Optional[TemporalQuery] = Field(
        default=None,
        description="Temporal Query"
    )
    scopeQ: Optional[str] = Field(
        default=None,
        description="Scope query"
    )
    lang: Optional[str] = Field(
        default=None,
        description="Language filter applied to the query"
    )

    class Config:
        allow_population_by_field_name = True
