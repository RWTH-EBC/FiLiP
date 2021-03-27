from unittest import TestCase
from filip.utils.unitcodes import units

class TestUnitCodes(TestCase):
    def test_units(self):
        print(units.sectors.mechanics)
        print(units.newton_second_per_metre.code)
        print(units['newton second per metre'])
        print(units.get_unit(code='C58'))
        print(units['C58'])