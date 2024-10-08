"""
IoT-Agent Module for API Client
"""
from __future__ import annotations

import json
from copy import deepcopy
from typing import List, Dict, Set, TYPE_CHECKING, Union, Optional
import warnings
from urllib.parse import urljoin
import requests
from pydantic import AnyHttpUrl
from pydantic.type_adapter import TypeAdapter
from filip.config import settings
from filip.clients.base_http_client import BaseHttpClient
from filip.models.base import FiwareHeader
from filip.models.ngsi_v2.iot import Device, ServiceGroup

from filip.utils.filter import filter_device_list, filter_group_list

if TYPE_CHECKING:
    from filip.clients.ngsi_v2.cb import ContextBrokerClient


class IoTAClient(BaseHttpClient):
    """
    Client for FIWARE IoT-Agents. The implementation follows the API
    specifications from here:
    https://iotagent-node-lib.readthedocs.io/en/latest/

    Args:
        url: Url of IoT-Agent
        session (requests.Session):
        fiware_header (FiwareHeader): fiware service and fiware service path
        **kwargs (Optional): Optional arguments that ``request`` takes.
    """

    def __init__(self,
                 url: str = None,
                 *,
                 session: requests.Session = None,
                 fiware_header: FiwareHeader = None,
                 **kwargs):
        # set service url
        url = url or settings.IOTA_URL
        super().__init__(url=url,
                         session=session,
                         fiware_header=fiware_header,
                         **kwargs)

    # ABOUT API
    def get_version(self) -> Dict:
        """
        Gets version of IoT Agent

        Returns:
            Dictionary with response
        """
        url = urljoin(self.base_url, 'iot/about')
        try:
            res = self.get(url=url, headers=self.headers)
            if res.ok:
                return res.json()
            res.raise_for_status()
        except requests.RequestException as err:
            self.logger.error(err)
        raise

    # SERVICE GROUP API
    def post_groups(self,
                    service_groups: Union[ServiceGroup, List[ServiceGroup]],
                    update: bool = False):
        """
        Creates a set of service groups for the given service and service_path.
        The service_group and subservice information will taken from the
        headers, overwriting any preexisting values.

        Args:
            service_groups (list of ServiceGroup): Service groups that will be
            posted to the agent's API
            update (bool): If service group already exists try to update its

        Returns:
            None
        """
        if not isinstance(service_groups, list):
            service_groups = [service_groups]
        for group in service_groups:
            if group.service:
                assert group.service == self.headers['fiware-service'], \
                    "Service group service does not math fiware service"
            if group.subservice:
                assert group.subservice == self.headers['fiware-servicepath'], \
                    "Service group subservice does not math fiware service path"

        url = urljoin(self.base_url, 'iot/services')
        headers = self.headers
        data = {'services': [group.model_dump(exclude={'service', 'subservice'},
                                              exclude_none=True)
                             for group in service_groups]}
        try:
            res = self.post(url=url, headers=headers, json=data)
            if res.ok:
                self.logger.info("Services successfully posted")
            elif res.status_code == 409:
                self.logger.warning(res.text)
                if len(service_groups) > 1:
                    self.logger.info("Trying to split bulk operation into "
                                     "single operations")
                    for group in service_groups:
                        self.post_group(service_group=group, update=update)
                elif update is True:
                    self.update_group(service_group=service_groups[0],
                                      fields=None)
                else:
                    res.raise_for_status()
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            self.log_error(err=err, msg=None)
            raise

    def post_group(self, service_group: ServiceGroup, update: bool = False):
        """
        Single service registration but using the bulk operation in background

        Args:
            service_group (ServiceGroup): Service that will be posted to the
            agent's API
            update (bool):

        Returns:
            None
        """
        return self.post_groups(service_groups=[service_group],
                                update=update)

    def get_group_list(self) -> List[ServiceGroup]:
        r"""
        Retrieves service_group groups from the database. If the servicepath
        header has the wildcard expression, /\*, all the subservices for the
        service_group are returned. The specific subservice parameters are
        returned in any other case.

        Returns:

        """
        url = urljoin(self.base_url, 'iot/services')
        headers = self.headers
        try:
            res = self.get(url=url, headers=headers)
            if res.ok:
                ta = TypeAdapter(List[ServiceGroup])
                return ta.validate_python(res.json()['services'])
            res.raise_for_status()
        except requests.RequestException as err:
            self.log_error(err=err, msg=None)
            raise

    def get_group(self, *, resource: str, apikey: str) -> ServiceGroup:
        """
        Retrieves service_group groups from the database based on resource and
        apikey
        Args:
            resource:
            apikey:
        Returns:

        """
        groups = self.get_group_list()
        groups = filter_group_list(group_list=groups, resources=resource, apikeys=apikey)
        if len(groups) == 1:
            group = groups[0]
            return group
        elif len(groups) == 0:
            raise KeyError(f"Service group with resource={resource} and apikey={apikey} was not found")
        else:
            raise NotImplementedError("There is a wierd error, try get_group_list() for debugging")

    def update_groups(self, *,
                      service_groups: Union[ServiceGroup, List[ServiceGroup]],
                      add: False,
                      fields: Union[Set[str], List[str]] = None) -> None:
        """
        Bulk operation for service group update.
        Args:
            fields:
            service_groups:
            add:

        Returns:

        """
        if not isinstance(service_groups, list):
            service_groups = [service_groups]
        for group in service_groups:
            self.update_group(service_group=group, fields=fields, add=add)

    def update_group(self, *, service_group: ServiceGroup,
                     fields: Union[Set[str], List[str]] = None,
                     add: bool = True):
        """
        Modifies the information for a service group configuration, identified
        by the resource and apikey query parameters. Takes a service group body
        as the payload. The body does not have to be complete: for incomplete
        bodies, just the existing attributes will be updated
        
        Args:
            service_group (ServiceGroup): Service to update.
            fields: Fields of the service_group to update. If 'None' all allowed
            fields will be updated
            add:
        Returns:
            None
        """
        if fields:
            if isinstance(fields, list):
                fields = set(fields)
        else:
            fields = None
        url = urljoin(self.base_url, 'iot/services')
        headers = self.headers
        params = service_group.model_dump(include={'resource', 'apikey'})
        try:
            res = self.put(url=url,
                           headers=headers,
                           params=params,
                           json=service_group.model_dump(
                               include=fields,
                               exclude={'service', 'subservice'},
                               exclude_none=True))
            if res.ok:
                self.logger.info("ServiceGroup updated!")
            elif (res.status_code == 404) & (add is True):
                self.post_group(service_group=service_group)
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            self.log_error(err=err, msg=None)
            raise

    def delete_group(self, *, resource: str, apikey: str):
        """
        Deletes a service group in in the IoT-Agent
        
        Args:
            resource:
            apikey:

        Returns:

        """
        url = urljoin(self.base_url, 'iot/services')
        headers = self.headers
        params = {'resource': resource,
                  'apikey': apikey}
        try:
            res = self.delete(url=url, headers=headers, params=params)
            if res.ok:
                self.logger.info("ServiceGroup with resource: '%s' and "
                                 "apikey: '%s' successfully deleted!",
                                 resource, apikey)
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not delete ServiceGroup with resource " \
                  f"'{resource}' and apikey '{apikey}'!"
            self.log_error(err=err, msg=msg)
            raise

    # DEVICE API
    def post_devices(self, *, devices: Union[Device, List[Device]],
                     update: bool = False) -> None:
        """
        Post a device from the device registry. No payload is required
        or received.
        If a device already exists in can be updated with update = True
        Args:
            devices (list of Devices):
            update (bool):  Whether if the device is already existent it
            should be updated
        Returns:
            None
        """
        if not isinstance(devices, list):
            devices = [devices]
        url = urljoin(self.base_url, 'iot/devices')
        headers = self.headers
        
        data = {"devices": [json.loads(device.model_dump_json(exclude_none=True)
                                       ) for device in devices]}
        try:
            res = self.post(url=url, headers=headers, json=data)
            if res.ok:
                self.logger.info("Devices successfully posted!")
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            if update:
                return self.update_devices(devices=devices, add=False)
            msg = "Could not post devices"
            self.log_error(err=err, msg=msg)
            raise

    def post_device(self, *, device: Device, update: bool = False) -> None:
        """
        Post a device configuration to the IoT-Agent
        
        Args:
            device: IoT device configuration to send
            update: update device if configuration already exists

        Returns:
            None
        """
        return self.post_devices(devices=[device], update=update)

    def get_device_list(self, *,
                        limit: int = None,
                        offset: int = None,
                        device_ids: Union[str, List[str]] = None,
                        entity_names: Union[str, List[str]] = None,
                        entity_types: Union[str, List[str]] = None) -> List[Device]:
        """
        Returns a list of all the devices in the device registry with all
        its data. The IoTAgent now only supports "limit" and "offset" as
        request parameters.

        Args:
            limit:
                if present, limits the number of devices returned in the
                list. Must be a number between 1 and 1000.
            offset:
                if present, skip that number of devices from the original
                query.
            device_ids:
                List of device_ids. If given, only devices with matching ids
                will be returned
            entity_names:
                The entity_ids of the devices. If given, only the devices
                with the specified entity_id will be returned
            entity_types:
                The entity_type of the device. If given, only the devices
                with the specified entity_type will be returned

        Returns:
            List of matching devices
        """
        if limit:
            if not 1 < limit < 1000:
                self.logger.error("'limit' must be an integer between 1 and "
                                  "1000!")
                raise ValueError
        url = urljoin(self.base_url, 'iot/devices')
        headers = self.headers
        params = {key: value for key, value in locals().items() if value is not
                  None}
        try:
            res = self.get(url=url, headers=headers, params=params)
            if res.ok:
                ta = TypeAdapter(List[Device])
                devices = ta.validate_python(res.json()['devices'])
                # filter by device_ids, entity_names or entity_types
                devices = filter_device_list(devices,
                                             device_ids,
                                             entity_names,
                                             entity_types)
                return devices
            res.raise_for_status()
        except requests.RequestException as err:
            self.log_error(err=err, msg=None)
            raise

    def get_device(self, *, device_id: str) -> Device:
        """
        Returns all the information about a particular device.
        
        Args:
            device_id:
        Raises:
            requests.RequestException, if device does not exist
        Returns:
            Device

        """
        url = urljoin(self.base_url, f'iot/devices/{device_id}')
        headers = self.headers
        try:
            res = self.get(url=url, headers=headers)
            if res.ok:
                return Device.model_validate(res.json())
            res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Device {device_id} was not found"
            self.log_error(err=err, msg=msg)
            raise

    def update_device(self, *, device: Device, add: bool = True) -> None:
        """
        Updates a device from the device registry.
        Adds, removes attributes from the device entry and changes
        attributes values.
        It does not change device settings (endpoint,..) and only adds
        attributes to the corresponding entity, their it does not
        change any attribute value and does not delete removed attributes

        Args:
            device:
            add (bool): If device not found add it
        Returns:
            None
        """
        url = urljoin(self.base_url, f'iot/devices/{device.device_id}')
        headers = self.headers
        try:
            res = self.put(url=url, headers=headers, json=device.model_dump(
                include={'attributes', 'lazy', 'commands', 'static_attributes'},
                exclude_none=True))
            if res.ok:
                self.logger.info("Device '%s' successfully updated!",
                                 device.device_id)
            elif (res.status_code == 404) & (add is True):
                self.post_device(device=device, update=False)
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not update device '{device.device_id}'"
            self.log_error(err=err, msg=msg)
            raise

    def update_devices(self, *, devices: Union[Device, List[Device]],
                       add: False) -> None:
        """
        Bulk operation for device update.
        Args:
            devices:
            add:

        Returns:

        """
        if not isinstance(devices, list):
            devices = [devices]
        for device in devices:
            self.update_device(device=device, add=add)

    def delete_device(self, *, device_id: str,
                      cb_url: AnyHttpUrl = settings.CB_URL,
                      delete_entity: bool = False,
                      force_entity_deletion: bool = False,
                      cb_client: ContextBrokerClient = None,
                      ) -> None:
        """
        Remove a device from the device registry. No payload is required
        or received.
        
        Args:
            device_id: str, ID of Device
            delete_entity:  False -> Only delete the device entry,
                                     the automatically created and linked
                                     context-entity will continue to
                                     exist in Fiware
                            True -> Also delete the automatically
                                    created and linked context-entity
                                    If multiple devices are linked to this
                                    entity, this operation is not executed and
                                    an exception is raised
            force_entity_deletion:
                bool, if delete_entity is true and multiple devices are linked
                to the linked entity, delete it and do not raise an error
            cb_client (ContextBrokerClient):
                Corresponding ContextBrokerClient object for entity manipulation
            cb_url (AnyHttpUrl):
                Url of the ContextBroker where the entity is found.
                This will autogenerate an CB-Client, mirroring the information
                of the IoTA-Client, e.g. FiwareHeader, and other headers
                (not recommended!)

        Returns:
            None
        """
        url = urljoin(self.base_url, f'iot/devices/{device_id}', )
        headers = self.headers

        device = self.get_device(device_id=device_id)

        try:
            res = self.delete(url=url, headers=headers)
            if res.ok:
                self.logger.info("Device '%s' successfully deleted!", device_id)
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            msg = f"Could not delete device {device_id}!"
            self.log_error(err=err, msg=msg)
            raise

        if delete_entity:
            # An entity can technically belong to multiple devices
            # Only delete the entity if
            devices = self.get_device_list(entity_names=[device.entity_name])

            # Zero because we count the remaining devices
            if len(devices) > 0 and not force_entity_deletion:
                raise Exception(f"The corresponding entity to the device "
                                f"{device_id} was not deleted because it is "
                                f"linked to multiple devices. ")
            else:
                try:
                    from filip.clients.ngsi_v2 import ContextBrokerClient

                    if cb_client:
                        cb_client_local = deepcopy(cb_client)
                    else:
                        warnings.warn("No `ContextBrokerClient` "
                                      "object providesd! Will try to generate "
                                      "one. This usage is not recommended.")

                        cb_client_local = ContextBrokerClient(
                            url=cb_url,
                            fiware_header=self.fiware_headers,
                            headers=headers)

                    cb_client_local.delete_entity(
                        entity_id=device.entity_name,
                        entity_type=device.entity_type)

                except requests.RequestException as err:
                    # Do not throw an error
                    # It is only important that the entity does not exist after
                    # this methode, not if this methode actively deleted it
                    pass

                cb_client_local.close()

    def patch_device(self,
                     device: Device,
                     patch_entity: bool = True,
                     cb_client: ContextBrokerClient = None,
                     cb_url: AnyHttpUrl = settings.CB_URL) -> None:
        """
        Updates a device state in Fiware, if the device does not exists it
        is created, else its values are updated.
        If the device settings (endpoint,..) were changed the device and
        entity are deleted and re-added.

        If patch_entity is true the corresponding entity in the ContextBroker is
        also correctly updated. Else only new attributes are added there.

        Args:
            device (Device): Device to be posted to /updated in Fiware
            patch_entity (bool): If true the corresponding entity is
                completely synced
            cb_client (ContextBrokerClient):
                Corresponding ContextBrokerClient object for entity manipulation
            cb_url (AnyHttpUrl):
                Url of the ContextBroker where the entity is found.
                This will autogenerate an CB-Client, mirroring the information
                of the IoTA-Client, e.g. FiwareHeader, and other headers
                (not recommended!)

        Returns:
            None
        """
        try:
            live_device = self.get_device(device_id=device.device_id)
        except requests.RequestException:
            # device does not exist yet, post it
            self.post_device(device=device)
            return

        # if the device settings were changed we need to delete the device
        # and repost it
        settings_dict = {"device_id", "service", "service_path",
                         "entity_name", "entity_type",
                         "timestamp", "apikey", "endpoint",
                         "protocol", "transport",
                         "expressionLanguage"}

        live_settings = live_device.model_dump(include=settings_dict)
        new_settings = device.model_dump(include=settings_dict)

        if not live_settings == new_settings:
            self.delete_device(device_id=device.device_id,
                               delete_entity=True,
                               force_entity_deletion=True,
                               cb_client=cb_client)
            self.post_device(device=device)
            return

        # We are at a state where the device exists, but only attributes were
        # changed.
        # we need to update the device, and the context entry separately,
        # as update device only takes over a part of the changes to the
        # ContextBroker.

        # update device
        self.update_device(device=device)

        # update context entry
        # 1. build context entity from information in device
        # 2. patch it
        from filip.models.ngsi_v2.context import \
            ContextEntity, NamedContextAttribute

        def build_context_entity_from_device(device: Device) -> ContextEntity:
            from filip.models.base import DataType
            entity = ContextEntity(id=device.entity_name,
                                   type=device.entity_type)

            for command in device.commands:
                entity.add_attributes([
                    # Command attribute will be registered by the device_update
                    NamedContextAttribute(
                        name=f"{command.name}_info",
                        type=DataType.COMMAND_RESULT
                    ),
                    NamedContextAttribute(
                        name=f"{command.name}_status",
                        type=DataType.COMMAND_STATUS
                    )
                ])
            for attribute in device.attributes:
                entity.add_attributes([
                    NamedContextAttribute(
                        name=attribute.name,
                        type=DataType.STRUCTUREDVALUE,
                        metadata=attribute.metadata
                    )
                ])
            for static_attribute in device.static_attributes:
                entity.add_attributes([
                    NamedContextAttribute(
                        name=static_attribute.name,
                        type=static_attribute.type,
                        value=static_attribute.value,
                        metadata=static_attribute.metadata
                    )
                ])
            return entity

        if patch_entity:
            from filip.clients.ngsi_v2 import ContextBrokerClient
            if cb_client:
                cb_client_local = deepcopy(cb_client)
            else:
                warnings.warn("No `ContextBrokerClient` object provided! "
                              "Will try to generate one. "
                              "This usage is not recommended.")

                cb_client_local = ContextBrokerClient(
                    url=cb_url,
                    fiware_header=self.fiware_headers,
                    headers=self.headers)

            cb_client_local.patch_entity(
                entity=build_context_entity_from_device(device))
            cb_client_local.close()

    def does_device_exists(self, device_id: str) -> bool:
        """
        Test if a device with the given id exists in Fiware
        Args:
            device_id (str)
        Returns:
            bool
        """
        try:
            self.get_device(device_id=device_id)
            return True
        except requests.RequestException as err:
            if not err.response.status_code == 404:
                raise
            return False

    # LOG API
    def get_loglevel_of_agent(self):
        """
        Get current loglevel of agent
        Returns:

        """
        url = urljoin(self.base_url, 'admin/log')
        headers = self.headers.copy()
        del headers['fiware-service']
        del headers['fiware-servicepath']
        try:
            res = self.get(url=url, headers=headers)
            if res.ok:
                return res.json()['level']
            res.raise_for_status()
        except requests.RequestException as err:
            self.log_error(err=err)
            raise

    def change_loglevel_of_agent(self, level: str):
        """
        Change current loglevel of agent
        
        Args:
            level:

        Returns:

        """
        level = level.upper()
        if level not in ['INFO', 'ERROR', 'FATAL', 'DEBUG', 'WARNING']:
            raise KeyError("Given log level is not supported")

        url = urljoin(self.base_url, 'admin/log')
        headers = self.headers.copy()
        del headers['fiware-service']
        del headers['fiware-servicepath']
        try:
            res = self.put(url=url, headers=headers, params=level)
            if res.ok:
                self.logger.info("Loglevel of agent at %s "
                                 "changed to '%s'", self.base_url, level)
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            self.log_error(err=err)
            raise
