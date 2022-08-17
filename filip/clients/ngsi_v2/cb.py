"""
Context Broker Module for API Client
"""
import re
import warnings
from enum import Enum
from math import inf
from typing import Any, Dict, List, Union, Optional
from urllib.parse import urljoin
import requests
from pydantic import \
    parse_obj_as, \
    PositiveInt, \
    PositiveFloat
from filip.clients.base_http_client import BaseHttpClient
from filip.config import settings
from filip.models.base import FiwareHeader, PaginationMethod
from filip.utils.simple_ql import QueryString
from filip.models.ngsi_v2.context import \
    ActionType, \
    AttrsFormat, \
    Command, \
    ContextEntity, \
    ContextEntityKeyValues, \
    ContextAttribute, \
    NamedCommand, \
    NamedContextAttribute, \
    Subscription, \
    Registration, \
    Query, \
    Update

class NgsiURLVersion(str, Enum):
    """
    URL part that defines the NGSI version for the API.
    """
    v2_url = "/v2"
    ld_url = "/ngsi-ld/v1"

class ContextBrokerClient(BaseHttpClient):
    """
    Implementation of NGSI Context Broker functionalities, such as creating
    entities and subscriptions; retrieving, updating and deleting data.
    Further documentation:
    https://fiware-orion.readthedocs.io/en/master/

    Api specifications for v2 are located here:
    https://telefonicaid.github.io/fiware-orion/api/v2/stable/
    """
    def __init__(self,
                 url: str = None,
                 *,
                 session: requests.Session = None,
                 fiware_header: FiwareHeader = None,
                 **kwargs):
        """

        Args:
            url: Url of context broker server
            session (requests.Session):
            fiware_header (FiwareHeader): fiware service and fiware service path
            **kwargs (Optional): Optional arguments that ``request`` takes.
        """
        # set service url
        url = url or settings.CB_URL
        self._url_version = NgsiURLVersion.v2_url
        super().__init__(url=url,
                         session=session,
                         fiware_header=fiware_header,
                         **kwargs)

    def __pagination(self,
                     *,
                     method: PaginationMethod = PaginationMethod.GET,
                     url: str,
                     headers: Dict,
                     limit: Union[PositiveInt, PositiveFloat] = None,
                     params: Dict = None,
                     data: str = None) -> List[Dict]:
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
            params['limit'] = 1000  # maximum items per request
        else:
            params['limit'] = limit

        if self.session:
            session = self.session
        else:
            session = requests.Session()
        with session:
            res = session.request(method=method,
                                  url=url,
                                  params=params,
                                  headers=headers,
                                  data=data)
            if res.ok:
                items = res.json()
                # do pagination
                count = int(res.headers['Fiware-Total-Count'])

                while len(items) < limit and len(items) < count:
                    # Establishing the offset from where entities are retrieved
                    params['offset'] = len(items)
                    params['limit'] = min(1000, (limit - len(items)))
                    res = session.request(method=method,
                                          url=url,
                                          params=params,
                                          headers=headers,
                                          data=data)
                    if res.ok:
                        items.extend(res.json())
                    else:
                        res.raise_for_status()
                self.logger.debug('Received: %s', items)
                return items
            res.raise_for_status()

    # MANAGEMENT API
    def get_version(self) -> Dict:
        """
        Gets version of IoT Agent
        Returns:
            Dictionary with response
        """
        url = urljoin(self.base_url, '/version')
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
        url = urljoin(self.base_url, self._url_version)
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
        url = urljoin(self.base_url, 'statistics')
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
    def post_entity(self,
                    entity: ContextEntity,
                    update: bool = False):
        """
        Function registers an Object with the NGSI Context Broker,
        if it already exists it can be automatically updated
        if the overwrite bool is True
        First a post request with the entity is tried, if the response code
        is 422 the entity is uncrossable, as it already exists there are two
        options, either overwrite it, if the attribute have changed
        (e.g. at least one new/new values) (update = True) or leave
        it the way it is (update=False)
        Args:
            update (bool): If the response.status_code is 422, whether the old
            entity should be updated or not
            entity (ContextEntity): Context Entity Object
        """
        url = urljoin(self.base_url, f'{self._url_version}/entities')
        headers = self.headers.copy()
        try:
            res = self.post(
                url=url,
                headers=headers,
                json=entity.dict(exclude_unset=True,
                                 exclude_defaults=True,
                                 exclude_none=True))
            if res.ok:
                self.logger.info("Entity successfully posted!")
                return res.headers.get('Location')
            res.raise_for_status()
        except requests.RequestException as err:
            if update and err.response.status_code == 422:
                return self.update_entity(entity=entity)
            msg = f"Could not post entity {entity.id}"
            self.log_error(err=err, msg=msg)
            raise

    def get_entity_list(self,
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
                        limit: int = inf,
                        attrs: List[str] = None,
                        metadata: str = None,
                        order_by: str = None,
                        response_format: Union[AttrsFormat, str] =
                        AttrsFormat.NORMALIZED
                        ) -> List[Union[ContextEntity,
                                        ContextEntityKeyValues,
                                        Dict[str, Any]]]:
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
        url = urljoin(self.base_url, f'{self._url_version}/entities/')
        headers = self.headers.copy()
        params = {}

        if entity_ids and id_pattern:
            raise ValueError
        if entity_types and type_pattern:
            raise ValueError
        if entity_ids:
            if not isinstance(entity_ids, list):
                entity_ids = [entity_ids]
            params.update({'id': ','.join(entity_ids)})
        if id_pattern:
            try:
                re.compile(id_pattern)
            except re.error as err:
                raise ValueError(f'Invalid Pattern: {err}') from err
            params.update({'idPattern': id_pattern})
        if entity_types:
            if not isinstance(entity_types, list):
                entity_types = [entity_types]
            params.update({'type': ','.join(entity_types)})
        if type_pattern:
            try:
                re.compile(type_pattern)
            except re.error as err:
                raise ValueError(f'Invalid Pattern: {err.msg}') from err
            params.update({'typePattern': type_pattern})
        if attrs:
            params.update({'attrs': ','.join(attrs)})
        if metadata:
            params.update({'metadata': ','.join(metadata)})
        if q:
            params.update({'q': str(q)})
        if mq:
            params.update({'mq': str(mq)})
        if geometry:
            params.update({'geometry': geometry})
        if georel:
            params.update({'georel': georel})
        if coords:
            params.update({'coords': coords})
        if order_by:
            params.update({'orderBy': order_by})
        if response_format not in list(AttrsFormat):
            raise ValueError(f'Value must be in {list(AttrsFormat)}')
        response_format = ','.join(['count', response_format])
        params.update({'options': response_format})
        try:
            items = self.__pagination(method=PaginationMethod.GET,
                                      limit=limit,
                                      url=url,
                                      params=params,
                                      headers=headers)
            if AttrsFormat.NORMALIZED in response_format:
                return parse_obj_as(List[ContextEntity], items)
            if AttrsFormat.KEY_VALUES in response_format:
                return parse_obj_as(List[ContextEntityKeyValues], items)
            return items

        except requests.RequestException as err:
            msg = "Could not load entities"
            self.log_error(err=err, msg=msg)
            raise

    def get_entity(self,
                   entity_id: str,
                   entity_type: str = None,
                   attrs: List[str] = None,
                   metadata: List[str] = None,
                   response_format: Union[AttrsFormat, str] =
                   AttrsFormat.NORMALIZED) \
            -> Union[ContextEntity, ContextEntityKeyValues, Dict[str, Any]]:
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
        url = urljoin(self.base_url, f'{self._url_version}/entities/{entity_id}')
        headers = self.headers.copy()
        params = {}
        if entity_type:
            params.update({'type': entity_type})
        if attrs:
            params.update({'attrs': ','.join(attrs)})
        if metadata:
            params.update({'metadata': ','.join(metadata)})
        if response_format not in list(AttrsFormat):
            raise ValueError(f'Value must be in {list(AttrsFormat)}')
        params.update({'options': response_format})

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

    def get_entity_attributes(self,
                              entity_id: str,
                              entity_type: str = None,
                              attrs: List[str] = None,
                              metadata: List[str] = None,
                              response_format: Union[AttrsFormat, str] =
                              AttrsFormat.NORMALIZED) -> \
            Dict[str, ContextAttribute]:
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
        url = urljoin(self.base_url, f'{self._url_version}/entities/{entity_id}/attrs')
        headers = self.headers.copy()
        params = {}
        if entity_type:
            params.update({'type': entity_type})
        if attrs:
            params.update({'attrs': ','.join(attrs)})
        if metadata:
            params.update({'metadata': ','.join(metadata)})
        if response_format not in list(AttrsFormat):
            raise ValueError(f'Value must be in {list(AttrsFormat)}')
        params.update({'options': response_format})
        try:
            res = self.get(url=url, params=params, headers=headers)
            if res.ok:
                if response_format == AttrsFormat.NORMALIZED:
                    return {key: ContextAttribute(**values)
                            for key, values in res.json().items()}
                return res.json()
            res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not load attributes from entity {entity_id} !"
            self.log_error(err=err, msg=msg)
            raise

    def update_entity(self,
                      entity: ContextEntity,
                      options: str = None,
                      append=False):
        """
        The request payload is an object representing the attributes to
        append or update.
        Args:
            entity (ContextEntity):
            append (bool):
            options:
        Returns:

        """
        url = urljoin(self.base_url, f'{self._url_version}/entities/{entity.id}/attrs')
        headers = self.headers.copy()
        params = {}
        if options:
            params.update({'options': options})
        try:
            res = self.post(url=url,
                            headers=headers,
                            json=entity.dict(exclude={'id', 'type'},
                                             exclude_unset=True,
                                             exclude_none=True))
            if res.ok:
                self.logger.info("Entity '%s' successfully updated!", entity.id)
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not update entity {entity.id} !"
            self.log_error(err=err, msg=msg)
            raise

    def delete_entity(self, entity_id: str, entity_type: str = None) -> None:

        """
        Remove a entity from the context broker. No payload is required
        or received.

        Args:
            entity_id: Id of the entity to be deleted
            entity_type: several entities with the same entity id.
        Returns:
            None
        """
        url = urljoin(self.base_url, f'{self._url_version}/entities/{entity_id}')
        headers = self.headers.copy()
        if entity_type:
            params = {'type': entity_type}
        else:
            params = {}
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

    def replace_entity_attributes(self,
                                  entity: ContextEntity,
                                  options: str = None,
                                  append: bool = True):
        """
        The attributes previously existing in the entity are removed and
        replaced by the ones in the request.

        Args:
            entity (ContextEntity):
            append (bool):
            options:
        Returns:

        """
        url = urljoin(self.base_url, f'{self._url_version}/entities/{entity.id}/attrs')
        headers = self.headers.copy()
        params = {}
        if options:
            params.update({'options': options})
        try:
            res = self.put(url=url,
                           headers=headers,
                           json=entity.dict(exclude={'id', 'type'},
                                            exclude_unset=True,
                                            exclude_none=True))
            if res.ok:
                self.logger.info("Entity '%s' successfully "
                                 "updated!", entity.id)
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not replace attribute of entity {entity.id} !"
            self.log_error(err=err, msg=msg)
            raise

    # Attribute operations
    def get_attribute(self,
                      entity_id: str,
                      attr_name: str,
                      entity_type: str = None,
                      metadata: str = None,
                      response_format = '') -> ContextAttribute:
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
        url = urljoin(self.base_url,
                      f'{self._url_version}/entities/{entity_id}/attrs/{attr_name}')
        headers = self.headers.copy()
        params = {}
        if entity_type:
            params.update({'type': entity_type})
        if metadata:
            params.update({'metadata': ','.join(metadata)})
        try:
            res = self.get(url=url, params=params, headers=headers)
            if res.ok:
                self.logger.debug('Received: %s', res.json())
                return ContextAttribute(**res.json())
            res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not load attribute '{attr_name}' from entity" \
                  f"'{entity_id}' "
            self.log_error(err=err, msg=msg)
            raise

    def update_entity_attribute(self,
                                entity_id: str,
                                attr: Union[ContextAttribute,
                                            NamedContextAttribute],
                                *,
                                entity_type: str = None,
                                attr_name: str = None):
        """
        Updates a specified attribute from an entity.
        Args:
            attr: context attribute to update
            entity_id: Id of the entity. Example: Bcn_Welt
            entity_type: Entity type, to avoid ambiguity in case there are
            several entities with the same entity id.
        """
        headers = self.headers.copy()
        if not isinstance(attr, NamedContextAttribute):
            assert attr_name is not None, "Missing name for attribute. " \
                                          "attr_name must be present if" \
                                          "attr is of type ContextAttribute"
        else:
            assert attr_name is None, "Invalid argument attr_name. Do not set " \
                                      "attr_name if attr is of type " \
                                      "NamedContextAttribute"
            attr_name = attr.name

        url = urljoin(self.base_url,
                      f'{self._url_version}/entities/{entity_id}/attrs/{attr_name}')
        params = {}
        if entity_type:
            params.update({'type': entity_type})
        try:
            res = self.put(url=url,
                           headers=headers,
                           json=attr.dict(exclude={'name'},
                                          exclude_unset=True,
                                          exclude_none=True))
            if res.ok:
                self.logger.info("Attribute '%s' of '%s' "
                                 "successfully updated!", attr_name, entity_id)
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not update attribute '{attr_name}' of entity" \
                  f"'{entity_id}' "
            self.log_error(err=err, msg=msg)
            raise

    def delete_entity_attribute(self,
                                entity_id: str,
                                attr_name: str,
                                entity_type: str = None) -> None:
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
        url = urljoin(self.base_url,
                      f'{self._url_version}/entities/{entity_id}/attrs/{attr_name}')
        headers = self.headers.copy()
        params = {}
        if entity_type:
            params.update({'type': entity_type})
        try:
            res = self.delete(url=url, headers=headers)
            if res.ok:
                self.logger.info("Attribute '%s' of '%s' "
                                 "successfully deleted!", attr_name, entity_id)
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not delete attribute '{attr_name}' of entity" \
                  f"'{entity_id}' "
            self.log_error(err=err, msg=msg)
            raise

    # Attribute value operations
    def get_attribute_value(self,
                            entity_id: str,
                            attr_name: str,
                            entity_type: str = None) -> Any:
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
        url = urljoin(self.base_url,
                      f'{self._url_version}/entities/{entity_id}/attrs/{attr_name}/value')
        headers = self.headers.copy()
        params = {}
        if entity_type:
            params.update({'type': entity_type})
        try:
            res = self.get(url=url, params=params, headers=headers)
            if res.ok:
                self.logger.debug('Received: %s', res.json())
                return res.json()
            res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not load value of attribute '{attr_name}' from " \
                  f"entity'{entity_id}' "
            self.log_error(err=err, msg=msg)
            raise

    def update_attribute_value(self, *,
                               entity_id: str,
                               attr_name: str,
                               value: Any,
                               entity_type: str = None):
        """
        Updates the value of a specified attribute of an entity

        Args:
            value: update value
            entity_id: Id of the entity. Example: Bcn_Welt
            attr_name: Name of the attribute to be retrieved.
                Example: temperature.
            entity_type: Entity type, to avoid ambiguity in case there are
                several entities with the same entity id.
        Returns:

        """
        url = urljoin(self.base_url,
                      f'{self._url_version}/entities/{entity_id}/attrs/{attr_name}/value')
        headers = self.headers.copy()
        params = {}
        if entity_type:
            params.update({'type': entity_type})
        try:
            if not isinstance(value, (dict, list)):
                headers.update({'Content-Type': 'text/plain'})
                if isinstance(value, str):
                    value = f'"{value}"'
                res = self.put(url=url,
                               headers=headers,
                               json=value)
            else:
                res = self.put(url=url,
                               headers=headers,
                               json=value)
            if res.ok:
                self.logger.info("Attribute '%s' of '%s' "
                                 "successfully updated!", attr_name, entity_id)
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not update value of attribute '{attr_name}' from " \
                  f"entity '{entity_id}' "
            self.log_error(err=err, msg=msg)
            raise

    # Types Operations
    def get_entity_types(self,
                         *,
                         limit: int = None,
                         offset: int = None,
                         options: str = None) -> List[Dict[str, Any]]:
        """

        Args:
            limit: Limit the number of types to be retrieved.
            offset: Skip a number of records.
            options: Options dictionary. Allowed: count, values

        Returns:

        """
        url = urljoin(self.base_url, f'{self._url_version}/types')
        headers = self.headers.copy()
        params = {}
        if limit:
            params.update({'limit': limit})
        if offset:
            params.update({'offset': offset})
        if options:
            params.update({'options': options})
        try:
            res = self.get(url=url, params=params, headers=headers)
            if res.ok:
                self.logger.debug('Received: %s', res.json())
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
        url = urljoin(self.base_url, f'{self._url_version}/types/{entity_type}')
        headers = self.headers.copy()
        params = {}
        try:
            res = self.get(url=url, params=params, headers=headers)
            if res.ok:
                self.logger.debug('Received: %s', res.json())
                return res.json()
            res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not load entities of type" \
                  f"'{entity_type}' "
            self.log_error(err=err, msg=msg)
            raise

    # SUBSCRIPTION API ENDPOINTS
    def get_subscription_list(self,
                              limit: PositiveInt = inf) -> List[Subscription]:
        """
        Returns a list of all the subscriptions present in the system.
        Args:
            limit: Limit the number of subscriptions to be retrieved
        Returns:
            list of subscriptions
        """
        url = urljoin(self.base_url, f'{self._url_version}/subscriptions/')
        headers = self.headers.copy()
        params = {}

        # We always use the 'count' option to check weather pagination is
        # required
        params.update({'options': 'count'})
        try:
            items = self.__pagination(limit=limit,
                                      url=url,
                                      params=params,
                                      headers=headers)
            return parse_obj_as(List[Subscription], items)
        except requests.RequestException as err:
            msg = "Could not load subscriptions!"
            self.log_error(err=err, msg=msg)
            raise

    def post_subscription(self, subscription: Subscription,
                          update: bool = False) -> str:
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
        Returns:
            str: Id of the (created) subscription

        """
        existing_subscriptions = self.get_subscription_list()

        sub_hash = subscription.json(include={'subject', 'notification'})
        for ex_sub in existing_subscriptions:
            if sub_hash == ex_sub.json(include={'subject', 'notification'}):
                self.logger.info("Subscription already exists")
                if update:
                    self.logger.info("Updated subscription")
                    subscription.id = ex_sub.id
                    self.update_subscription(subscription)
                else:
                    warnings.warn(f"Subscription existed already with the id"
                                  f" {ex_sub.id}")
                return ex_sub.id

        url = urljoin(self.base_url, 'v2/subscriptions')
        headers = self.headers.copy()
        headers.update({'Content-Type': 'application/json'})
        try:
            res = self.post(
                url=url,
                headers=headers,
                data=subscription.json(exclude={'id'},
                                       exclude_unset=True,
                                       exclude_defaults=True,
                                       exclude_none=True))
            if res.ok:
                self.logger.info("Subscription successfully created!")
                return res.headers['Location'].split('/')[-1]
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
        url = urljoin(self.base_url, f'{self._url_version}/subscriptions/{subscription_id}')
        headers = self.headers.copy()
        try:
            res = self.get(url=url, headers=headers)
            if res.ok:
                self.logger.debug('Received: %s', res.json())
                return Subscription(**res.json())
            res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not load subscription {subscription_id}"
            self.log_error(err=err, msg=msg)
            raise

    def update_subscription(self, subscription: Subscription):
        """
        Only the fields included in the request are updated in the subscription.
        Args:
            subscription: Subscription to update
        Returns:

        """
        url = urljoin(self.base_url, f'{self._url_version}/subscriptions/{subscription.id}')
        headers = self.headers.copy()
        headers.update({'Content-Type': 'application/json'})
        try:
            res = self.patch(
                url=url,
                headers=headers,
                data=subscription.json(exclude={'id'},
                                       exclude_unset=True,
                                       exclude_defaults=True,
                                       exclude_none=True))
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
        url = urljoin(self.base_url,
                      f'{self._url_version}/subscriptions/{subscription_id}')
        headers = self.headers.copy()
        try:
            res = self.delete(url=url, headers=headers)
            if res.ok:
                self.logger.info(f"Subscription '{subscription_id}' "
                                 f"successfully deleted!")
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not delete subscription {subscription_id}"
            self.log_error(err=err, msg=msg)
            raise

    # Registration API
    def get_registration_list(self,
                              *,
                              limit: PositiveInt = None) -> List[Registration]:
        """
        Lists all the context provider registrations present in the system.

        Args:
            limit: Limit the number of registrations to be retrieved
        Returns:

        """
        url = urljoin(self.base_url, f'{self._url_version}/registrations/')
        headers = self.headers.copy()
        params = {}

        # We always use the 'count' option to check weather pagination is
        # required
        params.update({'options': 'count'})
        try:
            items = self.__pagination(limit=limit,
                                      url=url,
                                      params=params,
                                      headers=headers)

            return parse_obj_as(List[Registration], items)
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
        url = urljoin(self.base_url, f'{self._url_version}/registrations')
        headers = self.headers.copy()
        headers.update({'Content-Type': 'application/json'})
        try:
            res = self.post(
                url=url,
                headers=headers,
                data=registration.json(exclude={'id'},
                                       exclude_unset=True,
                                       exclude_defaults=True,
                                       exclude_none=True))
            if res.ok:
                self.logger.info("Registration successfully created!")
                return res.headers['Location'].split('/')[-1]
            res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not send registration {registration.id} !"
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
        url = urljoin(self.base_url, f'{self._url_version}/registrations/{registration_id}')
        headers = self.headers.copy()
        try:
            res = self.get(url=url, headers=headers)
            if res.ok:
                self.logger.debug('Received: %s', res.json())
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
        url = urljoin(self.base_url, f'{self._url_version}/registrations/{registration.id}')
        headers = self.headers.copy()
        headers.update({'Content-Type': 'application/json'})
        try:
            res = self.patch(
                url=url,
                headers=headers,
                data=registration.json(exclude={'id'},
                                       exclude_unset=True,
                                       exclude_defaults=True,
                                       exclude_none=True))
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
        url = urljoin(self.base_url,
                      f'{self._url_version}/registrations/{registration_id}')
        headers = self.headers.copy()
        try:
            res = self.delete(url=url, headers=headers)
            if res.ok:
                self.logger.info("Registration '%s' "
                                 "successfully deleted!", registration_id)
            res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not delete registration {registration_id} !"
            self.log_error(err=err, msg=msg)
            raise

    # Batch operation API
    def update(self,
               *,
               entities: List[ContextEntity],
               action_type: Union[ActionType, str],
               update_format: str = None) -> None:
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

        Returns:

        """

        url = urljoin(self.base_url, f'{self._url_version}/op/update')
        headers = self.headers.copy()
        headers.update({'Content-Type': 'application/json'})
        params = {}
        if update_format:
            assert update_format == 'keyValues', \
                "Only 'keyValues' is allowed as update format"
            params.update({'options': 'keyValues'})
        update = Update(actionType=action_type, entities=entities)
        try:
            res = self.post(
                url=url,
                headers=headers,
                params=params,
                data=update.json(by_alias=True))
            if res.ok:
                self.logger.info("Update operation '%s' succeeded!",
                                 action_type)
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Update operation '{action_type}' failed!"
            self.log_error(err=err, msg=msg)
            raise

    def query(self,
              *,
              query: Query,
              limit: PositiveInt = None,
              order_by: str = None,
              response_format: Union[AttrsFormat, str] =
              AttrsFormat.NORMALIZED) -> List[Any]:
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
        url = urljoin(self.base_url, f'{self._url_version}/op/query')
        headers = self.headers.copy()
        headers.update({'Content-Type': 'application/json'})
        params = {'options': 'count'}

        if response_format:
            if response_format not in list(AttrsFormat):
                raise ValueError(f'Value must be in {list(AttrsFormat)}')
            params['options'] = ','.join([response_format, 'count'])
        try:
            items = self.__pagination(method=PaginationMethod.POST,
                                      url=url,
                                      headers=headers,
                                      params=params,
                                      data=query.json(exclude_unset=True,
                                                      exclude_none=True),
                                      limit=limit)
            if response_format == AttrsFormat.NORMALIZED:
                return parse_obj_as(List[ContextEntity], items)
            if response_format == AttrsFormat.KEY_VALUES:
                return parse_obj_as(List[ContextEntityKeyValues], items)
            return items
        except requests.RequestException as err:
            msg = "Query operation failed!"
            self.log_error(err=err, msg=msg)
            raise

    def post_command(self,
                     *,
                     entity_id: str,
                     entity_type: str,
                     command: Union[Command, NamedCommand, Dict],
                     command_name: str = None) -> None:
        """
        Post a command to a context entity
        Args:
            entity_id: Entity identifier
            command: Command
            entity_type: Entity type
            command_name: Name of the command in the entity
        Returns:
            None
        """
        url = urljoin(self.base_url, f'{self._url_version}/entities/{entity_id}/attrs')
        headers = self.headers.copy()
        params = {"type": entity_type}
        if command_name:
            assert isinstance(command, (Command, dict))
            if isinstance(command, dict):
                command = Command(**command)
            command = {command_name: command.dict()}
        else:
            assert isinstance(command, (NamedCommand, dict))
            if isinstance(command, dict):
                command = NamedCommand(**command)
            command = {command.name: command.dict(exclude={'name'})}
        try:
            res = self.patch(url=url,
                             headers=headers,
                             params=params,
                             json=command)
            if res.ok:
                return
            res.raise_for_status()
        except requests.RequestException as err:
            msg = "Query operation failed!"
            self.log_error(err=err, msg=msg)
            raise

