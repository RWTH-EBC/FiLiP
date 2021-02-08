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

class Sector(str, Enum):
    mechanics = 'Mechanics'
    electricity_and_magnetism = 'Electricity and Magnetism'


class Units:
    levels: pd.DataFrame = None
    units: pd.DataFrame = None

    def __init__(self):
        data = read_datapackage(
            "https://github.com/datasets/unece-units-of-measure")
        self.levels = data['levels']
        self.units = data['units-of-measure']

        #self.levels = [Level(**level) for level in data[
        #    'levels'].to_dict(orient="records")]
        #        self.units = {unit['Name']: Unit(**unit) for unit in data[
        #    'units-of-measure'].to_dict(
        #    orient="records")}


    def __getattr__(self, item):
        item = item.casefold().replace('_', ' ')
        return self.__getitem__(item)

    def __getitem__(self, item):
        row = self.units.loc[self.units.Name == item.casefold()]
        if len(row) == 0:
            raise KeyError
        return Unit(**row.to_dict(orient="records")[0])


    @property
    def sectors(self):
        return [sector for sector in self.units.Sector.unique()]

units = Units()

if __name__ == '__main__':
    print(units.levels)
    print(units.sectors)
    print(units.newton_second_per_metre.code)
    print(units['newton second per metre'])

