import requests
import logging
import json
from typing import List, Union
from urllib.parse import urljoin
from core import settings, FiwareHeader
from .models import Device, Service, Protocol

logger = logging.getLogger(__name__)


class IoTAClient():
    def __init__(self, fiware_header: FiwareHeader = None):
        self.headers = dict()
        if not fiware_header:
            fiware_header = FiwareHeader()
        self.headers.update(fiware_header.dict(by_alias=True))

    def get_version(self):
        url = urljoin(settings.IOTA_URL, 'version')
        try:
            res = requests.get(url=url, headers=self.headers)
            if res.ok:
                return res
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)

    def get_services(self):
        url = urljoin(settings.IOTA_URL, 'iot/services')
        headers = self.headers
        try:
            res = requests.get(url=url, headers=headers)
            if res.ok:
                return [Service(**service) for service in res.json()['services']]
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)

    def get_service(self, *, resource, apikey):
        """

        Args:
            resource:
            apikey:

        Returns:

        """
        url = urljoin(settings.IOTA_URL, 'iot/services')
        headers = self.headers
        params = {key: value for key, value in locals().items() if value is not
                  None}
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

    def post_service(self, service: Service):
        url = urljoin(settings.IOTA_URL, 'iot/services')
        headers = self.headers
        data = {'services': [service.dict(exclude={'service','subservice'},
                                          exclude_defaults=True)]}
        res = None
        try:
            res = requests.post(url=url, headers=headers, json=data)
            if res.ok:
                logger.info("Service successfully posted")
            else:
                print(res.text)
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)
            if res is not None:
                logger.error(res.content)


    def delete_service(self, *, resource, apikey):
        """

        Args:
            resource:
            apikey:

        Returns:

        """
        url = urljoin(settings.IOTA_URL, 'iot/services')
        headers = self.headers
        params = {key: value for key, value in locals().items() if value is not
                  None}
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


    def get_devices(self, *, limit: int = 20, offset: int = 20,
                    detailed: bool = None, entity: str = None,
                    protocol: Protocol = None) -> List[Device]:
        """
        Returns a list of all the devices in the device registry with all
        its data.
        Args:
            limit: if present, limits the number of devices returned in the list.
            offset: if present, skip that number of devices from the original query.
            detailed:
            entity:
            protocol:

        Returns:

        """
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


    def post_devices(self):
        url = urljoin(settings.IOTA_URL, 'version')

    def get_device(self, *, device_id) -> Device:
        """
        Returns all the information about a particular device.
        Args:
            device_id:

        Returns:
            Device

        """
        url = urljoin(settings.IOTA_URL, 'iot/devices', device_id)
        headers = self.headers
        try:
            res = requests.get(url=url, headers=headers)
            if res.ok:
                return Device.parse_raw(res.json())
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)

    def update_device(self, *, device_id):
        pass

    def delete_device(self, *, device_id) -> None:
        """
        Remove a device from the device registry. No payload is required
        or received.
        Args:
            device_id:

        Returns:
            None
        """
        url = urljoin(settings.IOTA_URL, 'iot/devices', device_id)
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
