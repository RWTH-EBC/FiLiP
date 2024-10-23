"""
Context Broker Module for API Client
"""
import json
import re
import warnings
from math import inf
from enum import Enum
from typing import Any, Dict, List, Union, Optional, Literal
from urllib.parse import urljoin
import requests
from pydantic import \
    TypeAdapter, \
    PositiveInt, \
    PositiveFloat
from filip.clients.base_http_client import BaseHttpClient
from filip.config import settings
from filip.models.base import FiwareLDHeader, PaginationMethod
from filip.utils.simple_ql import QueryString
from filip.models.ngsi_v2.base import AttrsFormat
from filip.models.ngsi_ld.subscriptions import Subscription
from filip.models.ngsi_ld.context import ContextLDEntity, ContextLDEntityKeyValues, ContextProperty, ContextRelationship, NamedContextProperty, \
    NamedContextRelationship, ActionTypeLD, UpdateLD
from filip.models.ngsi_v2.context import Query


class NgsiURLVersion(str, Enum):
    """
    URL part that defines the NGSI version for the API.
    """
    v2_url = "/v2"
    ld_url = "/ngsi-ld/v1"


class ContextBrokerLDClient(BaseHttpClient):
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
        #base_http_client overwrites empty header with FiwareHeader instead of FiwareLD
        init_header = FiwareLDHeader()
        if fiware_header:
            init_header=fiware_header
        super().__init__(url=url,
                         session=session,
                         fiware_header=init_header,
                         **kwargs)
        # set the version specific url-pattern
        self._url_version = NgsiURLVersion.ld_url
        # init Content-Type header , account for @context field further down
        self.headers.update({'Content-Type':'application/json'})

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
                if self._url_version == NgsiURLVersion.v2_url:
                    count = int(res.headers['Fiware-Total-Count'])
                elif self._url_version == NgsiURLVersion.ld_url:
                    count = int(res.headers['NGSILD-Results-Count'])
                else:
                    count = 0

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

    def get_version(self) -> Dict:
        """
        Gets version of Orion-LD context broker
        Returns:
            Dictionary with response
        """
        url = urljoin(self.base_url, '/version')
        try:
            res = self.get(url=url)
            if res.ok:
                return res.json()
            res.raise_for_status()
        except requests.RequestException as err:
            self.logger.error(err)
            raise

    def get_statistics(self) -> Dict:
        """
        Gets statistics of context broker
        Returns:
            Dictionary with response
        """
        url = urljoin(self.base_url, 'statistics')
        try:
            res = self.get(url=url)
            if res.ok:
                return res.json()
            res.raise_for_status()
        except requests.RequestException as err:
            self.logger.error(err)
            raise


    def post_entity(self,
                    entity: ContextLDEntity,
                    append: bool = False,
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
        if entity.model_dump().get('@context',None) is not None:
            headers.update({'Content-Type':'application/ld+json'})
            headers.update({'Link':None})
        try:
            res = self.post(
                url=url,
                headers=headers,
                json=entity.model_dump(exclude_unset=True,
                                 exclude_defaults=True,
                                 exclude_none=True))
            if res.ok:
                self.logger.info("Entity successfully posted!")
                return res.headers.get('Location')
            res.raise_for_status()
        except requests.RequestException as err:
            if append and err.response.status_code == 409:
                return self.append_entity_attributes(entity=entity)
            msg = f"Could not post entity {entity.id}"
            self.log_error(err=err, msg=msg)
            raise

    GeometryShape = Literal["Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon"]

    def get_entity(self,
                   entity_id: str,
                   entity_type: str = None,
                   attrs: List[str] = None,
                   options: Optional[str] = "keyValues",
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
            options (String): keyValues (simplified representation of entity)
                or sysAttrs (include generated attrs createdAt and modifiedAt)
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
        if options != 'keyValues' and options != 'sysAttrs':
            raise ValueError(f'Only available options are \'keyValues\' and \'sysAttrs\'')
        params.update({'options': options})

        try:
            res = self.get(url=url, params=params, headers=headers)
            if res.ok:
                self.logger.info("Entity successfully retrieved!")
                self.logger.debug("Received: %s", res.json())
                if options == "keyValues":
                    return ContextLDEntityKeyValues(**res.json())
                if options == "sysAttrs":
                    return ContextLDEntity(**res.json())
            res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not load entity {entity_id}"
            self.log_error(err=err, msg=msg)
            raise

    def get_entity_list(self,
                        entity_id: Optional[str] = None,
                        id_pattern: Optional[str] = ".*",
                        entity_type: Optional[str] = None,
                        attrs: Optional[List[str]] = None,
                        q: Optional[str] = None,
                        georel: Optional[str] = None,
                        geometry: Optional[GeometryShape] = None,  # So machen oder wie auch für response_format
                        coordinates: Optional[str] = None,
                        geoproperty: Optional[str] = None,
                        csf: Optional[str] = None,
                        limit: Optional[PositiveInt] = None,
                        options: Optional[str] = None,
                        ) -> List[Union[ContextLDEntity, ContextLDEntityKeyValues]]:

        url = urljoin(self.base_url, f'{self._url_version}/entities/')
        headers = self.headers.copy()
        params = {}
        if entity_id:
            params.update({'id': entity_id})
        if id_pattern:
            params.update({'idPattern': id_pattern})
        if entity_type:
            params.update({'type': entity_type})
        if attrs:
            params.update({'attrs': ','.join(attrs)})
        if q:
            params.update({'q': q})
        if georel:
            params.update({'georel': georel})
        if geometry:
            params.update({'geometry': geometry})
        if coordinates:
            params.update({'coordinates': coordinates})
        if geoproperty:
            params.update({'geoproperty': geoproperty})
        if csf:
            params.update({'csf': csf})
        if limit:
            params.update({'limit': limit})
        if options:
            if options != 'keyValues' and options != 'sysAttrs':
                raise ValueError(f'Only available options are \'keyValues\' and \'sysAttrs\'')
            params.update({'options': options})
        # params.update({'local': 'true'})

        try:
            res = self.get(url=url, params=params, headers=headers)
            if res.ok:
                self.logger.info("Entity successfully retrieved!")
                entity_list: List[Union[ContextLDEntity, ContextLDEntityKeyValues]] = []
                if options == "keyValues":
                    entity_list = [ContextLDEntityKeyValues(**item) for item in res.json()]
                    return entity_list
                else:
                    entity_list = [ContextLDEntity(**item) for item in res.json()]
                    return entity_list
            res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not load entity matching{params}"
            self.log_error(err=err, msg=msg)
            raise

    def replace_existing_attributes_of_entity(self, entity: ContextLDEntity, append: bool = False):
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
        if entity.model_dump().get('@context',None) is not None:
            headers.update({'Content-Type':'application/ld+json'})
            headers.update({'Link':None})
        try:
            res = self.patch(url=url,
                             headers=headers,
                             json=entity.model_dump(exclude={'id', 'type'},
                                              exclude_unset=True,
                                              exclude_none=True))
            if res.ok:
                self.logger.info(f"Entity {entity.id} successfully "
                                 "updated!")
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            if append and err.response.status_code == 207:
                return self.append_entity_attributes(entity=entity)
            msg = f"Could not replace attribute of entity {entity.id} !"
            self.log_error(err=err, msg=msg)
            raise

    def update_entity_attribute(self,
                                entity_id: str,
                                attr: Union[ContextProperty, ContextRelationship,
                                            NamedContextProperty, NamedContextRelationship],
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
                                      "NamedContextAttribute or NamedContextRelationship"

        url = urljoin(self.base_url,
                      f'{self._url_version}/entities/{entity_id}/attrs/{attr_name}')

        jsonnn = {}
        if isinstance(attr, list) or isinstance(attr, NamedContextProperty):
            jsonnn = attr.model_dump(exclude={'name'},
                                            exclude_unset=True,
                                            exclude_none=True)
        else:
            prop = attr.model_dump()
            for key, value in prop.items():
                if value and value != 'Property':
                    jsonnn[key] = value

        try:
            res = self.patch(url=url,
                             headers=headers,
                             json=jsonnn)
            if res.ok:
                self.logger.info(f"Attribute {attr_name} of {entity_id} successfully updated!")
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not update attribute '{attr_name}' of entity {entity_id}"
            self.log_error(err=err, msg=msg)
            raise

    def append_entity_attributes(self,
                                 entity: ContextLDEntity,
                                 options: Optional[str] = None
                                 ):
        """
        Append new Entity attributes to an existing Entity within an NGSI-LD system
        """
        url = urljoin(self.base_url, f'{self._url_version}/entities/{entity.id}/attrs')
        headers = self.headers.copy()
        if entity.model_dump().get('@context',None) is not None:
            headers.update({'Content-Type':'application/ld+json'})
            headers.update({'Link':None})
        params = {}

        if options:
            if options != 'noOverwrite':
                raise ValueError(f'The only available value is \'noOverwrite\'')
            params.update({'options': options})

        try:
            res = self.post(url=url,
                            headers=headers,
                            params=params,
                            json=entity.model_dump(exclude={'id', 'type'},
                                             exclude_unset=True,
                                             exclude_none=True))
            if res.ok:
                self.logger.info(f"Entity {entity.id} successfully updated!")
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not update entity {entity.id}!"
            self.log_error(err=err, msg=msg)
            raise

    def update_existing_attribute_by_name(self, entity: ContextLDEntity
                                          ):
        pass

    def delete_entity_by_id(self,
                            entity_id: str,
                            entity_type: Optional[str] = None):
        url = urljoin(self.base_url, f'{self._url_version}/entities/{entity_id}')
        headers = self.headers.copy()
        params = {}

        if entity_type:
            params.update({'type': entity_type})

        try:
            res = self.delete(url=url, headers=headers, params=params)
            if res.ok:
                self.logger.info(f"Entity {entity_id} successfully deleted")
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not delete entity {entity_id}"
            self.log_error(err=err, msg=msg)
            raise

    def delete_attribute(self,
                         entity_id: str,
                         attribute_id: str):
        url = urljoin(self.base_url, f'{self._url_version}/entities/{entity_id}/attrs/{attribute_id}')
        headers = self.headers.copy()

        try:
            res = self.delete(url=url, headers=headers)
            if res.ok:
                self.logger.info(f"Attribute {attribute_id} of Entity {entity_id} successfully deleted")
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not delete attribute {attribute_id} of entity {entity_id}"
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
            adapter = TypeAdapter(List[Subscription])
            return adapter.validate_python(items)
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

        sub_hash = subscription.model_dump_json(include={'subject', 'notification', 'type'})
        for ex_sub in existing_subscriptions:
            if sub_hash == ex_sub.model_dump_json(include={'subject', 'notification', 'type'}):
                self.logger.info("Subscription already exists")
                if update:
                    self.logger.info("Updated subscription")
                    subscription.id = ex_sub.id
                    self.update_subscription(subscription)
                else:
                    warnings.warn(f"Subscription existed already with the id"
                                  f" {ex_sub.id}")
                return ex_sub.id

        url = urljoin(self.base_url, f'{self._url_version}/subscriptions')
        headers = self.headers.copy()
        if subscription.model_dump().get('@context',None) is not None:
            headers.update({'Content-Type':'application/ld+json'})
            headers.update({'Link':None})
        try:
            res = self.post(
                url=url,
                headers=headers,
                data=subscription.model_dump_json(exclude_unset=False,
                                                  exclude_defaults=False,
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

    def update_subscription(self, subscription: Subscription) -> None:
        """
        Only the fields included in the request are updated in the subscription.
        Args:
            subscription: Subscription to update
        Returns:

        """
        url = urljoin(self.base_url, f'{self._url_version}/subscriptions/{subscription.id}')
        headers = self.headers.copy()
        if subscription.model_dump().get('@context',None) is not None:
            headers.update({'Content-Type':'application/ld+json'})
            headers.update({'Link':None})
        try:
            res = self.patch(
                url=url,
                headers=headers,
                data=subscription.model_dump_json(exclude={'id'},
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

    def log_multi_errors(self, errors: List[Dict]) -> None:
        for error in errors:
            entity_id = error['entityId']
            error_details: dict = error['error']
            error_title = error_details.get('title')
            error_status = error_details.get('status')
            # error_detail = error_details['detail']
            self.logger.error("Response status: %d, Entity: %s, Reason: %s",
                              error_status, entity_id, error_title)

    def handle_multi_status_response(self, res):
        try:
            res.raise_for_status()
            if res.text:
                response_data = res.json()
                if 'errors' in response_data:
                    errors = response_data['errors']
                    self.log_multi_errors(errors)
                if 'success' in response_data:
                    successList = response_data['success']
                    if len(successList) == 0:
                        raise RuntimeError("Batch operation resulted in errors only, see logs")
            else:
                self.logger.info("Empty response received.")
        except json.JSONDecodeError:
            self.logger.info("Error decoding JSON. Response may not be in valid JSON format.")

    # Batch operation API
    def entity_batch_operation(self,
                               *,
                               entities: List[ContextLDEntity],
                               action_type: Union[ActionTypeLD, str],
                               options: Literal['noOverwrite', 'replace', 'update'] = None) -> None:
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
            options (str): Optional 'noOverwrite' 'replace' 'update'

        Returns:

        """

        url = urljoin(self.base_url, f'{self._url_version}/entityOperations/{action_type.value}')
        headers = self.headers.copy()
        headers.update({'Content-Type': 'application/json'})
        params = {}
        if options:
            params.update({'options': options})
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
                    data=json.dumps(update.model_dump(by_alias=True,
                                                      exclude_unset=True,
                                                      ).get('entities'))
                )
            self.handle_multi_status_response(res)
        except RuntimeError as rerr:
            raise rerr
        except Exception as err:
            raise err
        else:
            self.logger.info(f"Update operation {action_type} succeeded!")

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
###################################################################################################################

# CONTEXT MANAGEMENT API ENDPOINTS
# Entity Operations
# def post_entity(self,
#                 entity: ContextLDEntity,
#                 update: bool = False):
#     """
#     Function registers an Object with the NGSI-LD Context Broker,
#     if it already exists it can be automatically updated
#     if the overwrite bool is True
#     First a post request with the entity is tried, if the response code
#     is 422 the entity is uncrossable, as it already exists there are two
#     options, either overwrite it, if the attribute have changed
#     (e.g. at least one new/new values) (update = True) or leave
#     it the way it is (update=False)
#
#     """
#     url = urljoin(self.base_url, f'{self._url_version}/entities')
#     headers = self.headers.copy()
#     try:
#         res = self.post(
#             url=url,
#             headers=headers,
#             json=entity.dict(exclude_unset=True,
#                              exclude_defaults=True,
#                              exclude_none=True))
#         if res.ok:
#             self.logger.info("Entity successfully posted!")
#             return res.headers.get('Location')
#         res.raise_for_status()
#     except requests.RequestException as err:
#         if update and err.response.status_code == 422:
#             return self.update_entity(entity=entity)
#         msg = f"Could not post entity {entity.id}"
#         self.log_error(err=err, msg=msg)
#         raise
#
# def get_entity_list(self,
#                     *,
#                     entity_ids: List[str] = None,
#                     entity_types: List[str] = None,
#                     id_pattern: str = None,
#                     type_pattern: str = None,
#                     q: Union[str, QueryString] = None,
#                     mq: Union[str, QueryString] = None,
#                     georel: str = None,
#                     geometry: str = None,
#                     coords: str = None,
#                     limit: int = inf,
#                     attrs: List[str] = None,
#                     order_by: str = None,
#                     response_format: Union[AttrsFormat, str] =
#                     AttrsFormat.NORMALIZED,
#                     **kwargs
#                     ) -> List[Union[ContextLDEntity,
#                                     ContextLDEntityKeyValues,
#                                     Dict[str, Any]]]:
#     r"""
#     Retrieves a list of context entities that match different criteria by
#     id, type, pattern matching (either id or type) and/or those which
#     match a query or geographical query (see Simple Query Language and
#     Geographical Queries). A given entity has to match all the criteria
#     to be retrieved (i.e., the criteria is combined in a logical AND
#     way). Note that pattern matching query parameters are incompatible
#     (i.e. mutually exclusive) with their corresponding exact matching
#     parameters, i.e. idPattern with id and typePattern with type.
#
#     Args:
#         entity_ids: A comma-separated list of elements. Retrieve entities
#             whose ID matches one of the elements in the list.
#             Incompatible with idPattern,e.g. Boe_Idarium
#         entity_types: comma-separated list of elements. Retrieve entities
#             whose type matches one of the elements in the list.
#             Incompatible with typePattern. Example: Room.
#         id_pattern: A correctly formatted regular expression. Retrieve
#             entities whose ID matches the regular expression. Incompatible
#             with id, e.g. ngsi-ld.* or sensor.*
#         type_pattern: is not supported in NGSI-LD
#         q (SimpleQuery): A query expression, composed of a list of
#             statements separated by ;, i.e.,
#             q=statement1;statement2;statement3. See Simple Query
#             Language specification. Example: temperature>40.
#         mq (SimpleQuery): A  query expression for attribute metadata,
#             composed of a list of statements separated by ;, i.e.,
#             mq=statement1;statement2;statement3. See Simple Query
#             Language specification. Example: temperature.accuracy<0.9.
#         georel: Spatial relationship between matching entities and a
#             reference shape. See Geographical Queries. Example: 'near'.
#         geometry: Geographical area to which the query is restricted.
#             See Geographical Queries. Example: point.
#         coords: List of latitude-longitude pairs of coordinates separated
#             by ';'. See Geographical Queries. Example: 41.390205,
#             2.154007;48.8566,2.3522.
#         limit: Limits the number of entities to be retrieved Example: 20
#         attrs: Comma-separated list of attribute names whose data are to
#             be included in the response. The attributes are retrieved in
#             the order specified by this parameter. If this parameter is
#             not included, the attributes are retrieved in arbitrary
#             order. See "Filtering out attributes and metadata" section
#             for more detail. Example: seatNumber.
#         metadata: A list of metadata names to include in the response.
#             See "Filtering out attributes and metadata" section for more
#             detail. Example: accuracy.
#         order_by: Criteria for ordering results. See "Ordering Results"
#             section for details. Example: temperature,!speed.
#         response_format (AttrsFormat, str): Response Format. Note: That if
#             'keyValues' or 'values' are used the response model will
#             change to List[ContextEntityKeyValues] and to List[Dict[str,
#             Any]], respectively.
#     Returns:
#
#     """
#     url = urljoin(self.base_url, f'{self._url_version}/entities/')
#     headers = self.headers.copy()
#     params = {}
#
#     if entity_ids and id_pattern:
#         raise ValueError
#     if entity_ids:
#         if not isinstance(entity_ids, list):
#             entity_ids = [entity_ids]
#         params.update({'id': ','.join(entity_ids)})
#     if id_pattern:
#         try:
#             re.compile(id_pattern)
#         except re.error as err:
#             raise ValueError(f'Invalid Pattern: {err}') from err
#         params.update({'idPattern': id_pattern})
#     if entity_types:
#         if not isinstance(entity_types, list):
#             entity_types = [entity_types]
#         params.update({'type': ','.join(entity_types)})
#     if type_pattern:
#         warnings.warn(f"type pattern are not supported by NGSI-LD and will be ignored in this request")
#     if attrs:
#         params.update({'attrs': ','.join(attrs)})
#     if q:
#         params.update({'q': str(q)})
#     if mq:
#         params.update({'mq': str(mq)})
#     if geometry:
#         params.update({'geometry': geometry})
#     if georel:
#         params.update({'georel': georel})
#     if coords:
#         params.update({'coords': coords})
#     if order_by:
#         params.update({'orderBy': order_by})
#     if response_format not in list(AttrsFormat):
#         raise ValueError(f'Value must be in {list(AttrsFormat)}')
#     #This interface is only realized via additional specifications.
#     #If no parameters are passed, the idPattern is set to "urn:*".
#     if not params:
#         default_idPattern = "urn:*"
#         params.update({'idPattern': default_idPattern})
#         warnings.warn(f"querying entities without additional parameters is not supported on ngsi-ld. the query is "
#                       f"performed with the idPattern {default_idPattern}")
#     response_format = ','.join(['count', response_format])
#     params.update({'options': response_format})
#     try:
#         items = self._ContextBrokerClient__pagination(method=PaginationMethod.GET,
#                                   limit=limit,
#                                   url=url,
#                                   params=params,
#                                   headers=headers)
#         if AttrsFormat.NORMALIZED in response_format:
#             return parse_obj_as(List[ContextLDEntity], items)
#         if AttrsFormat.KEY_VALUES in response_format:
#             return parse_obj_as(List[ContextLDEntityKeyValues], items)
#         return items
#
#     except requests.RequestException as err:
#         msg = "Could not load entities"
#         self.log_error(err=err, msg=msg)
#         raise
# There is no endpoint for getting attributes anymore
# TODO? get entity and return attributes?
    def get_entity_attributes(self,
                              entity_id: str,
                              entity_type: str = None,
                              attrs: List[str] = None,
                              response_format: Union[AttrsFormat, str] =
                              AttrsFormat.KEY_VALUES,
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
        url = urljoin(self.base_url, f'{self._url_version}/entities/{entity_id}/attrs')
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
                if response_format == AttrsFormat.KEY_VALUES:
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
