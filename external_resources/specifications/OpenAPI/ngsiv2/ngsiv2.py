# generated by datamodel-codegen:
#   filename:  ngsiv2-openapi.json
#   timestamp: 2020-12-04T10:07:39+00:00

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Model(BaseModel):
    __root__: Any


class RetrieveApiResourcesResponse(BaseModel):
    entities_url: str = Field(
        ...,
        description='URL which points to the entities resource',
        example='/v2/entities',
    )
    types_url: str = Field(
        ..., description='URL which points to the types resource', example='/v2/types'
    )
    subscriptions_url: str = Field(
        ...,
        description='URL which points to the\nsubscriptions resource',
        example='/v2/subscriptions',
    )
    registrations_url: str = Field(
        ...,
        description='URL which points to the\nregistrations resource',
        example='/v2/registrations',
    )


class Options(Enum):
    count = 'count'
    keyValues = 'keyValues'
    values = 'values'
    unique = 'unique'


class ListEntitiesResponse(BaseModel):
    type: str = Field(..., description='', example='Room')
    id: str = Field(..., description='', example='DC_S1-D41')
    temperature: Optional[Dict[str, Any]] = Field(
        None, description='', example={'value': 35.6, 'type': 'Number', 'metadata': {}}
    )
    speed: Optional[Dict[str, Any]] = Field(
        None,
        description='',
        example={
            'value': 100,
            'type': 'number',
            'metadata': {
                'accuracy': {'value': 2, 'type': 'Number'},
                'timestamp': {'value': '2015-06-04T07:20:27.378Z', 'type': 'DateTime'},
            },
        },
    )


class Options3(Enum):
    keyValues = 'keyValues'
    upsert = 'upsert'


class CreateEntityRequest(BaseModel):
    type: str = Field(..., description='', example='Room')
    id: str = Field(..., description='', example='Bcn-Welt')
    temperature: Dict[str, Any] = Field(..., description='', example={'value': 21.7})
    humidity: Dict[str, Any] = Field(..., description='', example={'value': 60})
    location: Dict[str, Any] = Field(
        ...,
        description='',
        example={
            'value': '41.3763726, 2.1864475',
            'type': 'geo:point',
            'metadata': {'crs': {'value': 'WGS84'}},
        },
    )


class Options6(Enum):
    keyValues = 'keyValues'
    values = 'values'
    unique = 'unique'


class RetrieveEntityResponse(BaseModel):
    type: str = Field(..., description='', example='Room')
    id: str = Field(..., description='', example='Bcn_Welt')
    temperature: Dict[str, Any] = Field(
        ..., description='', example={'value': 21.7, 'type': 'Number'}
    )
    humidity: Dict[str, Any] = Field(
        ..., description='', example={'value': 60, 'type': 'Number'}
    )
    location: Dict[str, Any] = Field(
        ...,
        description='',
        example={
            'value': '41.3763726, 2.1864475',
            'type': 'geo:point',
            'metadata': {'crs': {'value': 'WGS84', 'type': 'Text'}},
        },
    )


class RetrieveEntityAttributesResponse(BaseModel):
    temperature: Dict[str, Any] = Field(
        ..., description='', example={'value': 21.7, 'type': 'Number'}
    )
    humidity: Dict[str, Any] = Field(
        ..., description='', example={'value': 60, 'type': 'Number'}
    )
    location: Dict[str, Any] = Field(
        ...,
        description='',
        example={
            'value': '41.3763726, 2.1864475',
            'type': 'geo:point',
            'metadata': {'crs': {'value': 'WGS84', 'type': 'Text'}},
        },
    )


class Options10(Enum):
    append = 'append'
    keyValues = 'keyValues'


class UpdateOrAppendEntityAttributesRequest(BaseModel):
    ambientNoise: Dict[str, Any] = Field(..., description='', example={'value': 31.5})


class Options12(Enum):
    keyValues = 'keyValues'


class UpdateExistingEntityAttributesRequest(BaseModel):
    temperature: Dict[str, Any] = Field(..., description='', example={'value': 25.5})
    seatNumber: Dict[str, Any] = Field(..., description='', example={'value': 6})


class ReplaceAllEntityAttributesRequest(BaseModel):
    temperature: Dict[str, Any] = Field(..., description='', example={'value': 25.5})
    seatNumber: Dict[str, Any] = Field(..., description='', example={'value': 6})


