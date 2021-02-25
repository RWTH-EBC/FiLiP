import logging
import requests
from typing import List, Dict, Set, Union
from urllib.parse import urljoin
from core import settings
from core.base_client import _BaseClient
from core.models import FiwareHeader
from iota.models import Device, ServiceGroup, PayloadProtocol

logger = logging.getLogger(__name__)


class Agent(_BaseClient):
    """
    Client for FIWARE IoT-Agents. The implementation follows the API
    specifications from here:
    https://iotagent-node-lib.readthedocs.io/en/latest/
    """
    def __init__(self, session: requests.Session = None,
                 fiware_header: FiwareHeader = None):
        super().__init__(session=session,
                         fiware_header=fiware_header)

    # ABOUT API
    def get_version(self) -> Dict:
        """
        Gets version of IoT Agent
        Returns:
            Dictionary with response
        """
        url = urljoin(settings.IOTA_URL, 'iot/about')
        try:
            res = self.session.get(url=url, headers=self.headers)
            if res.ok:
                return res.json()
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)

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
            configuration
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

        url = urljoin(settings.IOTA_URL, 'iot/services')
        headers = self.headers
        data = {'services': [group.dict(exclude={'service', 'subservice'},
                                         exclude_defaults=True) for
                            group in service_groups]}
        res = None
        try:
            res = self.session.post(url=url, headers=headers, json=data)
            if res.ok:
                logger.info("Services successfully posted")
            elif res.status_code == 409:
                logger.warning(res.text)
                if  len(service_groups) > 1:
                    logger.info("Trying to split bulk operation into single "
                                "operations")
                    for group in service_groups:
                        self.post_group(service_group=group, update=update)
                elif update is True:
                    self.update_group(service_group=service_groups[0],
                                      fields=None)
                else:
                    res.raise_for_status()
            else:
                res.raise_for_status()
        except requests.RequestException as e:
            logger.error(e)
            if res:
                logger.error(res.text)

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

    def get_groups(self) -> List[ServiceGroup]:
        """
        Retrieves service_group groups from the database. If the servicepath
        header has the wildcard expression, /*, all the subservices for the
        service_group are returned. The specific subservice parameters are
        returned in any other case.
        Returns:

        """
        url = urljoin(settings.IOTA_URL, 'iot/services')
        headers = self.headers
        res = None
        try:
            res = self.session.get(url=url, headers=headers)
            if res.ok:
                return [ServiceGroup(**group)
                        for group in res.json()['services']]
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)
            if res:
                logger.error(res.text)

    def get_group(self, *, resource: str, apikey: str) -> ServiceGroup:
        """
        Retrieves service_group groups from the database based on resource and
        apikey
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
            res = self.session.get(url=url, headers=headers, params=params)
            if res.ok:
                return ServiceGroup(**res.json()['services'][0])
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)
            if res is not None:
                logger.error(res.text)

    def update_groups(self, *,
                      service_groups: Union[ServiceGroup, List[ServiceGroup]],
                      fields: Union[Set[str], List[str]] = None,
                      add: False) -> None:
        """
        Bulk operation for service group update.
        Args:
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
        url = urljoin(settings.IOTA_URL, 'iot/services')
        headers = self.headers.update()
        params = service_group.dict(include={'resource', 'apikey'})
        res = None
        try:
            res = self.session.put(url=url, headers=headers, params=params,
                               json=service_group.json(include=fields,
                                                       exclude={'service',
                                                                'subservice'},
                                                       skip_defaults=True))
            if res.ok:
                logger.info(f"ServiceGroup updated!")
            elif (res.status_code == 404) & (add is True):
                self.post_group(service_group=service_group)
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)
            if res is not None:
                logger.error(res.text)

    def delete_group(self, *, resource: str, apikey: str):
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
            res = self.session.delete(url=url, headers=headers, params=params)
            if res.ok:
                logger.info(f"ServiceGroup with resource: '{resource}' and "
                            f"apikey: '{apikey}' successfully deleted!")
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)
            logger.error(f"ServiceGroup with resource: '{resource}' and "
                         f"apikey: '{apikey}' could not deleted!")
            if res is not None:
                logger.error(res.text)

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
        url = urljoin(settings.IOTA_URL, f'iot/devices')
        headers = self.headers
        data = {"devices": [device.dict() for device in devices]}
        res = None
        try:
            res = self.session.post(url=url, headers=headers, json=data)
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

    def post_device(self, *, device: Device, update: bool = False) -> None:
        """

        Args:
            device:
            update:

        Returns:

        """
        return self.post_devices(devices=[device], update=update)


    def get_devices(self, *, limit: int = 20, offset: int = None,
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
        if 1 > limit > 1000:
            logger.error("'limit' must be an integer between 1 and 1000!")
            raise ValueError
        url = urljoin(settings.IOTA_URL, 'iot/devices')
        headers = self.headers
        params = {key: value for key, value in locals().items() if value is not
                  None}
        try:
            res = self.session.get(url=url, headers=headers, params=params)
            if res.ok:
                return [Device(**device) for device in res.json()['devices']]
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)

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
            res = self.session.get(url=url, headers=headers)
            if res.ok:
                return Device.parse_raw(res.json())
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)
            if res:
                logger.error(res.text)

    def update_device(self, *, device: Device, add: bool = True) -> None:
        """
        Updates a device from the device registry.
        Args:
            device:
            add (bool): If device not found add it
        Returns:
            None
        """
        url = urljoin(settings.IOTA_URL, f'iot/devices/{device.device_id}')
        headers = self.headers
        res = None
        try:
            res = self.session.put(url=url, headers=headers, json=device.dict(
                include={'attributes', 'lazy', 'commands',
                         'static_attributes'}))
            if res.ok:
                logger.info(f"Device '{device.device_id}' "
                            f"successfully updated!")
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
        url = urljoin(settings.IOTA_URL, f'iot/devices{device_id}', )
        headers = self.headers
        try:
            res = self.session.delete(url=url, headers=headers)
            if res.ok:
                logger.info(f"Device {device_id} successfully deleted!")
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)
            logger.error(f"Device {device_id} could not deleted!")

    # LOG API
    def get_loglevel_of_agent(self):
        url = urljoin(settings.IOTA_URL, 'admin/log')
        headers = self.headers.copy()
        del headers['fiware-service']
        del headers['fiware-servicepath']
        try:
            res = self.session.get(url=url, headers=headers)
            if res.ok:
                return res.json()['level']
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)

    def change_loglevel_of_agent(self, level: str):
        level = level.upper()
        if level not in ['INFO', 'ERROR', 'FATAL', 'DEBUG', 'WARNING']:
            raise KeyError

        url = urljoin(settings.IOTA_URL, 'admin/log')
        headers = self.headers.copy()
        del headers['fiware-service']
        del headers['fiware-servicepath']
        try:
            res = self.session.put(url=url, headers=headers, params=level)
            if res.ok:
                logger.info(f"Loglevel of agent at {settings.IOTA_URL} "
                            f"changed to '{level}'")
            else:
                res.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(e)


