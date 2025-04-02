"""
Tests for filip.cb.client
"""

import copy
import unittest
import logging
import time
import random
import json
import uuid

import paho.mqtt.client as mqtt
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
import requests
from requests import RequestException
from pydantic import AnyHttpUrl
from filip.clients.base_http_client import NgsiURLVersion, BaseHttpClient
from filip.models.base import FiwareHeader, DataType
from filip.utils.simple_ql import QueryString
from filip.clients.ngsi_v2 import ContextBrokerClient, IoTAClient
from filip.clients.ngsi_v2 import HttpClient, HttpClientConfig
from filip.models.ngsi_v2.context import (
    ContextEntity,
    ContextAttribute,
    NamedContextAttribute,
    NamedCommand,
    Query,
    ActionType,
    ContextEntityKeyValues,
)

from filip.models.ngsi_v2.base import AttrsFormat, EntityPattern, Status, NamedMetadata
from filip.models.ngsi_v2.subscriptions import (
    Mqtt,
    Message,
    Subscription,
    Condition,
    Notification,
)
from filip.models.ngsi_v2.iot import (
    Device,
    DeviceCommand,
    DeviceAttribute,
    ServiceGroup,
    StaticDeviceAttribute,
)
from filip.utils.cleanup import clear_all, clean_test
from tests.config import settings

logger = logging.getLogger(__name__)


