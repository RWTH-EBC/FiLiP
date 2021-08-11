"""
Implementation of UN/CEFACT units

We creating the data set of UNECE units from here.
"https://github.com/datasets/unece-units-of-measure"
It downloads the data and stores it in external resources if not
already present. For additional information on UNECE an the current state of
tables visit this website:
https://unece.org/trade/cefact/UNLOCODE-Download
https://unece.org/trade/uncefact/cl-recommendations
"""
import json
import logging
import pandas as pd
from functools import lru_cache
from fuzzywuzzy import process
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, root_validator, validator
from filip.models.base import NgsiVersion, DataType
from filip.utils.data import load_datapackage


logger = logging.getLogger(name=__name__)


@lru_cache()
def load_units() -> pd.DataFrame:
    """
    Loads data package from public repo if not already downloaded.
    This function will be cached for fast accessing the data set.
    Returns:
        Cleaned dataset containing all unit data
    """
    units = load_datapackage(
            url="https://github.com/datasets/unece-units-of-measure",
            filename="unece-units.hdf")["units_of_measure"]
    # remove deprecated entries
    units = units.loc[
            ((units.Status.str.casefold() != 'x') &
             (units.Status.str.casefold() != 'd'))]
    return units


class UnitCode(BaseModel):
    """
    The unit of measurement given using the UN/CEFACT Common Code (3 characters)
    or a URL. Other codes than the UN/CEFACT Common Code may be used with a
    prefix followed by a colon.
    https://schema.org/unitCode

    Note:
        Currently we only support the UN/CEFACT Common Codes
    """
    type: DataType = Field(default=DataType.TEXT,
                           const=True,
                           description="Data type")
    value: str = Field(...,
                       title="Code of unit ",
                       description="UN/CEFACT Common Code (3 characters)",
                       min_length=2,
                       max_length=3)

    @validator('value')
    def validate_code(cls, value):
        units = load_units()
        if len(units.loc[units.CommonCode == value.upper()]) == 1:
            return value
        raise KeyError("Code does not exist or is deprecated! '%s'", value)


class UnitText(BaseModel):
    """
    A string or text indicating the unit of measurement. Useful if you cannot
    provide a standard unit code for unitCode.
    https://schema.org/unitText

    Note:
        We use the names of units of measurements from UN/CEFACT for validation
    """
    type: DataType = Field(default=DataType.TEXT,
                           const=True,
                           description="Data type")
    value: str = Field(...,
                       title="Name of unit of measurement",
                       description="Verbose name of a unit using British "
                                   "spelling in singular form, "
                                   "e.g. 'newton second per metre'")

    @validator('value')
    def validate_text(cls, value):
        units = load_units()

        if len(units.loc[(units.Name.str.casefold() == value.casefold())]) >= 1:
            return value
        names = units.Name.tolist()
        suggestions = [item[0] for item in process.extractBests(
            query=value.casefold(),
            choices=names,
            score_cutoff=50,
            limit=5)]
        raise ValueError(f"Invalid 'name' for unit! '{value}' \n "
                         f"Did you mean one of the following? \n "
                         f"{suggestions}")


class Unit(BaseModel):
    """
    Model for a unit definition
    """
    _ngsi_version: NgsiVersion = Field(default=NgsiVersion.v2, const=True)
    name: Optional[Union[str, UnitText]] = Field(
        alias="unitText",
        default=None,
        description="A string or text indicating the unit of measurement")
    code: Optional[Union[str, UnitCode]] = Field(
        alias="unitCode",
        default=None,
        description="The unit of measurement given using the UN/CEFACT "
                    "Common Code (3 characters)")
    description: Dict[str, str] = Field(
        default=None,
        alias="unitDescription",
        description="Verbose description of unit",
        max_length=350)
    symbol: Dict[str, str] = Field(
        default=None,
        alias="unitSymbol",
        description="The symbol used to represent the unit of measure as "
                    "in ISO 31 / 80000.")
    conversion_factor: Dict[str, str] = Field(
        default=None,
        alias="unitConversionFactor",
        description="The value used to convert units to the equivalent SI "
                    "unit when applicable.")

    class Config:
        extra = 'ignore'
        allow_population_by_field_name = True

    @root_validator(pre=False)
    def check_consistency(cls, values):
        """
        Validate and auto complete unit data based on the UN/CEFACT data
        Args:
            values (dict): Values of a all data fields

        Returns:
            values (dict): Validated data
        """
        units = load_units()
        name = values.get("name")
        code = values.get("code")

        if isinstance(code, UnitCode):
            code = code.value
        if isinstance(name, UnitText):
            name = name.value

        if code and name:
            idx = units.index[((units.CommonCode == code) &
                               (units.Name == name))]
            if idx.empty:
                raise ValueError("Invalid combination of 'code' and 'name': ",
                                 code, name)
        elif code:
            idx = units.index[(units.CommonCode == code)]
            if idx.empty:
                raise ValueError("Invalid 'code': ", code)
        elif name:
            idx = units.index[(units.Name == name)]
            if idx.empty:
                names = units.Name.tolist()
                suggestions = [item[0] for item in process.extractBests(
                    query=name.casefold(),
                    choices=names,
                    score_cutoff=50,
                    limit=5)]
                raise ValueError(f"Invalid 'name' for unit! '{name}' \n "
                                 f"Did you mean one of the following? \n "
                                 f"{suggestions}")
        else:
            raise AssertionError("'name' or 'code' must be  provided!")

        values["code"] = UnitCode(value=units.CommonCode[idx[0]])
        values["name"] = UnitText(value=units.Name[idx[0]])
        values["symbol"] = {"type":     DataType.TEXT,
                            "value":    units.Symbol[idx[0]]}
        values["conversion_factor"] = \
            {"type":    DataType.TEXT,
             "value":   units.ConversionFactor[idx[0]]}
        if not values.get("description"):
            values["description"] = \
                {"type":    DataType.TEXT,
                 "value":   units.Description[idx[0]]}
        return values


