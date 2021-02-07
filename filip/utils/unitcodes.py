from pandas_datapackage_reader import read_datapackage
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
    levels: List[Level] = None
    units: Dict[str, Unit] = None

    def __init__(self):
        data = read_datapackage(
            "https://github.com/datasets/unece-units-of-measure")
        self.levels = [Level(**level) for level in data[
            'levels'].to_dict(orient="records")]
        self.units = {unit['Name']: Unit(**unit) for unit in data[
            'units-of-measure'].to_dict(
            orient="records")}

    def get_unit(self, name: str):
        return self.units.get(name.casefold(), None)

    def get_sector(self, sector: Sector):
        return [unit for unit in self.units.values() if unit.sector.casefold() ==
                sector.casefold()]

units = Units()

print(units.levels)

print(units.mechanics)
print(units.get_unit('Ampere').sector)
print(units.get_sector(Sector.electricity_and_magnetism))
