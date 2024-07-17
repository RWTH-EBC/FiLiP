"""
Context Broker Module for API Client
"""
from __future__ import annotations

from copy import deepcopy
from math import inf
from pkg_resources import parse_version
from pydantic import PositiveInt, PositiveFloat, AnyHttpUrl
from pydantic.type_adapter import TypeAdapter
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union
import re
import requests
from urllib.parse import urljoin
import warnings
from filip.clients.base_http_client import BaseHttpClient
from filip.config import settings
from filip.models.base import FiwareHeader, PaginationMethod
from filip.utils.simple_ql import QueryString
from filip.models.ngsi_v2.context import (
    ActionType,
    Command,
    ContextEntity,
    ContextEntityKeyValues,
    ContextAttribute,
    NamedCommand,
    NamedContextAttribute,
    Query,
    Update,
    PropertyFormat,
)
from filip.models.ngsi_v2.base import AttrsFormat
from filip.models.ngsi_v2.subscriptions import Subscription, Message
from filip.models.ngsi_v2.registrations import Registration

if TYPE_CHECKING:
    from filip.clients.ngsi_v2.iota import IoTAClient


class ContextBrokerClient(BaseHttpClient):
    """
    Implementation of NGSI Context Broker functionalities, such as creating
    entities and subscriptions; retrieving, updating and deleting data.
    Further documentation:
    https://fiware-orion.readthedocs.io/en/master/

    Api specifications for v2 are located here:
    https://telefonicaid.github.io/fiware-orion/api/v2/stable/

    Note:
        We use the reference implementation for development. Therefore, some
        other brokers may show slightly different behavior!
    """

    def __init__(
        self,
        url: str = None,
        *,
        session: requests.Session = None,
        fiware_header: FiwareHeader = None,
        **kwargs,
    ):
        """

        Args:
            url: Url of context broker server
            session (requests.Session):
            fiware_header (FiwareHeader): fiware service and fiware service path
            **kwargs (Optional): Optional arguments that ``request`` takes.
        """
        # set service url
        url = url or settings.CB_URL
        super().__init__(
            url=url, session=session, fiware_header=fiware_header, **kwargs
        )

    def __pagination(
        self,
        *,
        method: PaginationMethod = PaginationMethod.GET,
        url: str,
        headers: Dict,
        limit: Union[PositiveInt, PositiveFloat] = None,
        params: Dict = None,
        data: str = None,
    ) -> List[Dict]:
        """
        NGSIv2 implements a pagination mechanism in order to help clients to
        retrieve large sets of resources. This mechanism works for all listing
        operations in the API (e.g. GET /v2/entities, GET /v2/subscriptions,
        POST /v2/op/query, etc.). This function helps getting datasets that are
        larger than the limit for the different GET operations.

        https://fiware-orion.readthedocs.io/en/master/user/pagination/index.html

        Args:
            url: Information about the url, obtained from the original function
            headers: The headers from the original function
            params:
            limit:

        Returns:
            object:

        """
        if limit is None:
            limit = inf
        if limit > 1000:
            params["limit"] = 1000  # maximum items per request
        else:
            params["limit"] = limit

        if self.session:
            session = self.session
        else:
            session = requests.Session()
        with session:
            res = session.request(
                method=method, url=url, params=params, headers=headers, data=data
            )
            if res.ok:
                items = res.json()
                # do pagination
                count = int(res.headers["Fiware-Total-Count"])

                while len(items) < limit and len(items) < count:
                    # Establishing the offset from where entities are retrieved
                    params["offset"] = len(items)
                    params["limit"] = min(1000, (limit - len(items)))
                    res = session.request(
                        method=method,
                        url=url,
                        params=params,
                        headers=headers,
                        data=data,
                    )
                    if res.ok:
                        items.extend(res.json())
                    else:
                        res.raise_for_status()
                self.logger.debug("Received: %s", items)
                return items
            res.raise_for_status()

    # MANAGEMENT API
    def get_version(self) -> Dict:
        """
        Gets version of IoT Agent
        Returns:
            Dictionary with response
        """
        url = urljoin(self.base_url, "version")
        try:
            res = self.get(url=url, headers=self.headers)
            if res.ok:
                return res.json()
            res.raise_for_status()
        except requests.RequestException as err:
            self.logger.error(err)
            raise

    def get_resources(self) -> Dict:
        """
        Gets reo

        Returns:
            Dict
        """
        url = urljoin(self.base_url, "v2")
        try:
            res = self.get(url=url, headers=self.headers)
            if res.ok:
                return res.json()
            res.raise_for_status()
        except requests.RequestException as err:
            self.logger.error(err)
            raise

    # STATISTICS API
    def get_statistics(self) -> Dict:
        """
        Gets statistics of context broker
        Returns:
            Dictionary with response
        """
        url = urljoin(self.base_url, "statistics")
        try:
            res = self.get(url=url, headers=self.headers)
            if res.ok:
                return res.json()
            res.raise_for_status()
        except requests.RequestException as err:
            self.logger.error(err)
            raise

    # CONTEXT MANAGEMENT API ENDPOINTS
    # Entity Operations
    def post_entity(
        self,
        entity: Union[ContextEntity, ContextEntityKeyValues],
        update: bool = False,
        patch: bool = False,
        override_attr_metadata: bool = True,
        key_values: bool = False,
    ):
        """
        Function registers an Object with the NGSI Context Broker,
        if it already exists it can be automatically updated (overwritten)
        if the update bool is True.
        First a post request with the entity is tried, if the response code
        is 422 the entity is uncrossable, as it already exists there are two
        options, either overwrite it, if the attribute have changed
        (e.g. at least one new/new values) (update = True) or leave
        it the way it is (update=False)
        If you only want to manipulate the entities values, you need to set
        patch argument.

        Args:
            entity (ContextEntity/ContextEntityKeyValues):
                Context Entity Object
            update (bool):
                If the response.status_code is 422, whether the override and
                existing entity
            patch (bool):
                If the response.status_code is 422, whether to manipulate the
                existing entity. Omitted if update `True`.
            override_attr_metadata:
                Only applies for patch equal to `True`.
                Whether to override or append the attribute's metadata.
                `True` for overwrite or `False` for update/append
            key_values(bool):
                By default False. If set to True, "options=keyValues" will
                be included in params of  post request. The payload uses
                the keyValues simplified entity representation, i.e.
                ContextEntityKeyValues.
        """
        url = urljoin(self.base_url, "v2/entities")
        headers = self.headers.copy()
        params = {}
        options = []
        if key_values:
            assert isinstance(entity, ContextEntityKeyValues)
            options.append("keyValues")
        else:
            assert isinstance(entity, ContextEntity)
        if options:
            params.update({'options': ",".join(options)})
        try:
            res = self.post(
                url=url, headers=headers, json=entity.model_dump(exclude_none=True),
                params=params,
            )
            if res.ok:
                self.logger.info("Entity successfully posted!")
                return res.headers.get("Location")
            res.raise_for_status()
        except requests.RequestException as err:
            if update and err.response.status_code == 422:
                return self.override_entity(
                    entity=entity, key_values=key_values)
            if patch and err.response.status_code == 422:
                if not key_values:
                    return self.patch_entity(
                        entity=entity, override_attr_metadata=override_attr_metadata
                    )
                else:
                    return self.update_entity_key_values(entity=entity)
            msg = f"Could not post entity {entity.id}"
            self.log_error(err=err, msg=msg)
            raise

    def get_entity_list(
        self,
        *,
        entity_ids: List[str] = None,
        entity_types: List[str] = None,
        id_pattern: str = None,
        type_pattern: str = None,
        q: Union[str, QueryString] = None,
        mq: Union[str, QueryString] = None,
        georel: str = None,
        geometry: str = None,
        coords: str = None,
        limit: PositiveInt = inf,
        attrs: List[str] = None,
        metadata: str = None,
        order_by: str = None,
        response_format: Union[AttrsFormat, str] = AttrsFormat.NORMALIZED,
    ) -> List[Union[ContextEntity, ContextEntityKeyValues, Dict[str, Any]]]:
        r"""
        Retrieves a list of context entities that match different criteria by
        id, type, pattern matching (either id or type) and/or those which
        match a query or geographical query (see Simple Query Language and
        Geographical Queries). A given entity has to match all the criteria
        to be retrieved (i.e., the criteria is combined in a logical AND
        way). Note that pattern matching query parameters are incompatible
        (i.e. mutually exclusive) with their corresponding exact matching
        parameters, i.e. idPattern with id and typePattern with type.

        Args:
            entity_ids: A comma-separated list of elements. Retrieve entities
                whose ID matches one of the elements in the list.
                Incompatible with idPattern,e.g. Boe_Idarium
            entity_types: comma-separated list of elements. Retrieve entities
                whose type matches one of the elements in the list.
                Incompatible with typePattern. Example: Room.
            id_pattern: A correctly formatted regular expression. Retrieve
                entities whose ID matches the regular expression. Incompatible
                with id, e.g. ngsi-ld.* or sensor.*
            type_pattern: A correctly formatted regular expression. Retrieve
                entities whose type matches the regular expression.
                Incompatible with type, e.g. room.*
            q (SimpleQuery): A query expression, composed of a list of
                statements separated by ;, i.e.,
                q=statement1;statement2;statement3. See Simple Query
                Language specification. Example: temperature>40.
            mq (SimpleQuery): A  query expression for attribute metadata,
                composed of a list of statements separated by ;, i.e.,
                mq=statement1;statement2;statement3. See Simple Query
                Language specification. Example: temperature.accuracy<0.9.
            georel: Spatial relationship between matching entities and a
                reference shape. See Geographical Queries. Example: 'near'.
            geometry: Geographical area to which the query is restricted.
                See Geographical Queries. Example: point.
            coords: List of latitude-longitude pairs of coordinates separated
                by ';'. See Geographical Queries. Example: 41.390205,
                2.154007;48.8566,2.3522.
            limit: Limits the number of entities to be retrieved Example: 20
            attrs: Comma-separated list of attribute names whose data are to
                be included in the response. The attributes are retrieved in
                the order specified by this parameter. If this parameter is
                not included, the attributes are retrieved in arbitrary
                order. See "Filtering out attributes and metadata" section
                for more detail. Example: seatNumber.
            metadata: A list of metadata names to include in the response.
                See "Filtering out attributes and metadata" section for more
                detail. Example: accuracy.
            order_by: Criteria for ordering results. See "Ordering Results"
                section for details. Example: temperature,!speed.
            response_format (AttrsFormat, str): Response Format. Note: That if
                'keyValues' or 'values' are used the response model will
                change to List[ContextEntityKeyValues] and to List[Dict[str,
                Any]], respectively.
        Returns:

        """
        url = urljoin(self.base_url, "v2/entities/")
        headers = self.headers.copy()
        params = {}

        if entity_ids and id_pattern:
            raise ValueError
        if entity_types and type_pattern:
            raise ValueError
        if entity_ids:
            if not isinstance(entity_ids, list):
                entity_ids = [entity_ids]
            params.update({"id": ",".join(entity_ids)})
        if id_pattern:
            try:
                re.compile(id_pattern)
            except re.error as err:
                raise ValueError(f"Invalid Pattern: {err}") from err
            params.update({"idPattern": id_pattern})
        if entity_types:
            if not isinstance(entity_types, list):
                entity_types = [entity_types]
            params.update({"type": ",".join(entity_types)})
        if type_pattern:
            try:
                re.compile(type_pattern)
            except re.error as err:
                raise ValueError(f"Invalid Pattern: {err.msg}") from err
            params.update({"typePattern": type_pattern})
        if attrs:
            params.update({"attrs": ",".join(attrs)})
        if metadata:
            params.update({"metadata": ",".join(metadata)})
        if q:
            if isinstance(q, str):
                q = QueryString.parse_str(q)
            params.update({"q": str(q)})
        if mq:
            params.update({"mq": str(mq)})
        if geometry:
            params.update({"geometry": geometry})
        if georel:
            params.update({"georel": georel})
        if coords:
            params.update({"coords": coords})
        if order_by:
            params.update({"orderBy": order_by})
        if response_format not in list(AttrsFormat):
            raise ValueError(f"Value must be in {list(AttrsFormat)}")
        response_format = ",".join(["count", response_format])
        params.update({"options": response_format})
        try:
            items = self.__pagination(
                method=PaginationMethod.GET,
                limit=limit,
                url=url,
                params=params,
                headers=headers,
            )
            if AttrsFormat.NORMALIZED in response_format:
                adapter = TypeAdapter(List[ContextEntity])
                return adapter.validate_python(items)
            if AttrsFormat.KEY_VALUES in response_format:
                adapter = TypeAdapter(List[ContextEntityKeyValues])
                return adapter.validate_python(items)
            return items

        except requests.RequestException as err:
            msg = "Could not load entities"
            self.log_error(err=err, msg=msg)
            raise

    def get_entity(
        self,
        entity_id: str,
        entity_type: str = None,
        attrs: List[str] = None,
        metadata: List[str] = None,
        response_format: Union[AttrsFormat, str] = AttrsFormat.NORMALIZED,
    ) -> Union[ContextEntity, ContextEntityKeyValues, Dict[str, Any]]:
        """
        This operation must return one entity element only, but there may be
        more than one entity with the same ID (e.g. entities with same ID but
        different types). In such case, an error message is returned, with
        the HTTP status code set to 409 Conflict.

        Args:
            entity_id (String): Id of the entity to be retrieved
            entity_type (String): Entity type, to avoid ambiguity in case
                there are several entities with the same entity id.
            attrs (List of Strings): List of attribute names whose data must be
                included in the response. The attributes are retrieved in the
                order specified by this parameter.
                See "Filtering out attributes and metadata" section for more
                detail. If this parameter is not included, the attributes are
                retrieved in arbitrary order, and all the attributes of the
                entity are included in the response.
                Example: temperature, humidity.
            metadata (List of Strings): A list of metadata names to include in
                the response. See "Filtering out attributes and metadata"
                section for more detail. Example: accuracy.
            response_format (AttrsFormat, str): Representation format of
                response
        Returns:
            ContextEntity
        """
        url = urljoin(self.base_url, f"v2/entities/{entity_id}")
        headers = self.headers.copy()
        params = {}
        if entity_type:
            params.update({"type": entity_type})
        if attrs:
            params.update({"attrs": ",".join(attrs)})
        if metadata:
            params.update({"metadata": ",".join(metadata)})
        if response_format not in list(AttrsFormat):
            raise ValueError(f"Value must be in {list(AttrsFormat)}")
        params.update({"options": response_format})

        try:
            res = self.get(url=url, params=params, headers=headers)
            if res.ok:
                self.logger.info("Entity successfully retrieved!")
                self.logger.debug("Received: %s", res.json())
                if response_format == AttrsFormat.NORMALIZED:
                    return ContextEntity(**res.json())
                if response_format == AttrsFormat.KEY_VALUES:
                    return ContextEntityKeyValues(**res.json())
                return res.json()
            res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not load entity {entity_id}"
            self.log_error(err=err, msg=msg)
            raise

    def get_entity_attributes(
        self,
        entity_id: str,
        entity_type: str = None,
        attrs: List[str] = None,
        metadata: List[str] = None,
        response_format: Union[AttrsFormat, str] = AttrsFormat.NORMALIZED,
    ) -> Dict[str, ContextAttribute]:
        """
        This request is similar to retrieving the whole entity, however this
        one omits the id and type fields. Just like the general request of
        getting an entire entity, this operation must return only one entity
        element. If more than one entity with the same ID is found (e.g.
        entities with same ID but different type), an error message is
        returned, with the HTTP status code set to 409 Conflict.

        Args:
            entity_id (String): Id of the entity to be retrieved
            entity_type (String): Entity type, to avoid ambiguity in case
                there are several entities with the same entity id.
            attrs (List of Strings): List of attribute names whose data must be
                included in the response. The attributes are retrieved in the
                order specified by this parameter.
                See "Filtering out attributes and metadata" section for more
                detail. If this parameter is not included, the attributes are
                retrieved in arbitrary order, and all the attributes of the
                entity are included in the response. Example: temperature,
                humidity.
            metadata (List of Strings): A list of metadata names to include in
                the response. See "Filtering out attributes and metadata"
                section for more detail. Example: accuracy.
            response_format (AttrsFormat, str): Representation format of
                response
        Returns:
            Dict
        """
        url = urljoin(self.base_url, f"v2/entities/{entity_id}/attrs")
        headers = self.headers.copy()
        params = {}
        if entity_type:
            params.update({"type": entity_type})
        if attrs:
            params.update({"attrs": ",".join(attrs)})
        if metadata:
            params.update({"metadata": ",".join(metadata)})
        if response_format not in list(AttrsFormat):
            raise ValueError(f"Value must be in {list(AttrsFormat)}")
        params.update({"options": response_format})
        try:
            res = self.get(url=url, params=params, headers=headers)
            if res.ok:
                if response_format == AttrsFormat.NORMALIZED:
                    return {
                        key: ContextAttribute(**values)
                        for key, values in res.json().items()
                    }
                return res.json()
            res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not load attributes from entity {entity_id} !"
            self.log_error(err=err, msg=msg)
            raise

    def update_entity(self, entity: ContextEntity, append_strict: bool = False):
        """
        The request payload is an object representing the attributes to
        append or update.

        Note:
            Update means overwriting the existing entity. If you want to
            manipulate you should rather use patch_entity.

        Args:
            entity (ContextEntity):
            append_strict: If `False` the entity attributes are updated (if they
                previously exist) or appended (if they don't previously exist)
                with the ones in the payload.
                If `True` all the attributes in the payload not
                previously existing in the entity are appended. In addition
                to that, in case some of the attributes in the payload
                already exist in the entity, an error is returned.
                More precisely this means a strict append procedure.

        Returns:
            None
        """
        self.update_or_append_entity_attributes(
            entity_id=entity.id,
            entity_type=entity.type,
            attrs=entity.get_attributes(),
            append_strict=append_strict,
        )

    def update_entity_properties(self, entity: ContextEntity, append_strict: bool = False):
        """
        The request payload is an object representing the attributes, of any type
        but Relationship, to append or update.

        Note:
            Update means overwriting the existing entity. If you want to
            manipulate you should rather use patch_entity.

        Args:
            entity (ContextEntity):
            append_strict: If `False` the entity attributes are updated (if they
                previously exist) or appended (if they don't previously exist)
                with the ones in the payload.
                If `True` all the attributes in the payload not
                previously existing in the entity are appended. In addition
                to that, in case some of the attributes in the payload
                already exist in the entity, an error is returned.
                More precisely this means a strict append procedure.

        Returns:
            None
        """
        self.update_or_append_entity_attributes(
            entity_id=entity.id,
            entity_type=entity.type,
            attrs=entity.get_properties(),
            append_strict=append_strict,
        )

    def update_entity_relationships(self, entity: ContextEntity,
                                    append_strict: bool = False):
        """
        The request payload is an object representing only the attributes, of type
        Relationship, to append or update.

        Note:
            Update means overwriting the existing entity. If you want to
            manipulate you should rather use patch_entity.

        Args:
            entity (ContextEntity):
            append_strict: If `False` the entity attributes are updated (if they
                previously exist) or appended (if they don't previously exist)
                with the ones in the payload.
                If `True` all the attributes in the payload not
                previously existing in the entity are appended. In addition
                to that, in case some of the attributes in the payload
                already exist in the entity, an error is returned.
                More precisely this means a strict append procedure.

        Returns:
            None
        """
        self.update_or_append_entity_attributes(
            entity_id=entity.id,
            entity_type=entity.type,
            attrs=entity.get_relationships(),
            append_strict=append_strict,
        )

    def delete_entity(
        self,
        entity_id: str,
        entity_type: str= None,
        delete_devices: bool = False,
        iota_client: IoTAClient = None,
        iota_url: AnyHttpUrl = settings.IOTA_URL,
    ) -> None:
        """
        Remove a entity from the context broker. No payload is required
        or received.

        Args:
            entity_id:
                Id of the entity to be deleted
            entity_type:
                Entity type, to avoid ambiguity in case there are several
                entities with the same entity id.
            delete_devices:
                If True, also delete all devices that reference this
                entity (entity_id as entity_name)
            iota_client:
                Corresponding IoTA-Client used to access IoTA-Agent
            iota_url:
                URL of the corresponding IoT-Agent. This will autogenerate
                an IoTA-Client, mirroring the information of the
                ContextBrokerClient, e.g. FiwareHeader, and other headers

        Returns:
            None
        """
        url = urljoin(self.base_url, f"v2/entities/{entity_id}")
        headers = self.headers.copy()
        if entity_type:
            params = {'type': entity_type}
        else:
            params = None
        try:
            res = self.delete(url=url, params=params, headers=headers)
            if res.ok:
                self.logger.info("Entity '%s' successfully deleted!", entity_id)
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not delete entity {entity_id} !"
            self.log_error(err=err, msg=msg)
            raise

        if delete_devices:
            from filip.clients.ngsi_v2 import IoTAClient

            if iota_client:
                iota_client_local = deepcopy(iota_client)
            else:
                warnings.warn(
                    "No IoTA-Client object provided! "
                    "Will try to generate one. "
                    "This usage is not recommended."
                )

                iota_client_local = IoTAClient(
                    url=iota_url,
                    fiware_header=self.fiware_headers,
                    headers=self.headers,
                )

            for device in iota_client_local.get_device_list(
                    entity_names=[entity_id]):
                if entity_type:
                    if device.entity_type == entity_type:
                        iota_client_local.delete_device(device_id=device.device_id)
                else:
                    iota_client_local.delete_device(device_id=device.device_id)
            iota_client_local.close()

    def delete_entities(self, entities: List[ContextEntity]) -> None:
        """
        Remove a list of entities from the context broker. This methode is
        more efficient than to call delete_entity() for each entity

        Args:
            entities: List[ContextEntity]: List of entities to be deleted

        Raises:
            Exception, if one of the entities is not in the ContextBroker

        Returns:
            None
        """

        # update() delete, deletes all entities without attributes completely,
        # and removes the attributes for the other
        # The entities are sorted based on the fact if they have
        # attributes.
        entities_with_attributes: List[ContextEntity] = []
        for entity in entities:
            attribute_names = [
                key
                for key in entity.model_dump()
                if key not in ContextEntity.model_fields
            ]
            if len(attribute_names) > 0:
                entities_with_attributes.append(
                    ContextEntity(id=entity.id, type=entity.type)
                )

        # Post update_delete for those without attribute only once,
        # for the other post update_delete again but for the changed entity
        # in the ContextBroker (only id and type left)
        if len(entities) > 0:
            self.update(entities=entities, action_type="delete")
        if len(entities_with_attributes) > 0:
            self.update(entities=entities_with_attributes, action_type="delete")

    def update_or_append_entity_attributes(
            self,
            entity_id: str,
            attrs: List[Union[NamedContextAttribute,
                              Dict[str, ContextAttribute]]],
            entity_type: str = None,
            append_strict: bool = False,
            forcedUpdate: bool = False):
        """
        The request payload is an object representing the attributes to
        append or update. This corresponds to a 'POST' request if append is
        set to 'False'

        Note:
            Be careful not to update attributes that are
            provided via context registration, e.g. commands. Commands are
            removed before sending the request. To avoid breaking things.

        Args:
            entity_id: Entity id to be updated
            entity_type: Entity type, to avoid ambiguity in case there are
                several entities with the same entity id.
            attrs: List of attributes to update or to append
            append_strict: If `False` the entity attributes are updated (if they
                previously exist) or appended (if they don't previously exist)
                with the ones in the payload.
                If `True` all the attributes in the payload not
                previously existing in the entity are appended. In addition
                to that, in case some of the attributes in the payload
                already exist in the entity, an error is returned.
                More precisely this means a strict append procedure.
            forcedUpdate: Update operation have to trigger any matching
                subscription, no matter if there is an actual attribute
                update or no instead of the default behavior, which is to
                updated only if attribute is effectively updated.
        Returns:
            None

        """
        url = urljoin(self.base_url, f"v2/entities/{entity_id}/attrs")
        headers = self.headers.copy()
        params = {}
        if entity_type:
            params.update({'type': entity_type})
        else:
            entity_type = "dummy"

        options = []
        if append_strict:
            options.append("append")
        if forcedUpdate:
            options.append("forcedUpdate")
        if options:
            params.update({'options': ",".join(options)})

        entity = ContextEntity(id=entity_id, type=entity_type)
        entity.add_attributes(attrs)
        # exclude commands from the send data,
        # as they live in the IoTA-agent
        excluded_keys = {"id", "type"}
        excluded_keys.update(
            entity.get_commands(response_format=PropertyFormat.DICT).keys()
        )
        try:
            res = self.post(
                url=url,
                headers=headers,
                json=entity.model_dump(
                    exclude=excluded_keys,
                    exclude_none=True
                ),
                params=params,
            )
            if res.ok:
                self.logger.info("Entity '%s' successfully " "updated!", entity.id)
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not update or append attributes of entity" f" {entity.id} !"
            self.log_error(err=err, msg=msg)
            raise

    def update_entity_key_values(self,
                                 entity: Union[ContextEntityKeyValues, dict],):
        """
        The entity are updated with a ContextEntityKeyValues object or a
        dictionary contain the simplified entity data. This corresponds to a
        'PATCH' request.
        Only existing attribute can be updated!

        Args:
            entity: A ContextEntityKeyValues object or a dictionary contain
            the simplified entity data

        """
        if isinstance(entity, dict):
            entity = ContextEntityKeyValues(**entity)
        url = urljoin(self.base_url, f'v2/entities/{entity.id}/attrs')
        headers = self.headers.copy()
        params = {"type": entity.type,
                  "options": AttrsFormat.KEY_VALUES.value
                  }
        try:
            res = self.patch(url=url,
                             headers=headers,
                             json=entity.model_dump(exclude={'id', 'type'},
                                                    exclude_unset=True),
                             params=params)
            if res.ok:
                self.logger.info("Entity '%s' successfully "
                                 "updated!", entity.id)
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not update attributes of entity" \
                  f" {entity.id} !"
            self.log_error(err=err, msg=msg)
            raise

    def update_entity_attributes_key_values(self,
                                            entity_id: str,
                                            attrs: dict,
                                            entity_type: str = None,
                                            ):
        """
        Update entity with attributes in keyValues form.
        This corresponds to a 'PATcH' request.
        Only existing attribute can be updated!

        Args:
            entity_id: Entity id to be updated
            entity_type: Entity type, to avoid ambiguity in case there are
                several entities with the same entity id.
            attrs: a dictionary that contains the attribute values.
            e.g. {
                "temperature": 21.4,
                "humidity": 50
            }

        Returns:

        """
        if entity_type:
            pass
        else:
            _entity = self.get_entity(entity_id=entity_id)
            entity_type = _entity.type

        entity_dict = attrs.copy()
        entity_dict.update({
            "id": entity_id,
            "type": entity_type
        })
        entity = ContextEntityKeyValues(**entity_dict)
        self.update_entity_key_values(entity=entity)

    def update_existing_entity_attributes(
            self,
            entity_id: str,
            attrs: List[Union[NamedContextAttribute,
                              Dict[str, ContextAttribute]]],
            entity_type: str = None,
            forcedUpdate: bool = False,
            override_metadata: bool = False
    ):
        """
        The entity attributes are updated with the ones in the payload.
        In addition to that, if one or more attributes in the payload doesn't
        exist in the entity, an error is returned. This corresponds to a
        'PATCH' request.

        Args:
            entity_id: Entity id to be updated
            entity_type: Entity type, to avoid ambiguity in case there are
                several entities with the same entity id.
            attrs: List of attributes to update or to append
            forcedUpdate: Update operation have to trigger any matching
                subscription, no matter if there is an actual attribute
                update or no instead of the default behavior, which is to
                updated only if attribute is effectively updated.
            override_metadata:
                Bool,replace the existing metadata with the one provided in
                the request
        Returns:
            None

        """
        url = urljoin(self.base_url, f"v2/entities/{entity_id}/attrs")
        headers = self.headers.copy()
        if entity_type:
            params = {"type": entity_type}
        else:
            params = None
            entity_type = "dummy"

        entity = ContextEntity(id=entity_id, type=entity_type)
        entity.add_attributes(attrs)

        options = []
        if override_metadata:
            options.append("overrideMetadata")
        if forcedUpdate:
            options.append("forcedUpdate")
        if options:
            params.update({'options': ",".join(options)})

        try:
            res = self.patch(
                url=url,
                headers=headers,
                json=entity.model_dump(
                    exclude={"id", "type"},
                    exclude_none=True
                ),
                params=params,
            )
            if res.ok:
                self.logger.info("Entity '%s' successfully " "updated!", entity.id)
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not update attributes of entity" f" {entity.id} !"
            self.log_error(err=err, msg=msg)
            raise

    def override_entity(self,
                        entity: Union[ContextEntity, ContextEntityKeyValues],
                        **kwargs
                        ):
        """
        The request payload is an object representing the attributes to
        override the existing entity.

        Note:
            If you want to manipulate you should rather use patch_entity.

        Args:
            entity (ContextEntity or ContextEntityKeyValues):
        Returns:
            None
        """
        return self.replace_entity_attributes(entity_id=entity.id,
                                              entity_type=entity.type,
                                              attrs=entity.get_attributes(),
                                              **kwargs
                                              )

    def replace_entity_attributes(
            self,
            entity_id: str,
            attrs: Union[List[Union[NamedContextAttribute,
                              Dict[str, ContextAttribute]]],
                         Dict],
            entity_type: str = None,
            forcedUpdate: bool = False,
            key_values: bool = False,
    ):
        """
        The attributes previously existing in the entity are removed and
        replaced by the ones in the request. This corresponds to a 'PUT'
        request.

        Args:
            entity_id: Entity id to be updated
            entity_type: Entity type, to avoid ambiguity in case there are
                several entities with the same entity id.
            attrs: List of attributes to add to the entity or dict of
                attributes in case of key_values=True.
            forcedUpdate: Update operation have to trigger any matching
                subscription, no matter if there is an actual attribute
                update or no instead of the default behavior, which is to
                updated only if attribute is effectively updated.
            key_values(bool):
                By default False. If set to True, "options=keyValues" will
                be included in params of the request. The payload uses
                the keyValues simplified entity representation, i.e.
                ContextEntityKeyValues.
        Returns:
            None
        """
        url = urljoin(self.base_url, f"v2/entities/{entity_id}/attrs")
        headers = self.headers.copy()
        params = {}
        options = []
        if entity_type:
            params.update({"type": entity_type})
        else:
            entity_type = "dummy"

        if forcedUpdate:
            options.append("forcedUpdate")

        if key_values:
            options.append("keyValues")
            assert isinstance(attrs, dict)
        else:
            entity = ContextEntity(id=entity_id, type=entity_type)
            entity.add_attributes(attrs)
            attrs = entity.model_dump(
                    exclude={"id", "type"},
                    exclude_none=True
                )
        if options:
            params.update({'options': ",".join(options)})

        try:
            res = self.put(
                url=url,
                headers=headers,
                json=attrs,
                params=params,
            )
            if res.ok:
                self.logger.info("Entity '%s' successfully " "updated!", entity_id)
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not replace attribute of entity {entity_id} !"
            self.log_error(err=err, msg=msg)
            raise

    # Attribute operations
    def get_attribute(
        self,
        entity_id: str,
        attr_name: str,
        entity_type: str = None,
        metadata: str = None,
        response_format="",
    ) -> ContextAttribute:
        """
        Retrieves a specified attribute from an entity.

        Args:
            entity_id: Id of the entity. Example: Bcn_Welt
            attr_name: Name of the attribute to be retrieved.
            entity_type (Optional): Type of the entity to retrieve
            metadata (Optional): A list of metadata names to include in the
                response. See "Filtering out attributes and metadata" section
                for more detail.

        Returns:
            The content of the retrieved attribute as ContextAttribute

        Raises:
            Error

        """
        url = urljoin(self.base_url, f"v2/entities/{entity_id}/attrs/{attr_name}")
        headers = self.headers.copy()
        params = {}
        if entity_type:
            params.update({"type": entity_type})
        if metadata:
            params.update({"metadata": ",".join(metadata)})
        try:
            res = self.get(url=url, params=params, headers=headers)
            if res.ok:
                self.logger.debug("Received: %s", res.json())
                return ContextAttribute(**res.json())
            res.raise_for_status()
        except requests.RequestException as err:
            msg = (
                f"Could not load attribute '{attr_name}' from entity" f"'{entity_id}' "
            )
            self.log_error(err=err, msg=msg)
            raise

    def update_entity_attribute(self,
                                entity_id: str,
                                attr: Union[ContextAttribute,
                                            NamedContextAttribute],
                                *,
                                entity_type: str = None,
                                attr_name: str = None,
                                override_metadata: bool = True,
                                forcedUpdate: bool = False):
        """
        Updates a specified attribute from an entity.

        Args:
            attr:
                context attribute to update
            entity_id:
                Id of the entity. Example: Bcn_Welt
            entity_type:
                Entity type, to avoid ambiguity in case there are
                several entities with the same entity id.
            forcedUpdate: Update operation have to trigger any matching
                subscription, no matter if there is an actual attribute
                update or no instead of the default behavior, which is to
                updated only if attribute is effectively updated.
            attr_name:
                Name of the attribute to be updated.
            override_metadata:
                Bool, if set to `True` (default) the metadata will be
                overwritten. This is for backwards compatibility reasons.
                If `False` the metadata values will be either updated if
                already existing or append if not.
                See also:
                https://fiware-orion.readthedocs.io/en/master/user/metadata.html
        """
        headers = self.headers.copy()
        if not isinstance(attr, NamedContextAttribute):
            assert attr_name is not None, (
                "Missing name for attribute. "
                "attr_name must be present if"
                "attr is of type ContextAttribute"
            )
        else:
            assert attr_name is None, (
                "Invalid argument attr_name. Do not set "
                "attr_name if attr is of type "
                "NamedContextAttribute"
            )
            attr_name = attr.name

        url = urljoin(self.base_url, f"v2/entities/{entity_id}/attrs/{attr_name}")
        params = {}
        if entity_type:
            params.update({"type": entity_type})
        # set overrideMetadata option (we assure backwards compatibility here)
        options = []
        if override_metadata:
            options.append("overrideMetadata")
        if forcedUpdate:
            options.append("forcedUpdate")
        if options:
            params.update({'options': ",".join(options)})
        try:
            res = self.put(
                url=url,
                headers=headers,
                params=params,
                json=attr.model_dump(
                    exclude={"name"},
                    exclude_none=True
                ),
            )
            if res.ok:
                self.logger.info(
                    "Attribute '%s' of '%s' " "successfully updated!",
                    attr_name,
                    entity_id,
                )
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            msg = (
                f"Could not update attribute '{attr_name}' of entity" f"'{entity_id}' "
            )
            self.log_error(err=err, msg=msg)
            raise

    def delete_entity_attribute(
        self, entity_id: str, attr_name: str, entity_type: str = None
    ) -> None:
        """
        Removes a specified attribute from an entity.

        Args:
            entity_id: Id of the entity.
            attr_name: Name of the attribute to be retrieved.
            entity_type: Entity type, to avoid ambiguity in case there are
            several entities with the same entity id.
        Raises:
            Error

        """
        url = urljoin(self.base_url, f"v2/entities/{entity_id}/attrs/{attr_name}")
        headers = self.headers.copy()
        params = {}
        if entity_type:
            params.update({"type": entity_type})
        try:
            res = self.delete(url=url, headers=headers)
            if res.ok:
                self.logger.info(
                    "Attribute '%s' of '%s' " "successfully deleted!",
                    attr_name,
                    entity_id,
                )
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            msg = (
                f"Could not delete attribute '{attr_name}' of entity '{entity_id}'"
            )
            self.log_error(err=err, msg=msg)
            raise

    # Attribute value operations
    def get_attribute_value(
        self, entity_id: str, attr_name: str, entity_type: str = None
    ) -> Any:
        """
        This operation returns the value property with the value of the
        attribute.

        Args:
            entity_id: Id of the entity. Example: Bcn_Welt
            attr_name: Name of the attribute to be retrieved.
                Example: temperature.
            entity_type: Entity type, to avoid ambiguity in case there are
                several entities with the same entity id.

        Returns:

        """
        url = urljoin(self.base_url, f"v2/entities/{entity_id}/attrs/{attr_name}/value")
        headers = self.headers.copy()
        params = {}
        if entity_type:
            params.update({"type": entity_type})
        try:
            res = self.get(url=url, params=params, headers=headers)
            if res.ok:
                self.logger.debug("Received: %s", res.json())
                return res.json()
            res.raise_for_status()
        except requests.RequestException as err:
            msg = (
                f"Could not load value of attribute '{attr_name}' from "
                f"entity'{entity_id}' "
            )
            self.log_error(err=err, msg=msg)
            raise

    def update_attribute_value(self, *,
                               entity_id: str,
                               attr_name: str,
                               value: Any,
                               entity_type: str = None,
                               forcedUpdate: bool = False
                               ):
        """
        Updates the value of a specified attribute of an entity

        Args:
            value: update value
            entity_id: Id of the entity. Example: Bcn_Welt
            attr_name: Name of the attribute to be retrieved.
                Example: temperature.
            entity_type: Entity type, to avoid ambiguity in case there are
                several entities with the same entity id.
            forcedUpdate: Update operation have to trigger any matching
                subscription, no matter if there is an actual attribute
                update or no instead of the default behavior, which is to
                updated only if attribute is effectively updated.
        Returns:

        """
        url = urljoin(self.base_url, f"v2/entities/{entity_id}/attrs/{attr_name}/value")
        headers = self.headers.copy()
        params = {}
        if entity_type:
            params.update({'type': entity_type})
        options = []
        if forcedUpdate:
            options.append("forcedUpdate")
        if options:
            params.update({'options': ",".join(options)})
        try:
            if not isinstance(value, (dict, list)):
                headers.update({"Content-Type": "text/plain"})
                if isinstance(value, str):
                    value = f"{value}"
                res = self.put(url=url, headers=headers, json=value, params=params)
            else:
                res = self.put(url=url, headers=headers, json=value, params=params)
            if res.ok:
                self.logger.info(
                    "Attribute '%s' of '%s' " "successfully updated!",
                    attr_name,
                    entity_id,
                )
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            msg = (
                f"Could not update value of attribute '{attr_name}' from "
                f"entity '{entity_id}' "
            )
            self.log_error(err=err, msg=msg)
            raise

    # Types Operations
    def get_entity_types(
        self, *, limit: int = None, offset: int = None, options: str = None
    ) -> List[Dict[str, Any]]:
        """

        Args:
            limit: Limit the number of types to be retrieved.
            offset: Skip a number of records.
            options: Options dictionary. Allowed: count, values

        Returns:

        """
        url = urljoin(self.base_url, "v2/types")
        headers = self.headers.copy()
        params = {}
        if limit:
            params.update({"limit": limit})
        if offset:
            params.update({"offset": offset})
        if options:
            params.update({"options": options})
        try:
            res = self.get(url=url, params=params, headers=headers)
            if res.ok:
                self.logger.debug("Received: %s", res.json())
                return res.json()
            res.raise_for_status()
        except requests.RequestException as err:
            msg = "Could not load entity types!"
            self.log_error(err=err, msg=msg)
            raise

    def get_entity_type(self, entity_type: str) -> Dict[str, Any]:
        """

        Args:
            entity_type: Entity Type. Example: Room

        Returns:

        """
        url = urljoin(self.base_url, f"v2/types/{entity_type}")
        headers = self.headers.copy()
        params = {}
        try:
            res = self.get(url=url, params=params, headers=headers)
            if res.ok:
                self.logger.debug("Received: %s", res.json())
                return res.json()
            res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not load entities of type" f"'{entity_type}' "
            self.log_error(err=err, msg=msg)
            raise

    # SUBSCRIPTION API ENDPOINTS
    def get_subscription_list(self, limit: PositiveInt = inf) -> List[Subscription]:
        """
        Returns a list of all the subscriptions present in the system.
        Args:
            limit: Limit the number of subscriptions to be retrieved
        Returns:
            list of subscriptions
        """
        url = urljoin(self.base_url, "v2/subscriptions/")
        headers = self.headers.copy()
        params = {}

        # We always use the 'count' option to check weather pagination is
        # required
        params.update({"options": "count"})
        try:
            items = self.__pagination(
                limit=limit, url=url, params=params, headers=headers
            )
            adapter = TypeAdapter(List[Subscription])
            return adapter.validate_python(items)
        except requests.RequestException as err:
            msg = "Could not load subscriptions!"
            self.log_error(err=err, msg=msg)
            raise

    def post_subscription(
        self,
        subscription: Subscription,
        update: bool = False,
        skip_initial_notification: bool = False,
    ) -> str:
        """
        Creates a new subscription. The subscription is represented by a
        Subscription object defined in filip.cb.models.

        If the subscription already exists, the adding is prevented and the id
        of the existing subscription is returned.

        A subscription is deemed as already existing if there exists a
        subscription with the exact same subject and notification fields. All
        optional fields are not considered.

        Args:
            subscription: Subscription
            update: True - If the subscription already exists, update it
                    False- If the subscription already exists, throw warning
            skip_initial_notification: True - Initial Notifications will be
                sent to recipient containing the whole data. This is
                deprecated and removed from version 3.0 of the context broker.
                False - skip the initial notification
        Returns:
            str: Id of the (created) subscription

        """
        existing_subscriptions = self.get_subscription_list()

        sub_dict = subscription.model_dump(include={'subject',
                                                    'notification'})
        for ex_sub in existing_subscriptions:
            if self._subscription_dicts_are_equal(
                    sub_dict,
                    ex_sub.model_dump(include={'subject', 'notification'})
            ):
                self.logger.info("Subscription already exists")
                if update:
                    self.logger.info("Updated subscription")
                    subscription.id = ex_sub.id
                    self.update_subscription(subscription)
                else:
                    warnings.warn(
                        f"Subscription existed already with the id" f" {ex_sub.id}"
                    )
                return ex_sub.id

        params = {}
        if skip_initial_notification:
            version = self.get_version()["orion"]["version"]
            if parse_version(version) <= parse_version("3.1"):
                params.update({"options": "skipInitialNotification"})
            else:
                pass
            warnings.warn(
                f"Skip initial notifications is a deprecated "
                f"feature of older versions <=3.1 of the context "
                f"broker. The Context Broker that you requesting has "
                f"version: {version}. For newer versions we "
                f"automatically skip this option. Consider "
                f"refactoring and updating your services",
                DeprecationWarning,
            )

        url = urljoin(self.base_url, "v2/subscriptions")
        headers = self.headers.copy()
        headers.update({"Content-Type": "application/json"})
        try:
            res = self.post(
                url=url,
                headers=headers,
                data=subscription.model_dump_json(exclude={"id"}, exclude_none=True),
                params=params,
            )
            if res.ok:
                self.logger.info("Subscription successfully created!")
                return res.headers["Location"].split("/")[-1]
            res.raise_for_status()
        except requests.RequestException as err:
            msg = "Could not send subscription!"
            self.log_error(err=err, msg=msg)
            raise

    def get_subscription(self, subscription_id: str) -> Subscription:
        """
        Retrieves a subscription from
        Args:
            subscription_id: id of the subscription

        Returns:

        """
        url = urljoin(self.base_url, f"v2/subscriptions/{subscription_id}")
        headers = self.headers.copy()
        try:
            res = self.get(url=url, headers=headers)
            if res.ok:
                self.logger.debug("Received: %s", res.json())
                return Subscription(**res.json())
            res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not load subscription {subscription_id}"
            self.log_error(err=err, msg=msg)
            raise

    def update_subscription(
        self, subscription: Subscription, skip_initial_notification: bool = False
    ):
        """
        Only the fields included in the request are updated in the subscription.

        Args:
            subscription: Subscription to update
            skip_initial_notification: True - Initial Notifications will be
                sent to recipient containing the whole data. This is
                deprecated and removed from version 3.0 of the context broker.
                False - skip the initial notification

        Returns:
            None
        """
        params = {}
        if skip_initial_notification:
            version = self.get_version()["orion"]["version"]
            if parse_version(version) <= parse_version("3.1"):
                params.update({"options": "skipInitialNotification"})
            else:
                pass
            warnings.warn(
                f"Skip initial notifications is a deprecated "
                f"feature of older versions <3.1 of the context "
                f"broker. The Context Broker that you requesting has "
                f"version: {version}. For newer versions we "
                f"automatically skip this option. Consider "
                f"refactoring and updating your services",
                DeprecationWarning,
            )

        url = urljoin(self.base_url, f"v2/subscriptions/{subscription.id}")
        headers = self.headers.copy()
        headers.update({"Content-Type": "application/json"})
        try:
            res = self.patch(
                url=url,
                headers=headers,
                data=subscription.model_dump_json(
                    exclude={"id"},
                    exclude_none=True
                ),
            )
            if res.ok:
                self.logger.info("Subscription successfully updated!")
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not update subscription {subscription.id}"
            self.log_error(err=err, msg=msg)
            raise

    def delete_subscription(self, subscription_id: str) -> None:
        """
        Deletes a subscription from a Context Broker
        Args:
            subscription_id: id of the subscription
        """
        url = urljoin(self.base_url, f"v2/subscriptions/{subscription_id}")
        headers = self.headers.copy()
        try:
            res = self.delete(url=url, headers=headers)
            if res.ok:
                self.logger.info(
                    f"Subscription '{subscription_id}' " f"successfully deleted!"
                )
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not delete subscription {subscription_id}"
            self.log_error(err=err, msg=msg)
            raise

    # Registration API
    def get_registration_list(self, *, limit: PositiveInt = None) -> List[Registration]:
        """
        Lists all the context provider registrations present in the system.

        Args:
            limit: Limit the number of registrations to be retrieved
        Returns:

        """
        url = urljoin(self.base_url, "v2/registrations/")
        headers = self.headers.copy()
        params = {}

        # We always use the 'count' option to check weather pagination is
        # required
        params.update({"options": "count"})
        try:
            items = self.__pagination(
                limit=limit, url=url, params=params, headers=headers
            )
            adapter = TypeAdapter(List[Registration])
            return adapter.validate_python(items)
        except requests.RequestException as err:
            msg = "Could not load registrations!"
            self.log_error(err=err, msg=msg)
            raise

    def post_registration(self, registration: Registration):
        """
        Creates a new context provider registration. This is typically used
        for binding context sources as providers of certain data. The
        registration is represented by cb.models.Registration

        Args:
            registration (Registration):

        Returns:

        """
        url = urljoin(self.base_url, "v2/registrations")
        headers = self.headers.copy()
        headers.update({"Content-Type": "application/json"})
        try:
            res = self.post(
                url=url,
                headers=headers,
                data=registration.model_dump_json(exclude={"id"}, exclude_none=True),
            )
            if res.ok:
                self.logger.info("Registration successfully created!")
                return res.headers["Location"].split("/")[-1]
            res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not send registration {registration.id}!"
            self.log_error(err=err, msg=msg)
            raise

    def get_registration(self, registration_id: str) -> Registration:
        """
        Retrieves a registration from context broker by id

        Args:
            registration_id: id of the registration

        Returns:
            Registration
        """
        url = urljoin(self.base_url, f"v2/registrations/{registration_id}")
        headers = self.headers.copy()
        try:
            res = self.get(url=url, headers=headers)
            if res.ok:
                self.logger.debug("Received: %s", res.json())
                return Registration(**res.json())
            res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not load registration {registration_id} !"
            self.log_error(err=err, msg=msg)
            raise

    def update_registration(self, registration: Registration):
        """
        Only the fields included in the request are updated in the registration.

        Args:
            registration: Registration to update
        Returns:

        """
        url = urljoin(self.base_url, f"v2/registrations/{registration.id}")
        headers = self.headers.copy()
        headers.update({"Content-Type": "application/json"})
        try:
            res = self.patch(
                url=url,
                headers=headers,
                data=registration.model_dump_json(
                    exclude={"id"},
                    exclude_none=True
                ),
            )
            if res.ok:
                self.logger.info("Registration successfully updated!")
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not update registration {registration.id} !"
            self.log_error(err=err, msg=msg)
            raise

    def delete_registration(self, registration_id: str) -> None:
        """
        Deletes a subscription from a Context Broker
        Args:
            registration_id: id of the subscription
        """
        url = urljoin(self.base_url, f"v2/registrations/{registration_id}")
        headers = self.headers.copy()
        try:
            res = self.delete(url=url, headers=headers)
            if res.ok:
                self.logger.info(
                    "Registration '%s' " "successfully deleted!", registration_id
                )
            res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not delete registration {registration_id} !"
            self.log_error(err=err, msg=msg)
            raise

    # Batch operation API
    def update(self,
               *,
               entities: List[Union[ContextEntity, ContextEntityKeyValues]],
               action_type: Union[ActionType, str],
               update_format: str = None,
               forcedUpdate: bool = False,
               override_metadata: bool = False,
               ) -> None:
        """
        This operation allows to create, update and/or delete several entities
        in a single batch operation.

        This operation is split in as many individual operations as entities
        in the entities vector, so the actionType is executed for each one of
        them. Depending on the actionType, a mapping with regular non-batch
        operations can be done:

        append: maps to POST /v2/entities (if the entity does not already exist)
        or POST /v2/entities/<id>/attrs (if the entity already exists).

        appendStrict: maps to POST /v2/entities (if the entity does not
        already exist) or POST /v2/entities/<id>/attrs?options=append (if the
        entity already exists).

        update: maps to PATCH /v2/entities/<id>/attrs.

        delete: maps to DELETE /v2/entities/<id>/attrs/<attrName> on every
            attribute included in the entity or to DELETE /v2/entities/<id> if
            no attribute were included in the entity.

        replace: maps to PUT /v2/entities/<id>/attrs.

        Args:
            entities: "an array of entities, each entity specified using the "
                      "JSON entity representation format "
            action_type (Update): "actionType, to specify the kind of update
                    action to do: either append, appendStrict, update, delete,
                    or replace. "
            update_format (str): Optional 'keyValues'
            forcedUpdate: Update operation have to trigger any matching
                subscription, no matter if there is an actual attribute
                update or no instead of the default behavior, which is to
                updated only if attribute is effectively updated.
            override_metadata:
                Bool, replace the existing metadata with the one provided in
                the request
        Returns:

        """

        url = urljoin(self.base_url, "v2/op/update")
        headers = self.headers.copy()
        headers.update({"Content-Type": "application/json"})
        params = {}
        options = []
        if override_metadata:
            options.append("overrideMetadata")
        if forcedUpdate:
            options.append("forcedUpdate")
        if update_format:
            assert (
                update_format == "keyValues"
            ), "Only 'keyValues' is allowed as update format"
            options.append("keyValues")
        if options:
            params.update({'options': ",".join(options)})
        update = Update(actionType=action_type, entities=entities)
        try:
            res = self.post(
                url=url,
                headers=headers,
                params=params,
                json=update.model_dump(by_alias=True),
            )
            if res.ok:
                self.logger.info("Update operation '%s' succeeded!", action_type)
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Update operation '{action_type}' failed!"
            self.log_error(err=err, msg=msg)
            raise

    def query(
        self,
        *,
        query: Query,
        limit: PositiveInt = None,
        order_by: str = None,
        response_format: Union[AttrsFormat, str] = AttrsFormat.NORMALIZED,
    ) -> List[Any]:
        """
        Generate api query
        Args:
            query (Query):
            limit (PositiveInt):
            order_by (str):
            response_format (AttrsFormat, str):
        Returns:
            The response payload is an Array containing one object per matching
            entity, or an empty array [] if no entities are found. The entities
            follow the JSON entity representation format (described in the
            section "JSON Entity Representation").
        """
        url = urljoin(self.base_url, "v2/op/query")
        headers = self.headers.copy()
        headers.update({"Content-Type": "application/json"})
        params = {"options": "count"}

        if response_format:
            if response_format not in list(AttrsFormat):
                raise ValueError(f"Value must be in {list(AttrsFormat)}")
            params["options"] = ",".join([response_format, "count"])
        try:
            items = self.__pagination(
                method=PaginationMethod.POST,
                url=url,
                headers=headers,
                params=params,
                data=query.model_dump_json(exclude_none=True),
                limit=limit,
            )
            if response_format == AttrsFormat.NORMALIZED:
                adapter = TypeAdapter(List[ContextEntity])
                return adapter.validate_python(items)
            if response_format == AttrsFormat.KEY_VALUES:
                adapter = TypeAdapter(List[ContextEntityKeyValues])
                return adapter.validate_python(items)
            return items
        except requests.RequestException as err:
            msg = "Query operation failed!"
            self.log_error(err=err, msg=msg)
            raise

    def notify(self, message: Message) -> None:
        """
        This operation is intended to consume a notification payload so that
        all the entity data included by such notification is persisted,
        overwriting if necessary. This operation is useful when one NGSIv2
        endpoint is subscribed to another NGSIv2 endpoint (federation
        scenarios). The request payload must be an NGSIv2 notification
        payload. The behaviour must be exactly the same as 'update'
        with 'action_type' equal to append.

        Args:
            message: Notification message

        Returns:
            None
        """
        url = urljoin(self.base_url, "v2/op/notify")
        headers = self.headers.copy()
        headers.update({"Content-Type": "application/json"})
        params = {}
        try:
            res = self.post(
                url=url,
                headers=headers,
                params=params,
                data=message.model_dump_json(by_alias=True),
            )
            if res.ok:
                self.logger.info("Notification message sent!")
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            msg = (
                f"Sending notifcation message failed! \n "
                f"{message.model_dump_json(indent=2)}"
            )
            self.log_error(err=err, msg=msg)
            raise

    def post_command(
        self,
        *,
        entity_id: str,
        command: Union[Command, NamedCommand, Dict],
        entity_type: str = None,
        command_name: str = None,
    ) -> None:
        """
        Post a command to a context entity this corresponds to 'PATCH' of the
        specified command attribute.

        Args:
            entity_id: Entity identifier
            command: Command
            entity_type: Entity type
            command_name: Name of the command in the entity

        Returns:
            None
        """
        if command_name:
            assert isinstance(command, (Command, dict))
            if isinstance(command, dict):
                command = Command(**command)
            command = {command_name: command.model_dump()}
        else:
            assert isinstance(command, (NamedCommand, dict))
            if isinstance(command, dict):
                command = NamedCommand(**command)

        self.update_existing_entity_attributes(
            entity_id=entity_id, entity_type=entity_type, attrs=[command]
        )

    def does_entity_exist(self, entity_id: str, entity_type: str) -> bool:
        """
        Test if an entity with given id and type is present in the CB

        Args:
            entity_id: Entity id
            entity_type: Entity type

        Returns:
            bool; True if entity exists

        Raises:
            RequestException, if any error occurs (e.g: No Connection),
            except that the entity is not found
        """
        url = urljoin(self.base_url, f"v2/entities/{entity_id}")
        headers = self.headers.copy()
        params = {"type": entity_type}

        try:
            res = self.get(url=url, params=params, headers=headers)
            if res.ok:
                return True
            res.raise_for_status()
        except requests.RequestException as err:
            if err.response is None or not err.response.status_code == 404:
                raise
            return False

    def patch_entity(self,
                     entity: ContextEntity,
                     old_entity: Optional[ContextEntity] = None,
                     override_attr_metadata: bool = True) -> None:
        """
        Takes a given entity and updates the state in the CB to match it.
        It is an extended equivalent to the HTTP method PATCH, which applies
        partial modifications to a resource.

        Args:
            entity: Entity to update
            old_entity: OPTIONAL, if given only the differences between the
                       old_entity and entity are updated in the CB.
                       Other changes made to the entity in CB, can be kept.
                       If type or id was changed, the old_entity will be
                       deleted.
            override_attr_metadata:
                Whether to override or append the attributes metadata.
                `True` for overwrite or `False` for update/append

        Returns:
           None
        """

        new_entity = entity

        if old_entity is None:
            # If no old entity_was provided we use the current state to compare
            # the entity to
            if self.does_entity_exist(
                entity_id=new_entity.id, entity_type=new_entity.type
            ):
                old_entity = self.get_entity(
                    entity_id=new_entity.id, entity_type=new_entity.type
                )
            else:
                # the entity is new, post and finish
                self.post_entity(new_entity, update=False)
                return

        else:
            # An old_entity was provided
            # check if the old_entity (still) exists else recall methode
            # and discard old_entity
            if not self.does_entity_exist(
                entity_id=old_entity.id, entity_type=old_entity.type
            ):
                self.patch_entity(
                    new_entity, override_attr_metadata=override_attr_metadata
                )
                return

            # if type or id was changed, the old_entity needs to be deleted
            # and the new_entity created
            # In this case we will lose the current state of the entity
            if old_entity.id != new_entity.id or old_entity.type != new_entity.type:
                self.delete_entity(entity_id=old_entity.id, entity_type=old_entity.type)

                if not self.does_entity_exist(
                    entity_id=new_entity.id, entity_type=new_entity.type
                ):
                    self.post_entity(entity=new_entity, update=False)
                    return

        # At this point we know that we need to patch only the attributes of
        # the entity
        # Check the differences between the attributes of old and new entity
        # Delete the removed attributes, create the new ones,
        # and update the existing if necessary
        old_attributes = old_entity.get_attributes()
        new_attributes = new_entity.get_attributes()

        # Manage attributes that existed before
        for old_attr in old_attributes:
            # commands do not exist in the ContextEntity and are only
            # registrations to the corresponding device. Operations as
            # delete will fail as it does not technically exist
            corresponding_new_attr = None
            for new_attr in new_attributes:
                if new_attr.name == old_attr.name:
                    corresponding_new_attr = new_attr

            if corresponding_new_attr is None:
                # Attribute no longer exists, delete it
                try:
                    self.delete_entity_attribute(
                        entity_id=new_entity.id,
                        entity_type=new_entity.type,
                        attr_name=old_attr.name,
                    )
                except requests.RequestException as err:
                    # if the attribute is provided by a registration the
                    # deletion will fail
                    if not err.response.status_code == 404:
                        raise
            else:
                # Check if attributed changed in any way, if yes update
                # else do nothing and keep current state
                if old_attr != corresponding_new_attr:
                    try:
                        self.update_entity_attribute(
                            entity_id=new_entity.id,
                            entity_type=new_entity.type,
                            attr=corresponding_new_attr,
                            override_metadata=override_attr_metadata,
                        )
                    except requests.RequestException as err:
                        # if the attribute is provided by a registration the
                        # update will fail
                        if not err.response.status_code == 404:
                            raise

        # Create new attributes
        update_entity = ContextEntity(id=entity.id, type=entity.type)
        update_needed = False
        for new_attr in new_attributes:
            # commands do not exist in the ContextEntity and are only
            # registrations to the corresponding device. Operations as
            # delete will fail as it does not technically exists
            attr_existed = False
            for old_attr in old_attributes:
                if new_attr.name == old_attr.name:
                    attr_existed = True

            if not attr_existed:
                update_needed = True
                update_entity.add_attributes([new_attr])

        if update_needed:
            self.update_entity(update_entity)

    def _subscription_dicts_are_equal(self, first: dict, second: dict):
        """
        Check if two dictionaries and all sub-dictionaries are equal.
        Logs a warning if the keys are not equal, but ignores the
        comparison of such keys.

        Args:
            first dict: Dictionary of first subscription
            second dict: Dictionary of second subscription

        Returns:
            True if equal, else False
        """

        def _value_is_not_none(value):
            """
            Recursive function to check if a value equals none.
            If the value is a dict and any value of the dict is not none,
            the value is not none.
            If the value is a list and any item is not none, the value is not none.
            If it's neither dict nore list, bool is used.
            """
            if isinstance(value, dict):
                return any([_value_is_not_none(value=_v)
                            for _v in value.values()])
            if isinstance(value, list):
                return any([_value_is_not_none(value=_v)for _v in value])
            else:
                return bool(value)
        if first.keys() != second.keys():
            warnings.warn(
                "Subscriptions contain a different set of fields. "
                "Only comparing to new fields of the new one."
            )
        for k, v in first.items():
            ex_value = second.get(k, None)
            if isinstance(v, dict) and isinstance(ex_value, dict):
                equal = self._subscription_dicts_are_equal(v, ex_value)
                if equal:
                    continue
                else:
                    return False
            if v != ex_value:
                self.logger.debug(f"Not equal fields for key {k}: ({v}, {ex_value})")
                if not _value_is_not_none(v) and not _value_is_not_none(ex_value) or k == "timesSent":
                    continue
                return False
        return True