#    def get_subjects(self, object_entity_name: str, object_entity_type: str, subject_type=None):
#        """
#        Function gets the JSON for child / subject entities for a parent /
#        object entity.
#        :param object_entity_name: The parent / object entity name
#        :param object_entity_type: The type of the parent / object entity
#        :param subject_type: optional parameter, if added only those child /
#        subject entities are returned that match the type
#        :return: JSON containing the child / subject information
#        """
#        url = self.url + '/v2/entities/?q=ref' + object_entity_type + '==' + object_entity_name + '&options=count'
#        if subject_type is not None:
#            url = url + '&attrs=type&type=' + subject_type
#        headers = self.get_header()
#        response = self.session.get(url=url, headers=headers, )
#        ok, retstr = requtils.response_ok(response)
#        if not ok:
#            level, retstr = requtils.logging_switch(response)
#            self.log_switch(level, retstr)
#        else:
#            return response.text
#
#    def get_objects(self, subject_entity_name: str, subject_entity_type:
#    str, object_type=None):
#        """
#        Function returns a List of all objects associated to a subject. If
#        object type is not None,
#        only those are returned, that match the object type.
#        :param subject_entity_name: The child / subject entity name
#        :param subject_entity_type: The type of the child / subject entity
#        :param object_type:
#        :return: List containing all associated objects
#        """
#        url = self.url + '/v2/entities/' + subject_entity_name + '/?type=' + subject_entity_type + '&options=keyValues'
#        if object_type is not None:
#            url = url + '&attrs=ref' + object_type
#        headers = self.get_header()
#        response = self.session.get(url=url, headers=headers)
#        ok, retstr = requtils.response_ok(response)
#        if not ok:
#            level, retstr = requtils.logging_switch(response)
#            self.log_switch(level, retstr)
#        else:
#            return response.text
#
#    def get_associated(self, name: str, entity_type: str,
#    associated_type=None):
#        """
#        Function returns all associated data for a given entity name and type
#        :param name: name of the entity
#        :param entity_type: type of the entity
#        :param associated_type: if only associated data of one type should
#        be returned, this parameter has to be the type
#        :return: A dictionary, containing the data of the entity,
#        a key "subjects" and "objects" that contain each a list
#                with the reflective data
#        """
#        data_dict = {}
#        associated_objects = self.get_objects(subject_entity_name=name,
#        subject_entity_type=entity_type,
#                                              object_type=associated_type)
#        associated_subjects = self.get_subjects(object_entity_name=name,
#        object_entity_type=entity_type,
#                                                subject_type=associated_type)
#        if associated_subjects is not None:
#            data_dict["subjects"] = json.loads(associated_subjects)
#        if associated_objects is not None:
#            object_json = json.loads(associated_objects)
#            data_dict["objects"] = []
#            if isinstance(object_json, list):
#                for associated_object in object_json:
#                    entity_name = associated_object["id"]
#                    object_data = json.loads(self.get_entity(
#                    entity_name=entity_name))
#                    data_dict["objects"].append(object_data)
#            else:
#                entity_name = object_json["id"]
#                object_data = json.loads(self.get_entity(
#                entity_name=entity_name))
#                data_dict["objects"].append(object_data)
#
#        entity_dict = json.loads(self.get_entity(entity_name=name))
#
#        whole_dict = {**entity_dict, **data_dict}
#
#        return whole_dict
#

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
#                            entities list
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

# def post_cmd_v1(self, entity_id: str, entity_type: str, cmd_name: str,
# cmd_value: str): url = self.url + '/v1/updateContext' payload = {
# "updateAction": "UPDATE", "contextElements": [ {"id": entity_id, "type":
# entity_type, "isPattern": "false", "attributes": [ {"name": cmd_name,
# "type": "command", "value": cmd_value }] }] } headers = self.get_header(
# requtils.HEADER_CONTENT_JSON) data = json.dumps(payload) response =
# self.session.post(url, headers=headers, data=data) ok, retstr =
# requtils.response_ok(response) if not ok: level, retstr =
# requtils.logging_switch(response) self.log_switch(level, retstr)
