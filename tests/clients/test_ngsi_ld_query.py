"""
Tests for filip.cb.client
"""

import unittest
import logging
import re
import math
import time
from dateutil.parser import parse
from collections.abc import Iterable
from requests import RequestException
from filip.clients.ngsi_ld.cb import ContextBrokerLDClient
from filip.models.base import FiwareLDHeader
from filip.models.ngsi_ld.context import (
    ActionTypeLD,
    ContextLDEntity,
    ContextProperty,
    NamedContextProperty,
    NamedContextRelationship,
)
from tests.config import settings
from random import Random
from filip.utils.cleanup import clear_context_broker_ld


# Setting up logging
logging.basicConfig(
    level="ERROR", format="%(asctime)s %(name)s %(levelname)s: %(message)s"
)


class TestLDQueryLanguage(unittest.TestCase):
    """
    Test class for ContextBrokerClient
    """

    def setUp(self) -> None:
        """
        Setup test data
        Returns:
            None
        """
        # Extra size parameters for modular testing
        self.cars_nb = 500
        self.span = 3

        # client parameters
        self.fiware_header = FiwareLDHeader(ngsild_tenant=settings.FIWARE_SERVICE)
        self.cb = ContextBrokerLDClient(
            fiware_header=self.fiware_header, url=settings.LD_CB_URL
        )

        # Prep db
        clear_context_broker_ld(cb_ld_client=self.cb)

        # base id
        self.base = "urn:ngsi-ld:"

        # Some entities for relationships
        self.garage = ContextLDEntity(id=f"{self.base}garage0", type=f"garage")
        self.cam = ContextLDEntity(id=f"{self.base}cam0", type=f"camera")
        self.cb.post_entity(entity=self.garage)
        self.cb.post_entity(entity=self.cam)

        # Entities to post/test on
        self.cars = [
            ContextLDEntity(id=f"{self.base}car0{i}", type=f"{self.base}car")
            for i in range(0, self.cars_nb - 1)
        ]

        # Some dictionaries for randomizing properties
        self.brands = ["Batmobile", "DeLorean", "Knight 2000"]
        self.timestamps = [
            "2020-12-24T11:00:00Z",
            "2020-12-24T12:00:00Z",
            "2020-12-24T13:00:00Z",
        ]
        self.addresses = [
            {
                "country": "Germany",
                "street-address": {"street": "Mathieustr.", "number": 10},
                "postal-code": 52072,
            },
            {
                "country": "USA",
                "street-address": {"street": "Goosetown Drive", "number": 810},
                "postal-code": 27320,
            },
            {
                "country": "Nigeria",
                "street-address": {"street": "Mustapha Street", "number": 46},
                "postal-code": 65931,
            },
        ]

        # base properties/relationships
        self.humidity = NamedContextProperty(name="humidity", value=1)
        self.temperature = NamedContextProperty(name="temperature", value=0)
        self.isParked = NamedContextRelationship(name="isParked", object="placeholder")
        self.isMonitoredBy = NamedContextRelationship(
            name="isMonitoredBy", object="placeholder"
        )

        # q Expressions to test
        self.qs = [
            "temperature > 0",
            'brand != "Batmobile"',
            "isParked | isMonitoredBy",
            'isParked == "urn:ngsi-ld:garage0"',
            'temperature < 60; isParked == "urn:ngsi-ld:garage0"',
            '(temperature >= 59 | humidity < 3); brand == "DeLorean"',
            "(isMonitoredBy; temperature<30) | isParked",
            "(temperature > 30; temperature < 90)| humidity <= 5",
            'temperature.observedAt >= "2020-12-24T12:00:00Z"',
            'address[country] == "Germany"',
            "address[street-address.number] == 810",
            "address[street-address.number]",
            "address[street-address.extra]",
        ]

        self.post()

    def tearDown(self) -> None:
        """
        Cleanup test server
        """
        clear_context_broker_ld(cb_ld_client=self.cb)
        self.cb.close()

    def test_ld_query_language(self):
        # Itertools product actually interferes with test results here
        for q in self.qs:
            entities = self.cb.get_entity_list(q=q, limit=1000)
            tokenized, keys_dict = self.extract_keys(q)

            # Replace logical ops with python ones
            tokenized = tokenized.replace("|", " or ")
            tokenized = tokenized.replace(";", " and ")
            size = len(
                [x for x in self.cars if self.search_predicate(x, tokenized, keys_dict)]
            )
            # Check we get the same number of entities
            self.assertEqual(size, len(entities), msg=q)
            for e in entities:
                copy = tokenized
                for token, keylist in keys_dict.items():
                    copy = self.sub_key_with_val(copy, e, keylist, token)

                # Check each obtained entity obeys the q expression
                self.assertTrue(eval(copy), msg=q)

    def test_quoted_string_validation(self):
        incorrect = [
            "(temperature >= 59 | humidity < 3); brand == 'DeLorean'",
            "temperature.observedAt > '2020-12-24T12:00:00Z'",
            "address[country] == '\"G\"ermany'",
            "address[country] >= 'Germany'",
            "address[country] < '250'",
        ]

        for q in incorrect:
            with self.assertRaises(ValueError):
                self.cb.get_entity_list(q=q)

        correct = [
            'brand != "Batmobile"',
            'isParked == "urn:ngsi-ld:garage0"',
            'temperature < 60; isParked == "urn:ngsi-ld:garage0"',
            "brand > \"Bat'mobile'\"",
            'isParked < "1999"',
        ]

        for q in correct:
            try:
                self.cb.get_entity_list(q=q)
            except:
                self.fail(f"Test failed on supposedly correct expression {q}")

    def extract_keys(self, q: str):
        """
        Extract substring from string expression that is likely to be the name of a
        property/relationship of a given entity
        Returns:
            str,dict
        """
        # Trim empty spaces
        n = q.replace(" ", "")

        # Find all literals that are not logical operators or parentheses -> keys/values
        res = re.findall("[^<>=)()|;!]*", n)
        keys = {}
        i = 0
        for r in res:
            # Skip empty string from the regex search result
            if len(r) == 0:
                continue

            # Skip anything purely numeric -> Definitely a value
            if r.isnumeric():
                continue
            # Skip anything with a double quote -> string or date
            if '"' in r:
                try:
                    # replace date with unix ts
                    timestamp = r.replace('"', "")
                    date = parse(timestamp)
                    timestamp = str(time.mktime(date.timetuple()))
                    n = n.replace(r, timestamp)
                except Exception as e:
                    r = f'"{r}"'
                continue

            # Skip keys we already encountered
            if [r] in keys.values():
                continue

            # Replace the key name with a custom token in the string
            token = f"${i}"
            n = n.replace(r, token)
            i += 1

            # Flatten composite keys by chaining them together
            l = []
            # Composite of the form x[...]
            if "[" in r:
                idx_st = r.index("[")
                idx_e = r.index("]")
                outer_key = r[:idx_st]
                l.append(outer_key)
                inner_key = r[idx_st + 1 : idx_e]

                # Composite of the form x[y.z...]
                if "." in inner_key:
                    rest = inner_key.split(".")
                # Composite of the form x[y]
                else:
                    rest = [inner_key]
                l += rest
            # Composite of the form x.y...
            elif "." in r:
                l += r.split(".")
            # Simple key
            else:
                l = [r]

            # Finalize incomplete key presence check
            idx_next = n.index(token) + len(token)
            if idx_next >= len(n) or n[idx_next] not in [">", "<", "=", "!"]:
                n = n.replace(token, f"{token} != None")

            # Associate each chain of nested keys with the token it was replaced with
            keys[token] = l
        return n, keys

    def sub_key_with_val(self, q: str, entity: ContextLDEntity, keylist, token: str):
        """
        Substitute key names in q expression with corresponding entity property/
        relationship values. All while accounting for access of nested properties
        Returns:
            str
        """
        obj = entity.model_dump()
        for key in keylist:
            if key in obj:
                obj = obj[key]
            elif "value" in obj and key in obj["value"]:
                obj = obj["value"][key]
            else:
                obj = None
                break

        if isinstance(obj, Iterable):
            if "value" in obj:
                obj = obj["value"]
            elif "object" in obj:
                obj = obj["object"]

        if obj is not None and re.compile("[a-zA-Z]+").search(str(obj)) is not None:
            try:
                date = parse(obj)
                obj = str(time.mktime(date.timetuple()))  # convert to unix ts
            except Exception as e:
                obj = f'"{str(obj)}"'

        # replace key names with entity values
        n = q.replace(token, str(obj))
        return n

    def search_predicate(self, e, tokenized, keys_dict):
        """
        Search function to search our posted data for checks
        This function is needed because , whereas the context broker will not return
        an entity with no nested key if that key is given as a filter, our eval attempts
        to compare None values using logical operators
        """
        copy = tokenized
        for token, keylist in keys_dict.items():
            copy = self.sub_key_with_val(copy, e, keylist, token)

        try:
            return eval(copy)
        except:
            return False

    def post(self):
        """
        Somewhat randomized generation of data. Can be made further random by
        Choosing a bigger number of cars, and a more irregular number for remainder
        Calculations (self.cars_nb & self.span)
        Returns:
            None
        """
        for i in range(len(self.cars)):
            # Big number rnd generator
            r = Random().randint(1, self.span)
            tri_rnd = Random().randint(0, (10 * self.span) ** 2)
            r = math.trunc(tri_rnd / r) % self.span
            r_2 = Random().randint(0, r)

            a = r_2 * 30
            b = a + 30

            # Every car will have temperature, humidity, brand and address
            t = self.temperature.model_copy()
            t.value = Random().randint(a, b)
            t.observedAt = self.timestamps[r]

            h = self.humidity.model_copy()
            h.value = Random().randint(math.trunc(a / 10), math.trunc(b / 10))

            self.cars[i].add_properties(
                [
                    t,
                    h,
                    NamedContextProperty(name="brand", value=self.brands[r]),
                    NamedContextProperty(name="address", value=self.addresses[r]),
                ]
            )

            p = self.isParked.model_copy()
            p.object = self.garage.id

            m = self.isMonitoredBy.model_copy()
            m.object = self.cam.id

            # Every car is endowed with a set of relationships/nested key
            if r == 0:
                self.cars[i].add_relationships([p])
            elif r == 1:
                self.cars[i].add_relationships([m])
            elif r == 2:
                self.cars[i].add_relationships([p, m])

        # Post everything
        self.cb.entity_batch_operation(
            action_type=ActionTypeLD.CREATE, entities=self.cars
        )
