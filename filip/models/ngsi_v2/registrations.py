"""
This module contains NGSIv2 models for context registrations in the context
broker.
"""
from typing import List, Union, Optional
from datetime import datetime
from aenum import Enum
from pydantic import ConfigDict, BaseModel, Field
from filip.models.ngsi_v2.base import EntityPattern, Expression, Http, Status


class ForwardingMode(str, Enum):
    _init_ = 'value __doc__'

    NONE = "none", "This provider does not support request forwarding."
    QUERY = "query", "This provider only supports request forwarding to " \
                     "query data."
    UPDATE = "update", "This provider only supports request forwarding to " \
                       "update data."
    ALL = "all", "This provider supports both query and update forwarding " \
                 "requests. (Default value)"


class Provider(BaseModel):
    http: Http = Field(
        description="It is used to convey parameters for providers that "
                    "deliver information through the HTTP protocol. (Only "
                    "protocol supported nowadays). It must contain a subfield "
                    "named url with the URL that serves as the endpoint that "
                    "offers the providing interface. The endpoint must not "
                    "include the protocol specific part (for instance "
                    "/v2/entities). "
    )
    supportedForwardingMode: ForwardingMode = Field(
        default=ForwardingMode.ALL,
        description="It is used to convey the forwarding mode supported by "
                    "this context provider. By default all."
    )


class ForwardingInformation(BaseModel):
    model_config = ConfigDict(frozen=True)

    timesSent: int = Field(
        description="(not editable, only present in GET operations): "
                    "Number of forwarding requests sent due to this "
                    "registration."
    )
    lastForwarding: datetime = Field(
        description="(not editable, only present in GET operations): "
                    "Last forwarding timestamp in ISO8601 format."
    )
    lastFailure: Optional[datetime] = Field(
        default=None,
        description="(not editable, only present in GET operations): "
                    "Last failure timestamp in ISO8601 format. Not present "
                    "if registration has never had a problem with forwarding."
    )
    lastSuccess: Optional[datetime] = Field(
        default=None,
        description="(not editable, only present in GET operations): "
                    "Timestamp in ISO8601 format for last successful "
                    "request forwarding. Not present if registration has "
                    "never had a successful notification."
    )


class DataProvided(BaseModel):
    """
    Model for provided data
    """
    entities: List[EntityPattern] = Field(
        description="A list of objects, each one composed by an entity object"
    )
    attrs: Optional[List[str]] = Field(
        default=None,
        description="List of attributes to be provided "
                    "(if not specified, all attributes)"
    )
    expression: Optional[Union[str, Expression]] = Field(
        default=None,
        description="By means of a filtering expression, allows to express "
                    "what is the scope of the data provided. Currently only "
                    "geographical scopes are supported "
    )


class Registration(BaseModel):
    """
    A Context Registration allows to bind external context information
    sources so that they can play the role of providers of certain subsets
    (entities, attributes) of the context information space, including those
    located at specific geographical areas.
    """
    id: Optional[str] = Field(
        default=None,
        description="Unique identifier assigned to the registration. "
                    "Automatically generated at creation time."
    )
    description: Optional[str] = Field(
        default=None,
        description="A free text used by the client to describe the "
                    "registration.",
        example="Relative Humidity Context Source"
    )
    provider: Provider = Field(
        description="Object that describes the context source registered.",
        example='"http": {"url": "http://localhost:1234"}'
    )
    dataProvided: DataProvided = Field(
        description="Object that describes the data provided by this source",
        example='{'
                '   "entities": [{"id": "room2", "type": "Room"}],'
                '   "attrs": ["relativeHumidity"]'
                '},'
    )
    status: Optional[Status] = Field(
        default=Status.ACTIVE,
        description="Either active (for active registration) or inactive "
                    "(for inactive registration). If this field is not "
                    "provided at registration creation time, new registration "
                    "are created with the active status, which can be changed"
                    " by clients afterwards. For expired registration, this "
                    "attribute is set to expired (no matter if the client "
                    "updates it to active/inactive). Also, for subscriptions "
                    "experiencing problems with notifications, the status is "
                    "set to failed. As soon as the notifications start working "
                    "again, the status is changed back to active."
    )
    expires: Optional[datetime] = Field(
        default=None,
        description="Registration expiration date in ISO8601 format. "
                    "Permanent registrations must omit this field."
    )
    forwardingInformation: Optional[ForwardingInformation] = Field(
        default=None,
        description="Information related to the forwarding operations made "
                    "against the provider. Automatically provided by the "
                    "implementation, in the case such implementation supports "
                    "forwarding capabilities."
    )
