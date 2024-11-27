from typing import List, Optional, Literal
from pydantic import ConfigDict, BaseModel, Field, HttpUrl, AnyUrl, \
    field_validator, model_validator
import dateutil.parser
from filip.models.ngsi_ld.base import GeoQuery, validate_ngsi_ld_query


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
        description="Fully Qualified Name of an Entity Type or the Entity Type Name as a "
                    "short-hand string. See clause 4.6.2"
    )
    model_config = ConfigDict(populate_by_name=True)


class KeyValuePair(BaseModel):
    key: str
    value: str


class Endpoint(BaseModel):
    """
    This datatype represents the parameters that are required in order to define
    an endpoint for notifications. This can include the endpoint's URI, a
    generic{key, value} array, named receiverInfo, which contains, in a
    generalized form, whatever extra information the broker shall convey to the
    receiver in order for the broker to successfully communicate with
    receiver (e.g Authorization material), or for the receiver to correctly
    interpret the received content (e.g. the Link URL to fetch an @context).

    Additionally, it can include another generic{key, value} array, named
    notifierInfo, which contains the configuration that the broker needs to
    know in order to correctly set up the communication channel towards the
    receiver

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
    uri: AnyUrl = Field(
        description="Dereferenceable URI"
    )
    accept: Optional[str] = Field(
        default=None,
        description="MIME type for the notification payload body "
                    "(application/json, application/ld+json, "
                    "application/geo+json)"
    )
    receiverInfo: Optional[List[KeyValuePair]] = Field(
        default=None,
        description="Generic {key, value} array to convey optional information "
                    "to the receiver"
    )
    notifierInfo: Optional[List[KeyValuePair]] = Field(
        default=None,
        description="Generic {key, value} array to set up the communication "
                    "channel"
    )
    model_config = ConfigDict(populate_by_name=True)

    @field_validator("uri")
    @classmethod
    def check_uri(cls, uri: AnyUrl):
        if uri.scheme not in ("http", "mqtt"):
            raise ValueError("NGSI-LD currently only support http and mqtt")
        return uri

    @field_validator("notifierInfo")
    @classmethod
    def check_notifier_info(cls, notifierInfo: List[KeyValuePair]):
        # TODO add validation of notifierInfo for MQTT notification
        return notifierInfo


class NotificationParams(BaseModel):
    """
    NGSI-LD Notification model. It contains the parameters that allow to
    convey the details of a notification, as described in NGSI-LD Spec section 5.2.14
    """
    attributes: Optional[List[str]] = Field(
        default=None,
        description="Entity Attribute Names (Properties or Relationships) to be included "
                    "in the notification payload body. If undefined, it will mean all Attributes"
    )
    format: Optional[str] = Field(
        default="normalized",
        description="Conveys the representation format of the entities delivered at "
                    "notification time. By default, it will be in normalized format"
    )
    endpoint: Endpoint = Field(
        ...,
        description="Notification endpoint details"
    )
    # status can either be "ok" or "failed"
    status: Literal["ok", "failed"] = Field(
        default="ok",
        description="Status of the Notification. It shall be 'ok' if the last attempt "
                    "to notify the subscriber succeeded. It shall be 'failed' if the last"
                    " attempt to notify the subscriber failed"
    )

    # Additional members
    timesSent: Optional[int] = Field(
        default=None,
        description="Number of times that the notification was sent. Provided by the "
                    "system when querying the details of a subscription"
    )
    lastNotification: Optional[str] = Field(
        default=None,
        description="Timestamp corresponding to the instant when the last notification "
                    "was sent. Provided by the system when querying the details of a subscription"
    )
    lastFailure: Optional[str] = Field(
        default=None,
        description="Timestamp corresponding to the instant when the last notification"
                    " resulting in failure was sent. Provided by the system when querying the details of a subscription"
    )
    lastSuccess: Optional[str] = Field(
        default=None,
        description="Timestamp corresponding to the instant when the last successful "
                    "notification was sent. Provided by the system when querying the details of a subscription"
    )
    model_config = ConfigDict(populate_by_name=True)


class TemporalQuery(BaseModel):
    """
    Temporal query according to NGSI-LD Spec section 5.2.21

    timerel:
        Temporal relationship, one of "before", "after" and "between".
        "before": before the time specified by timeAt.
        "after": after the time specified by timeAt.
        "between": after the time specified by timeAt and before the time specified by
            endtimeAt
    timeAt:
        A DateTime object following ISO 8061, e.g. 2007-12-24T18:21Z
    endTimeAt (optional):
        A DateTime object following ISO 8061, e.g. 2007-12-24T18:21Z
        Only required when timerel="between"
    timeproperty: str
        Representing a Propertyname of the Property that contains the temporal data that
        will be used to resolve the temporal query. If not specified, the default is
        "observedAt"

    """
    model_config = ConfigDict(populate_by_name=True)
    timerel: Literal['before', 'after', 'between'] = Field(
        ...,
        description="String representing the temporal relationship as defined by clause "
                    "4.11 (Allowed values: 'before', 'after', and 'between') "
    )
    timeAt: str = Field(
        ...,
        description="String representing the timeAt parameter as defined by clause "
                    "4.11. It shall be a DateTime "
    )
    endTimeAt: Optional[str] = Field(
        default=None,
        description="String representing the endTimeAt parameter as defined by clause "
                    "4.11. It shall be a DateTime. Cardinality shall be 1 if timerel is "
                    "equal to 'between' "
    )
    timeproperty: Optional[str] = Field(
        default=None,
        description="String representing a Property name. The name of the Property that "
                    "contains the temporal data that will be used to resolve the "
                    "temporal query. If not specified, "
    )

    @field_validator("timeAt", "endTimeAt")
    @classmethod
    def check_uri(cls, v: str):
        if not v:
            return v
        else:
            try:
                dateutil.parser.isoparse(v)
            except ValueError:
                raise ValueError("timeAt must be in ISO8061 format")
            return v

    # when timerel=between, endTimeAt must be specified
    @model_validator(mode='after')
    def check_passwords_match(self) -> 'TemporalQuery':
        if self.timerel == "between" and self.endTimeAt is None:
            raise ValueError('When timerel="between", endTimeAt must be specified')
        return self


class SubscriptionLD(BaseModel):
    """
    Context Subscription model according to NGSI-LD Spec section 5.2.12
    """
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
    @field_validator("q")
    @classmethod
    def check_q(cls, v: str):
        return validate_ngsi_ld_query(v)
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
    lang: Optional[str] = Field(
        default=None,
        description="Language filter applied to the query"
    )
    model_config = ConfigDict(populate_by_name=True)
