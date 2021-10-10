"""
Test for filip.models.units
"""
from unittest import TestCase
from filip.models.ngsi_v2.units import \
    Unit, \
    Units, \
    UnitCode, \
    UnitText, \
    load_units

class TestUnitCodes(TestCase):
    def setUp(self):
        self.units_data = load_units()
        self.units = Units()
        self.unit = {"code": {"type": "Text",
                              "value": "C58"},
                     "name": {"type": "Text",
                              "value": "newton second per metre"}}

    def test_unit_code(self):
        """
        test unit code model
        Returns:
            None
        """
        for index, row in self.units_data.iterrows():
            UnitCode(value=row.CommonCode)

    def test_unit_text(self):
        """
        test unit text/name model
        Returns:
            None
        """
        for index, row in self.units_data.iterrows():
            UnitText(value=row.Name)

    def test_unit_model(self):
        """
        Test unit model
        Returns:
            None
        """
        unit = Unit(**self.unit)
        unit_from_json = Unit.parse_raw(unit.json(by_alias=True))
        self.assertEqual(unit, unit_from_json)

    def test_units(self):
        """
        Test units api
        Returns:
            None
        """
        units = Units()
        self.assertEqual(self.units_data.Name.to_list(), units.keys())
        self.assertEqual(self.units_data.Name.to_list(), units.names)
        self.assertEqual(self.units_data.CommonCode.to_list(),
                         units.keys(by_code=True))
        self.assertEqual(self.units_data.CommonCode.to_list(), units.codes)

        for unit in units.values():
            cmdout = unit.json(indent=2)
            #print(cmdout)

    def test_unit_validator(self):
        """
        Test if unit hints are given for typos
        Returns:
            None
        """
        unit_data = self.unit.copy()
        unit_data['name']['value'] = "celcius"
        with self.assertRaises(ValueError):
            Unit(**unit_data)

