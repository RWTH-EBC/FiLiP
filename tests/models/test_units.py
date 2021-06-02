from unittest import TestCase
from filip.utils.units import Unit, units

class TestUnitCodes(TestCase):
    def setUp(self):
        self.unit = {"code": {"type": "Text",
                              "value": "C58"},
                     "name": {"type": "Text",
                              "value": "newton second per metre"}}

    def test_unit_model(self):
        unit = Unit(**self.unit)
        print(unit.json())
        print(unit.key_values)


    def test_units(self):
        print(units.sectors.mechanics)
        print(units.newton_second_per_metre.code)
        print(units['newton second per metre'])
        print(units.get_unit(code='C58'))
        print(units['C58'])