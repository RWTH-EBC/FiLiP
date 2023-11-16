"""
Data models for interacting with FIWARE's time series-api (aka QuantumLeap)
"""
from __future__ import annotations
import logging
from typing import Any, List, Union
from datetime import datetime
import numpy as np
import pandas as pd
from aenum import Enum
from pydantic import ConfigDict, BaseModel, Field


logger = logging.getLogger(__name__)


class TimeSeriesBase(BaseModel):
    """
    Base model for other time series api models
    """
    index: Union[List[datetime], datetime] = Field(
        default=None,
        description="Array of the timestamps which are indexes of the response "
                    "for the requested data. It's a parallel array to 'values'."
                    " The timestamp will be in the ISO8601 format "
                    "(e.g. 2010-10-10T07:09:00.792) or in milliseconds since "
                    "epoch whichever format was used in the input "
                    "(notification), but ALWAYS in UTC. When using aggregation "
                    "options, the format of this remains the same, only the "
                    "semantics will change. For example, if aggrPeriod is day, "
                    "each index will be a valid timestamp of a moment in the "
                    "corresponding day."
    )


class TimeSeriesHeader(TimeSeriesBase):
    """
    Model to describe an available entity in the time series api
    """
    model_config = ConfigDict(populate_by_name=True)
    # aliases are required due to formally inconsistencies in the api-specs
    entityId: str = Field(default=None,
                          alias="id",
                          description="The entity id the time series api."
                                      "If the id is unique among all entity "
                                      "types, this could be used to uniquely "
                                      "identify the entity instance. Otherwise,"
                                      " you will have to use the entityType "
                                      "attribute to resolve ambiguity.")
    entityType: str = Field(default=None,
                            alias="type",
                            description="The type of an entity")


class IndexedValues(BaseModel):
    """
    Model for time indexed values
    """
    values: List[Any] = Field(
        default=None,
        description="Array of values of the selected attribute, in the same "
                    "corresponding order of the 'index' array. When using "
                    "aggregation options, the format of this remains the same, "
                    "only the semantics will change. For example, if "
                    "aggrPeriod is day, each value of course may not "
                    "correspond to original measurements but rather the "
                    "aggregate of measurements in each day."
    )


class AttributeValues(IndexedValues):
    """
    Model for indexed values that contain attribute name
    """
    attrName: str = Field(
        title="Attribute name",
        description=""
    )


class TimeSeries(TimeSeriesHeader):
    """
    Model for time series data
    """
    model_config = ConfigDict(populate_by_name=True)
    attributes: List[AttributeValues] = None

    def extend(self, other: TimeSeries) -> None:
        """
        Extends the current `TimeSeries` object with an other
        `TimeSeries` object. With the same format.

        Args:
            other: TimeSeries Object that will be added to the original object

        Returns:
            None

        Raises:
            Assertion Error: if header fields do not fit or if index is not
                rising
        """
        assert self.entityId == other.entityId
        assert self.entityType == other.entityType
        assert self.index[-1] < other.index[0]

        for attr, other_attr in zip(self.attributes, other.attributes):
            assert attr.attrName == other_attr.attrName
            attr.values.extend(other_attr.values)
        self.index.extend(other.index)

    def to_pandas(self) -> pd.DataFrame:
        """
        Converts time series data to pandas dataframe
        Returns:
            pandas.DataFrame
        """
        index = pd.Index(data=self.index, name='datetime')
        attr_names = [attr.attrName for attr in self.attributes]
        values = np.array([attr.values for attr in self.attributes]).transpose()
        columns = pd.MultiIndex.from_product(
            [[self.entityId], [self.entityType], attr_names],
            names=['entityId', 'entityType', 'attribute'])

        return pd.DataFrame(data=values, index=index, columns=columns)


class AggrMethod(str, Enum):
    """
    Aggregation Methods
    """
    _init_ = 'value __doc__'
    COUNT = "count", "Number of Entries"
    SUM = "sum", "Sum"
    AVG = "avg", "Average"
    MIN = "min", "Minimum"
    MAX = "max", "Maximum"


class AggrPeriod(str, Enum):
    """
    Aggregation Periods
    """
    _init_ = 'value __doc__'
    YEAR = "year", "year"
    MONTH = "month", "month"
    DAY = "day", "day"
    HOUR = "hour", "hour"
    MINUTE = "minute", "minute"
    SECOND = "second", "second"


class AggrScope(str, Enum):
    """
    Aggregation Periods
    When the query results cover historical data for
    multiple entities instances, you can define the aggregation method to be
    applied for each entity instance [entity] or across them [global].
    """
    _init_ = 'value __doc__'
    ENTITY = "entity", "Entity (default)"
    GLOBAL = "global", "Global"
