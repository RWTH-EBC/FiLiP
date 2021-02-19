import requests
import logging
import json
from typing import List, Union
from urllib.parse import urljoin
from core import settings, FiwareHeader
from .models import Device, Protocol

logger = logging.getLogger(__name__)


class IoTAClient():
    def __init__(self, fiware_header: FiwareHeader = None):
        self.headers = dict()
        if not fiware_header:
            fiware_header = FiwareHeader()
        self.headers.update(fiware_header.dict(by_alias=True))

    def get_version(self):
        url = urljoin(settings.IOTA_URL, 'version')
        url = 'http://github.com/'
        try:
            res = requests.get(url=url, headers=self.headers)
            res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)

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
        params = {param for param in locals().items() if param is not None}
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
            logger.error(f"Device {device_id} was not deleted!")
