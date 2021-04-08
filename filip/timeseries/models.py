from __future__ import annotations
import logging
import numbers
import pandas as pd
from typing import Any, Optional, List, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from filip.cb.models import ContextEntity


logger = logging.getLogger()


class IndexArray(list):
    """
    Array of the timestamps which are indexes of the response for the
    requested data. It's a parallel array to 'values'. The timestamp will be
    in the ISO8601 format (e.g. 2010-10-10T07:09:00.792) or in milliseconds
    since epoch whichever format was used in the input (notification), but
    ALWAYS in UTC. When using aggregation options, the format of this remains
    the same, only the semantics will change. For example, if aggrPeriod is day,
     each index will be a valid timestamp of a moment in the corresponding day.
    """
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update()

    @classmethod
    def validate(cls, v):
        if not isinstance(v, list):
            raise TypeError('list required')

        for idx, timestamp in enumerate(v):
            try:
                float(timestamp)
                v[idx] = datetime.strptime(timestamp, '%d.%m.%Y %H:%M:%S.%f')
            except Exception:
                pass
            try:
                v[idx] = datetime.fromtimestamp(timestamp/1000.0)
            except Exception:
                raise TypeError
        return v

    def __repr__(self):
        return f'IndexArray({super().__repr__()})'


class ValuesArray(list):
    """
    Array of values of the selected attribute, in the same corresponding order
    of the 'index' array. When using aggregation options, the format of this
    remains the same, only the semantics will change. For example, if aggrPeriod
    is day, each value of course may not correspond to original measurements
    but rather the aggregate of measurements in each day.
    """
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, list):
            raise TypeError('list required')
        if not isinstance(all(v), (str, numbers.Number)):
            raise TypeError('Alphanumeric values required!')
        return v

    def __repr__(self):
        return f'ValuesArray({super().__repr__()})'


class BaseValues(BaseModel):
    values: List[Any] = Field(
        description="Array of values of the selected attribute, in the same "
                    "corresponding order of the 'index' array. When using "
                    "aggregation options, the format of this remains the same, "
                    "only the semantics will change. For example, if "
                    "aggrPeriod is day, each value of course may not "
                    "correspond to original measurements but rather the "
                    "aggregate of measurements in each day."
    )

    def to_pandas(self):
        return pd.DataFrame(self)


class IndexedValues(BaseValues):
    index: List[Union[float, str, datetime]] = Field(
        description="Array of the timestamps which are indexes of the response "
                    "for the requested data. It's a parallel array to 'values'. "
                    "The timestamp will be in the ISO8601 format "
                    "(e.g. 2010-10-10T07:09:00.792) or in milliseconds since "
                    "epoch whichever format was used in the input "
                    "(notification), but ALWAYS in UTC. When using aggregation "
                    "options, the format of this remains the same, only the "
                    "semantics will change. For example, if aggrPeriod is day, "
                    "each index will be a valid timestamp of a moment in the "
                    "corresponding day."
    )

    @validator('index')
    def validate_index(cls, v):
        for idx, timestamp in enumerate(v):
            if isinstance(timestamp, datetime):
                return v
            elif isinstance(timestamp, float):
                v[idx] = datetime.fromtimestamp(timestamp / 1000.0)
            elif isinstance(timestamp, str):
                v[idx] = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f')
            else:
                raise TypeError
        return v


class AttributeValues(BaseValues):
    attrName: str = Field(
        title="Attribute name",
        description=""
    )


class EntityIndexedValues(IndexedValues):
    entityId: str = Field(
        title="Entity Id",
        description=""
    )


class NotificationMessage(BaseModel):
    subscriptionId: Optional[str] = Field(
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


class ResponseModel(BaseModel):
    entityId: str = None
    index: List[str] = None
    attributes: List[AttributeValues] = None
    values: ValuesArray = None
    entityType: str = None
    attrName: str = None
    entities: List[EntityIndexedValues] = None

    def to_pandas(self):
        print(self.dict())
        list_of_dataframes = []
        #if attr_id, attr_values_id
        if self.index is not None and self.attributes is None:
            index = pd.MultiIndex.from_product([[self.entityId], self.index],
                                               names=['entity_id', 'index'])
            columns = pd.MultiIndex.from_product([[self.attrName]])
            df_all = pd.DataFrame(self.values, index=index, columns=columns)
        elif self.entities is not None:
            #if attr_type
            for entity in self.entities:
                index = pd.MultiIndex.from_product([[entity.entityId], entity.index],
                                                   names=['entity_id', 'index'])
                columns = pd.MultiIndex.from_product([[self.attrName]])
                dataframe = pd.DataFrame(entity.values, index=index, columns=columns)
                list_of_dataframes.append(dataframe)
            df_all = pd.concat(list_of_dataframes, ignore_index=False)
        elif self.attributes is not None:
            # if attrs_values_id, attrs_id
            for entity in self.attributes:
                index = pd.MultiIndex.from_product([[self.entityId], self.index],
                                                   names=['entity_id', 'index'])
                columns = pd.MultiIndex.from_product([[entity.attrName]])
                dataframe = pd.DataFrame(entity.values, index=index, columns=columns)
                list_of_dataframes.append(dataframe)
            df_all = pd.concat(list_of_dataframes, ignore_index=False)
        elif self.values is not None:
            # if attr_values_type
            for entity in self.values:
                index = pd.MultiIndex.from_product([[entity["entityId"]], entity["index"]],
                                                   names=['entity_id', 'index'])
                columns = pd.MultiIndex.from_product([["attribute"]])
                dataframe = pd.DataFrame(entity["values"], index=index, columns=columns)
                list_of_dataframes.append(dataframe)
            df_all = pd.concat(list_of_dataframes, ignore_index=False)

        return df_all