#
#
#    def check_duplicate_subscription(self, subscription_body, limit: int = 20):
#        """
#        Function compares the subject of the subscription body, on whether a subscription
#        already exists for a device / entity.
#        :param subscription_body: the body of the new subscripton
#        :param limit: pagination parameter, to set the number of
#        subscriptions bodies the get request should grab
#        :return: exists, boolean -> True, if such a subscription allready
#        exists
#        """
#        exists = False
#        subscription_subject = json.loads(subscription_body)["subject"]
#        # Exact keys depend on subscription body
#        try:
#            subscription_url = json.loads(subscription_body)[
#            "notification"]["httpCustom"]["url"]
#        except KeyError:
#            subscription_url = json.loads(subscription_body)[
#            "notification"]["http"]["url"]
#
#        # If the number of subscriptions is larger then the limit,
#        paginations methods have to be used
#        url = self.url + '/v2/subscriptions?limit=' + str(limit) +
#        '&options=count'
#        response = self.session.get(url, headers=self.get_header())
#
#        sub_count = float(response.headers["Fiware-Total-Count"])
#        response = json.loads(response.text)
#        if sub_count >= limit:
#            response = self.get_pagination(url=url, headers=self.get_header(),
#                                           limit=limit, count=sub_count)
#            response = json.loads(response)
#
#        for existing_subscription in response:
#            # check whether the exact same subscriptions already exists
#            if existing_subscription["subject"] == subscription_subject:
#                exists = True
#                break
#            try:
#                existing_url = existing_subscription["notification"][
#                "http"]["url"]
#            except KeyError:
#                existing_url = existing_subscription["notification"][
#                "httpCustom"]["url"]
#            # check whether both subscriptions notify to the same path
#            if existing_url != subscription_url:
#                continue
#            else:
#                # iterate over all entities included in the subscription object
#                for entity in subscription_subject["entities"]:
#                    if 'type' in entity.keys():
#                        subscription_type = entity['type']
#                    else:
#                        subscription_type = entity['typePattern']
#                    if 'id' in entity.keys():
#                        subscription_id = entity['id']
#                    else:
#                        subscription_id = entity["idPattern"]
#                    # iterate over all entities included in the exisiting
#                    subscriptions
#                    for existing_entity in existing_subscription["subject"][
#                    "entities"]:
#                        if "type" in entity.keys():
#                            type_existing = entity["type"]
#                        else:
#                            type_existing = entity["typePattern"]
#                        if "id" in entity.keys():
#                            id_existing = entity["id"]
#                        else:
#                            id_existing = entity["idPattern"]
#                        # as the ID field is non optional, it has to match
#                        # check whether the type match
#                        # if the type field is empty, they match all types
#                        if (type_existing == subscription_type) or\
#                                ('*' in subscription_type) or \
#                                ('*' in type_existing)\
#                                or (type_existing == "") or (
#                                subscription_type == ""):
#                            # check if on of the subscriptions is a pattern,
#                            or if they both refer to the same id
#                            # Get the attrs first, to avoid code duplication
#                            # last thing to compare is the attributes
#                            # Assumption -> position is the same as the
#                            entities _list
#                            # i == j
#                            i = subscription_subject["entities"].index(entity)
#                            j = existing_subscription["subject"][
#                            "entities"].index(existing_entity)
#                            try:
#                                subscription_attrs = subscription_subject[
#                                "condition"]["attrs"][i]
#                            except (KeyError, IndexError):
#                                subscription_attrs = []
#                            try:
#                                existing_attrs = existing_subscription[
#                                "subject"]["condition"]["attrs"][j]
#                            except (KeyError, IndexError):
#                                existing_attrs = []
#
#                            if (".*" in subscription_id) or ('.*' in
#                            id_existing) or (subscription_id == id_existing):
#                                # Attributes have to match, or the have to
#                                be an empty array
#                                if (subscription_attrs == existing_attrs) or
#                                (subscription_attrs == []) or (existing_attrs == []):
#                                        exists = True
#                            # if they do not match completely or subscribe
#                            to all ids they have to match up to a certain position
#                            elif ("*" in subscription_id) or ('*' in
#                            id_existing):
#                                    regex_existing = id_existing.find('*')
#                                    regex_subscription =
#                                    subscription_id.find('*')
#                                    # slice the strings to compare
#                                    if (id_existing[:regex_existing] in
#                                    subscription_id) or (subscription_id[:regex_subscription] in id_existing) or \
#                                            (id_existing[regex_existing:] in
#                                            subscription_id) or (subscription_id[regex_subscription:] in id_existing):
#                                            if (subscription_attrs ==
#                                            existing_attrs) or (subscription_attrs == []) or (existing_attrs == []):
#                                                exists = True
#                                            else:
#                                                continue
#                                    else:
#                                        continue
#                            else:
#                                continue
#                        else:
#                            continue
#                    else:
#                        continue
#        return exists
#