class Units:
    """
    Class for easy accessing the data set of UNECE units from here.
    "https://github.com/datasets/unece-units-of-measure"
    """
    units = load_units()

    def __getattr__(self, item):
        """
        Return unit as attribute by name or code.
        Notes:
            Underscores will be substituted with whitespaces
        Args:
            item: if len(row) == 0:

        Returns:
            Unit
        """
        item = item.casefold().replace('_', ' ')
        return self.__getitem__(item)

    @property
    def quantities(self):
        """
        Get list of units ordered by measured quantities
        Returns:
            list of units ordered by measured quantities
        """
        raise NotImplementedError("The used dataset does currently not "
                                  "contain the information about quantity")

    def __getitem__(self, item: str) -> Unit:
        """
        Get unit by name or code

        Args:
            item (str): name or code

        Returns:
            Unit
        """
        idx = self.units.index[((self.units.CommonCode == item.upper()) |
                                (self.units.Name == item.casefold()))]
        if idx.empty:
            names = self.units.Name.tolist()
            suggestions = [item[0] for item in process.extractBests(
                query=item.casefold(),
                choices=names,
                score_cutoff=50,
                limit=5)]
            raise ValueError(f"Invalid 'name' for unit! '{item}' \n "
                             f"Did you mean one of the following? \n "
                             f"{suggestions}")

        return Unit(code=self.units.CommonCode[idx[0]])

    @classmethod
    def keys(cls, by_code: bool = False) -> List[str]:
        """
        Returns list of all unit names or codes

        Args:
            by_code (bool): if 'True' the keys will contain the unit codes
                instead of their names.

        Returns:
            List[str] containing the names or list
        """
        if by_code:
            return cls.units.CommonCode.to_list()
        return cls.units.Name.to_list()

    @property
    def names(self) -> List[str]:
        """
        Returns list of all unit names

        Returns:
            List[str] containing the names or list
        """
        return self.keys()

    @property
    def codes(self) -> List[str]:
        """
        Returns list of all unit codes

        Returns:
            List[str] containing the codes
        """
        return self.keys(by_code=True)

    def values(self) -> List[Unit]:
        """
        Get list of all units

        Returns:
            List[Unit] containing all units
        """

        return [Unit(code=code) for code in self.units.CommonCode]

    def get(self, item: str, default: Any = None):
        """
        Get unit by name or by code

        Args:
            item (str): name or code of unit
            default (Any): Default value to return if unit does not exist.
        Returns:
            Unit
        """
        try:
            return self.__getitem__(item)
        except KeyError:
            return default


def validate_unit_data(data: Dict) -> Dict:
    """
    Validator for unit objects
    Args:
        data (Dict): Dictionary containing the metadata of an object

    Returns:
        Validated dictionary of metadata
    """
    _unit_models = {'unit': Unit,
                    "unitText": UnitText,
                    "unitCode": UnitCode}
    for modelname, model in _unit_models.items():
        if data.get("name", "").casefold() == modelname.casefold():
            if data.get("name", "").casefold() == 'unit':
                data["type"] = 'Unit'
                data["value"] = model.parse_obj(data["value"])
                return data
            else:
                data.update(model.parse_obj(data).dict())
                return data
    raise ValueError(f"Invalid unit data found: \n "
                     f"{json.dumps(data, indent=2)}")
