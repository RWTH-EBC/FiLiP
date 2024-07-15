"""
TimeSeries Module for QuantumLeap API Client
"""
import logging
import time
from math import inf
from collections import deque
from itertools import count,chain
from typing import Dict, List, Union, Deque, Optional
from urllib.parse import urljoin
import requests
from pydantic import AnyHttpUrl
from pydantic.type_adapter import TypeAdapter
from filip import settings
from filip.clients.base_http_client import BaseHttpClient
from filip.models.base import FiwareHeader
from filip.models.ngsi_v2.subscriptions import Message
from filip.models.ngsi_v2.timeseries import \
    AggrPeriod, \
    AggrMethod, \
    AggrScope, \
    AttributeValues, \
    TimeSeries, \
    TimeSeriesHeader


logger = logging.getLogger(__name__)


class QuantumLeapClient(BaseHttpClient):
    """
    Implements functions to use the FIWARE's QuantumLeap, which subscribes to an
    Orion Context Broker and stores the subscription data in a time series
    database (CrateDB). Further Information:
    https://smartsdk.github.io/ngsi-timeseries-api/#quantumleap
    https://app.swaggerhub.com/apis/heikkilv/quantumleap-api/

    Args:
        url: url of the quantumleap service
        session (Optional):
        fiware_header:
        **kwargs:
    """

    def __init__(self,
                 url: str = None,
                 *,
                 session: requests.Session = None,
                 fiware_header: FiwareHeader = None,
                 **kwargs):
        # set service url
        url = url or settings.QL_URL
        super().__init__(url=url,
                         session=session,
                         fiware_header=fiware_header,
                         **kwargs)

    # META API ENDPOINTS
    def get_version(self) -> Dict:
        """
        Gets version of QuantumLeap-Service.

        Returns:
            Dictionary with response
        """
        url = urljoin(self.base_url, 'version')
        try:
            res = self.get(url=url, headers=self.headers)
            if res.ok:
                return res.json()
            res.raise_for_status()
        except requests.exceptions.RequestException as err:
            self.logger.error(err)
            raise

    def get_health(self) -> Dict:
        """
        This endpoint is intended for administrators of QuantumLeap. Using the
        information returned by this endpoint they can diagnose problems in the
        service or its dependencies. This information is also useful for cloud
        tools such as orchestrators and load balancers with rules based on
        health-checks. Due to the lack of a standardized response format, we
        base the implementation on the draft of
        https://inadarei.github.io/rfc-healthcheck/

        Returns:
            Dictionary with response
        """
        url = urljoin(self.base_url, 'health')
        try:
            res = self.get(url=url, headers=self.headers)
            if res.ok:
                return res.json()
            res.raise_for_status()
        except requests.exceptions.RequestException as err:
            self.logger.error(err)
            raise

    def post_config(self):
        """
        (To Be Implemented) Customize your persistence configuration to
        better suit your needs.
        """
        raise NotImplementedError("Endpoint to be implemented..")

    # INPUT API ENDPOINTS
    def post_notification(self, notification: Message):
        """
        Notify QuantumLeap the arrival of a new NGSI notification.

        Args:
            notification: Notification Message Object
        """
        url = urljoin(self.base_url, 'v2/notify')
        headers = self.headers.copy()
        data = []
        for entity in notification.data:
            data.append(entity.model_dump(exclude_none=True))
        data_set = {
            "data": data,
            "subscriptionId": notification.subscriptionId
        }

        try:
            res = self.post(
                url=url,
                headers=headers,
                json=data_set)
            if res.ok:
                self.logger.debug(res.text)
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as err:
            msg = f"Could not post notification for subscription id " \
                  f"{notification.subscriptionId}"
            self.log_error(err=err, msg=msg)
            raise

    def post_subscription(self,
                          cb_url: Union[AnyHttpUrl, str],
                          ql_url: Union[AnyHttpUrl, str],
                          entity_type: str = None,
                          entity_id: str = None,
                          id_pattern: str = None,
                          attributes: str = None,
                          observed_attributes: str = None,
                          notified_attributes: str = None,
                          throttling: int = None,
                          time_index_attribute: str = None):
        """
        Subscribe QL to process Orion notifications of certain type.
        This endpoint simplifies the creation of the subscription in orion
        that will generate the notifications to be consumed by QuantumLeap in
        order to save historical records. If you want an advanced specification
        of the notifications, you can always create the subscription in orion
        at your will. This endpoint just aims to simplify the common use case.

        Args:
            cb_url:
                url of the context broker
            ql_url:
                The url where Orion can reach QuantumLeap. Do not include
                specific paths.
            entity_type (String):
                The type of entities for which to create a
                subscription, so as to persist historical data of entities of
                this type.
            entity_id (String):
                Id of the entity to track. If specified, it
                takes precedence over the idPattern parameter.
            id_pattern (String): The pattern covering the entity ids for which
                to subscribe. If not specified, QL will track all entities of
                the specified type.
            attributes (String): Comma-separated list of attribute names to
                track.
            observed_attributes (String): Comma-separated list of attribute
                names to track.
            notified_attributes (String): Comma-separated list of attribute
                names to be used to restrict the data of which QL will keep a
                history.
            throttling (int): Minimal period of time in seconds which must
                elapse between two consecutive notifications.
            time_index_attribute (String): The name of a custom attribute to be
                used as a
            time index.
        """
        raise DeprecationWarning("Subscription endpoint of Quantumleap API is "
                                 "deprecated, use the ORION subscription endpoint "
                                 "instead")

    def delete_entity(self, entity_id: str,
                      entity_type: Optional[str] = None) -> str:
        """
        Given an entity (with type and id), delete all its historical records.

        Args:
            entity_id (String): Entity id is required.
            entity_type (Optional[String]): Entity type if entity_id alone
                can not uniquely define the entity.

        Raises:
            RequestException, if entity was not found
            Exception, if deleting was not successful

        Returns:
            The entity_id of entity that is deleted.
        """
        url = urljoin(self.base_url, f'v2/entities/{entity_id}')
        headers = self.headers.copy()
        if entity_type is not None:
            params = {'type': entity_type}
        else:
            params = {}

        # The deletion does not always resolves in a success even if an ok is
        # returned.
        # Try to delete multiple times with incrementing waits.
        # If the entity is no longer found the methode returns with a success
        # If the deletion attempt fails after the 10th try, raise an
        # Exception: it could not be deleted
        counter = 0
        while counter < 10:
            self.delete(url=url, headers=headers, params=params)
            try:
                self.get_entity_by_id(entity_id=entity_id,
                                      entity_type=entity_type)
            except requests.exceptions.RequestException as err:
                self.logger.info("Entity id '%s' successfully deleted!",
                                 entity_id)
                return entity_id
            time.sleep(counter * 5)
            counter += 1

        msg = f"Could not delete QL entity of id {entity_id}"
        logger.error(msg=msg)
        raise Exception(msg)

    def delete_entity_type(self, entity_type: str) -> str:
        """
        Given an entity type, delete all the historical records of all
        entities of such type.
        Args:
            entity_type (String): Type of entities data to be deleted.
        Returns:
            Entity type of the entities deleted.
        """
        url = urljoin(self.base_url, f'v2/types/{entity_type}')
        headers = self.headers.copy()
        try:
            res = self.delete(url=url, headers=headers)
            if res.ok:
                self.logger.info("Entities of type '%s' successfully deleted!",
                                 entity_type)
                return entity_type
            res.raise_for_status()
        except requests.exceptions.RequestException as err:
            msg = f"Could not delete entities of type {entity_type}"
            self.log_error(err=err, msg=msg)
            raise

    # QUERY API ENDPOINTS
    def __query_builder(self,
                        url,
                        *,
                        entity_id: str = None,
                        id_pattern: str = None,
                        options: str = None,
                        entity_type: str = None,
                        aggr_method: Union[str, AggrMethod] = None,
                        aggr_period: Union[str, AggrPeriod] = None,
                        from_date: str = None,
                        to_date: str = None,
                        last_n: int = None,
                        limit: int = 10000,
                        offset: int = 0,
                        georel: str = None,
                        geometry: str = None,
                        coords: str = None,
                        attrs: str = None,
                        aggr_scope: Union[str, AggrScope] = None
                        ) -> Deque[Dict]:
        """
        Private Function to call respective API endpoints, chops large
        requests into multiple single requests and merges the
        responses

        Args:
            url:
            entity_id:
            options:
            entity_type:
            aggr_method:
            aggr_period:
            from_date:
            to_date:
            last_n:
            limit:
                Maximum number of results to retrieve in a single response.
            offset:
                Offset to apply to the response results. For example, if the
                query was to return 10 results and you use an offset of 1, the
                response will return the last 9 values. Make sure you don't
                give more offset than the number of results.
            georel:
            geometry:
            coords:
            attrs:
            aggr_scope:
            id_pattern (str): The pattern covering the entity ids for which
                to subscribe. The pattern follow regular expressions (POSIX
                Extendede) e.g. ".*", "Room.*". Detail information:
                https://en.wikibooks.org/wiki/Regular_Expressions/POSIX-Extended_Regular_Expressions

        Returns:
            Dict
        """
        assert (id_pattern is None or entity_id is None), "Cannot have both id and idPattern as parameter."
        params = {}
        headers = self.headers.copy()
        max_records_per_request = 10000
        # create a double ending queue
        res_q: Deque[Dict] = deque([])

        if options:
            params.update({'options': options})
        if entity_type:
            params.update({'type': entity_type})
        if aggr_method:
            aggr_method = AggrMethod(aggr_method)
            params.update({'aggrMethod': aggr_method.value})
        if aggr_period:
            aggr_period = AggrPeriod(aggr_period)
            params.update({'aggrPeriod': aggr_period.value})
        if from_date:
            params.update({'fromDate': from_date})
        if to_date:
            params.update({'toDate': to_date})
        # These values are required for the integrated pagination mechanism
        # maximum items per request
        if limit is None:
            limit = inf
        if offset is None:
            offset = 0
        if georel:
            params.update({'georel': georel})
        if coords:
            params.update({'coords': coords})
        if geometry:
            params.update({'geometry': geometry})
        if attrs:
            params.update({'attrs': attrs})
        if aggr_scope:
            aggr_scope = AggrScope(aggr_scope)
            params.update({'aggr_scope': aggr_scope.value})
        if entity_id:
            params.update({'id': entity_id})
        if id_pattern:
            params.update({'idPattern': id_pattern})

        # This loop will chop large requests into smaller junks.
        # The individual functions will then merge the final response models
        for i in count(0, max_records_per_request):
            try:
                params['offset'] = offset + i

                params['limit'] = min(limit - i, max_records_per_request)
                if params['limit'] <= 0:
                    break

                if last_n:
                    params['lastN'] = min(last_n - i, max_records_per_request)
                    if params['lastN'] <= 0:
                        break

                res = self.get(url=url, params=params, headers=headers)

                if res.ok:
                    self.logger.debug('Received: %s', res.json())

                    # revert append direction when using last_n
                    if last_n:
                        res_q.appendleft(res.json())
                    else:
                        res_q.append(res.json())
                res.raise_for_status()

            except requests.exceptions.RequestException as err:
                if err.response.status_code == 404 and \
                        err.response.json().get('error') == 'Not Found' and \
                        len(res_q) > 0:
                    break
                else:
                    msg = "Could not load entity data"
                    self.log_error(err=err, msg=msg)
                    raise

        self.logger.info("Successfully retrieved entity data")
        return res_q

    # v2/entities
    def get_entities(self, *,
                     entity_type: str = None,
                     id_pattern: str = None,
                     from_date: str = None,
                     to_date: str = None,
                     limit: int = 10000,
                     offset: int = None
                     ) -> List[TimeSeriesHeader]:
        """
        Get list of all available entities and their context information
        about EntityType and last update date.

        Args:
            entity_type (str): Comma-separated list of entity types whose data
                are to be included in the response. Use only one (no comma)
                when required. If used to resolve ambiguity for the given
                entityId, make sure the given entityId exists for this
                entityType.
            id_pattern (str): The pattern covering the entity ids for which
                to subscribe. The pattern follow regular expressions (POSIX
                Extendede) e.g. ".*", "Room.*". Detail information:
                https://en.wikibooks.org/wiki/Regular_Expressions/POSIX-Extended_Regular_Expressions
            from_date (str): The starting date and time (inclusive) from which
                the context information is queried. Must be in ISO8601 format
                (e.g., 2018-01-05T15:44:34)
            to_date (str): The final date and time (inclusive) from which the
                context information is queried. Must be in ISO8601 format
                (e.g., 2018-01-05T15:44:34).
            limit (int): Maximum number of results to be retrieved.
                Default value : 10000
            offset (int): Offset for the results.

        Returns:
            List of TimeSeriesHeader
        """
        url = urljoin(self.base_url, 'v2/entities')
        res = self.__query_builder(url=url,
                                   id_pattern=id_pattern,
                                   entity_type=entity_type,
                                   from_date=from_date,
                                   to_date=to_date,
                                   limit=limit,
                                   offset=offset)
        
        ta = TypeAdapter(List[TimeSeriesHeader])
        return ta.validate_python(res[0])

    # /entities/{entityId}
    def get_entity_by_id(self,
                         entity_id: str,
                         *,
                         attrs: str = None,
                         entity_type: str = None,
                         aggr_method: Union[str, AggrMethod] = None,
                         aggr_period: Union[str, AggrPeriod] = None,
                         from_date: str = None,
                         to_date: str = None,
                         last_n: int = None,
                         limit: int = 10000,
                         offset: int = None,
                         georel: str = None,
                         geometry: str = None,
                         coords: str = None,
                         options: str = None
                         ) -> TimeSeries:

        """
        History of N attributes of a given entity instance
        For example, query max water level of the central tank throughout the
        last year. Queries can get more
        sophisticated with the use of filters and query attributes.

        Args:
            entity_id (String): Entity id is required.
            attrs (String):
                Comma-separated list of attribute names whose data are to be
                included in the response. The attributes are retrieved in the
                order specified by this parameter. If not specified, all
                attributes are included in the response in arbitrary order.
            entity_type (String): Comma-separated list of entity types whose
                data are to be included in the response.
            aggr_method (String):
                The function to apply to the raw data filtered by the query
                parameters. If not given, the returned data are the same raw
                inserted data.

                Allowed values: count, sum, avg, min, max
            aggr_period (String):
                If not defined, the aggregation will apply to all the values
                contained in the search result. If defined, the aggregation
                function will instead be applied N times, once for each
                period, and all those results will be considered for the
                response. For example, a query asking for the average
                temperature of an attribute will typically return 1 value.
                However, with an aggregationPeriod of day, you get the daily
                average of the temperature instead (more than one value
                assuming you had measurements across many days within the
                scope of your search result). aggrPeriod must be accompanied
                by an aggrMethod, and the aggrMethod will be applied to all
                the numeric attributes specified in attrs; the rest of the
                non-numerical attrs will be ignored. By default, the response
                is grouped by entity_id. See aggrScope to create aggregation
                across entities:

                Allowed values: year, month, day, hour, minute, second

            from_date (String):
                The starting date and time (inclusive) from which the context
                information is queried. Must be in ISO8601 format (e.g.,
                2018-01-05T15:44:34)
            to_date (String):
                The final date and time (inclusive) from which the context
                information is queried. Must be in ISO8601 format (e.g.,
                2018-01-05T15:44:34)
            last_n (int):
                Used to request only the last N values that satisfy the
                request conditions.
            limit (int): Maximum number of results to be retrieved.
                Default value : 10000
            offset (int):
                Offset to apply to the response results.
            georel (String):
                It specifies a spatial relationship between matching entities
                and a reference shape (geometry). This parameter is used to
                perform geographical queries with the same semantics as in the
                FIWARE-NGSI v2 Specification. Full details can be found in the
                Geographical Queries section of the specification:
                https://fiware.github.io/specifications/ngsiv2/stable/.
            geometry (String):
                Required if georel is specified.  point, line, polygon, box
            coords (String):
                Optional but required if georel is specified. This parameter
                defines the reference shape (geometry) in terms of WGS 84
                coordinates and has the same semantics as in the
                FIWARE-NGSI v2 Specification, except we only accept coordinates
                in decimal degrees---e.g. 40.714,-74.006 is okay, but not
                40 42' 51'',74 0' 21''. Full details can be found in the
                Geographical Queries section of the specification:
                https://fiware.github.io/specifications/ngsiv2/stable/.
            options (String): Key value pair options.

        Returns:
            TimeSeries
        """
        url = urljoin(self.base_url, f'v2/entities/{entity_id}')
        res_q = self.__query_builder(url=url,
                                     attrs=attrs,
                                     options=options,
                                     entity_type=entity_type,
                                     aggr_method=aggr_method,
                                     aggr_period=aggr_period,
                                     from_date=from_date,
                                     to_date=to_date,
                                     last_n=last_n,
                                     limit=limit,
                                     offset=offset,
                                     georel=georel,
                                     geometry=geometry,
                                     coords=coords)
        # merge response chunks
        res = TimeSeries.model_validate(res_q.popleft())
        for item in res_q:
            res.extend(TimeSeries.model_validate(item))

        return res

    # /entities/{entityId}/value
    def get_entity_values_by_id(self,
                                entity_id: str,
                                *,
                                attrs: str = None,
                                entity_type: str = None,
                                aggr_method: Union[str, AggrMethod] = None,
                                aggr_period: Union[str, AggrPeriod] = None,
                                from_date: str = None,
                                to_date: str = None,
                                last_n: int = None,
                                limit: int = 10000,
                                offset: int = None,
                                georel: str = None,
                                geometry: str = None,
                                coords: str = None,
                                options: str = None
                                ) -> TimeSeries:
        """
        History of N attributes (values only) of a given entity instance
        For example, query the average pressure, temperature and humidity (
        values only, no metadata) of this
        month in the weather station WS1.

        Args:
            entity_id (String): Entity id is required.
            attrs (String): Comma-separated list of attribute names
            entity_type (String): Comma-separated list of entity types whose
                data are to be included in the response.
            aggr_method (String): The function to apply to the raw data
                filtered. count, sum, avg, min, max
            aggr_period (String): year, month, day, hour, minute, second
            from_date (String): Starting date and time inclusive.
            to_date (String): Final date and time inclusive.
            last_n (int): Request only the last N values.
            limit (int): Maximum number of results to be retrieved.
                Default value : 10000
            offset (int): Offset for the results.
            georel (String): Geographical pattern
            geometry (String): Required if georel is specified.  point, line,
                polygon, box
            coords (String): Required if georel is specified.
                e.g. 40.714,-74.006
            options (String): Key value pair options.

        Returns:
            Response Model
        """
        url = urljoin(self.base_url, f'v2/entities/{entity_id}/value')
        res_q = self.__query_builder(url=url,
                                     attrs=attrs,
                                     options=options,
                                     entity_type=entity_type,
                                     aggr_method=aggr_method,
                                     aggr_period=aggr_period,
                                     from_date=from_date,
                                     to_date=to_date,
                                     last_n=last_n,
                                     limit=limit,
                                     offset=offset,
                                     georel=georel,
                                     geometry=geometry,
                                     coords=coords)

        # merge response chunks
        res = TimeSeries(entityId=entity_id, **res_q.popleft())
        for item in res_q:
            res.extend(TimeSeries(entityId=entity_id, **item))

        return res

    # /entities/{entityId}/attrs/{attrName}
    def get_entity_attr_by_id(self,
                              entity_id: str,
                              attr_name: str,
                              *,
                              entity_type: str = None,
                              aggr_method: Union[str, AggrMethod] = None,
                              aggr_period: Union[str, AggrPeriod] = None,
                              from_date: str = None,
                              to_date: str = None,
                              last_n: int = None,
                              limit: int = 10000,
                              offset: int = None,
                              georel: str = None,
                              geometry: str = None,
                              coords: str = None,
                              options: str = None
                              ) -> TimeSeries:
        """
        History of an attribute of a given entity instance
        For example, query max water level of the central tank throughout the
        last year. Queries can get more
        sophisticated with the use of filters and query attributes.

        Args:
            entity_id (String): Entity id is required.
            attr_name (String): The attribute name is required.
            entity_type (String): Comma-separated list of entity types whose
                data are to be included in the response.
            aggr_method (String): The function to apply to the raw data
                filtered. count, sum, avg, min, max
            aggr_period (String): year, month, day, hour, minute, second
            from_date (String): Starting date and time inclusive.
            to_date (String): Final date and time inclusive.
            last_n (int): Request only the last N values.
            limit (int): Maximum number of results to be retrieved.
                Default value : 10000
            offset (int): Offset for the results.
            georel (String): Geographical pattern
            geometry (String): Required if georel is specified.  point, line,
                polygon, box
            coords (String): Required if georel is specified.
                e.g. 40.714,-74.006
            options (String): Key value pair options.

        Returns:
            Response Model
        """
        url = urljoin(self.base_url, f'v2/entities/{entity_id}/attrs'
                                     f'/{attr_name}')
        req_q = self.__query_builder(url=url,
                                     entity_id=entity_id,
                                     options=options,
                                     entity_type=entity_type,
                                     aggr_method=aggr_method,
                                     aggr_period=aggr_period,
                                     from_date=from_date,
                                     to_date=to_date,
                                     last_n=last_n,
                                     limit=limit,
                                     offset=offset,
                                     georel=georel,
                                     geometry=geometry,
                                     coords=coords)

        # merge response chunks
        first = req_q.popleft()
        res = TimeSeries(entityId=entity_id,
                         index=first.get('index'),
                         attributes=[AttributeValues(**first)])
        for item in req_q:
            res.extend(TimeSeries(entityId=entity_id,
                                  index=item.get('index'),
                                  attributes=[AttributeValues(**item)]))

        return res

    # /entities/{entityId}/attrs/{attrName}/value
    def get_entity_attr_values_by_id(self,
                                     entity_id: str,
                                     attr_name: str,
                                     *,
                                     entity_type: str = None,
                                     aggr_method: Union[str, AggrMethod] = None,
                                     aggr_period: Union[str, AggrPeriod] = None,
                                     from_date: str = None,
                                     to_date: str = None,
                                     last_n: int = None,
                                     limit: int = 10000,
                                     offset: int = None,
                                     georel: str = None,
                                     geometry: str = None,
                                     coords: str = None,
                                     options: str = None
                                     ) -> TimeSeries:
        """
        History of an attribute (values only) of a given entity instance
        Similar to the previous, but focusing on the values regardless of the
        metadata.

        Args:
            entity_id (String): Entity id is required.
            attr_name (String): The attribute name is required.
            entity_type (String): Comma-separated list of entity types whose
                data are to be included in the response.
            aggr_method (String): The function to apply to the raw data
                filtered. count, sum, avg, min, max
            aggr_period (String): year, month, day, hour, minute, second
            from_date (String): Starting date and time inclusive.
            to_date (String): Final date and time inclusive.
            last_n (int): Request only the last N values.
            limit (int): Maximum number of results to be retrieved.
                Default value : 10000
            offset (int): Offset for the results.
            georel (String): Geographical pattern
            geometry (String): Required if georel is specified.  point, line,
                polygon, box
            coords (String): Required if georel is specified.
                e.g. 40.714,-74.006
            options (String): Key value pair options.

        Returns:
            Response Model
        """
        url = urljoin(self.base_url, f'v2/entities/{entity_id}/attrs'
                                     f'/{attr_name}/value')
        res_q = self.__query_builder(url=url,
                                     options=options,
                                     entity_type=entity_type,
                                     aggr_method=aggr_method,
                                     aggr_period=aggr_period,
                                     from_date=from_date,
                                     to_date=to_date,
                                     last_n=last_n,
                                     limit=limit,
                                     offset=offset,
                                     georel=georel,
                                     geometry=geometry,
                                     coords=coords)
        # merge response chunks
        first = res_q.popleft()
        res = TimeSeries(
            entityId=entity_id,
            index=first.get('index'),
            attributes=[AttributeValues(attrName=attr_name,
                                        values=first.get('values'))])
        for item in res_q:
            res.extend(
                TimeSeries(
                    entityId=entity_id,
                    index=item.get('index'),
                    attributes=[AttributeValues(attrName=attr_name,
                                                values=item.get('values'))]))

        return res

    # /types/{entityType}
    def get_entity_by_type(self,
                           entity_type: str,
                           *,
                           attrs: str = None,
                           entity_id: str = None,
                           id_pattern: str = None,
                           aggr_method: Union[str, AggrMethod] = None,
                           aggr_period: Union[str, AggrPeriod] = None,
                           from_date: str = None,
                           to_date: str = None,
                           last_n: int = None,
                           limit: int = 10000,
                           offset: int = None,
                           georel: str = None,
                           geometry: str = None,
                           coords: str = None,
                           options: str = None,
                           aggr_scope: Union[str, AggrScope] = None
                           ) -> List[TimeSeries]:
        """
        History of N attributes of N entities of the same type.
        For example, query the average pressure, temperature and humidity of
        this month in all the weather stations.
        """
        url = urljoin(self.base_url, f'v2/types/{entity_type}')
        res_q = self.__query_builder(url=url,
                                     entity_id=entity_id,
                                     id_pattern=id_pattern,
                                     attrs=attrs,
                                     options=options,
                                     aggr_method=aggr_method,
                                     aggr_period=aggr_period,
                                     from_date=from_date,
                                     to_date=to_date,
                                     last_n=last_n,
                                     limit=limit,
                                     offset=offset,
                                     georel=georel,
                                     geometry=geometry,
                                     coords=coords,
                                     aggr_scope=aggr_scope)

        # merge chunks of response
        res = [TimeSeries(entityType=entity_type, **item)
               for item in res_q.popleft().get('entities')]

        for chunk in res_q:
            chunk = [TimeSeries(entityType=entity_type, **item)
                     for item in chunk.get('entities')]
            for new, old in zip(chunk, res):
                old.extend(new)

        return res

    # /types/{entityType}/value
    def get_entity_values_by_type(self,
                                  entity_type: str,
                                  *,
                                  attrs: str = None,
                                  entity_id: str = None,
                                  id_pattern: str = None,
                                  aggr_method: Union[str, AggrMethod] = None,
                                  aggr_period: Union[str, AggrPeriod] = None,
                                  from_date: str = None,
                                  to_date: str = None,
                                  last_n: int = None,
                                  limit: int = 10000,
                                  offset: int = None,
                                  georel: str = None,
                                  geometry: str = None,
                                  coords: str = None,
                                  options: str = None,
                                  aggr_scope: Union[str, AggrScope] = None
                                  ) -> List[TimeSeries]:
        """
        History of N attributes (values only) of N entities of the same type.
        For example, query the average pressure, temperature and humidity (
        values only, no metadata) of this month in
        all the weather stations.
        """
        url = urljoin(self.base_url, f'v2/types/{entity_type}/value')
        res_q = self.__query_builder(url=url,
                                     entity_id=entity_id,
                                     id_pattern=id_pattern,
                                     attrs=attrs,
                                     options=options,
                                     entity_type=entity_type,
                                     aggr_method=aggr_method,
                                     aggr_period=aggr_period,
                                     from_date=from_date,
                                     to_date=to_date,
                                     last_n=last_n,
                                     limit=limit,
                                     offset=offset,
                                     georel=georel,
                                     geometry=geometry,
                                     coords=coords,
                                     aggr_scope=aggr_scope)
        # merge chunks of response
        res = [TimeSeries(entityType=entity_type, **item)
               for item in res_q.popleft().get('values')]

        for chunk in res_q:
            chunk = [TimeSeries(entityType=entity_type, **item)
                     for item in chunk.get('values')]
            for new, old in zip(chunk, res):
                old.extend(new)

        return res

    # /types/{entityType}/attrs/{attrName}
    def get_entity_attr_by_type(self,
                                entity_type: str,
                                attr_name: str,
                                *,
                                entity_id: str = None,
                                id_pattern: str = None,
                                aggr_method: Union[str, AggrMethod] = None,
                                aggr_period: Union[str, AggrPeriod] = None,
                                from_date: str = None,
                                to_date: str = None,
                                last_n: int = None,
                                limit: int = 10000,
                                offset: int = None,
                                georel: str = None,
                                geometry: str = None,
                                coords: str = None,
                                options: str = None,
                                aggr_scope: Union[str, AggrScope] = None
                                ) -> List[TimeSeries]:
        """
        History of an attribute of N entities of the same type.
        For example, query the pressure measurements of this month in all the
        weather stations. Note in the response,
        the index and values arrays are parallel. Also, when using
        aggrMethod, the aggregation is done by-entity
        instance. In this case, the index array is just the fromDate and
        toDate values user specified in the request
        (if any).

        Args:
            entity_type (String): Entity type is required.
            attr_name (String): The attribute name is required.
            entity_id (String): Comma-separated list of entity ids whose data
                are to be included in the response.
            aggr_method (String): The function to apply to the raw data
                filtered. count, sum, avg, min, max
            aggr_period (String): year, month, day, hour, minute, second
            aggr_scope (str): Optional. (This parameter is not yet supported).
                When the query results cover historical data for multiple
                entities instances, you can define the aggregation method to be
                applied for each entity instance [entity] or across
                them [global]
            from_date (String): Starting date and time inclusive.
            to_date (String): Final date and time inclusive.
            last_n (int): Request only the last N values.
            limit (int): Maximum number of results to be retrieved.
                Default value : 10000
            offset (int): Offset for the results.
            georel (String): Geographical pattern
            geometry (String): Required if georel is specified.  point, line,
                polygon, box
            coords (String): Required if georel is specified.
                e.g. 40.714,-74.006
            options (String): Key value pair options.

        Returns:
            Response Model
        """
        url = urljoin(self.base_url, f'v2/types/{entity_type}/attrs'
                                     f'/{attr_name}')
        res_q = self.__query_builder(url=url,
                                     entity_id=entity_id,
                                     id_pattern=id_pattern,
                                     options=options,
                                     entity_type=entity_type,
                                     aggr_method=aggr_method,
                                     aggr_period=aggr_period,
                                     from_date=from_date,
                                     to_date=to_date,
                                     last_n=last_n,
                                     limit=limit,
                                     offset=offset,
                                     georel=georel,
                                     geometry=geometry,
                                     coords=coords,
                                     aggr_scope=aggr_scope)

        # merge chunks of response
        first = res_q.popleft()
        res = [TimeSeries(index=item.get('index'),
                          entityType=entity_type,
                          entityId=item.get('entityId'),
                          attributes=[
                              AttributeValues(
                                  attrName=first.get('attrName'),
                                  values=item.get('values'))])
               for item in first.get('entities')]

        for chunk in res_q:
            chunk = [TimeSeries(index=item.get('index'),
                                entityType=entity_type,
                                entityId=item.get('entityId'),
                                attributes=[
                                    AttributeValues(
                                        attrName=chunk.get('attrName'),
                                        values=item.get('values'))])
                     for item in chunk.get('entities')]
            for new, old in zip(chunk, res):
                old.extend(new)

        return res

    # /types/{entityType}/attrs/{attrName}/value
    def get_entity_attr_values_by_type(self,
                                       entity_type: str,
                                       attr_name: str,
                                       *,
                                       entity_id: str = None,
                                       id_pattern: str = None,
                                       aggr_method: Union[
                                           str, AggrMethod] = None,
                                       aggr_period: Union[
                                           str, AggrPeriod] = None,
                                       from_date: str = None,
                                       to_date: str = None,
                                       last_n: int = None,
                                       limit: int = 10000,
                                       offset: int = None,
                                       georel: str = None,
                                       geometry: str = None,
                                       coords: str = None,
                                       options: str = None,
                                       aggr_scope: Union[str, AggrScope] = None
                                       ) -> List[TimeSeries]:
        """
        History of an attribute (values only) of N entities of the same type.
        For example, query the average pressure (values only, no metadata) of
        this month in all the weather stations.

        Args:
            aggr_scope:
            entity_type (String): Entity type is required.
            attr_name (String): The attribute name is required.
            entity_id (String): Comma-separated list of entity ids whose data
                are to be included in the response.
            aggr_method (String): The function to apply to the raw data
                filtered. count, sum, avg, min, max
            aggr_period (String): year, month, day, hour, minute, second
            aggr_scope (String):
            from_date (String): Starting date and time inclusive.
            to_date (String): Final date and time inclusive.
            last_n (int): Request only the last N values.
            limit (int): Maximum number of results to be retrieved.
                Default value : 10000
            offset (int): Offset for the results.
            georel (String): Geographical pattern
            geometry (String): Required if georel is specified.  point, line,
                polygon, box
            coords (String): Required if georel is specified.
                e.g. 40.714,-74.006
            options (String): Key value pair options.

        Returns:
            Response Model
        """
        url = urljoin(self.base_url, f'v2/types/{entity_type}/attrs/'
                                     f'{attr_name}/value')
        res_q = self.__query_builder(url=url,
                                     entity_id=entity_id,
                                     id_pattern=id_pattern,
                                     options=options,
                                     entity_type=entity_type,
                                     aggr_method=aggr_method,
                                     aggr_period=aggr_period,
                                     from_date=from_date,
                                     to_date=to_date,
                                     last_n=last_n,
                                     limit=limit,
                                     offset=offset,
                                     georel=georel,
                                     geometry=geometry,
                                     coords=coords,
                                     aggr_scope=aggr_scope)

        # merge chunks of response
        res = [TimeSeries(index=item.get('index'),
                          entityType=entity_type,
                          entityId=item.get('entityId'),
                          attributes=[
                              AttributeValues(attrName=attr_name,
                                              values=item.get('values'))])
               for item in res_q.popleft().get('values')]

        for chunk in res_q:
            chunk = [TimeSeries(index=item.get('index'),
                                entityType=entity_type,
                                entityId=item.get('entityId'),
                                attributes=[
                                    AttributeValues(attrName=attr_name,
                                                    values=item.get('values'))])
                     for item in chunk.get('values')]

            for new, old in zip(chunk, res):
                old.extend(new)
        return res

    # v2/attrs
    def get_entity_by_attrs(self, *,
                            entity_type: str = None,
                            from_date: str = None,
                            to_date: str = None,
                            limit: int = 10000,
                            offset: int = None
                            ) -> List[TimeSeries]:
        """
        Get list of timeseries data grouped by each existing attribute name.
        The timeseries data include all entities corresponding to each
        attribute name as well as the index and values of this attribute in
        this entity.

        Args:
            entity_type (str): Comma-separated list of entity types whose data
                are to be included in the response. Use only one (no comma)
                when required. If used to resolve ambiguity for the given
                entityId, make sure the given entityId exists for this
                entityType.
            from_date (str): The starting date and time (inclusive) from which
                the context information is queried. Must be in ISO8601 format
                (e.g., 2018-01-05T15:44:34)
            to_date (str): The final date and time (inclusive) from which the
                context information is queried. Must be in ISO8601 format
                (e.g., 2018-01-05T15:44:34).
            limit (int): Maximum number of results to be retrieved.
                Default value : 10000
            offset (int): Offset for the results.
        
        Returns:
            List of TimeSeriesEntities
        """
        url = urljoin(self.base_url, 'v2/attrs')
        res_q = self.__query_builder(url=url,
                                   entity_type=entity_type,
                                   from_date=from_date,
                                   to_date=to_date,
                                   limit=limit,
                                   offset=offset)
        first = res_q.popleft()
        
        res = chain.from_iterable(map(lambda x: self.transform_attr_response_model(x), 
                          first.get("attrs")))
        for chunk in res_q:
            chunk = chain.from_iterable(map(lambda x: self.transform_attr_response_model(x), 
                                        chunk.get("attrs")))
            
            for new, old in zip(chunk, res):
                old.extend(new)
        
        return list(res)

    # v2/attrs/{attr_name}
    def get_entity_by_attr_name(self, *,
                                attr_name: str,
                                entity_type: str = None,
                                from_date: str = None,
                                to_date: str = None,
                                limit: int = 10000,
                                offset: int = None
                                ) -> List[TimeSeries]:
        """
        Get list of all entities containing this attribute name, as well as
        getting the index and values of this attribute in every corresponding
        entity.

        Args:
            attr_name (str): The attribute name in interest.
            entity_type (str): Comma-separated list of entity types whose data
                are to be included in the response. Use only one (no comma)
                when required. If used to resolve ambiguity for the given
                entityId, make sure the given entityId exists for this
                entityType.
            from_date (str): The starting date and time (inclusive) from which
                the context information is queried. Must be in ISO8601 format
                (e.g., 2018-01-05T15:44:34)
            to_date (str): The final date and time (inclusive) from which the
                context information is queried. Must be in ISO8601 format
                (e.g., 2018-01-05T15:44:34).
            limit (int): Maximum number of results to be retrieved.
                Default value : 10000
            offset (int): Offset for the results.

        Returns:
            List of TimeSeries
        """
        url = urljoin(self.base_url, f'/v2/attrs/{attr_name}')
        res_q = self.__query_builder(url=url,
                                     entity_type=entity_type,
                                     from_date=from_date,
                                     to_date=to_date,
                                     limit=limit,
                                     offset=offset)

        first = res_q.popleft()
        res = self.transform_attr_response_model(first)

        for chunk in res_q:
            chunk = self.transform_attr_response_model(chunk)
            for new, old in zip(chunk, res):
                old.extend(new)
        return list(res)

    def transform_attr_response_model(self, attr_response):
        res = []
        attr_name = attr_response.get("attrName")
        for entity_group in attr_response.get("types"):
            timeseries = map(lambda entity: 
                             TimeSeries(entityId=entity.get("entityId"),
                                        entityType=entity_group.get("entityType"),
                                        index=entity.get("index"),
                                        attributes=[
                                             AttributeValues(attrName=attr_name,
                                                             values=entity.get("values"))]
                                        ),
                             entity_group.get("entities"))
            res.append(timeseries)
        return chain.from_iterable(res)
