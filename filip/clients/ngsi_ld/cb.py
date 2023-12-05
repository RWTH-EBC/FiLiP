"""
Context Broker Module for API Client
"""
import json
import re
import warnings
from math import inf
from typing import Any, Dict, List, Union, Optional
from urllib.parse import urljoin
import requests
from pydantic import \
    parse_obj_as, \
    PositiveInt, \
    PositiveFloat
from filip.clients.ngsi_v2.cb import ContextBrokerClient, NgsiURLVersion
from filip.config import settings
from filip.models.base import FiwareLDHeader, PaginationMethod
from filip.models.ngsi_ld.context import ActionTypeLD, UpdateLD, ContextLDEntity, ContextLDEntityKeyValues, ContextProperty, \
    ContextRelationship, NamedContextProperty, NamedContextRelationship
from filip.utils.simple_ql import QueryString
from filip.models.ngsi_v2.context import \
    AttrsFormat, \
    Command, \
    NamedCommand, \
    Query


class ContextBrokerLDClient(ContextBrokerClient):
    """
    Implementation of NGSI-LD Context Broker functionalities, such as creating
    entities and subscriptions; retrieving, updating and deleting data.
    Further documentation:
    https://fiware-orion.readthedocs.io/en/master/

    Api specifications for LD are located here:
    https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.04.01_60/gs_cim009v010401p.pdf
    """

    def __init__(self,
                 url: str = None,
                 *,
                 session: requests.Session = None,
                 fiware_header: FiwareLDHeader = None,
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
        super().__init__(url=url,
                         session=session,
                         fiware_header=fiware_header,
                         **kwargs)
        # set the version specific url-pattern
        self._url_version = NgsiURLVersion.ld_url




    # CONTEXT MANAGEMENT API ENDPOINTS
    # Entity Operations
    def post_entity(self,
                    entity: ContextLDEntity,
                    update: bool = False):
        """
        Function registers an Object with the NGSI-LD Context Broker,
        if it already exists it can be automatically updated
        if the overwrite bool is True
        First a post request with the entity is tried, if the response code
        is 422 the entity is uncrossable, as it already exists there are two
        options, either overwrite it, if the attribute have changed
        (e.g. at least one new/new values) (update = True) or leave
        it the way it is (update=False)

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
                        order_by: str = None,
                        response_format: Union[AttrsFormat, str] =
                        AttrsFormat.NORMALIZED,
                        **kwargs
                        ) -> List[Union[ContextLDEntity,
                                        ContextLDEntityKeyValues,
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
            type_pattern: is not supported in NGSI-LD
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
            warnings.warn(f"type pattern are not supported by NGSI-LD and will be ignored in this request")
        if attrs:
            params.update({'attrs': ','.join(attrs)})
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
        #This interface is only realized via additional specifications.
        #If no parameters are passed, the idPattern is set to "urn:*".
        if not params:
            default_idPattern = "urn:*"
            params.update({'idPattern': default_idPattern})
            warnings.warn(f"querying entities without additional parameters is not supported on ngsi-ld. the query is "
                          f"performed with the idPattern {default_idPattern}")
        response_format = ','.join(['count', response_format])
        params.update({'options': response_format})
        try:
            items = self._ContextBrokerClient__pagination(method=PaginationMethod.GET,
                                      limit=limit,
                                      url=url,
                                      params=params,
                                      headers=headers)
            if AttrsFormat.NORMALIZED in response_format:
                return parse_obj_as(List[ContextLDEntity], items)
            if AttrsFormat.KEY_VALUES in response_format:
                return parse_obj_as(List[ContextLDEntityKeyValues], items)
            return items

        except requests.RequestException as err:
            msg = "Could not load entities"
            self.log_error(err=err, msg=msg)
            raise

    def get_entity(self,
                   entity_id: str,
                   entity_type: str = None,
                   attrs: List[str] = None,
                   response_format: Union[AttrsFormat, str] =
                   AttrsFormat.NORMALIZED,
                   **kwargs  # TODO how to handle metadata?
                   ) \
            -> Union[ContextLDEntity, ContextLDEntityKeyValues, Dict[str, Any]]:
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

        if response_format not in list(AttrsFormat):
            raise ValueError(f'Value must be in {list(AttrsFormat)}')
        params.update({'options': response_format})

        try:
            res = self.get(url=url, params=params, headers=headers)
            if res.ok:
                self.logger.info("Entity successfully retrieved!")
                self.logger.debug("Received: %s", res.json())
                if response_format == AttrsFormat.NORMALIZED:
                    return ContextLDEntity(**res.json())
                if response_format == AttrsFormat.KEY_VALUES:
                    return ContextLDEntityKeyValues(**res.json())
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
                              response_format: Union[AttrsFormat, str] =
                              AttrsFormat.NORMALIZED,
                              **kwargs
                              ) -> \
            Dict[str, Union[ContextProperty, ContextRelationship]]:
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
            response_format (AttrsFormat, str): Representation format of
                response
        Returns:
            Dict
        """
        url = urljoin(self.base_url, f'/v2/entities/{entity_id}/attrs') # TODO --> nicht nutzbar
        headers = self.headers.copy()
        params = {}
        if entity_type:
            params.update({'type': entity_type})
        if attrs:
            params.update({'attrs': ','.join(attrs)})
        if response_format not in list(AttrsFormat):
            raise ValueError(f'Value must be in {list(AttrsFormat)}')
        params.update({'options': response_format})
        try:
            res = self.get(url=url, params=params, headers=headers)
            if res.ok:
                if response_format == AttrsFormat.NORMALIZED:
                    attr = {}
                    for key, values in res.json().items():
                        if "value" in values:
                            attr[key] = ContextProperty(**values)
                        else:
                            attr[key] = ContextRelationship(**values)
                    return attr
                return res.json()
            res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not load attributes from entity {entity_id} !"
            self.log_error(err=err, msg=msg)
            raise

    def update_entity(self,
                      entity: ContextLDEntity,
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

    def replace_entity_attributes(self,
                                  entity: ContextLDEntity,
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
                      response_format='',
                      **kwargs
                      ) -> Union[ContextProperty, ContextRelationship]:
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
        try:
            res = self.get(url=url, params=params, headers=headers)
            if res.ok:
                self.logger.debug('Received: %s', res.json())
                if "property" in res.json():
                    return ContextProperty(**res.json())
                else:
                    return ContextRelationship(**res.json())
            res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not load attribute '{attr_name}' from entity" \
                  f"'{entity_id}' "
            self.log_error(err=err, msg=msg)
            raise

    def update_entity_attribute(self,
                                entity_id: str,
                                attr: Union[ContextProperty, ContextRelationship,
                                            NamedContextProperty, NamedContextRelationship],
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
        if not isinstance(attr, NamedContextProperty) or not isinstance(attr, NamedContextRelationship):
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

    def get_all_attributes(self) -> List:
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
                      f'{self._url_version}/attributes')
        headers = self.headers.copy()
        params = {}
        try:
            res = self.get(url=url, params=params, headers=headers)
            if res.ok:
                self.logger.debug('Received: %s', res.json())
                if "attributeList" in res.json():
                    return res.json()["attributeList"]
            res.raise_for_status()

        except requests.RequestException as err:
            msg = f"Could not asks for Attributes"
            self.log_error(err=err, msg=msg)
            raise


    #
    # # SUBSCRIPTION API ENDPOINTS
    # def get_subscription_list(self,
    #                           limit: PositiveInt = inf) -> List[Subscription]:
    #     """
    #     Returns a list of all the subscriptions present in the system.
    #     Args:
    #         limit: Limit the number of subscriptions to be retrieved
    #     Returns:
    #         list of subscriptions
    #     """
    #     url = urljoin(self.base_url, f'{self._url_version}/subscriptions/')
    #     headers = self.headers.copy()
    #     params = {}
    #
    #     # We always use the 'count' option to check weather pagination is
    #     # required
    #     params.update({'options': 'count'})
    #     try:
    #         items = self.__pagination(limit=limit,
    #                                   url=url,
    #                                   params=params,
    #                                   headers=headers)
    #         return parse_obj_as(List[Subscription], items)
    #     except requests.RequestException as err:
    #         msg = "Could not load subscriptions!"
    #         self.log_error(err=err, msg=msg)
    #         raise
    #
    # def post_subscription(self, subscription: Subscription,
    #                       update: bool = False) -> str:
    #     """
    #     Creates a new subscription. The subscription is represented by a
    #     Subscription object defined in filip.cb.models.
    #
    #     If the subscription already exists, the adding is prevented and the id
    #     of the existing subscription is returned.
    #
    #     A subscription is deemed as already existing if there exists a
    #     subscription with the exact same subject and notification fields. All
    #     optional fields are not considered.
    #
    #     Args:
    #         subscription: Subscription
    #         update: True - If the subscription already exists, update it
    #                 False- If the subscription already exists, throw warning
    #     Returns:
    #         str: Id of the (created) subscription
    #
    #     """
    #     existing_subscriptions = self.get_subscription_list()
    #
    #     sub_hash = subscription.json(include={'subject', 'notification'})
    #     for ex_sub in existing_subscriptions:
    #         if sub_hash == ex_sub.json(include={'subject', 'notification'}):
    #             self.logger.info("Subscription already exists")
    #             if update:
    #                 self.logger.info("Updated subscription")
    #                 subscription.id = ex_sub.id
    #                 self.update_subscription(subscription)
    #             else:
    #                 warnings.warn(f"Subscription existed already with the id"
    #                               f" {ex_sub.id}")
    #             return ex_sub.id
    #
    #     url = urljoin(self.base_url, 'v2/subscriptions')
    #     headers = self.headers.copy()
    #     headers.update({'Content-Type': 'application/json'})
    #     try:
    #         res = self.post(
    #             url=url,
    #             headers=headers,
    #             data=subscription.json(exclude={'id'},
    #                                    exclude_unset=True,
    #                                    exclude_defaults=True,
    #                                    exclude_none=True))
    #         if res.ok:
    #             self.logger.info("Subscription successfully created!")
    #             return res.headers['Location'].split('/')[-1]
    #         res.raise_for_status()
    #     except requests.RequestException as err:
    #         msg = "Could not send subscription!"
    #         self.log_error(err=err, msg=msg)
    #         raise
    #
    # def get_subscription(self, subscription_id: str) -> Subscription:
    #     """
    #     Retrieves a subscription from
    #     Args:
    #         subscription_id: id of the subscription
    #
    #     Returns:
    #
    #     """
    #     url = urljoin(self.base_url, f'{self._url_version}/subscriptions/{subscription_id}')
    #     headers = self.headers.copy()
    #     try:
    #         res = self.get(url=url, headers=headers)
    #         if res.ok:
    #             self.logger.debug('Received: %s', res.json())
    #             return Subscription(**res.json())
    #         res.raise_for_status()
    #     except requests.RequestException as err:
    #         msg = f"Could not load subscription {subscription_id}"
    #         self.log_error(err=err, msg=msg)
    #         raise
    #
    # def update_subscription(self, subscription: Subscription):
    #     """
    #     Only the fields included in the request are updated in the subscription.
    #     Args:
    #         subscription: Subscription to update
    #     Returns:
    #
    #     """
    #     url = urljoin(self.base_url, f'{self._url_version}/subscriptions/{subscription.id}')
    #     headers = self.headers.copy()
    #     headers.update({'Content-Type': 'application/json'})
    #     try:
    #         res = self.patch(
    #             url=url,
    #             headers=headers,
    #             data=subscription.json(exclude={'id'},
    #                                    exclude_unset=True,
    #                                    exclude_defaults=True,
    #                                    exclude_none=True))
    #         if res.ok:
    #             self.logger.info("Subscription successfully updated!")
    #         else:
    #             res.raise_for_status()
    #     except requests.RequestException as err:
    #         msg = f"Could not update subscription {subscription.id}"
    #         self.log_error(err=err, msg=msg)
    #         raise
    #
    # def delete_subscription(self, subscription_id: str) -> None:
    #     """
    #     Deletes a subscription from a Context Broker
    #     Args:
    #         subscription_id: id of the subscription
    #     """
    #     url = urljoin(self.base_url,
    #                   f'{self._url_version}/subscriptions/{subscription_id}')
    #     headers = self.headers.copy()
    #     try:
    #         res = self.delete(url=url, headers=headers)
    #         if res.ok:
    #             self.logger.info(f"Subscription '{subscription_id}' "
    #                              f"successfully deleted!")
    #         else:
    #             res.raise_for_status()
    #     except requests.RequestException as err:
    #         msg = f"Could not delete subscription {subscription_id}"
    #         self.log_error(err=err, msg=msg)
    #         raise
    #
    # # Registration API
    # def get_registration_list(self,
    #                           *,
    #                           limit: PositiveInt = None) -> List[Registration]:
    #     """
    #     Lists all the context provider registrations present in the system.
    #
    #     Args:
    #         limit: Limit the number of registrations to be retrieved
    #     Returns:
    #
    #     """
    #     url = urljoin(self.base_url, f'{self._url_version}/registrations/')
    #     headers = self.headers.copy()
    #     params = {}
    #
    #     # We always use the 'count' option to check weather pagination is
    #     # required
    #     params.update({'options': 'count'})
    #     try:
    #         items = self.__pagination(limit=limit,
    #                                   url=url,
    #                                   params=params,
    #                                   headers=headers)
    #
    #         return parse_obj_as(List[Registration], items)
    #     except requests.RequestException as err:
    #         msg = "Could not load registrations!"
    #         self.log_error(err=err, msg=msg)
    #         raise
    #
    # def post_registration(self, registration: Registration):
    #     """
    #     Creates a new context provider registration. This is typically used
    #     for binding context sources as providers of certain data. The
    #     registration is represented by cb.models.Registration
    #
    #     Args:
    #         registration (Registration):
    #
    #     Returns:
    #
    #     """
    #     url = urljoin(self.base_url, f'{self._url_version}/registrations')
    #     headers = self.headers.copy()
    #     headers.update({'Content-Type': 'application/json'})
    #     try:
    #         res = self.post(
    #             url=url,
    #             headers=headers,
    #             data=registration.json(exclude={'id'},
    #                                    exclude_unset=True,
    #                                    exclude_defaults=True,
    #                                    exclude_none=True))
    #         if res.ok:
    #             self.logger.info("Registration successfully created!")
    #             return res.headers['Location'].split('/')[-1]
    #         res.raise_for_status()
    #     except requests.RequestException as err:
    #         msg = f"Could not send registration {registration.id} !"
    #         self.log_error(err=err, msg=msg)
    #         raise
    #
    # def get_registration(self, registration_id: str) -> Registration:
    #     """
    #     Retrieves a registration from context broker by id
    #     Args:
    #         registration_id: id of the registration
    #     Returns:
    #         Registration
    #     """
    #     url = urljoin(self.base_url, f'{self._url_version}/registrations/{registration_id}')
    #     headers = self.headers.copy()
    #     try:
    #         res = self.get(url=url, headers=headers)
    #         if res.ok:
    #             self.logger.debug('Received: %s', res.json())
    #             return Registration(**res.json())
    #         res.raise_for_status()
    #     except requests.RequestException as err:
    #         msg = f"Could not load registration {registration_id} !"
    #         self.log_error(err=err, msg=msg)
    #         raise
    #
    # def update_registration(self, registration: Registration):
    #     """
    #     Only the fields included in the request are updated in the registration.
    #     Args:
    #         registration: Registration to update
    #     Returns:
    #
    #     """
    #     url = urljoin(self.base_url, f'{self._url_version}/registrations/{registration.id}')
    #     headers = self.headers.copy()
    #     headers.update({'Content-Type': 'application/json'})
    #     try:
    #         res = self.patch(
    #             url=url,
    #             headers=headers,
    #             data=registration.json(exclude={'id'},
    #                                    exclude_unset=True,
    #                                    exclude_defaults=True,
    #                                    exclude_none=True))
    #         if res.ok:
    #             self.logger.info("Registration successfully updated!")
    #         else:
    #             res.raise_for_status()
    #     except requests.RequestException as err:
    #         msg = f"Could not update registration {registration.id} !"
    #         self.log_error(err=err, msg=msg)
    #         raise
    #
    # def delete_registration(self, registration_id: str) -> None:
    #     """
    #     Deletes a subscription from a Context Broker
    #     Args:
    #         registration_id: id of the subscription
    #     """
    #     url = urljoin(self.base_url,
    #                   f'{self._url_version}/registrations/{registration_id}')
    #     headers = self.headers.copy()
    #     try:
    #         res = self.delete(url=url, headers=headers)
    #         if res.ok:
    #             self.logger.info("Registration '%s' "
    #                              "successfully deleted!", registration_id)
    #         res.raise_for_status()
    #     except requests.RequestException as err:
    #         msg = f"Could not delete registration {registration_id} !"
    #         self.log_error(err=err, msg=msg)
    #         raise

    # Batch operation API
    def update(self,
               *,
               entities: List[ContextLDEntity],
               action_type: Union[ActionTypeLD, str],
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

        url = urljoin(self.base_url, f'{self._url_version}/entityOperations/{action_type}')
        headers = self.headers.copy()
        headers.update({'Content-Type': 'application/json'})
        params = {}
        if update_format:
            assert update_format == 'keyValues', \
                "Only 'keyValues' is allowed as update format"
            params.update({'options': 'keyValues'})
        update = UpdateLD(entities=entities)
        try:
            if action_type == ActionTypeLD.DELETE:
                id_list = [entity.id for entity in entities]
                res = self.post(
                    url=url,
                    headers=headers,
                    params=params,
                    data=json.dumps(id_list))
            else:
                res = self.post(
                    url=url,
                    headers=headers,
                    params=params,
                    data=update.json(by_alias=True)[12:-1])
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

        self.log_error(err=Exception, msg="not yet implemented (by FIWARE)")