class TestContextBroker(unittest.TestCase):
    """
    Test class for ContextBrokerClient
    """

    def setUp(self) -> None:
        """
        Setup test data
        Returns:
            None
        """
        self.fiware_header = FiwareHeader(
            service=settings.FIWARE_SERVICE, service_path=settings.FIWARE_SERVICEPATH
        )
        clear_all(
            fiware_header=self.fiware_header,
            cb_url=settings.CB_URL,
            iota_url=settings.IOTA_JSON_URL,
        )
        self.resources = {
            "entities_url": "/v2/entities",
            "types_url": "/v2/types",
            "subscriptions_url": "/v2/subscriptions",
            "registrations_url": "/v2/registrations",
        }
        self.attr = {"temperature": {"value": 20.0, "type": "Number"}}
        self.entity = ContextEntity(id="MyId", type="MyType", **self.attr)

        self.iotac = IoTAClient(
            url=settings.IOTA_JSON_URL, fiware_header=self.fiware_header
        )

        self.client = ContextBrokerClient(
            url=settings.CB_URL, fiware_header=self.fiware_header
        )
        self.subscription = Subscription.model_validate(
            {
                "description": "One subscription to rule them all",
                "subject": {
                    "entities": [{"idPattern": ".*", "type": "Room"}],
                    "condition": {
                        "attrs": ["temperature"],
                        "expression": {"q": "temperature>40"},
                    },
                },
                "notification": {
                    "http": {"url": "http://localhost:1234"},
                    "attrs": ["temperature", "humidity"],
                },
                "expires": datetime.now() + timedelta(days=1),
                "throttling": 0,
            }
        )

    def test_url_composition(self):
        """
        Test URL composition for context broker client
        """
        user_input_urls = {
            "http://example.org/orion/": "http://example.org/orion/v2/entities",
            "http://example.org/orion": "http://example.org/orion/v2/entities",
            "http://123.0.0.0:1026": "http://123.0.0.0:1026/v2/entities",
            "http://123.0.0.0:1026/": "http://123.0.0.0:1026/v2/entities",
            "http://123.0.0.0/orion": "http://123.0.0.0/orion/v2/entities",
            "http://123.0.0.0/orion/": "http://123.0.0.0/orion/v2/entities",
        }
        for url in user_input_urls:
            url_correct = AnyHttpUrl(user_input_urls[url])
            bhc = BaseHttpClient(url=url)
            url_filip = AnyHttpUrl(
                urljoin(bhc.base_url, f"{NgsiURLVersion.v2_url.value}/entities")
            )
            self.assertEqual(url_correct, url_filip)

    def test_management_endpoints(self):
        """
        Test management functions of context broker client
        """
        with ContextBrokerClient(
            url=settings.CB_URL, fiware_header=self.fiware_header
        ) as client:
            self.assertIsNotNone(client.get_version())
            self.assertEqual(client.get_resources(), self.resources)

    def test_statistics(self):
        """
        Test statistics of context broker client
        """
        with ContextBrokerClient(
            url=settings.CB_URL, fiware_header=self.fiware_header
        ) as client:
            self.assertIsNotNone(client.get_statistics())

    @clean_test(
        fiware_service=settings.FIWARE_SERVICE,
        fiware_servicepath=settings.FIWARE_SERVICEPATH,
        cb_url=settings.CB_URL,
        iota_url=settings.IOTA_JSON_URL,
    )
    def test_pagination(self):
        """
        Test pagination of context broker client
        Test pagination. only works if enough entities are available
        """
        with ContextBrokerClient(
            url=settings.CB_URL, fiware_header=self.fiware_header
        ) as client:
            entities_a = [
                ContextEntity(id=str(i), type=f"filip:object:TypeA")
                for i in range(0, 1000)
            ]
            client.update(action_type=ActionType.APPEND, entities=entities_a)
            entities_b = [
                ContextEntity(id=str(i), type=f"filip:object:TypeB")
                for i in range(1000, 2001)
            ]
            client.update(action_type=ActionType.APPEND, entities=entities_b)
            self.assertLessEqual(len(client.get_entity_list(limit=1)), 1)
            self.assertLessEqual(len(client.get_entity_list(limit=999)), 999)
            self.assertLessEqual(len(client.get_entity_list(limit=1001)), 1001)
            self.assertLessEqual(len(client.get_entity_list(limit=2001)), 2001)

    @clean_test(
        fiware_service=settings.FIWARE_SERVICE,
        fiware_servicepath=settings.FIWARE_SERVICEPATH,
        cb_url=settings.CB_URL,
    )
    def test_entity_filtering(self):
        """
        Test filter operations of context broker client
        """
        with ContextBrokerClient(
            url=settings.CB_URL, fiware_header=self.fiware_header
        ) as client:
            # test patterns
            with self.assertRaises(ValueError):
                client.get_entity_list(id_pattern="(&()?")
            with self.assertRaises(ValueError):
                client.get_entity_list(type_pattern="(&()?")
            entities_a = [
                ContextEntity(id=str(i), type=f"filip:object:TypeA")
                for i in range(0, 5)
            ]

            client.update(action_type=ActionType.APPEND, entities=entities_a)
            entities_b = [
                ContextEntity(id=str(i), type=f"filip:object:TypeB")
                for i in range(6, 10)
            ]

            client.update(action_type=ActionType.APPEND, entities=entities_b)

            entities_all = client.get_entity_list()
            entities_by_id_pattern = client.get_entity_list(id_pattern=".*[1-5]")
            self.assertLess(len(entities_by_id_pattern), len(entities_all))

            entities_by_type_pattern = client.get_entity_list(type_pattern=".*TypeA$")
            self.assertLess(len(entities_by_type_pattern), len(entities_all))

            qs = QueryString(qs=[("presentValue", ">", 0)])
            entities_by_query = client.get_entity_list(q=qs)
            self.assertLess(len(entities_by_query), len(entities_all))

            # test options
            for opt in list(AttrsFormat):
                entities_by_option = client.get_entity_list(response_format=opt)
                self.assertEqual(len(entities_by_option), len(entities_all))
                self.assertEqual(
                    client.get_entity(entity_id="0", response_format=opt),
                    entities_by_option[0],
                )
            with self.assertRaises(ValueError):
                client.get_entity_list(response_format="not in AttrFormat")

            client.update(action_type=ActionType.DELETE, entities=entities_a)

            client.update(action_type=ActionType.DELETE, entities=entities_b)

    @clean_test(
        fiware_service=settings.FIWARE_SERVICE,
        fiware_servicepath=settings.FIWARE_SERVICEPATH,
        cb_url=settings.CB_URL,
    )
    def test_entity_operations(self):
        """
        Test entity operations of context broker client
        """
        with ContextBrokerClient(
            url=settings.CB_URL, fiware_header=self.fiware_header
        ) as client:
            client.post_entity(entity=self.entity, update=True)
            res_entity = client.get_entity(entity_id=self.entity.id)
            self.assertEqual(
                res_entity,
                client.get_entity(
                    entity_id=self.entity.id,
                    attrs=list(res_entity.get_attribute_names()),
                ),
            )
            self.assertEqual(
                client.get_entity_attributes(entity_id=self.entity.id),
                res_entity.get_properties(response_format="dict"),
            )
            res_entity.temperature.value = 25
            client.update_entity(entity=res_entity)
            self.assertEqual(client.get_entity(entity_id=self.entity.id), res_entity)
            res_entity.add_attributes(
                {"pressure": ContextAttribute(type="Number", value=1050)}
            )
            client.update_entity(entity=res_entity)
            self.assertEqual(client.get_entity(entity_id=self.entity.id), res_entity)
            # delete attribute
            res_entity.delete_attributes(
                attrs={"pressure": ContextAttribute(type="Number", value=1050)}
            )
            client.post_entity(entity=res_entity, update=True)
            self.assertEqual(client.get_entity(entity_id=self.entity.id), res_entity)

    @clean_test(
        fiware_service=settings.FIWARE_SERVICE,
        fiware_servicepath=settings.FIWARE_SERVICEPATH,
        cb_url=settings.CB_URL,
    )
    def test_get_entity_list_with_bad_validation(self):

        def post_entity_request(data):
            headers = {"Content-Type": "application/json"}
            headers.update(self.fiware_header.model_dump(by_alias=True))
            url = f"{settings.CB_URL}v2/entities"
            response = requests.request("POST", url, headers=headers, data=data)
            return response

        # Send bad entities to the Context Broker
        entity_wrong_value_type = {
            "id": "test:weather_station_1",
            "type": "WeatherStation",
            "temperature": {"type": "Number", "value": "Error"},
        }

        entity_wrong_unit = {
            "id": "test:weather_station_2",
            "type": "WeatherStation",
            "temperature": {
                "type": "Number",
                "value": 20,
                "metadata": {"unitCode": {"type": "Text", "value": "Error"}},
            },
        }

        entities_invalid = [entity_wrong_value_type, entity_wrong_unit]

        for entity in entities_invalid:
            payload = json.dumps(entity)
            post_entity_request(data=payload)

        # send dummy valid entities to the Context Broker
        entities_valid = [
            ContextEntity(id=f"test374:Entity:{i}", type="Test") for i in range(10)
        ]
        self.client.update(entities=entities_valid, action_type="append")

        # The bad entities should not block the whole request
        entities_res = self.client.get_entity_list()
        entities_res_all = self.client.get_entity_list(include_invalid=True)

        self.assertEqual(len(entities_res), len(entities_valid))
        self.assertEqual(
            (
                len(entities_res_all.valid_entities)
                + len(entities_res_all.invalid_entities)
            ),
            (len(entities_valid) + len(entities_invalid)),
        )

    @clean_test(
        fiware_service=settings.FIWARE_SERVICE,
        fiware_servicepath=settings.FIWARE_SERVICEPATH,
        cb_url=settings.CB_URL,
    )
    def test_entity_update(self):
        """
        Test different ways (post, update, override, patch) to update entity
        Both with the update scenario
        1) append attribute
        2) update existing attribute value
        1) delete attribute

        Returns:

        """
        with ContextBrokerClient(
            url=settings.CB_URL, fiware_header=self.fiware_header
        ) as client:
            entity_init = self.entity.model_copy(deep=True)
            attr_init = entity_init.get_attribute("temperature")
            attr_init.metadata = {
                "metadata_init": {"type": "Text", "value": "something"}
            }
            attr_append = NamedContextAttribute(
                **{"name": "pressure", "type": "Number", "value": 1050}
            )
            entity_init.update_attribute(attrs=[attr_init])

            # Post
            if "post":
                client.post_entity(entity=entity_init, update=True)
                entity_post = entity_init.model_copy(deep=True)
                # 1) append attribute
                entity_post.add_attributes(attrs=[attr_append])
                client.post_entity(entity=entity_post, patch=True)
                self.assertEqual(
                    client.get_entity(entity_id=entity_post.id), entity_post
                )
                # 2) update existing attribute value
                attr_append_update = NamedContextAttribute(
                    **{"name": "pressure", "type": "Number", "value": 2050}
                )
                entity_post.update_attribute(attrs=[attr_append_update])
                client.post_entity(entity=entity_post, patch=True)
                self.assertEqual(
                    client.get_entity(entity_id=entity_post.id), entity_post
                )
                # 3) delete attribute
                entity_post.delete_attributes(attrs=[attr_append])
                client.post_entity(entity=entity_post, update=True)
                self.assertEqual(
                    client.get_entity(entity_id=entity_post.id), entity_post
                )
                clear_all(fiware_header=self.fiware_header, cb_url=settings.CB_URL)

            # update_entity()
            if "update_entity":
                client.post_entity(entity=entity_init, update=True)
                entity_update = entity_init.model_copy(deep=True)
                # 1) append attribute
                entity_update.add_attributes(attrs=[attr_append])
                # change the value of existing attributes
                entity_update.temperature.value = 30
                with self.assertRaises(requests.RequestException):
                    client.update_entity(entity=entity_update, append_strict=True)
                entity_updated = client.get_entity(entity_id=entity_update.id)
                self.assertEqual(
                    entity_updated.get_attribute_names(),
                    entity_update.get_attribute_names(),
                )
                self.assertNotEqual(
                    entity_updated.temperature.value, entity_update.temperature.value
                )
                # change back the value
                entity_update.temperature.value = 20.0
                # 2) update existing attribute value
                attr_append_update = NamedContextAttribute(
                    **{"name": "pressure", "type": "Number", "value": 2050}
                )
                entity_update.update_attribute(attrs=[attr_append_update])
                client.update_entity(
                    entity=ContextEntity(
                        **{
                            "id": entity_update.id,
                            "type": entity_update.type,
                            "pressure": {"type": "Number", "value": 2050},
                        }
                    )
                )
                self.assertEqual(
                    client.get_entity(entity_id=entity_update.id), entity_update
                )
                # 3) delete attribute
                entity_update.delete_attributes(attrs=[attr_append])
                client.update_entity(entity=entity_update)
                self.assertNotEqual(
                    client.get_entity(entity_id=entity_update.id), entity_update
                )
                clear_all(fiware_header=self.fiware_header, cb_url=settings.CB_URL)

            # override_entity()
            if "override_entity":
                client.post_entity(entity=entity_init, update=True)
                entity_override = entity_init.model_copy(deep=True)
                # 1) append attribute
                entity_override.add_attributes(attrs=[attr_append])
                client.override_entity(entity=entity_override)
                self.assertEqual(
                    client.get_entity(entity_id=entity_override.id), entity_override
                )
                # 2) update existing attribute value
                attr_append_update = NamedContextAttribute(
                    **{"name": "pressure", "type": "Number", "value": 2050}
                )
                entity_override.update_attribute(attrs=[attr_append_update])
                client.override_entity(entity=entity_override)
                self.assertEqual(
                    client.get_entity(entity_id=entity_override.id), entity_override
                )
                # 3) delete attribute
                entity_override.delete_attributes(attrs=[attr_append])
                client.override_entity(entity=entity_override)
                self.assertEqual(
                    client.get_entity(entity_id=entity_override.id), entity_override
                )
                clear_all(fiware_header=self.fiware_header, cb_url=settings.CB_URL)

            # patch_entity
            if "patch_entity":
                client.post_entity(entity=entity_init, update=True)
                entity_patch = entity_init.model_copy(deep=True)
                # 1) append attribute
                entity_patch.add_attributes(attrs=[attr_append])
                client.patch_entity(entity=entity_patch)
                self.assertEqual(
                    client.get_entity(entity_id=entity_patch.id), entity_patch
                )
                # 2) update existing attribute value
                attr_append_update = NamedContextAttribute(
                    **{"name": "pressure", "type": "Number", "value": 2050}
                )
                entity_patch.update_attribute(attrs=[attr_append_update])
                client.patch_entity(entity=entity_patch)
                self.assertEqual(
                    client.get_entity(entity_id=entity_patch.id), entity_patch
                )
                # 3) delete attribute
                entity_patch.delete_attributes(attrs=[attr_append])
                client.patch_entity(entity=entity_patch)
                self.assertEqual(
                    client.get_entity(entity_id=entity_patch.id), entity_patch
                )
                clear_all(fiware_header=self.fiware_header, cb_url=settings.CB_URL)

            # 4) update only property or relationship
            if "update_entity_properties" or "update_entity_relationship":
                # post entity with a relationship attribute
                entity_init = self.entity.model_copy(deep=True)
                attrs = [
                    NamedContextAttribute(
                        name="in", type="Relationship", value="dummy1"
                    )
                ]
                entity_init.add_attributes(attrs=attrs)
                client.post_entity(entity=entity_init, update=True)

                # create entity that differs in both attributes
                entity_update = entity_init.model_copy(deep=True)
                attrs = [
                    NamedContextAttribute(name="temperature", type="Number", value=21),
                    NamedContextAttribute(
                        name="in", type="Relationship", value="dummy2"
                    ),
                ]
                entity_update.update_attribute(attrs=attrs)

                # update only properties and compare
                client.update_entity_properties(entity_update)
                entity_db = client.get_entity(entity_update.id)
                db_attrs = entity_db.get_attribute(attribute_name="temperature")
                update_attrs = entity_update.get_attribute(attribute_name="temperature")
                self.assertEqual(db_attrs, update_attrs)
                db_attrs = entity_db.get_attribute(attribute_name="in")
                update_attrs = entity_update.get_attribute(attribute_name="in")
                self.assertNotEqual(db_attrs, update_attrs)

                # update only relationship and compare
                attrs = [
                    NamedContextAttribute(name="temperature", type="Number", value=22)
                ]
                entity_update.update_attribute(attrs=attrs)
                client.update_entity_relationships(entity_update)
                entity_db = client.get_entity(entity_update.id)
                self.assertEqual(
                    entity_db.get_attribute(attribute_name="in"),
                    entity_update.get_attribute(attribute_name="in"),
                )
                self.assertNotEqual(
                    entity_db.get_attribute(attribute_name="temperature"),
                    entity_update.get_attribute(attribute_name="temperature"),
                )

                # change both, update both, compare
                attrs = [
                    NamedContextAttribute(name="temperature", type="Number", value=23),
                    NamedContextAttribute(
                        name="in", type="Relationship", value="dummy3"
                    ),
                ]
                entity_update.update_attribute(attrs=attrs)
                client.update_entity(entity_update)
                entity_db = client.get_entity(entity_update.id)
                db_attrs = entity_db.get_attribute(attribute_name="in")
                update_attrs = entity_update.get_attribute(attribute_name="in")
                self.assertEqual(db_attrs, update_attrs)
                db_attrs = entity_db.get_attribute(attribute_name="temperature")
                update_attrs = entity_update.get_attribute(attribute_name="temperature")
                self.assertEqual(db_attrs, update_attrs)

    @clean_test(
        fiware_service=settings.FIWARE_SERVICE,
        fiware_servicepath=settings.FIWARE_SERVICEPATH,
        cb_url=settings.CB_URL,
    )
    def test_attribute_operations(self):
        """
        Test attribute operations of context broker client
        """
        with ContextBrokerClient(
            url=settings.CB_URL, fiware_header=self.fiware_header
        ) as client:
            entity = self.entity
            attr_txt = NamedContextAttribute(name="attr_txt", type="Text", value="Test")
            attr_bool = NamedContextAttribute(
                name="attr_bool", type="Boolean", value=True
            )
            attr_float = NamedContextAttribute(
                name="attr_float", type="Number", value=round(random.random(), 5)
            )
            attr_list = NamedContextAttribute(
                name="attr_list", type="StructuredValue", value=[1, 2, 3]
            )
            attr_dict = NamedContextAttribute(
                name="attr_dict", type="StructuredValue", value={"key": "value"}
            )
            entity.add_attributes(
                [attr_txt, attr_bool, attr_float, attr_list, attr_dict]
            )

            self.assertIsNotNone(client.post_entity(entity=entity, update=True))
            res_entity = client.get_entity(entity_id=entity.id)

            for attr in entity.get_properties():
                self.assertIn(attr, res_entity.get_properties())
                res_attr = client.get_attribute(
                    entity_id=entity.id, attr_name=attr.name
                )

                self.assertEqual(type(res_attr.value), type(attr.value))
                self.assertEqual(res_attr.value, attr.value)
                value = client.get_attribute_value(
                    entity_id=entity.id, attr_name=attr.name
                )
                # unfortunately FIWARE returns an int for 20.0 although float
                # is expected
                if isinstance(value, int) and not isinstance(value, bool):
                    value = float(value)
                self.assertEqual(type(value), type(attr.value))
                self.assertEqual(value, attr.value)

            for attr_name, attr in entity.get_properties(
                response_format="dict"
            ).items():

                client.update_entity_attribute(
                    entity_id=entity.id, attr_name=attr_name, attr=attr
                )
                value = client.get_attribute_value(
                    entity_id=entity.id, attr_name=attr_name
                )
                # unfortunately FIWARE returns an int for 20.0 although float
                # is expected
                if isinstance(value, int) and not isinstance(value, bool):
                    value = float(value)
                self.assertEqual(type(value), type(attr.value))
                self.assertEqual(value, attr.value)

            new_value = 1337.0
            client.update_attribute_value(
                entity_id=entity.id, attr_name="temperature", value=new_value
            )
            attr_value = client.get_attribute_value(
                entity_id=entity.id, attr_name="temperature"
            )
            self.assertEqual(attr_value, new_value)

    @clean_test(
        fiware_service=settings.FIWARE_SERVICE,
        fiware_servicepath=settings.FIWARE_SERVICEPATH,
        cb_url=settings.CB_URL,
    )
    def test_type_operations(self):
        """
        Test type operations of context broker client
        """
        with ContextBrokerClient(
            url=settings.CB_URL, fiware_header=self.fiware_header
        ) as client:
            self.assertIsNotNone(client.post_entity(entity=self.entity, update=True))
            client.get_entity_types()
            client.get_entity_types(options="count")
            client.get_entity_types(options="values")
            client.get_entity_type(entity_type="MyType")
            client.delete_entity(entity_id=self.entity.id, entity_type=self.entity.type)

    # @unittest.skip('Does currently not reliably work in CI')
    @clean_test(
        fiware_service=settings.FIWARE_SERVICE,
        fiware_servicepath=settings.FIWARE_SERVICEPATH,
        cb_url=settings.CB_URL,
    )
    def test_subscriptions(self):
        """
        Test subscription operations of context broker client
        """
        with ContextBrokerClient(
            url=settings.CB_URL, fiware_header=self.fiware_header
        ) as client:
            sub_id = client.post_subscription(
                subscription=self.subscription, skip_initial_notification=True
            )
            sub_res = client.get_subscription(subscription_id=sub_id)
            time.sleep(2)
            sub_update = sub_res.model_copy(
                update={"expires": datetime.now() + timedelta(days=2), "throttling": 1},
            )
            client.update_subscription(subscription=sub_update)
            sub_res_updated = client.get_subscription(subscription_id=sub_id)
            self.assertNotEqual(sub_res.expires, sub_res_updated.expires)
            self.assertEqual(sub_res.id, sub_res_updated.id)
            self.assertGreaterEqual(sub_res_updated.expires, sub_res.expires)
            self.assertEqual(sub_res_updated.throttling, sub_update.throttling)

            sub_with_nans = Subscription.model_validate(
                {
                    "description": "Test subscription with empty values",
                    "subject": {"entities": [{"idPattern": ".*", "type": "Device"}]},
                    "notification": {"http": {"url": "http://localhost:1234"}},
                    "expires": datetime.now() + timedelta(days=1),
                    "throttling": 0,
                }
            )

            sub_with_empty_list = sub_with_nans.model_copy(deep=True)
            sub_with_empty_list.notification.attrs = []

            test_subscriptions = [sub_with_empty_list, sub_with_nans, self.subscription]

            for _sub_raw in test_subscriptions:
                # test duplicate prevention and update
                sub = self.subscription.model_copy(deep=True)
                id1 = client.post_subscription(sub, update=True)
                sub_first_version = client.get_subscription(id1)
                sub.description = "This subscription shall not pass"

                # update=False, should not override the existing
                id2 = client.post_subscription(sub, update=False)
                self.assertEqual(id1, id2)
                sub_second_version = client.get_subscription(id2)
                self.assertEqual(
                    sub_first_version.description, sub_second_version.description
                )

                # update=True, should override the existing
                id2 = client.post_subscription(sub, update=True)
                self.assertEqual(id1, id2)
                sub_second_version = client.get_subscription(id2)
                self.assertNotEqual(
                    sub_first_version.description, sub_second_version.description
                )

                # test that duplicate prevention does not prevent to much
                sub2 = _sub_raw.model_copy()
                sub2.description = "Take this subscription to Fiware"
                sub2.subject.entities = [
                    EntityPattern.model_validate(
                        {"idPattern": ".*", "type": "Building"}
                    )
                ]
                id3 = client.post_subscription(sub2)
                self.assertNotEqual(id1, id3)

                # clean the subscriptions after finish each loop
                client.delete_subscription(id1)
                client.delete_subscription(id3)

    @clean_test(
        fiware_service=settings.FIWARE_SERVICE,
        fiware_servicepath=settings.FIWARE_SERVICEPATH,
        cb_url=settings.CB_URL,
        iota_url=settings.IOTA_JSON_URL,
    )
    def test_subscription_set_status(self):
        """
        Test subscription operations of context broker client
        """
        sub = self.subscription.model_copy(
            update={"expires": datetime.now() + timedelta(days=2)}
        )
        with ContextBrokerClient(
            url=settings.CB_URL, fiware_header=self.fiware_header
        ) as client:
            sub_id = client.post_subscription(subscription=sub)
            sub_res = client.get_subscription(subscription_id=sub_id)
            self.assertEqual(sub_res.status, Status.ACTIVE)

            sub_inactive = sub_res.model_copy(update={"status": Status.INACTIVE})
            client.update_subscription(subscription=sub_inactive)
            sub_res_inactive = client.get_subscription(subscription_id=sub_id)
            self.assertEqual(sub_res_inactive.status, Status.INACTIVE)

            sub_active = sub_res_inactive.model_copy(update={"status": Status.ACTIVE})
            client.update_subscription(subscription=sub_active)
            sub_res_active = client.get_subscription(subscription_id=sub_id)
            self.assertEqual(sub_res_active.status, Status.ACTIVE)

            sub_expired = sub_res_active.model_copy(
                update={"expires": datetime.now() - timedelta(days=365)}
            )
            client.update_subscription(subscription=sub_expired)
            sub_res_expired = client.get_subscription(subscription_id=sub_id)
            self.assertEqual(sub_res_expired.status, Status.EXPIRED)

    @clean_test(
        fiware_service=settings.FIWARE_SERVICE,
        fiware_servicepath=settings.FIWARE_SERVICEPATH,
        cb_url=settings.CB_URL,
        iota_url=settings.IOTA_JSON_URL,
    )
    def test_subscription_alterationtypes(self):
        """
        Test behavior of subscription alterationtypes since Orion 3.7.0
        """
        sub = self.subscription.model_copy()
        sub.subject.condition = Condition(alterationTypes=[])
        sub.notification = Notification(
            mqtt=Mqtt(
                url=settings.MQTT_BROKER_URL_INTERNAL, topic="test/alterationtypes"
            )
        )
        test_entity = ContextEntity(
            id="test:alterationtypes",
            type="Room",
            temperature={"type": "Number", "value": 25.0},
        )

        # test default with empty alterationTypes, triggered during actual change
        self.client.post_entity(test_entity)
        sub_id_default = self.client.post_subscription(subscription=sub)
        test_entity = self.client.get_entity(entity_id=test_entity.id)
        test_entity.temperature.value = 26.0
        self.client.update_entity(test_entity)
        time.sleep(2)
        sub_result_default = self.client.get_subscription(sub_id_default)
        self.assertEqual(sub_result_default.notification.timesSent, 1)
        # not triggered during with no actual update
        self.client.update_entity(test_entity)
        time.sleep(2)
        sub_result_default = self.client.get_subscription(sub_id_default)
        self.assertEqual(sub_result_default.notification.timesSent, 1)
        self.client.delete_subscription(sub_id_default)

        # test entityChange
        sub.subject.condition.alterationTypes = ["entityChange"]
        sub_id_change = self.client.post_subscription(subscription=sub)
        test_entity.temperature.value = 27.0
        self.client.update_entity(test_entity)
        time.sleep(2)
        sub_result_change = self.client.get_subscription(sub_id_change)
        self.assertEqual(sub_result_change.notification.timesSent, 1)
        # not triggered during with no actual update
        self.client.update_entity(test_entity)
        time.sleep(2)
        sub_result_change = self.client.get_subscription(sub_id_change)
        self.assertEqual(sub_result_change.notification.timesSent, 1)
        self.client.delete_subscription(sub_id_change)

        # test entityCreate
        test_entity_create = ContextEntity(
            id="test:alterationtypes2",
            type="Room",
            temperature={"type": "Number", "value": 25.0},
        )
        sub.subject.condition.alterationTypes = ["entityCreate"]
        sub_id_create = self.client.post_subscription(subscription=sub)
        self.client.post_entity(test_entity_create)
        time.sleep(2)
        sub_result_create = self.client.get_subscription(sub_id_create)
        self.assertEqual(sub_result_create.notification.timesSent, 1)
        # not triggered during when update
        test_entity_create = self.client.get_entity(entity_id=test_entity_create.id)
        test_entity_create.temperature.value = 26.0
        self.client.update_entity(test_entity_create)
        time.sleep(2)
        sub_result_create = self.client.get_subscription(sub_id_create)
        self.assertEqual(sub_result_create.notification.timesSent, 1)
        self.client.delete_subscription(sub_id_create)

        # test entityDelete
        sub.subject.condition.alterationTypes = ["entityDelete"]
        sub_id_delete = self.client.post_subscription(subscription=sub)
        self.client.delete_entity(test_entity_create.id)
        time.sleep(2)
        sub_result_delete = self.client.get_subscription(sub_id_delete)
        self.assertEqual(sub_result_delete.notification.timesSent, 1)
        self.client.delete_subscription(sub_id_delete)

        # test entityUpdate (no matter if the entity actually changed or not)
        sub.subject.condition.alterationTypes = ["entityUpdate"]
        sub_id_update = self.client.post_subscription(subscription=sub)
        # triggered when actual change
        test_entity.temperature.value = 28.0
        self.client.update_entity(test_entity)
        time.sleep(2)
        sub_result_update = self.client.get_subscription(sub_id_update)
        self.assertEqual(sub_result_update.notification.timesSent, 1)
        # triggered when no actual change
        self.client.update_entity(test_entity)
        time.sleep(2)
        sub_result_update = self.client.get_subscription(sub_id_update)
        self.assertEqual(sub_result_update.notification.timesSent, 2)
        self.client.delete_subscription(sub_id_update)

    @clean_test(
        fiware_service=settings.FIWARE_SERVICE,
        fiware_servicepath=settings.FIWARE_SERVICEPATH,
        cb_url=settings.CB_URL,
        iota_url=settings.IOTA_JSON_URL,
    )
    def test_mqtt_subscriptions(self):
        mqtt_url = settings.MQTT_BROKER_URL
        mqtt_url_internal = settings.MQTT_BROKER_URL_INTERNAL
        mqtt_topic = "".join([settings.FIWARE_SERVICE, settings.FIWARE_SERVICEPATH])
        notification = self.subscription.notification.model_copy(
            update={"http": None, "mqtt": Mqtt(url=mqtt_url_internal, topic=mqtt_topic)}
        )
        subscription = self.subscription.model_copy(
            update={
                "notification": notification,
                "description": "MQTT test subscription",
                "expires": None,
            }
        )
        entity = ContextEntity(id="myID", type="Room", **self.attr)

        self.client.post_entity(entity=entity)
        sub_id = self.client.post_subscription(subscription)

        sub_message = None

        def on_connect(client, userdata, flags, reasonCode, properties=None):
            if reasonCode != 0:
                logger.error(f"Connection failed with error code: " f"'{reasonCode}'")
                raise ConnectionError
            else:
                logger.info(
                    "Successfully, connected with result code " + str(reasonCode)
                )
            client.subscribe(mqtt_topic)

        def on_subscribe(client, userdata, mid, granted_qos, properties=None):
            logger.info("Successfully subscribed to with QoS: %s", granted_qos)

        def on_message(client, userdata, msg):
            logger.info(msg.topic + " " + str(msg.payload))
            nonlocal sub_message
            sub_message = Message.model_validate_json(msg.payload)

        def on_disconnect(client, userdata, flags, reasonCode, properties=None):
            logger.info("MQTT client disconnected with reasonCode " + str(reasonCode))

        import paho.mqtt.client as mqtt

        mqtt_client = mqtt.Client(
            userdata=None,
            protocol=mqtt.MQTTv5,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            transport="tcp",
        )
        # add our callbacks to the client
        mqtt_client.on_connect = on_connect
        mqtt_client.on_subscribe = on_subscribe
        mqtt_client.on_message = on_message
        mqtt_client.on_disconnect = on_disconnect

        # connect to the server
        mqtt_client.connect(
            host=mqtt_url.host,
            port=mqtt_url.port,
            keepalive=60,
            bind_address="",
            bind_port=0,
            clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY,
            properties=None,
        )

        # create a non-blocking thread for mqtt communication
        mqtt_client.loop_start()
        new_value = 50

        time.sleep(2)
        self.client.update_attribute_value(
            entity_id=entity.id,
            attr_name="temperature",
            value=new_value,
            entity_type=entity.type,
        )
        time.sleep(2)

        # test if the subscriptions arrives and the content aligns with updates
        self.assertIsNotNone(sub_message)
        self.assertEqual(sub_id, sub_message.subscriptionId)
        self.assertEqual(new_value, sub_message.data[0].temperature.value)
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        time.sleep(2)

    @clean_test(
        fiware_service=settings.FIWARE_SERVICE,
        fiware_servicepath=settings.FIWARE_SERVICEPATH,
        cb_url=settings.CB_URL,
    )
    def test_override_entity_keyvalues(self):
        entity1 = self.entity.model_copy(deep=True)
        # initial entity
        self.client.post_entity(entity1)

        # entity with key value
        entity1_key_value = self.client.get_entity(
            entity_id=entity1.id, response_format=AttrsFormat.KEY_VALUES
        )

        # override entity with ContextEntityKeyValues
        entity1_key_value.temperature = 30
        self.client.override_entity(entity=entity1_key_value, key_values=True)
        self.assertEqual(
            entity1_key_value,
            self.client.get_entity(
                entity_id=entity1.id, response_format=AttrsFormat.KEY_VALUES
            ),
        )
        # test replace all attributes
        entity1_key_value_dict = entity1_key_value.model_dump()
        entity1_key_value_dict["temp"] = 40
        entity1_key_value_dict["humidity"] = 50
        self.client.override_entity(
            entity=ContextEntityKeyValues(**entity1_key_value_dict), key_values=True
        )
        self.assertEqual(
            entity1_key_value_dict,
            self.client.get_entity(
                entity_id=entity1.id, response_format=AttrsFormat.KEY_VALUES
            ).model_dump(),
        )

    @clean_test(
        fiware_service=settings.FIWARE_SERVICE,
        fiware_servicepath=settings.FIWARE_SERVICEPATH,
        cb_url=settings.CB_URL,
    )
    def test_update_entity_keyvalues(self):
        entity1 = self.entity.model_copy(deep=True)
        # initial entity
        self.client.post_entity(entity1)

        # key value
        entity1_key_value = self.client.get_entity(
            entity_id=entity1.id, response_format=AttrsFormat.KEY_VALUES
        )

        # update entity with ContextEntityKeyValues
        entity1_key_value.temperature = 30
        self.client.update_entity(entity=entity1_key_value, key_values=True)
        self.assertEqual(
            entity1_key_value,
            self.client.get_entity(
                entity_id=entity1.id, response_format=AttrsFormat.KEY_VALUES
            ),
        )
        entity2 = self.client.get_entity(entity_id=entity1.id)
        self.assertEqual(entity1.temperature.type, entity2.temperature.type)

        # update entity with dictionary
        entity1_key_value_dict = entity1_key_value.model_dump()
        entity1_key_value_dict["temperature"] = 40
        self.client.update_entity(entity=entity1_key_value_dict, key_values=True)
        self.assertEqual(
            entity1_key_value_dict,
            self.client.get_entity(
                entity_id=entity1.id, response_format=AttrsFormat.KEY_VALUES
            ).model_dump(),
        )
        entity3 = self.client.get_entity(entity_id=entity1.id)
        self.assertEqual(entity1.temperature.type, entity3.temperature.type)
        # if attribute not existing, will be created
        entity1_key_value_dict.update({"humidity": 50})
        self.client.update_entity(entity=entity1_key_value_dict, key_values=True)
        self.assertEqual(
            entity1_key_value_dict,
            self.client.get_entity(
                entity_id=entity1.id, response_format=AttrsFormat.KEY_VALUES
            ).model_dump(),
        )

    @clean_test(
        fiware_service=settings.FIWARE_SERVICE,
        fiware_servicepath=settings.FIWARE_SERVICEPATH,
        cb_url=settings.CB_URL,
    )
    def test_update_attributes_keyvalues(self):
        entity1 = self.entity.model_copy(deep=True)
        # initial entity
        self.client.post_entity(entity1)

        # update existing attributes
        self.client.update_or_append_entity_attributes(
            entity_id=entity1.id, attrs={"temperature": 30}, key_values=True
        )
        self.assertEqual(
            30,
            self.client.get_attribute_value(
                entity_id=entity1.id, attr_name="temperature"
            ),
        )

        # update not existing attributes
        self.client.update_or_append_entity_attributes(
            entity_id=entity1.id, attrs={"humidity": 40}, key_values=True
        )
        self.assertEqual(
            40,
            self.client.get_attribute_value(entity_id=entity1.id, attr_name="humidity"),
        )

        # update both existing and not existing attributes
        with self.assertRaises(RequestException):
            self.client.update_or_append_entity_attributes(
                entity_id=entity1.id,
                attrs={"humidity": 50, "co2": 300},
                append_strict=True,
                key_values=True,
            )
        self.client.update_or_append_entity_attributes(
            entity_id=entity1.id, attrs={"humidity": 50, "co2": 300}, key_values=True
        )
        self.assertEqual(
            50,
            self.client.get_attribute_value(entity_id=entity1.id, attr_name="humidity"),
        )
        self.assertEqual(
            300, self.client.get_attribute_value(entity_id=entity1.id, attr_name="co2")
        )
        self.assertEqual(
            30,
            self.client.get_attribute_value(
                entity_id=entity1.id, attr_name="temperature"
            ),
        )

    @clean_test(
        fiware_service=settings.FIWARE_SERVICE,
        fiware_servicepath=settings.FIWARE_SERVICEPATH,
        cb_url=settings.CB_URL,
    )
    def test_validate_relationships(self):
        """
        Test the features to validate the relationships based on the target entities.
        """
        # create entities with relationships
        # create 10 entities as target
        entities_target = [
            ContextEntity(id=f"test:relationship:target:00{i}", type="Test")
            for i in range(10)
        ]
        self.client.update(entities=entities_target, action_type=ActionType.APPEND)

        # create 10 entities point to the target entities (5 normalized, and 5 keyValues)
        entities_n = [
            ContextEntity(
                id=f"test:relationship:normal:00{i}",
                type="Test",
                dummyAttr={
                    "type": DataType.NUMBER.value,
                    "value": None,
                },
                relatedTo={
                    "type": DataType.RELATIONSHIP.value,  # the relationship is correct
                    "value": entities_target[i].id,
                },
            )
            for i in range(5)
        ]
        self.client.update(entities=entities_n, action_type=ActionType.APPEND)

        entities_kv = [
            ContextEntityKeyValues(
                id=f"test:relationship:kv:00{i}",
                type="Test",
                dummyAttr=None,
                relatedTo=entities_target[i + 5].id,
            )
            for i in range(5)
        ]
        self.client.update(
            entities=entities_kv,
            update_format=AttrsFormat.KEY_VALUES.value,
            action_type=ActionType.APPEND,
        )

        # test update valid relationships
        entities_kv_cb = self.client.get_entity_list(
            entity_ids=[e.id for e in entities_kv]
        )
        for entity in entities_kv_cb:  # before update no relationships are recognized
            self.assertEqual(len(entity.get_relationships()), 0)

        entities_kv_updated = self.client.add_valid_relationships(
            entities=entities_kv_cb
        )
        for entity in entities_kv_updated:
            self.assertEqual(len(entity.get_relationships()), 1)

        # test remove invalid relationships
        entities_n_cb = self.client.get_entity_list(
            entity_ids=[e.id for e in entities_n]
        )
        for entity in entities_n_cb:
            self.assertEqual(len(entity.get_relationships()), 1)
        # delete all target entities to make the relationships invalid
        self.client.delete_entities(entities_target)
        entities_n_updated_hard = self.client.remove_invalid_relationships(
            entities=entities_n_cb, hard_remove=True
        )
        for entity in entities_n_updated_hard:
            self.assertEqual(len(entity.get_relationships()), 0)
            self.assertEqual(len(entity.get_properties()), 1)
        entities_n_updated_soft = self.client.remove_invalid_relationships(
            entities=entities_n_cb, hard_remove=False
        )
        for entity in entities_n_updated_soft:
            self.assertEqual(len(entity.get_relationships()), 0)
            self.assertEqual(len(entity.get_properties()), 2)

    @clean_test(
        fiware_service=settings.FIWARE_SERVICE,
        fiware_servicepath=settings.FIWARE_SERVICEPATH,
        cb_url=settings.CB_URL,
    )
    def test_notification(self):
        mqtt_url = settings.MQTT_BROKER_URL
        mqtt_url_internal = settings.MQTT_BROKER_URL_INTERNAL
        entity = ContextEntity.model_validate(
            {
                "id": "Test:001",
                "type": "Test",
                "temperature": {"type": "Number", "value": 0},
                "humidity": {"type": "Number", "value": 0},
                "co2": {"type": "Number", "value": 0},
            }
        )
        mqtt_topic = "notification/test"
        sub_with_empty_notification = Subscription.model_validate(
            {
                "description": "Test notification with empty values",
                "subject": {"entities": [{"id": "Test:001", "type": "Test"}]},
                "notification": {
                    "mqtt": {"url": mqtt_url_internal, "topic": mqtt_topic},
                    "attrs": [],  # empty attrs list
                },
                "expires": datetime.now() + timedelta(days=1),
                "throttling": 0,
            }
        )
        sub_with_none_notification = Subscription.model_validate(
            {
                "description": "Test notification with none values",
                "subject": {"entities": [{"id": "Test:001", "type": "Test"}]},
                "notification": {
                    "mqtt": {"url": mqtt_url_internal, "topic": mqtt_topic},
                    "attrs": None,  # attrs = None
                },
                "expires": datetime.now() + timedelta(days=1),
                "throttling": 0,
            }
        )
        sub_with_single_attr_notification = Subscription.model_validate(
            {
                "description": "Test notification with single attribute",
                "subject": {"entities": [{"id": "Test:001", "type": "Test"}]},
                "notification": {
                    "mqtt": {"url": mqtt_url_internal, "topic": mqtt_topic},
                    "attrs": ["temperature"],
                },
                "expires": datetime.now() + timedelta(days=1),
                "throttling": 0,
            }
        )

        mqtt_custom_topic = "notification/custom"
        sub_with_mqtt_custom_notification_payload = Subscription.model_validate(
            {
                "description": "Test mqtt custom notification with payload message",
                "subject": {"entities": [{"id": "Test:001", "type": "Test"}]},
                "notification": {
                    "mqttCustom": {
                        "url": mqtt_url_internal,
                        "topic": mqtt_custom_topic,
                        "payload": "The value of the %22temperature%22 attribute %28of the device ${id}, ${type}%29 is"
                        " ${temperature}. Humidity is ${humidity} and CO2 is ${co2}.",
                    },
                    "attrs": ["temperature", "humidity", "co2"],
                    "onlyChangedAttrs": False,
                },
                "expires": datetime.now() + timedelta(days=1),
                "throttling": 0,
            }
        )

        sub_with_mqtt_custom_notification_json = Subscription.model_validate(
            {
                "description": "Test mqtt custom notification with json message",
                "subject": {"entities": [{"id": "Test:001", "type": "Test"}]},
                "notification": {
                    "mqttCustom": {
                        "url": mqtt_url_internal,
                        "topic": mqtt_custom_topic,
                        "json": {
                            "t": "${temperature}",
                            "h": "${humidity}",
                            "c": "${co2}",
                        },
                    },
                    "attrs": ["temperature", "humidity", "co2"],
                    "onlyChangedAttrs": False,
                },
                "expires": datetime.now() + timedelta(days=1),
                "throttling": 0,
            }
        )

        sub_with_mqtt_custom_notification_ngsi = Subscription.model_validate(
            {
                "description": "Test mqtt custom notification with ngsi message",
                "subject": {"entities": [{"id": "Test:001", "type": "Test"}]},
                "notification": {
                    "mqttCustom": {
                        "url": mqtt_url_internal,
                        "topic": mqtt_custom_topic,
                        "ngsi": {
                            "id": "prefix:${id}",
                            "type": "newType",
                            "temperature": {"value": 123, "type": "Number"},
                            "co2_new": {"value": "${co2}", "type": "Number"},
                        },
                    },
                    "onlyChangedAttrs": False,
                },
                "expires": datetime.now() + timedelta(days=1),
                "throttling": 0,
            }
        )

        sub_with_covered_attrs_notification = Subscription.model_validate(
            {
                "description": "Test notification with covered attributes",
                "subject": {"entities": [{"id": "Test:001", "type": "Test"}]},
                "notification": {
                    "mqtt": {"url": mqtt_url_internal, "topic": mqtt_topic},
                    "attrs": ["temperature", "not_exist_attr"],
                    "covered": True,
                },
                "expires": datetime.now() + timedelta(days=1),
                "throttling": 0,
            }
        )

        # MQTT settings
        custom_sub_message = None
        sub_message = None
        sub_messages = {}

        def on_connect(client, userdata, flags, reasonCode, properties=None):
            if reasonCode != 0:
                logger.error(f"Connection failed with error code: " f"'{reasonCode}'")
                raise ConnectionError
            else:
                logger.info(
                    "Successfully, connected with result code " + str(reasonCode)
                )
            client.subscribe(mqtt_topic)
            client.subscribe(mqtt_custom_topic)

        def on_subscribe(client, userdata, mid, granted_qos, properties=None):
            logger.info("Successfully subscribed to with QoS: %s", granted_qos)

        def on_message(client, userdata, msg):
            logger.info("Received MQTT message: " + msg.topic + " " + str(msg.payload))
            nonlocal sub_message
            nonlocal custom_sub_message
            if msg.topic == mqtt_topic:
                sub_message = Message.model_validate_json(msg.payload)
                sub_messages[sub_message.subscriptionId] = sub_message
            elif msg.topic == mqtt_custom_topic:
                custom_sub_message = msg.payload

        def on_disconnect(client, userdata, flags, reasonCode, properties=None):
            logger.info("MQTT client disconnected with reasonCode " + str(reasonCode))

        import paho.mqtt.client as mqtt

        mqtt_client = mqtt.Client(
            userdata=None,
            protocol=mqtt.MQTTv5,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            transport="tcp",
        )
        # add our callbacks to the client
        mqtt_client.on_connect = on_connect
        mqtt_client.on_subscribe = on_subscribe
        mqtt_client.on_message = on_message
        mqtt_client.on_disconnect = on_disconnect
        # connect to the server
        mqtt_client.connect(
            host=mqtt_url.host,
            port=mqtt_url.port,
            keepalive=60,
            bind_address="",
            bind_port=0,
            clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY,
            properties=None,
        )

        # create a non-blocking thread for mqtt communication
        mqtt_client.loop_start()

        with ContextBrokerClient(
            url=settings.CB_URL, fiware_header=self.fiware_header
        ) as client:
            client.post_entity(entity=entity)
            # test1 notification with empty attrs
            sub_id_1 = client.post_subscription(
                subscription=sub_with_empty_notification
            )
            time.sleep(2)
            client.update_attribute_value(
                entity_id=entity.id, attr_name="temperature", value=10
            )
            # check the notified entities
            time.sleep(2)
            sub_1 = client.get_subscription(sub_id_1)
            self.assertEqual(sub_1.notification.timesSent, 1)
            self.assertEqual(len(sub_message.data[0].get_attributes()), 3)

            # test2 notification with None attrs, which should be identical to
            # the previous one
            sub_id_2 = client.post_subscription(subscription=sub_with_none_notification)
            time.sleep(2)
            subscription_list = client.get_subscription_list()
            self.assertEqual(sub_id_1, sub_id_2)
            self.assertEqual(len(subscription_list), 1)

            client.update_attribute_value(
                entity_id=entity.id, attr_name="humidity", value=20
            )
            time.sleep(2)
            sub_1 = client.get_subscription(sub_id_1)
            self.assertEqual(sub_1.notification.timesSent, 2)
            self.assertEqual(sub_message.data[0].get_attribute("humidity").value, 20)

            # test3 notification with single attribute, which should create a
            # new subscription
            sub_id_3 = client.post_subscription(
                subscription=sub_with_single_attr_notification
            )
            time.sleep(2)
            subscription_list = client.get_subscription_list()
            self.assertNotEqual(sub_id_1, sub_id_3)
            self.assertEqual(len(subscription_list), 2)

            # both sub1 and sub3 will be triggered by this update
            client.update_attribute_value(
                entity_id=entity.id, attr_name="co2", value=30
            )
            time.sleep(2)
            sub_1 = client.get_subscription(sub_id_1)
            sub_3 = client.get_subscription(sub_id_3)
            self.assertEqual(sub_1.notification.timesSent, 3)
            self.assertEqual(sub_3.notification.timesSent, 1)
            self.assertEqual(len(sub_messages[sub_id_1].data[0].get_attributes()), 3)
            self.assertEqual(
                sub_messages[sub_id_1].data[0].get_attribute("co2").value, 30
            )
            self.assertEqual(len(sub_messages[sub_id_3].data[0].get_attributes()), 1)
            self.assertEqual(
                sub_messages[sub_id_3].data[0].get_attribute("temperature").value, 10
            )

            # test4 notification with mqtt custom notification (payload)
            sub_id_4 = client.post_subscription(
                subscription=sub_with_mqtt_custom_notification_payload
            )
            time.sleep(2)
            client.update_attribute_value(
                entity_id=entity.id, attr_name="temperature", value=44
            )
            time.sleep(2)
            sub_4 = client.get_subscription(sub_id_4)
            self.assertEqual(
                first=custom_sub_message,
                second=b'The value of the "temperature" attribute (of the device Test:001, Test) is 44. '
                b"Humidity is 20 and CO2 is 30.",
            )
            self.assertEqual(sub_4.notification.timesSent, 1)
            client.delete_subscription(sub_id_4)

            # test5 notification with mqtt custom notification (json)
            sub_id_5 = client.post_subscription(
                subscription=sub_with_mqtt_custom_notification_json
            )
            time.sleep(2)
            client.update_attribute_value(
                entity_id=entity.id, attr_name="humidity", value=67
            )
            time.sleep(2)
            sub_5 = client.get_subscription(sub_id_5)
            self.assertEqual(first=custom_sub_message, second=b'{"t":44,"h":67,"c":30}')
            self.assertEqual(sub_5.notification.timesSent, 1)
            client.delete_subscription(sub_id_5)

            # test6 notification with mqtt custom notification (ngsi)
            sub_id_6 = client.post_subscription(
                subscription=sub_with_mqtt_custom_notification_ngsi
            )
            time.sleep(2)
            client.update_attribute_value(
                entity_id=entity.id, attr_name="co2", value=78
            )
            time.sleep(2)
            sub_6 = client.get_subscription(sub_id_6)
            sub_message = Message.model_validate_json(custom_sub_message)
            self.assertEqual(sub_6.notification.timesSent, 1)
            self.assertEqual(len(sub_message.data[0].get_attributes()), 4)
            self.assertEqual(sub_message.data[0].id, "prefix:Test:001")
            self.assertEqual(sub_message.data[0].type, "newType")
            self.assertEqual(sub_message.data[0].get_attribute("co2").value, 78)
            self.assertEqual(sub_message.data[0].get_attribute("co2_new").value, 78)
            self.assertEqual(
                sub_message.data[0].get_attribute("temperature").value, 123
            )
            client.delete_subscription(sub_id_6)

            # test7 notification with covered attributes
            sub_id_7 = client.post_subscription(
                subscription=sub_with_covered_attrs_notification,
            )
            time.sleep(2)
            client.update_attribute_value(
                entity_id=entity.id, attr_name="temperature", value=40
            )
            time.sleep(2)
            sub_4 = client.get_subscription(sub_id_7)
            self.assertEqual(sub_4.notification.timesSent, 1)
            notified_attr_names = sub_messages[sub_id_7].data[0].get_attribute_names()
            self.assertEqual(len(notified_attr_names), 2)
            self.assertIn("temperature", notified_attr_names)
            self.assertIn("not_exist_attr", notified_attr_names)
            with self.assertRaises(KeyError):
                # The attribute "not_exist_attr" has type None,
                #  so it will not be taken as an attribute by filip
                sub_messages[sub_id_7].data[0].get_attribute("not_exist_attr")

    @clean_test(
        fiware_service=settings.FIWARE_SERVICE,
        fiware_servicepath=settings.FIWARE_SERVICEPATH,
        cb_url=settings.CB_URL,
    )
    def test_batch_operations(self):
        """
        Test batch operations of context broker client
        """
        with ContextBrokerClient(
            url=settings.CB_URL, fiware_header=self.fiware_header
        ) as client:
            entities = [
                ContextEntity(id=str(i), type=f"filip:object:TypeA")
                for i in range(0, 1000)
            ]
            client.update(entities=entities, action_type=ActionType.APPEND)
            entities = [
                ContextEntity(id=str(i), type=f"filip:object:TypeB")
                for i in range(0, 1000)
            ]
            client.update(entities=entities, action_type=ActionType.APPEND)
            entity = EntityPattern(idPattern=".*", typePattern=".*TypeA$")
            query = Query.model_validate(
                {"entities": [entity.model_dump(exclude_unset=True)]}
            )
            self.assertEqual(
                1000, len(client.query(query=query, response_format="keyValues"))
            )
            # update with keyValues
            entities_keyvalues = [
                ContextEntityKeyValues(
                    id=str(i),
                    type=f"filip:object:TypeC",
                    attr1="text attribute",
                    attr2=1,
                )
                for i in range(0, 1000)
            ]
            client.update(
                entities=entities_keyvalues,
                update_format="keyValues",
                action_type=ActionType.APPEND,
            )
            entity_keyvalues = EntityPattern(idPattern=".*", typePattern=".*TypeC$")
            query_keyvalues = Query.model_validate(
                {"entities": [entity_keyvalues.model_dump(exclude_unset=True)]}
            )
            entities_keyvalues_query = client.query(
                query=query_keyvalues, response_format="keyValues"
            )
            self.assertEqual(1000, len(entities_keyvalues_query))
            self.assertEqual(1000, sum([e.attr2 for e in entities_keyvalues_query]))

    def test_batch_operations_custom_models(self):
        from pydantic import ConfigDict, Field

        # Inherit from ContextEntity
        class WeatherStation(ContextEntity):
            """
            A context specific model for a weather station
            """

            # add default for type if not explicitly set
            type: str = "WeatherStation"
            temperature: ContextAttribute = ContextAttribute(
                type="Number",
                value=20.0,
            )

        # Inherit from ContextEntityKeyValues
        class WeatherStationKeyValues(ContextEntityKeyValues):
            """
            A context specific model for a weather station in keyValues format
            """

            model_config = ConfigDict(coerce_numbers_to_str=True, extra="ignore")
            type: str = "WeatherStation"
            temperature: float = Field(default=20.0)

        # test with normalized model
        weather_station_list = [
            WeatherStation(
                id=f"test_custom_batch:weather_station_{i}",
                temperature={"type": "Number", "value": 20 + i},
            )
            for i in range(5)
        ]

        self.client.update(entities=weather_station_list, action_type="append")
        entities = self.client.get_entity_list()
        # assert entities should have temperature
        self.assertTrue(
            all(
                [
                    entity.model_dump().get("temperature") is not None
                    for entity in entities
                ]
            )
        )
        # delete created entities
        self.client.delete_entities(entities=entities)

        # test with keyValues model
        weather_station_list_keyvalues = [
            WeatherStationKeyValues(
                id=f"test_custom_batch_kv:weather_station_{i}", temperature=20 + i
            )
            for i in range(5)
        ]
        self.client.update(
            entities=weather_station_list_keyvalues,
            update_format="keyValues",
            action_type="append",
        )
        entities_kv = self.client.get_entity_list()
        self.assertTrue(
            all(
                [
                    entity.model_dump().get("temperature") is not None
                    for entity in entities_kv
                ]
            )
        )

    def test_force_update_option(self):
        """
        Test the functionality of the flag forceUpdate
        """
        entity_dict = {
            "id": "TestForceupdate:001",
            "type": "Test",
            "temperature": {"type": "Number", "value": 20},
            "humidity": {"type": "Number", "value": 50},
        }
        entity = ContextEntity(**entity_dict)
        self.client.post_entity(entity=entity)

        # test with only changed attrs
        sub_only_changed_attrs = Subscription(
            **{
                "description": "One subscription to rule them all",
                "subject": {
                    "entities": [
                        {
                            "id": entity.id,
                        }
                    ]
                },
                "notification": {
                    "http": {"url": "http://localhost:1234"},
                    "attrs": ["temperature", "humidity"],
                    "onlyChangedAttrs": True,
                },
            }
        )
        sub_id_1 = self.client.post_subscription(subscription=sub_only_changed_attrs)
        time_sent_1 = 0

        # not activate
        self.client.update_attribute_value(
            entity_id=entity.id, attr_name="temperature", value=20
        )
        time.sleep(2)
        sub_1 = self.client.get_subscription(sub_id_1)
        time_sent_1_is = (
            sub_1.notification.timesSent if sub_1.notification.timesSent else 0
        )
        self.assertEqual(time_sent_1_is, time_sent_1)

        # activate because value changed
        self.client.update_attribute_value(
            entity_id=entity.id, attr_name="temperature", value=21
        )
        time_sent_1 += 1  # should be activated
        time.sleep(2)
        sub_1 = self.client.get_subscription(sub_id_1)
        time_sent_1_is = (
            sub_1.notification.timesSent if sub_1.notification.timesSent else 0
        )
        self.assertEqual(time_sent_1_is, time_sent_1)

        # activate because forceUpdate
        self.client.update_attribute_value(
            entity_id=entity.id, attr_name="temperature", value=21, forcedUpdate=True
        )
        time_sent_1 += 1  # should be activated
        time.sleep(2)
        sub_1 = self.client.get_subscription(sub_id_1)
        time_sent_1_is = (
            sub_1.notification.timesSent if sub_1.notification.timesSent else 0
        )
        self.assertEqual(time_sent_1_is, time_sent_1)

        # test with conditions
        sub_with_conditions = Subscription(
            **{
                "description": "One subscription to rule them all",
                "subject": {
                    "entities": [
                        {
                            "id": entity.id,
                        }
                    ],
                    "condition": {
                        "attrs": ["temperature"],
                        "expression": {"q": "temperature>40"},
                    },
                },
                "notification": {
                    "http": {"url": "http://localhost:1234"},
                    "attrs": ["temperature", "humidity"],
                },
            }
        )
        sub_id_2 = self.client.post_subscription(subscription=sub_with_conditions)
        time_sent_2 = 0

        # not activate
        self.client.update_attribute_value(
            entity_id=entity.id, attr_name="temperature", value=20
        )
        time.sleep(2)
        sub_2 = self.client.get_subscription(sub_id_2)
        time_sent_2_is = (
            sub_2.notification.timesSent if sub_2.notification.timesSent else 0
        )
        self.assertEqual(time_sent_2_is, time_sent_2)

        # activate because condition fulfilled
        self.client.update_attribute_value(
            entity_id=entity.id, attr_name="temperature", value=41
        )
        time_sent_2 += 1  # should be activated
        time.sleep(2)
        sub_2 = self.client.get_subscription(sub_id_2)
        time_sent_2_is = (
            sub_2.notification.timesSent if sub_2.notification.timesSent else 0
        )
        self.assertEqual(time_sent_2_is, time_sent_2)

        # not activate even with forceUpdate
        self.client.update_attribute_value(
            entity_id=entity.id, attr_name="temperature", value=20, forcedUpdate=True
        )
        time.sleep(2)
        sub_2 = self.client.get_subscription(sub_id_2)
        time_sent_2_is = (
            sub_2.notification.timesSent if sub_2.notification.timesSent else 0
        )
        self.assertEqual(time_sent_2_is, time_sent_2)

    @clean_test(
        fiware_service=settings.FIWARE_SERVICE,
        fiware_servicepath=settings.FIWARE_SERVICEPATH,
        cb_url=settings.CB_URL,
        iota_url=settings.IOTA_JSON_URL,
    )
    def test_command_with_mqtt(self):
        """
        Test if a command can be send to a device in FIWARE

        To test this a virtual device is created and provisioned to FIWARE and
        a hosted MQTT Broker

        This test only works if the address of a running MQTT Broker is given in
        the environment ('MQTT_BROKER_URL')

        The main part of this test was taken out of the iot_mqtt_example, see
        there for a complete documentation
        """
        mqtt_broker_url = settings.MQTT_BROKER_URL

        device_attr1 = DeviceAttribute(
            name="temperature",
            object_id="t",
            type="Number",
            metadata={
                "unit": {
                    "type": "Unit",
                    "value": {"name": {"type": "Text", "value": "degree " "Celsius"}},
                }
            },
        )

        # creating a static attribute that holds additional information
        static_device_attr = StaticDeviceAttribute(
            name="info", type="Text", value="Filip example for " "virtual IoT device"
        )
        # creating a command that the IoT device will liston to
        device_command = DeviceCommand(name="heater", type="Boolean")

        device = Device(
            device_id="MyDevice",
            entity_name="MyDevice",
            entity_type="Thing2",
            protocol="IoTA-JSON",
            transport="MQTT",
            apikey=settings.FIWARE_SERVICEPATH.strip("/"),
            attributes=[device_attr1],
            static_attributes=[static_device_attr],
            commands=[device_command],
        )

        device_attr2 = DeviceAttribute(
            name="humidity",
            object_id="h",
            type="Number",
            metadata={"unitText": {"value": "percent", "type": "Text"}},
        )

        device.add_attribute(attribute=device_attr2)

        # Send device configuration to FIWARE via the IoT-Agent. We use the
        # general ngsiv2 httpClient for this.
        service_group = ServiceGroup(
            service=self.fiware_header.service,
            subservice=self.fiware_header.service_path,
            apikey=settings.FIWARE_SERVICEPATH.strip("/"),
            resource="/iot/json",
        )

        # create the Http client node that once sent the device cannot be posted
        # again and you need to use the update command
        config = HttpClientConfig(
            cb_url=settings.CB_URL, iota_url=settings.IOTA_JSON_URL
        )
        client = HttpClient(fiware_header=self.fiware_header, config=config)
        client.iota.post_group(service_group=service_group, update=True)
        client.iota.post_device(device=device, update=True)

        time.sleep(0.5)

        # check if the device is correctly configured. You will notice that
        # unfortunately the iot API does not return all the metadata. However,
        # it will still appear in the context-entity
        device = client.iota.get_device(device_id=device.device_id)

        # check if the data entity is created in the context broker
        entity = client.cb.get_entity(
            entity_id=device.device_id, entity_type=device.entity_type
        )

        # create a mqtt client that we use as representation of an IoT device
        # following the official documentation of Paho-MQTT.
        # https://www.eclipse.org/paho/index.php?page=clients/python/
        # docs/index.php

        # The callback for when the mqtt client receives a CONNACK response from
        # the server. All callbacks need to have this specific arguments,
        # Otherwise the client will not be able to execute them.
        def on_connect(client, userdata, flags, reasonCode, properties=None):
            client.subscribe(f"/{device.apikey}/{device.device_id}/cmd")

        # Callback when the command topic is succesfully subscribed
        def on_subscribe(client, userdata, mid, granted_qos, properties=None):
            pass

        # NOTE: We need to use the apikey of the service-group to send the
        # message to the platform
        def on_message(client, userdata, msg):
            data = json.loads(msg.payload)
            res = {k: v for k, v in data.items()}
            client.publish(
                topic=f"/json/{service_group.apikey}" f"/{device.device_id}/cmdexe",
                payload=json.dumps(res),
            )

        def on_disconnect(client, userdata, flags, reasonCode, properties=None):
            pass

        mqtt_client = mqtt.Client(
            client_id="filip-test",
            userdata=None,
            protocol=mqtt.MQTTv5,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            transport="tcp",
        )

        # add our callbacks to the client
        mqtt_client.on_connect = on_connect
        mqtt_client.on_subscribe = on_subscribe
        mqtt_client.on_message = on_message
        mqtt_client.on_disconnect = on_disconnect

        # extract the form the environment
        mqtt_client.connect(
            host=mqtt_broker_url.host,
            port=mqtt_broker_url.port,
            keepalive=60,
            bind_address="",
            bind_port=0,
            clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY,
            properties=None,
        )
        # create a non-blocking thread for mqtt communication
        mqtt_client.loop_start()

        for attr in device.attributes:
            mqtt_client.publish(
                topic=f"/json/{service_group.apikey}/{device.device_id}/attrs",
                payload=json.dumps({attr.object_id: random.randint(0, 9)}),
            )

        time.sleep(5)
        entity = client.cb.get_entity(
            entity_id=device.device_id, entity_type=device.entity_type
        )

        # create and send a command via the context broker
        context_command = NamedCommand(name=device_command.name, value=False)
        client.cb.post_command(
            entity_id=entity.id, entity_type=entity.type, command=context_command
        )

        time.sleep(5)
        # check the entity the command attribute should now show OK
        entity = client.cb.get_entity(
            entity_id=device.device_id, entity_type=device.entity_type
        )

        # The main part of this test, for all this setup was done
        # This validation is deprecated as it is not stable
        # self.assertEqual("OK", entity.heater_status.value)

        # close the mqtt listening thread
        mqtt_client.loop_stop()
        # disconnect the mqtt device
        mqtt_client.disconnect()

    def test_patch_entity(self) -> None:
        """
        Test the methode: patch_entity

        Returns:
           None
        """

        # setup test-entity
        entity = ContextEntity(id="test_id1", type="test_type1")
        attr1 = NamedContextAttribute(name="attr1", value="1")
        attr1.metadata["m1"] = NamedMetadata(name="meta1", type="metatype", value="2")
        attr2 = NamedContextAttribute(name="attr2", value="2")
        attr1.metadata["m2"] = NamedMetadata(name="meta2", type="metatype", value="3")
        entity.add_attributes([attr1, attr2])

        # sub-Test1: Post new. No old entity not exist or is provided!
        self.client.patch_entity(entity=entity)
        self.assertEqual(entity, self.client.get_entity(entity_id=entity.id))
        self.tearDown()

        # sub-Test2: ID/type of old_entity changed. Old entity is provided and
        # updated!
        self.client.post_entity(entity=entity)
        test_entity = ContextEntity(id="newID", type="newType")
        test_entity.add_attributes([attr1, attr2])
        self.client.patch_entity(test_entity, old_entity=entity)
        self.assertEqual(test_entity, self.client.get_entity(entity_id=test_entity.id))
        # assert that former entity_id is freed again
        with self.assertRaises(RequestException):
            self.client.get_entity(entity_id=entity.id)
        self.tearDown()

        # sub-Test3: a non valid old_entity is provided, but already entity
        # exists
        self.client.post_entity(entity=entity)
        old_entity = ContextEntity(id="newID", type="newType")
        self.client.patch_entity(entity, old_entity=old_entity)
        self.assertEqual(entity, self.client.get_entity(entity_id=entity.id))
        self.tearDown()

        # sub-Test4: non valid old_entity provided, entity is new
        old_entity = ContextEntity(id="newID", type="newType")
        self.client.patch_entity(entity, old_entity=old_entity)
        self.assertEqual(entity, self.client.get_entity(entity_id=entity.id))
        self.tearDown()

        # sub-Test5: New attr, attr del, and attr changed. No Old_entity given
        self.client.post_entity(entity=entity)
        test_entity = ContextEntity(id="test_id1", type="test_type1")
        # check if the test_entity corresponds to the original entity
        self.assertEqual(test_entity.id, entity.id)
        self.assertEqual(test_entity.type, entity.type)
        attr1_changed = NamedContextAttribute(name="attr1", value="2")
        attr1_changed.metadata["m4"] = NamedMetadata(
            name="meta3", type="metatype5", value="4"
        )
        attr3 = NamedContextAttribute(name="attr3", value="3")
        test_entity.add_attributes([attr1_changed, attr3])
        self.client.patch_entity(test_entity)

        self.assertEqual(test_entity, self.client.get_entity(entity_id=entity.id))
        self.tearDown()

        # sub-Test6: Attr changes, concurrent changes in Fiware,
        #            old_entity given

        self.client.post_entity(entity=entity)

        concurrent_entity = ContextEntity(id="test_id1", type="test_type1")
        attr1_changed = copy.deepcopy(attr1)
        attr1_changed.metadata["m1"].value = "3"
        attr1_changed.value = "4"
        concurrent_entity.add_attributes([attr1_changed, attr2])
        self.client.patch_entity(concurrent_entity)

        user_entity = copy.deepcopy(entity)
        attr3 = NamedContextAttribute(name="attr3", value="3")
        user_entity.add_attributes([attr3])
        self.client.patch_entity(user_entity, old_entity=entity)

        result_entity = concurrent_entity
        result_entity.add_attributes([attr2, attr3])

        self.assertEqual(result_entity, self.client.get_entity(entity_id=entity.id))
        self.tearDown()

    def test_delete_entity_devices(self):
        # create devices
        base_device_id = "device:"

        base_entity_id_1 = "urn:ngsi-ld:TemperatureSensor:"
        entity_type_1 = "TemperatureSensor"

        base_entity_id_2 = "urn:ngsi-ld:HumiditySensor:"
        entity_type_2 = "HumiditySensor"

        devices = []

        for i in range(20):
            base_entity_id = base_entity_id_1 if i < 10 else base_entity_id_2
            entity_type = entity_type_1 if i < 10 else entity_type_2

            device_id = base_device_id + str(i)
            entity_id = base_entity_id + str(i)
            device = Device(
                service=settings.FIWARE_SERVICE,
                service_path=settings.FIWARE_SERVICEPATH,
                device_id=device_id,
                entity_type=entity_type,
                entity_name=entity_id,
            )
            devices.append(device)
        self.iotac.post_devices(devices=devices)
        while devices:
            device = devices.pop()
            self.client.delete_entity(
                entity_id=device.entity_name,
                entity_type=device.entity_type,
                delete_devices=True,
                iota_url=settings.IOTA_JSON_URL,
            )
            self.assertEqual(len(self.iotac.get_device_list()), len(devices))

    @clean_test(
        fiware_service=settings.FIWARE_SERVICE,
        fiware_servicepath=settings.FIWARE_SERVICEPATH,
        cb_url=settings.CB_URL,
    )
    def test_send_receive_string(self):
        # test updating a string value
        entity = ContextEntity(id="string_test", type="test_type1")
        entityAttr = NamedContextAttribute(name="data", value="")
        entity.add_attributes([entityAttr])
        self.client.post_entity(entity=entity)

        testData = "hello_test"
        self.client.update_attribute_value(
            entity_id="string_test", attr_name="data", value=testData
        )

        readback = self.client.get_attribute_value(
            entity_id="string_test", attr_name="data"
        )

        self.assertEqual(testData, readback)

        self.client.delete_entity(entity_id="string_test", entity_type="test_type1")

    def test_optional_entity_type(self):
        """
        Test whether the entity type can be optional
        """
        test_entity_id = "entity_type_test"
        test_entity_type = "test1"
        entity = ContextEntity(id=test_entity_id, type=test_entity_type)
        entityAttr = NamedContextAttribute(name="data1", value="")
        entity.add_attributes([entityAttr])
        self.client.post_entity(entity=entity)

        # test post_command
        device_command = DeviceCommand(name="heater", type="Boolean")
        device = Device(
            device_id="MyDevice",
            entity_name="MyDevice",
            entity_type="Thing",
            protocol="IoTA-JSON",
            transport="MQTT",
            apikey=settings.FIWARE_SERVICEPATH.strip("/"),
            commands=[device_command],
        )
        self.iotac.post_device(device=device)
        test_command = NamedCommand(name="heater", value=True)
        self.client.post_command(entity_id="MyDevice", command=test_command)

        # update_or_append_entity_attributes
        entityAttr.value = "value1"
        attr_data2 = NamedContextAttribute(name="data2", value="value2")
        self.client.update_or_append_entity_attributes(
            entity_id=test_entity_id, attrs=[entityAttr, attr_data2]
        )

        # update_existing_entity_attributes
        self.client.update_existing_entity_attributes(
            entity_id=test_entity_id, attrs=[entityAttr, attr_data2]
        )

        # replace_entity_attributes
        self.client.replace_entity_attributes(
            entity_id=test_entity_id, attrs=[entityAttr, attr_data2]
        )

        # delete entity
        self.client.delete_entity(entity_id=test_entity_id)

        # another entity with the same id but different type
        test_entity_id_2 = "entity_type_test"
        test_entity_type_2 = "test2"
        entity_2 = ContextEntity(id=test_entity_id_2, type=test_entity_type_2)
        self.client.post_entity(entity=entity_2)
        self.client.post_entity(entity=entity)

        # update_or_append_entity_attributes
        entityAttr.value = "value1"
        attr_data2 = NamedContextAttribute(name="data2", value="value2")
        with self.assertRaises(requests.HTTPError):
            self.client.update_or_append_entity_attributes(
                entity_id=test_entity_id, attrs=[entityAttr, attr_data2]
            )

        # update_existing_entity_attributes
        with self.assertRaises(requests.HTTPError):
            self.client.update_existing_entity_attributes(
                entity_id=test_entity_id, attrs=[entityAttr, attr_data2]
            )

        # replace_entity_attributes
        with self.assertRaises(requests.HTTPError):
            self.client.replace_entity_attributes(
                entity_id=test_entity_id, attrs=[entityAttr, attr_data2]
            )

        # delete entity
        with self.assertRaises(requests.HTTPError):
            self.client.delete_entity(entity_id=test_entity_id)

    def test_does_entity_exist(self):
        _id = uuid.uuid4()

        entity = ContextEntity(id=str(_id), type="test_type1")
        self.assertFalse(
            self.client.does_entity_exist(entity_id=entity.id, entity_type=entity.type)
        )
        self.client.post_entity(entity=entity)
        self.assertTrue(
            self.client.does_entity_exist(entity_id=entity.id, entity_type=entity.type)
        )

    def tearDown(self) -> None:
        """
        Cleanup test server
        """
        self.client.close()
        clear_all(
            fiware_header=self.fiware_header,
            cb_url=settings.CB_URL,
            iota_url=settings.IOTA_JSON_URL,
        )
