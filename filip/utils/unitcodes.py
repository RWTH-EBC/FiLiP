from pandas_datapackage_reader import read_datapackage
import pandas as pd
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum


class Level(BaseModel):
    level: str = Field(alias="LevelAndCategory")
    description: str = Field(alias="Description")

class Unit(BaseModel):
    level: str = Field(alias="LevelAndCategory")
    name: str = Field(alias="Name")
    sector: str = Field(alias="Sector")
    code: str = Field(alias="CommonCode")
    description: Optional[str] = Field(alias="Description")
    quantity: str = Field(alias="Quantity")

class Units:
    levels: pd.DataFrame = None
    units: pd.DataFrame = None

    def __init__(self):
        data = read_datapackage(
            "https://github.com/datasets/unece-units-of-measure")
        self.levels = data['levels']
        self.units = data['units-of-measure']
        self.sectors = Enum('sectors', {str(sector).casefold().replace(' ','_'):
                                           sector for sector in
                                    self.units.Sector.unique()},
                      module=__name__,
                      type=str)

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
        return Unit(**row.to_dict(orient="records")[0])

    def get_unit(self, *, name: str=None, code: str=None):
        if name is not None and code is None:
            row = self.units.loc[(self.units.Name == name.casefold())]
        elif name is None and code is not None:
            row = self.units.loc[(self.units.CommonCode.str.casefold() ==
                                  code.casefold())]
        else:
            raise Exception
        if len(row) == 0:
            raise KeyError
        return Unit(**row.to_dict(orient="records")[0])

    def get_sector(self, sector: str):
        rows = self.units.loc[(self.units.Name == sector.casefold())]
        return [Unit(**unit) for unit in rows.to_dict(orient="records")]

units = Units()

if __name__ == '__main__':
    print(units.sectors.mechanics=='Mechanics')
    print(units.newton_second_per_metre.code)
    print(units['newton second per metre'])
    print(units.get_unit(code='C58'))
    print(units['C58'])
