"""
TimeSeries Module for QuantumLeap API Client
"""
import logging
from typing import Dict, List, Union
from urllib.parse import urljoin
import requests
from pydantic import parse_obj_as
from filip.core import settings
from filip.core.base_client import BaseClient
from filip.core.models import FiwareHeader
from filip.timeseries.models import \
    AggrPeriod, \
    AggrMethod, \
    AggrScope, \
    AttributeValues, \
    NotificationMessage, \
    TimeSeries, \
    TimeSeriesEntity


logger = logging.getLogger(__name__)


class QuantumLeapClient(BaseClient):
    """
    Implements functions to use the FIWAREs QuantumLeap, which subscribes to an
    Orion Context Broker and stores the subscription data in a timeseries
    database (CrateDB). Further Information:
    https://smartsdk.github.io/ngsi-timeseries-api/#quantumleap
    https://app.swaggerhub.com/apis/heikkilv/quantumleap-api/
    """
    def __init__(self,
                 *,
                 url: str = None,
                 session: requests.Session = None,
                 fiware_header: FiwareHeader = None):
        url = url or settings.QL_URL
        super().__init__(url=url,
                         session=session,
                         fiware_header=fiware_header)

    # META API ENDPOINTS
    def get_version(self) -> Dict:
        """
        Returns the version of QuantumLeap.
        Returns:
            Dictionary with response
        """
        url = urljoin(self.base_url, '/version')
        try:
            res = self.session.get(url=url)
            if res.ok:
                return res.json()
            res.raise_for_status()
        except requests.exceptions.RequestException as err:
            self.logger.error(err)
            raise

    def get_health(self):
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
        url = urljoin(self.base_url, '/health')
        try:
            res = self.session.get(url=url)
            if res.ok:
                return res.json()
            res.raise_for_status()
        except requests.exceptions.RequestException as err:
            self.logger.error(err)
            raise

    def post_config(self):
        """
        (To Be Implemented) Customize your persistence configuration to
        better suit your needs."""
        raise NotImplementedError("Endpoint to be implemented..")

    # INPUT API ENDPOINTS
    def post_notification(self, notification: NotificationMessage):
        """
        Notify QuantumLeap the arrival of a new NGSI notification.
        Args:
            notification (NotificationMessage): Notification Message Object
        """
        url = urljoin(self.base_url, '/v2/notify')
        headers = self.headers.copy()
        data = []
        for entity in notification.data:
            data.append(entity.dict(exclude_unset=True,
                                    exclude_defaults=True,
                                    exclude_none=True))
        data_set = {
            "data": data,
            "subscriptionId": notification.subscriptionId
        }

        try:
            res = self.session.post(
                url=url,
                headers=headers,
                json=data_set)
            if res.ok:
                self.logger.info(res.text)
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as err:
            msg = f"Could not post notification for subscription id " \
                  f"{notification.subscriptionId}"
            self.log_error(err=err, msg=msg)
            raise

    def post_subscription(self,
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
        at your will.
        This endpoint just aims to simplify the common use case.
        Args:
            entity_type (String): The type of entities for which to create a
                subscription, so as to persist historical data of entities of
                this type.
            entity_id (String): Id of the entity to track. If specified, it
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
        headers = self.headers.copy()
        params = {}
        url = urljoin(self.base_url, '/v2/subscribe')
        orion_url = urljoin(settings.CB_URL, '/v2')
        ql_url = urljoin(self.base_url, '/v2')
        params.update({'orionUrl': orion_url.encode('utf-8')})
        params.update({'quantumleapUrl': ql_url.encode('utf-8')})
        if entity_type:
            params.update({'entityType': entity_type})
        if entity_id:
            params.update({'entityId': entity_id})
        if id_pattern:
            params.update({'idPattern': id_pattern})
        if attributes:
            params.update({'attributes': attributes})
        if observed_attributes:
            params.update({'observedAttributes': observed_attributes})
        if notified_attributes:
            params.update({'notifiedAttributes': notified_attributes})
        if throttling:
            if throttling < 1:
                raise TypeError("Throttling must be a positive integer")
            params.update({'throttling': throttling})
        if time_index_attribute:
            params.update({'timeIndexAttribute': time_index_attribute})

        try:
            res = self.session.post(
                url=url,
                headers=headers,
                params=params)
            if res.ok:
                msg = "Subscription created successfully!"
                self.logger.info(msg)
                return msg
            res.raise_for_status()
        except requests.exceptions.RequestException as err:
            msg = "Could not create subscription."
            self.log_error(err=err, msg=msg)
            raise

    def delete_entity(self, entity_id: str, entity_type: str) -> str:
        """
        Given an entity (with type and id), delete all its historical records.
        Args:
            entity_id (String): Entity id is required.
            entity_type (String): Entity type if entity_id alone can not
                uniquely
            define the entity.
        Returns:
            The entity_id of entity that is deleted.
        """
        url = urljoin(self.base_url, f'/v2/entities/{entity_id}')
        headers = self.headers.copy()
        if entity_type:
            params = {'type': entity_type}
        else:
            params = {}
        try:
            res = self.session.delete(url=url, headers=headers, params=params)
            if res.ok:
                self.logger.info("Entity id '%s' successfully deleted!",
                                 entity_id)
                return entity_id
            res.raise_for_status()
        except requests.exceptions.RequestException as err:
            msg = f"Could not delete entity of id {entity_id}"
            self.log_error(err=err, msg=msg)
            raise

    def delete_entity_type(self, entity_type: str) -> str:
        """
        Given an entity type, delete all the historical records of all
        entities of such type.
        Args:
            entity_type (String): Type of entities data to be deleted.
        Returns:
            Entity type of the entities deleted.
        """
        url = urljoin(self.base_url, f'/v2/types/{entity_type}')
        headers = self.headers.copy()
        try:
            res = self.session.delete(url=url, headers=headers)
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
    def __get_entity_data(self,
                          url,
                          *,
                          entity_id: str = None,
                          attr_name: str = None,
                          values_only: bool = False,
                          options: str = None,
                          entity_type: str = None,
                          aggr_method: Union[str, AggrMethod] = None,
                          aggr_period: Union[str, AggrPeriod] = None,
                          from_date: str = None,
                          to_date: str = None,
                          last_n: int = None,
                          limit: int = None,
                          offset: int = None,
                          georel: str = None,
                          geometry: str = None,
                          coords: str = None,
                          by_type: bool = False,
                          attrs: str = None,
                          aggr_scope: Union[str, AggrScope] = None
                          ) -> Dict:
        """
        Private Function to call respective API endpoints
        """
        #if by_type:
        #    url = urljoin(self.base_url, f'/v2/types/{entity_type}')
        #else:
        #    url = urljoin(self.base_url, f'/v2/entities/{entity_id}')
#
        #if attr_name:
        #    url = urljoin(url, f'/attrs/{attr_name}')
        #if values_only:
        #    url = urljoin(url, '/value')
        params = {}
        if options:
            params.update({'options': options})
        if entity_type and not by_type:
            params.update({'entity_type': entity_type})
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
        if last_n:
            params.update({'lastN': last_n})
        if limit:
            params.update({'limit': limit})
        if offset:
            params.update({'offset': offset})
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
        if entity_id and by_type:
            params.update({'id': entity_id})
        try:
            res = self.session.get(url=url, params=params)
            if res.ok:
                self.logger.info("Successfully received entity data")
                self.logger.debug('Received: %s', res.json())
                return res.json()
            res.raise_for_status()
        except requests.exceptions.RequestException as err:
            msg = "Could not load entity data"
            self.log_error(err=err, msg=msg)
            raise

    # v2/entities
    def get_entities(self, *,
                     entity_type: str = None,
                     from_date: str = None,
                     to_date: str = None,
                     limit: int = None,
                     offset: int = None
                     ) -> List[TimeSeriesEntity]:
        """
        Get list of all available entities and their context information
        about EntityType and last update date.
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
            List of TimeSeriesEntity
        """
        url = urljoin(self.base_url, 'v2/entities')
        res = self.__get_entity_data(url=url,
                                     entity_type=entity_type,
                                     from_date=from_date,
                                     to_date=to_date,
                                     limit=limit,
                                     offset=offset)
        return parse_obj_as(List[TimeSeriesEntity], res)


    # /entities/{entityId}
    def get_entity_attrs_by_id(self,
                               entity_id: str,
                               *,
                               attrs: str = None,
                               entity_type: str = None,
                               aggr_method: Union[str, AggrMethod] = None,
                               aggr_period: Union[str, AggrPeriod] = None,
                               from_date: str = None,
                               to_date: str = None,
                               last_n: int = None,
                               limit: int = None,
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
            TimeSeries
        """
        res = self.__get_entity_data(entity_id=entity_id,
                                     attrs=attrs,
                                     values_only=False,
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
                                     by_type=False)
        return TimeSeries.parse_obj(res)

    # /entities/{entityId}/value
    def get_entity_attrs_values_by_id(self, *,
                                      entity_id: str,
                                      attrs: str = None,
                                      entity_type: str = None,
                                      aggr_method: Union[
                                          str, AggrMethod] = None,
                                      aggr_period: Union[
                                          str, AggrPeriod] = None,
                                      from_date: str = None,
                                      to_date: str = None,
                                      last_n: int = None,
                                      limit: int = None,
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
        res = self.__get_entity_data(entity_id=entity_id,
                                     attrs=attrs,
                                     values_only=True,
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
                                     by_type=False)
        return TimeSeries(entityId=entity_id,
                          **res)

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
                              limit: int = None,
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

        res = self.__get_entity_data(entity_id=entity_id,
                                     attr_name=attr_name,
                                     values_only=False,
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
                                     by_type=False)
        return TimeSeries(entityId=entity_id,
                          index=res.get('index'),
                          attributes=[AttributeValues(**res)])

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
                                     limit: int = None,
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

        res = self.__get_entity_data(entity_id=entity_id,
                                     attr_name=attr_name,
                                     values_only=True,
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
                                     by_type=False)
        return TimeSeries(entityId=entity_id,
                          index=res.get('index'),
                          attributes=[AttributeValues(attrName=attr_name,
                                                      values=res.get(
                                                          'values'))])

    # /types/{entityType}
    def get_entity_by_type(self,
                           entity_type: str,
                           *,
                           attrs: str = None,
                           entity_id: str = None,
                           aggr_method: Union[str, AggrMethod] = None,
                           aggr_period: Union[str, AggrPeriod] = None,
                           from_date: str = None,
                           to_date: str = None,
                           last_n: int = None,
                           limit: int = None,
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
        res = self.__get_entity_data(entity_id=entity_id,
                                     attrs=attrs,
                                     values_only=False,
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
                                     by_type=True,
                                     aggr_scope=aggr_scope)
        return [TimeSeries(entityType=entity_type, **item)
                for item in res.get('entities')]

    # /types/{entityType}/value
    def get_entity_values_by_type(self,
                                  entity_type: str,
                                  *,
                                  attrs: str = None,
                                  entity_id: str = None,
                                  aggr_method: Union[str, AggrMethod] = None,
                                  aggr_period: Union[str, AggrPeriod] = None,
                                  from_date: str = None,
                                  to_date: str = None,
                                  last_n: int = None,
                                  limit: int = None,
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
        res = self.__get_entity_data(entity_id=entity_id,
                                     attrs=attrs,
                                     values_only=False,
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
                                     by_type=True,
                                     aggr_scope=aggr_scope)
        return [TimeSeries(entityType=entity_type, **item)
                for item in res.get('values')]

    # /types/{entityType}/attrs/{attrName}
    def get_entity_attr_by_type(self,
                                entity_type: str,
                                attr_name: str,
                                *,
                                entity_id: str = None,
                                aggr_method: Union[str, AggrMethod] = None,
                                aggr_period: Union[str, AggrPeriod] = None,
                                from_date: str = None,
                                to_date: str = None,
                                last_n: int = None,
                                limit: int = None,
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
        res = self.__get_entity_data(entity_id=entity_id,
                                     attr_name=attr_name,
                                     values_only=False,
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
                                     by_type=True,
                                     aggr_scope=aggr_scope)
        return [TimeSeries(entityType=entity_type,
                           entityId=item.get('entityId'),
                           attributes=[
                               AttributeValues(attrName=res.get('attrName'),
                                               values=item.get('values'))])
                for item in res.get('entities')]

    # /types/{entityType}/attrs/{attrName}/value
    def get_entity_attr_values_by_type(self,
                                       entity_type: str,
                                       attr_name: str,
                                       *,
                                       entity_id: str = None,
                                       aggr_method: Union[
                                           str, AggrMethod] = None,
                                       aggr_period: Union[
                                           str, AggrPeriod] = None,
                                       from_date: str = None,
                                       to_date: str = None,
                                       last_n: int = None,
                                       limit: int = None,
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
        res = self.__get_entity_data(entity_id=entity_id,
                                     attr_name=attr_name,
                                     values_only=True,
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
                                     by_type=True,
                                     aggr_scope=aggr_scope)
        return [TimeSeries(entityType=entity_type,
                           entityId=item.get('entityId'),
                           attributes=[
                               AttributeValues(attrName=attr_name,
                                               values=item.get('values'))])
                for item in res.get('entities')]
