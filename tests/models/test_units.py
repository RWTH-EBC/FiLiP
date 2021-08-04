"""
Test for filip.models.units
"""
from unittest import TestCase
from filip.models.units import Unit, Units, UnitCode, UnitText, UNITS

class TestUnitCodes(TestCase):
    def setUp(self):
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
        for index, row in UNITS.iterrows():
            UnitCode(value=row.CommonCode)

    def test_unit_text(self):
        """
        test unit text/name model
        Returns:
            None
        """
        for index, row in UNITS.iterrows():
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
        self.assertEqual(UNITS.Name.to_list(), units.keys())
        self.assertEqual(UNITS.Name.to_list(), units.names)
        self.assertEqual(UNITS.CommonCode.to_list(), units.keys(by_code=True))
        self.assertEqual(UNITS.CommonCode.to_list(), units.codes)

        for unit in units.values():
            print(unit.json(indent=2))
