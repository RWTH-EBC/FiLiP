"""
Context Broker Module for API Client
"""
import json
import os
from math import inf
from typing import Any, Dict, List, Union, Optional, Literal
from urllib.parse import urljoin
import requests
from pydantic import \
    TypeAdapter, \
    PositiveInt, \
    PositiveFloat
from filip.clients.base_http_client import BaseHttpClient, NgsiURLVersion
from filip.config import settings
from filip.models.base import FiwareLDHeader, PaginationMethod, core_context
from filip.models.ngsi_v2.base import AttrsFormat
from filip.models.ngsi_ld.subscriptions import SubscriptionLD
from filip.models.ngsi_ld.context import ContextLDEntity, ContextLDEntityKeyValues, \
    ContextProperty, ContextRelationship, NamedContextProperty, \
    NamedContextRelationship, ActionTypeLD, UpdateLD
from filip.models.ngsi_v2.context import Query


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
        url = url or settings.LD_CB_URL
        #base_http_client overwrites empty header with FiwareHeader instead of FiwareLD
        init_header = fiware_header if fiware_header else FiwareLDHeader()        
        if init_header.link_header is None:
            init_header.set_context(core_context)
        super().__init__(url=url,
                         session=session,
                         fiware_header=init_header,
                         **kwargs)
        # set the version specific url-pattern
        self._url_version = NgsiURLVersion.ld_url.value
        # For uplink requests, the Content-Type header is essential,
        # Accept will be ignored
        # For downlink requests, the Accept header is essential,
        # Content-Type will be ignored

        # default uplink content JSON
        self.headers.update({'Content-Type': 'application/json'})
        # default downlink content JSON-LD
        self.headers.update({'Accept': 'application/ld+json'})

        if init_header.ngsild_tenant is not None:
            self.__make_tenant()

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
                if self._url_version == NgsiURLVersion.v2_url.value:
                    count = int(res.headers['Fiware-Total-Count'])
                elif self._url_version == NgsiURLVersion.ld_url.value:
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

    def __make_tenant(self):
        """
        Create tenant if tenant
        is given in headers
        """
        idhex = f"urn:ngsi-ld:{os.urandom(6).hex()}"
        e = ContextLDEntity(id=idhex,type=f"urn:ngsi-ld:{os.urandom(6).hex()}")
        try:
            self.post_entity(entity=e)
            self.delete_entity_by_id(idhex)
        except Exception as err:
            self.log_error(err=err,msg="Error while creating tenant")
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
        if the update flag bool is True.
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
            if err.response.status_code == 409:
                if append:  # 409 entity already exists
                    return self.append_entity_attributes(entity=entity)
                elif update:
                    return self.override_entities(entities=[entity])
            msg = f"Could not post entity {entity.id}"
            self.log_error(err=err, msg=msg)
            raise

    def override_entities(self, entities: List[ContextLDEntity]):
        """
        Function to create or override existing entites with the NGSI-LD Context Broker.
        The batch operation with Upsert will be used.
        """
        return self.entity_batch_operation(entities=entities,
                                           action_type=ActionTypeLD.UPSERT,
                                           options="replace")

    def get_entity(self,
                   entity_id: str,
                   entity_type: str = None,
                   attrs: List[str] = None,
                   options: Optional[str] = None,
                   geometryProperty: Optional[str] = None,
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
            geometryProperty (String): Name of a GeoProperty. In the case of GeoJSON
                Entity representation, this parameter indicates which GeoProperty to
                use for the "geometry" element. By default, it shall be 'location'.
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
        if geometryProperty:
            params.update({'geometryProperty': geometryProperty})
        if options:
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
                else:
                    return ContextLDEntity(**res.json())
            res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not load entity {entity_id}"
            self.log_error(err=err, msg=msg)
            raise

    GeometryShape = Literal["Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon"]

    def get_entity_list(self,
                        entity_id: Optional[str] = None,
                        id_pattern: Optional[str] = ".*",
                        entity_type: Optional[str] = None,
                        attrs: Optional[List[str]] = None,
                        q: Optional[str] = None,
                        georel: Optional[str] = None,
                        geometry: Optional[GeometryShape] = None,
                        coordinates: Optional[str] = None,
                        geoproperty: Optional[str] = None,
                        # csf: Optional[str] = None,  # Context Source Filter
                        limit: Optional[PositiveInt] = None,
                        options: Optional[str] = None,
                        ) -> List[Union[ContextLDEntity, ContextLDEntityKeyValues]]:
        """
        This operation retrieves a list of entities based on different query options.
        By default, the operation retrieves all the entities in the context broker.
        Args:
            entity_id:
                Id of the entity to be retrieved
            id_pattern:
                Regular expression to match the entity id
            entity_type:
                Entity type, to avoid ambiguity in case there are several
                entities with the same entity id.
            attrs:
                List of attribute names whose data must be included in the response.
            q:
                Query expression, composed of attribute names, operators and values.
            georel:
                Geospatial relationship between the query geometry and the entities.
            geometry:
                Type of geometry for the query. The possible values are Point,
                MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon.
            coordinates:
                Coordinates of the query geometry. The coordinates must be
                expressed as a string of comma-separated values.
            geoproperty:
                Name of a GeoProperty. In the case of GeoJSON Entity representation,
                this parameter indicates which GeoProperty to use for the "geometry" element.
            limit:
                Maximum number of entities to retrieve.
            options:
                Further options for the query. The available options are:
                 - keyValues (simplified representation of entity)
                 - sysAttrs (including createdAt and modifiedAt, etc.)
                 - count (include number of all matched entities in response header)
        """
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
        # if csf:  # ContextSourceRegistration not supported yet
        #     params.update({'csf': csf})
        if limit:
            if limit > 1000:
                raise ValueError("limit must be an integer value <= 1000")
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
        Args:
            entity (ContextLDEntity):
                Entity to append attributes to.
            options (str):
                Options for the request. The only available value is
                'noOverwrite'. If set, it will raise 400, if all attributes
                exist already.

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

    # def update_existing_attribute_by_name(self, entity: ContextLDEntity
    #                                       ):
    #     pass

    def delete_entity_by_id(self,
                            entity_id: str,
                            entity_type: Optional[str] = None):
        """
        Deletes an entity by its id. For deleting mulitple entities at once,
        entity_batch_operation() is more efficient.
        Args:
            entity_id:
                ID of entity to delete.
            entity_type:
                Type of entity to delete.
        """
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
        """
        Deletes an attribute from an entity.
        Args:
            entity_id:
                ID of the entity.
            attribute_id:
                Name of the attribute to delete.
        Returns:

        """
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
                              limit: PositiveInt = inf) -> List[SubscriptionLD]:
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
            adapter = TypeAdapter(List[SubscriptionLD])
            return adapter.validate_python(items)
        except requests.RequestException as err:
            msg = "Could not load subscriptions!"
            self.log_error(err=err, msg=msg)
            raise

    def post_subscription(self, subscription: SubscriptionLD,
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
                    self.logger.warning(f"Subscription existed already with the id"
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

    def get_subscription(self, subscription_id: str) -> SubscriptionLD:
        """
        Retrieves a subscription from the context broker.
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
                return SubscriptionLD(**res.json())
            res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not load subscription {subscription_id}"
            self.log_error(err=err, msg=msg)
            raise

    def update_subscription(self, subscription: SubscriptionLD) -> None:
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

    def handle_multi_status_response(self, res: requests.Response):
        """
        Handles the response of a batch_operation. If the response contains
        errors, they are logged. If the response contains only errors, a RuntimeError
        is raised.
        Args:
            res:

        Returns:

        """
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
                                                      exclude_none=True,
                                                      ).get('entities'))
                )
            self.handle_multi_status_response(res)
        except RuntimeError as rerr:
            raise rerr
        except Exception as err:
            raise err
        else:
            self.logger.info(f"Update operation {action_type} succeeded!")
