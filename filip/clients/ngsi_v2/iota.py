"""
IoT-Agent Module for API Client
"""
from typing import List, Dict, Set, Union
from urllib.parse import urljoin
import requests
from pydantic import parse_obj_as
from filip.config import settings
from filip.clients.base_http_client import BaseHttpClient
from filip.models.base import FiwareHeader
from filip.models.ngsi_v2.iot import Device, ServiceGroup, PayloadProtocol


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
        data = {'services': [group.dict(exclude={'service', 'subservice'},
                                        exclude_defaults=True) for
                             group in service_groups]}
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
                return parse_obj_as(List[ServiceGroup], res.json()['services'])
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
        url = urljoin(self.base_url, 'iot/services')
        headers = self.headers
        params = {'resource': resource,
                  'apikey': apikey}

        try:
            res = self.get(url=url, headers=headers, params=params)
            if res.ok:
                return ServiceGroup(**res.json()['services'][0])
            res.raise_for_status()
        except requests.RequestException as err:
            self.log_error(err=err, msg=None)
            raise

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
        headers = self.headers.update()
        params = service_group.dict(include={'resource', 'apikey'})
        try:
            res = self.put(url=url,
                           headers=headers,
                           params=params,
                           json=service_group.json(
                               include=fields,
                               exclude={'service', 'subservice'},
                               exclude_unset=True))
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
        data = {"devices": [device.dict(exclude_none=True) for device in
                            devices]}
        try:
            res = self.post(url=url, headers=headers, json=data)
            if res.ok:
                self.logger.info("Devices successfully posted!")
            else:
                res.raise_for_status()
        except requests.RequestException as err:
            if update:
                return self.update_devices(devices=devices, add=False)
            msg = "Could not update devices"
            self.log_error(err=err, msg=msg)
            raise

    def post_device(self, *, device: Device, update: bool = False) -> None:
        """

        Args:
            device:
            update:

        Returns:

        """
        return self.post_devices(devices=[device], update=update)

    def get_device_list(self, *, limit: int = None, offset: int = None,
                        detailed: bool = None, entity: str = None,
                        protocol: PayloadProtocol = None) -> List[Device]:
        """
        Returns a list of all the devices in the device registry with all
        its data.
        Args:
            limit: if present, limits the number of devices returned in the
            list. Must be a number between 1 and 1000.
            offset: if present, skip that number of devices from the original
            query.
            detailed:
            entity:
            protocol:
        Returns:

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
                return parse_obj_as(List[Device], res.json()['devices'])
            res.raise_for_status()
        except requests.RequestException as err:
            self.log_error(err=err, msg=None)
            raise

    def get_device(self, *, device_id: str) -> Device:
        """
        Returns all the information about a particular device.
        Args:
            device_id:

        Returns:
            Device

        """
        url = urljoin(self.base_url, f'iot/devices/{device_id}')
        headers = self.headers
        try:
            res = self.get(url=url, headers=headers)
            if res.ok:
                return Device.parse_obj(res.json())
            res.raise_for_status()
        except requests.RequestException as err:
            self.log_error(err=err, msg=None)
            raise

    def update_device(self, *, device: Device, add: bool = True) -> None:
        """
        Updates a device from the device registry.
        Args:
            device:
            add (bool): If device not found add it
        Returns:
            None
        """
        url = urljoin(self.base_url, f'iot/devices/{device.device_id}')
        headers = self.headers
        try:
            res = self.put(url=url, headers=headers, json=device.dict(
                include={'attributes', 'lazy', 'commands', 'static_attributes'},
                exclude_none=True))
            if res.ok:
                self.logger.info("Device '%s' successfully updated!",
                                 device.device_id)
            elif (res.status_code == 409) & (add is True):
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

    def delete_device(self, *, device_id) -> None:
        """
        Remove a device from the device registry. No payload is required
        or received.
        Args:
            device_id:

        Returns:
            None
        """
        url = urljoin(self.base_url, f'iot/devices/{device_id}', )
        headers = self.headers
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
            raise KeyError

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
