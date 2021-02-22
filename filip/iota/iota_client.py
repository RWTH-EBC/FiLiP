import requests
import logging
import json
from typing import List, Dict, Set, Union
from urllib.parse import urljoin
from core import settings, FiwareHeader
from .models import Device, Service, Protocol

logger = logging.getLogger(__name__)


class IoTAClient():
    """
    Client for FIWARE IoT-Agents. The implementation follows the API
    specifications from here:
    https://iotagent-node-lib.readthedocs.io/en/latest/
    """
    def __init__(self, fiware_header: FiwareHeader = None):
        self.headers = dict()
        if not fiware_header:
            fiware_header = FiwareHeader()
        self.headers.update(fiware_header.dict(by_alias=True))

    def get_version(self) -> Dict:
        """
        Gets version of IoT Agent
        Returns:
            Dictionary with response
        """
        url = urljoin(settings.IOTA_URL, 'iot/about')
        try:
            res = requests.get(url=url, headers=self.headers)
            if res.ok:
                return res.json()
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)

    def post_services(self, services: Union[Service, List[Service]],
                      update: bool = False):
        """
        Creates a set of service groups for the given service and service path.
        The service and subservice information will taken from the headers,
        overwritting any preexisting values.
        Args:
            services (list of Service): Services that will be posted to
            the agent's API
            update (bool): If service already exists try to update its
            configuration
        Returns:
            None
        """
        if not isinstance(services, list):
            services = list(services)
        url = urljoin(settings.IOTA_URL, 'iot/services')
        headers = self.headers
        data = {'services': [service.dict(exclude={'service','subservice'},
                                          exclude_defaults=True) for
                             service in services]}
        res = None
        try:
            res = requests.post(url=url, headers=headers, json=data)
            if res.ok:
                logger.info("Services successfully posted")
            elif (res.status_code == 409):
                logger.warning("res.content")
                if  len(services) > 1:
                    logger.info("Trying to split bulk operation into single "
                                "operation")
                    for service in services:
                        self.post_service(service=service, update=update)
                elif update is True:
                    self.update_service(service=services[0], fields=None)
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)
            if res is not None:
                logger.error(res.content)

    def post_service(self, service: Service, update: bool = False):
        """
        Single service registration but using the bulk operation in background
        Args:
            service (Service): Service that will be posted to the agent's API
            update (bool):
        Returns:
            None
        """
        return self.post_services(services=list(service), update=update)

    def get_services(self) -> List[Service]:
        """

        Returns:

        """
        url = urljoin(settings.IOTA_URL, 'iot/services')
        headers = self.headers
        res = None
        try:
            res = requests.get(url=url, headers=headers)
            if res.ok:
                return [Service(**service)
                        for service in res.json()['services']]
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)
            if res:
                logger.error(res.content)

    def get_service(self, *, resource: str, apikey: str) -> Service:
        """

        Args:
            resource:
            apikey:

        Returns:

        """
        url = urljoin(settings.IOTA_URL, 'iot/services')
        headers = self.headers
        params = {key: value for key, value in locals().items()}
        res = None
        try:
            res = requests.get(url=url, headers=headers, params=params)
            if res.ok:
                return Service(**res.json()['services'][0])
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)
            if res is not None:
                logger.error(res.content)

    def update_service(self, *, service: Service,
                       fields: Union[Set[str], List[str]] = None):
        """
        Modifies the information for a service group configuration, identified
        by the resource and apikey query parameters. Takes a service group body
        as the payload. The body does not have to be complete: for incomplete
        bodies, just the existing attributes will be updated
        Args:
            service
            fields
        Returns:
            None
        """
        if fields:
            if isinstance(fields, list):
                fields = set(fields)
        else:
            fields = None
        url = urljoin(settings.IOTA_URL, 'iot/services')
        headers = self.headers
        params = {key: value for key, value in locals().items()}
        res = None
        try:
            res = requests.put(url=url, headers=headers, params=params,
                               json=service.json(include=fields,
                                                 exclude={'service',
                                                          'subservice'},
                                                 skip_defaults=True))
            if res.ok:
                logger.info(f"Service updated!")
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)
            if res is not None:
                logger.error(res.content)

    def delete_service(self, *, resource: str, apikey: str):
        """

        Args:
            resource:
            apikey:

        Returns:

        """
        url = urljoin(settings.IOTA_URL, 'iot/services')
        headers = self.headers
        params = {key: value for key, value in locals().items()}
        res = None
        try:
            res = requests.delete(url=url, headers=headers, params=params)
            if res.ok:
                logger.info(f"Service with resource: '{resource}' and apikey: "
                            f"'{apikey}' successfully deleted!")
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)
            logger.error(f"Service with resource: '{resource}' and apikey: "
                         f"'{apikey}' could not deleted!")
            if res is not None:
                logger.error(res.content)

    def get_devices(self, *, limit: int = 20, offset: int = None,
                    detailed: bool = None, entity: str = None,
                    protocol: Protocol = None) -> List[Device]:
        """
        Returns a list of all the devices in the device registry with all
        its data.
        Args:
            limit: if present, limits the number of devices returned in the
            list. Must be a number between 1 and 1000.
            offset: if present, skip that number of devices from the original query.
            detailed:
            entity:
            protocol:
        Returns:

        """
        if limit < 1 and limit > 1000:
            logger.error("limit must be an integer between 1 and 1000!")
            raise Exception
        url = urljoin(settings.IOTA_URL, 'iot/devices')
        headers = self.headers
        params = {key: value for key, value in locals().items() if value is not
                  None}
        try:
            res = requests.get(url=url, headers=headers, params=params)
            if res.ok:
                return [Device(**device) for device in res.json()['devices']]
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)

    def post_device(self, *,device: Device, update: bool = False) -> None:
        """

        Args:
            device:
            update:

        Returns:

        """
        return self.post_devices(devices=list(device), update=update)

    def post_devices(self, *,devices: Union[Device, List[Device]],
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
            devices = list(devices)
        url = urljoin(settings.IOTA_URL, f'iot/devices')
        headers = self.headers
        data = {"devices": [device.dict() for device in devices]}
        res = None
        try:
            res = requests.post(url=url, headers=headers, json=data)
            if res.ok:
                logger.info(f"Device successfully posted!")
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            if update:
                self.update_devices(devices=devices, add=False)
            logger.error(e)
            if res:
                logger.error(f"Devices could not updated! "
                             f"Reason: {res.text}")

    def get_device(self, *, device_id: str) -> Device:
        """
        Returns all the information about a particular device.
        Args:
            device_id:

        Returns:
            Device

        """
        url = urljoin(settings.IOTA_URL, f'iot/devices/{device_id}')
        headers = self.headers
        res = None
        try:
            res = requests.get(url=url, headers=headers)
            if res.ok:
                return Device.parse_raw(res.json())
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)
            if res:
                logger.error(res.content)


    def update_device(self, *, device: Device, add: bool = True):
        """
        Updates a device from the device registry.
        Args:
            device_id:
            add (bool): If device not found add it
        Returns:
            None
        """
        url = urljoin(settings.IOTA_URL, f'iot/devices/{device.device_id}')
        headers = self.headers
        res = None
        try:
            res = requests.put(url=url, headers=headers, json=device.dict(
                include={'attributes', 'lazy', 'commands',
                         'static_attributes'}))
            if res.ok:
                logger.info(f"Device '{device.device_id}' successfully updated!")
            elif (res.status_code == 409) & (add is True):
                self.post_device(device=device, update=False)
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)
            if res:
                logger.error(f"Device '{device.device_id}' could not updated! "
                             f"Reason: {res.text}")

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
            devices = list(devices)
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
        url = urljoin(settings.IOTA_URL, f'iot/devices{device_id}', )
        headers = self.headers
        try:
            res = requests.delete(url=url, headers=headers)
            if res.ok:
                logger.info(f"Device {device_id} successfully deleted!")
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)
            logger.error(f"Device {device_id} could not deleted!")
