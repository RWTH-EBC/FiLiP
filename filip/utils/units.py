"""
Fiware recommends unit codes for meta data. This class helps to validate
the codes.
Implementation of Unit Codes

"""
import os
from enum import Enum
from pathlib import Path
from typing import List, Optional
from pandas_datapackage_reader import read_datapackage
from pydantic import BaseModel, Field, validator, root_validator
from filip.core.models import DataType


class BaseUnitProperty(BaseModel):
    """
    Base model for all unit properties
    """
    type: DataType = Field(default=DataType.TEXT,
                           const=True,
                           allow_mutation=False)
    value: str

    class Config:
        validate_assignment = True
        allow_population_by_field_name = True


class UnitCode(BaseUnitProperty):
    value: str = Field(
        title="unit code",
        description="Code of the measured quantity")

    @validator('value')
    def validate_code(cls, value):
        units.get_unit(code=value)
        return value


class UnitName(BaseUnitProperty):
    value: str = Field(default=None,
                       description="")

    @validator('value')
    def validate_name(cls, value):
        units.get_unit(name=value)
        return value


class UnitSymbol(BaseUnitProperty):
    value: str = Field(description="")


class UnitDescription(BaseUnitProperty):
    value: str = Field(default=None,
                       description="",
                       max_length=256)

class UnitKeyValues(BaseModel):
    """
    Model for a unit definiton
    """
    level: str = Field(alias="LevelAndCategory")
    name: str = Field(alias="Name")
    sector: str = Field(alias="Sector")
    code: str = Field(alias="CommonCode")
    description: Optional[str] = Field(alias="Description")
    quantity: str = Field(alias="Quantity")


class Unit(BaseModel):
    code: UnitCode = Field(
        default=None,
        alias="CommonCode",
        description="UNECE Internal code of ")
    name: UnitName = Field(default=None, alias="Name")
    symbol: UnitSymbol = Field(default=None, alias="Symbol")
    description: UnitDescription = Field(default=None, alias="Description")

    @root_validator
    def check_consistency(cls, values):
        code = values.get("code", None)
        if code:
            units.get_unit(code=code.value)
        return values

    @property
    def key_values(self):
        return {k: v.value for k, v in self}

    class Config:
        validate_assignment = True
        allow_population_by_field_name = True


class Units:
    """
    Class for creating the data set of unece units
    It downloads the data and stores it in external resources if not
    already present.
    """
    levels: pd.DataFrame = None
    units: pd.DataFrame = None

    def __init__(self):
        self.load_data()

    def __getattr__(self, item):
        item = item.casefold().replace('_', ' ')
        return self.__getitem__(item)

    def __getitem__(self, item):
        row = self.units.loc[(self.units.Name.str.casefold() ==
                              item.casefold())]
        if len(row) == 0:
            row = (self.units.loc[(self.units.CommonCode.str.casefold() ==
                                   item.casefold())])
        if len(row) == 0:
            raise KeyError
        return UnitKeyValues(**row.to_dict(orient="records")[0])

    def load_data(self):
        data = 'unece-units-of-measure.hdf'
        # create directory for data if not exists
        dirpath = Path(__file__).parent.parent.absolute().joinpath('data')
        dirpath.mkdir(parents=True, exist_ok=True)
        filepath = dirpath.joinpath(data)
        if os.path.isfile(filepath):
            self.units = pd.read_hdf(filepath, key='units')
            self.levels = pd.read_hdf(filepath, key='levels')
        else:
            # This will cause a warning at first time usage
            data = read_datapackage(
                "https://github.com/datasets/unece-units-of-measure")
            self.levels = data['levels']
            self.units = data['units-of-measure']
            self.units.to_hdf(data, key='units')
            self.levels.to_hdf(data, key='levels')

        self.sectors = Enum('sectors',
                            {str(sector).casefold().replace(' ','_'):
                                 sector for sector in
                             self.units.Sector.unique()},
                            module=__name__,
                            type=str)

    def get_unit(self, *, name: str=None, code: str=None) -> Unit:
        """
        Get unit by name or code
        Args:
            name:
            code:

        Returns:
        """
        if name is not None and code is None:
            row = self.units.loc[(self.units.Name == name.casefold())]
        elif name is None and code is not None:
            row = self.units.loc[(self.units.CommonCode.str.casefold() ==
                                  code.casefold())]
        else:
            raise Exception
        if len(row) == 0:
            raise KeyError
        return UnitKeyValues(**row.to_dict(orient="records")[0])

    def get_sector(self, sector: str) -> List[Unit]:
        """
        Filter units by sector
        Args:
            sector:

        Returns:
            List of units
        """
        rows = self.units.loc[(self.units.Name == sector.casefold())]
        return [UnitKeyValues(**unit) for unit in rows.to_dict(orient="records")]


units = Units()