class GetAttributeDataResponse(BaseModel):
    value: float = Field(..., description='', example=21.7)
    type: str = Field(..., description='', example='Number')
    metadata: Dict[str, Any] = Field(..., description='', example={})


class UpdateAttributeDataRequest(BaseModel):
    value: float = Field(..., description='', example=25)
    metadata: Dict[str, Any] = Field(
        ..., description='', example={'unitCode': {'value': 'CEL'}}
    )


class GetAttributeValueResponse(BaseModel):
    address: str = Field(..., description='', example='Ronda de la Comunicacion s/n')
    zipCode: int = Field(..., description='', example=28050)
    city: str = Field(..., description='', example='Madrid')
    country: str = Field(..., description='', example='Spain')


class UpdateAttributeValueRequest(BaseModel):
    address: str = Field(..., description='', example='Ronda de la Comunicacion s/n')
    zipCode: int = Field(..., description='', example=28050)
    city: str = Field(..., description='', example='Madrid')
    country: str = Field(..., description='', example='Spain')


class Options20(Enum):
    count = 'count'
    values = 'values'


class ListEntityTypesResponse(BaseModel):
    type: str = Field(..., description='', example='Car')
    attrs: Dict[str, Any] = Field(
        ...,
        description='',
        example={
            'speed': {'types': ['Number']},
            'fuel': {'types': ['gasoline', 'diesel']},
            'temperature': {'types': ['urn:phenomenum:temperature']},
        },
    )
    count: int = Field(..., description='', example=12)


class RetrieveEntityTypeResponse(BaseModel):
    attrs: Dict[str, Any] = Field(
        ...,
        description='',
        example={
            'pressure': {'types': ['Number']},
            'humidity': {'types': ['percentage']},
            'temperature': {'types': ['urn:phenomenum:temperature']},
        },
    )
    count: int = Field(..., description='', example=7)


class Options23(Enum):
    count = 'count'


class ListSubscriptionsResponse(BaseModel):
    id: str = Field(..., description='', example='abcdefg')
    description: str = Field(
        ..., description='', example='One subscription to rule them all'
    )
    subject: Dict[str, Any] = Field(
        ...,
        description='',
        example={
            'entities': [{'id': 'Bcn_Welt', 'type': 'Room'}],
            'condition': {
                'attrs': ['temperature '],
                'expression': {'q': 'temperature>40'},
            },
        },
    )
    notification: Dict[str, Any] = Field(
        ...,
        description='',
        example={
            'httpCustom': {
                'url': 'http://localhost:1234',
                'headers': {'X-MyHeader': 'foo'},
                'qs': {'authToken': 'bar'},
            },
            'attrsFormat': 'keyValues',
            'attrs': ['temperature', 'humidity'],
            'timesSent': 12,
            'lastNotification': '2015-10-05T16:00:00Z',
            'lastFailure': '2015-10-06T16:00:00Z',
        },
    )
    expires: str = Field(..., description='', example='4/5/2016 2:00:00 PM')
    status: str = Field(..., description='', example='failed')
    throttling: int = Field(..., description='', example=5)


class CreateSubscriptionRequest(BaseModel):
    description: Optional[str] = Field(
        None, description='', example='One subscription to rule them all'
    )
    subject: Dict[str, Any] = Field(
        ...,
        description='',
        example={
            'entities': [{'idPattern': '.*', 'type': 'Room'}],
            'condition': {
                'attrs': ['temperature'],
                'expression': {'q': 'temperature>40'},
            },
        },
    )
    notification: Dict[str, Any] = Field(
        ...,
        description='',
        example={
            'http': {'url': 'http://localhost:1234'},
            'attrs': ['temperature', 'humidity'],
        },
    )
    expires: Optional[str] = Field(None, description='', example='4/5/2016 2:00:00 PM')
    throttling: Optional[int] = Field(None, description='', example=5)


class UpdateSubscriptionRequest(BaseModel):
    expires: str = Field(..., description='', example='4/5/2016 2:00:00 PM')


