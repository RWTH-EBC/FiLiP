"""
Test for filip.models.units
"""
from unittest import TestCase
import functools
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
        self.unit = {"code": "C58",
                     "name": "newton second per metre"}

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
        # test creation
        unit = Unit(**self.unit)
        unit_from_json = Unit.parse_raw(unit.json(by_alias=True))
        self.assertEqual(unit, unit_from_json)

    def test_unit_model_caching(self):
        """
        Test caching of unit model

        Returns:
            None
        """

        unit = Unit(**self.unit)
        # testing hashing and caching
        from functools import lru_cache
        from time import perf_counter_ns

        self.assertEqual(unit.__hash__(), unit.__hash__())

        @functools.lru_cache
        def cache_unit(unit: Unit):
            return Unit(name=unit.name)

        timers = []
        for i in range(5):
            start = perf_counter_ns()
            cache_unit(unit)
            stop = perf_counter_ns()
            timers.append(stop - start)
            if i > 0:
                self.assertLess(timers[i], timers[0])

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
            # print(cmdout)

    def test_unit_validator(self):
        """
        Test if unit hints are given for typos
        Returns:
            None
        """
        # using garbage collector to clean up all caches
        import gc
        gc.collect()

        # All objects collected
        objects = [i for i in gc.get_objects()
                   if isinstance(i, functools._lru_cache_wrapper)]

        # All objects cleared
        for object in objects:
            object.cache_clear()

        unit_data = self.unit.copy()
        unit_data['name'] = "celcius"
        with self.assertRaises(ValueError):
            Unit(**unit_data)

