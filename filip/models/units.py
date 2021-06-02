"""
Implementation of Unit Codes
"""
import os
from enum import Enum
from pathlib import Path
from typing import List, Optional
import pandas as pd
from pandas_datapackage_reader import read_datapackage
from pydantic import BaseModel, Field


class Unit(BaseModel):
    """
    Model for a unit definition
    """
    level: str = Field(alias="LevelAndCategory")
    name: str = Field(alias="Name")
    sector: str = Field(alias="Sector")
    code: str = Field(alias="CommonCode")
    description: Optional[str] = Field(alias="Description")
    quantity: str = Field(alias="Quantity")


class Units:
    """
    Class for creating the data set of unece units
    It downloads the data and stores it in external resources if not
    already present.
    """
    def __init__(self):
        filename = 'unece-units.hdf'

        # create directory for data if not exists
        path = Path(__file__).parent.parent.absolute().joinpath('data')
        path.mkdir(parents=True, exist_ok=True)
        filepath = path.joinpath(filename)
        if os.path.isfile(filepath):
            self.units = pd.read_hdf(filepath, key='units')
            self.levels = pd.read_hdf(filepath, key='levels')
        else:
            # download external data and store data
            data = read_datapackage(
                "https://github.com/datasets/unece-units-of-measure")
            self.levels = data['levels']
            self.units = data['units-of-measure']
            self.units.to_hdf(str(filepath), key='units')
            self.levels.to_hdf(str(filepath), key='levels')

        self.sectors = Enum('sectors',
                            {str(sector).casefold().replace(' ', '_'):
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

    def get_unit(self, *, name: str = None, code: str = None) -> Unit:
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
        return Unit(**row.to_dict(orient="records")[0])

    def get_sector(self, sector: str) -> List[Unit]:
        """
        Filter units by sector
        Args:
            sector:

        Returns:
            List of units
        """
        rows = self.units.loc[(self.units.Name == sector.casefold())]
        return [Unit(**unit) for unit in rows.to_dict(orient="records")]


units = Units()