class ListRegistrationsResponse(BaseModel):
    id: str = Field(..., description='', example='abcdefg')
    description: str = Field(..., description='', example='Example Context Source')
    dataProvided: Dict[str, Any] = Field(
        ...,
        description='',
        example={
            'entities': [{'id': 'Bcn_Welt', 'type': 'Room'}],
            'attrs': ['temperature'],
        },
    )
    provider: Dict[str, Any] = Field(
        ...,
        description='',
        example={
            'http': {'url': 'http://contextsource.example.org'},
            'supportedForwardingMode': 'all',
        },
    )
    expires: str = Field(..., description='', example='10/31/2017 12:00:00 PM')
    status: str = Field(..., description='', example='active')
    forwardingInformation: Dict[str, Any] = Field(
        ...,
        description='',
        example={
            'timesSent': 12,
            'lastForwarding': '2017-10-06T16:00:00Z',
            'lastSuccess': '2017-10-06T16:00:00Z',
            'lastFailure': '2017-10-05T16:00:00Z',
        },
    )


class CreateRegistrationRequest(BaseModel):
    description: str = Field(
        ..., description='', example='Relative Humidity Context Source'
    )
    dataProvided: Dict[str, Any] = Field(
        ...,
        description='',
        example={
            'entities': [{'id': 'room2', 'type': 'Room'}],
            'attrs': ['relativeHumidity'],
        },
    )
    provider: Dict[str, Any] = Field(
        ..., description='', example={'http': {'url': 'http://localhost:1234'}}
    )


class RetrieveRegistrationResponse(BaseModel):
    id: str = Field(..., description='', example='abcdefg')
    description: str = Field(..., description='', example='Example Context Source')
    dataProvided: Dict[str, Any] = Field(
        ...,
        description='',
        example={
            'entities': [{'id': 'Bcn_Welt', 'type': 'Room'}],
            'attrs': ['temperature'],
        },
    )
    provider: Dict[str, Any] = Field(
        ...,
        description='',
        example={
            'http': {'url': 'http://contextsource.example.org'},
            'supportedForwardingMode': 'all',
        },
    )
    expires: str = Field(..., description='', example='10/31/2017 12:00:00 PM')
    status: str = Field(..., description='', example='failed')
    forwardingInformation: Dict[str, Any] = Field(
        ...,
        description='',
        example={
            'timesSent': 12,
            'lastForwarding': '2017-10-06T16:00:00Z',
            'lastFailure': '2017-10-06T16:00:00Z',
            'lastSuccess': '2017-10-05T18:25:00Z',
        },
    )


class UpdateRegistrationRequest(BaseModel):
    expires: str = Field(..., description='', example='10/4/2017 12:00:00 AM')


class UpdateRequest(BaseModel):
    actionType: str = Field(..., description='', example='append')
    entities: List[Dict[str, Any]] = Field(
        ...,
        description='',
        example=[
            {
                'type': 'Room',
                'id': 'Bcn-Welt',
                'temperature': {'value': 21.7},
                'humidity': {'value': 60},
            },
            {
                'type': 'Room',
                'id': 'Mad_Aud',
                'temperature': {'value': 22.9},
                'humidity': {'value': 85},
            },
        ],
    )


class QueryRequest(BaseModel):
    entities: List[Dict[str, Any]] = Field(
        ...,
        description='',
        example=[
            {'idPattern': '.*', 'type': 'Room'},
            {'id': 'Car', 'type': 'P-9873-K'},
        ],
    )
    attrs: List[str] = Field(..., description='', example=['temperature', 'humidity'])
    expression: Dict[str, Any] = Field(
        ..., description='', example={'q': 'temperature>20'}
    )
    metadata: List[str] = Field(..., description='', example=['accuracy', 'timestamp'])


class QueryResponse(BaseModel):
    type: str = Field(..., description='', example='Room')
    id: str = Field(..., description='', example='DC_S1-D41')
    temperature: Dict[str, Any] = Field(
        ..., description='', example={'value': 35.6, 'type': 'Number'}
    )


class NotifyRequest(BaseModel):
    subscriptionId: str = Field(..., description='', example='5aeb0ee97d4ef10a12a0262f')
    data: List[Dict[str, Any]] = Field(
        ...,
        description='',
        example=[
            {
                'type': 'Room',
                'id': 'DC_S1-D41',
                'temperature': {'value': 35.6, 'type': 'Number'},
            },
            {
                'type': 'Room',
                'id': 'Boe-Idearium',
                'temperature': {'value': 22.5, 'type': 'Number'},
            },
        ],
    )