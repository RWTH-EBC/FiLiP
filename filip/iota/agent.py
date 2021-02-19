import requests
import datetime
import json
import logging

from filip.utils import request_utils as requtils
from core import test
from filip.iota.device_group import DeviceGroup
from filip.iota.device import Device
from filip.config import Config

log = logging.getLogger('iot')
PROTOCOLS = ['IoTA-JSON', 'IoTA-UL']


class Agent:
    # https://iotagent-node-lib.readthedocs.io/en/latest/
    # https://fiware-iotagent-json.readthedocs.io/en/latest/usermanual/index.html
    def __init__(self, config: Config, session=None):
        self.session = session or requests.Session()
        self.test_config(config)
        self.host = config.iota.get("host")
        self.port = config.iota.get("port")
        self.url = config.iota.get("url")
        self.protocol = config.iota.get("protocol")
        #TODO: Figuring our how to register the service and conncet with devices
        self.services = []

    def test_config(self, config: Config):
        print(config.data)
        test.test_config('iota', config.data)

    def test_connection(self):
        """
        Function utilises the test.test_connection() function to check the availability of a given url and service.
        :return: Boolean, True if the service is reachable, False if not.
        """
        boolean = test.test_connection(client=self.session,
                                       service_name=__name__,
                                       url=self.url+'/version')
        return boolean

    def log_switch(self, level, response):
        """
        Function returns the required log_level with the repsonse
        :param level: The logging level that should be returned
        :param response: The message for the logger
        :return:
        """
        switch_dict = {"INFO": logging.info,
                       "ERROR":  logging.error,
                       "WARNING": logging.warning
                       }.get(level, logging.info)(msg=response)

    def get_groups(self, device_group: DeviceGroup):
        url = self.url + '/iot/services'
        headers = device_group.get_header()
        response = self.session.request("GET", url, headers=headers)
        ok, retstr = requtils.response_ok(response)
        if not ok:
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, retstr)
        else:
            return response.text

    def delete_group(self, device_group: DeviceGroup):
        url = self.url + '/iot/services'
        headers = device_group.get_header()
        querystring = {"resource": device_group.get_resource(),
                       "apikey": device_group.get_apikey()}
        response = self.session.request("DELETE", url,
                                    headers=headers, params=querystring)
        if response.status_code == 204:
            log.info(f"Device group successfully deleted!")
        else:
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, retstr)

    def post_group(self, device_group: DeviceGroup, force_update: bool = False):
        """
        Function post a device group (service). If force_update = True, the info cannot  unable to register
        configuration (409 : Duplicate_Group) is ignored and the group is updated.
        :param device_group: The device group that should be updated. An Instance of the Device_group Class
        :param force_update: Boolean whether an update should be forced.
        """
        url = self.url + '/iot/services'
        headers = {**requtils.HEADER_CONTENT_JSON, **device_group.get_header()}
        payload = dict()
        payload['services'] = [json.loads(device_group.get_json())]
        payload = json.dumps(payload, indent=4)
        response = self.session.request("POST", url, data=payload,
                                    headers=headers)
        if (response.status_code == 409) & (force_update is True):
            querystring = {"resource": device_group.get_resource_last(),
                           "apikey": device_group.get_apikey_last()}
            response = requests.request("PUT", url=url, data=payload, headers=headers, params=querystring)

        if response.status_code not in [201, 200, 204]:
            log.warning(f"Unable to register default configuration for service "
                        f"{device_group.get_header()['fiware-service']}, "
                        f"path {device_group.get_header()['fiware-servicepath']}"
                        f" Code: {response.status_code} - Info: {response.text}")
            return None

    def update_group(self, device_group: DeviceGroup):
        url = self.url + '/iot/services'
        headers = {**requtils.HEADER_CONTENT_JSON, **device_group.get_header_last()}
        querystring = {"resource": device_group.get_resource_last(),
                       "apikey": device_group.get_apikey_last()}
        payload = json.loads(device_group.get_json())
        payload = json.dumps(payload, indent=4)
        log.info(f" {datetime.datetime.now()} - Update group with: {payload}")
        response = self.session.request("PUT", url,
                                    data=payload, headers=headers,
                                    params=querystring)
        ok, retstr = requtils.response_ok(response)
        if not ok:
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, retstr)
        else:
            log.info(f"Device group sucessfully updated")

    def post_device(self, device_group: DeviceGroup, device: Device, force_update: bool = True):
        """
        Function registers a device with the iot-Agent to the respective device group.
        If a device allready exists in can be updated with update = True
        :param device_group: A device group is a necessary for connecting devices, as it provides a authentication key
        :param device: The device which provides the measurments / accepts the commands
        :param update: Whether if the device is already existent it should be updated
        :return:
        """
        url = self.url + '/iot/devices'
        headers = {**requtils.HEADER_CONTENT_JSON, **device_group.get_header()}
        payload = dict()
        payload['devices'] = [json.loads(device.get_json())]
        payload = json.dumps(payload, indent=4)
        response = self.session.request("POST", url, data=payload,
                                    headers=headers)

        if (response.status_code == 409) & (force_update is True):
            device_data = dict()
            device_data["attributes"] = \
                json.loads(device.get_json())["attributes"]
            device_data = json.dumps(device_data, indent=4)
            self.update_device(device_group, device, device_data)

        elif response.status_code != 201:
            log.warning(f"Unable to post device: ", response.text)

        else:
            log.info(f"Device {device.device_id} successfully posted.")

    def delete_device(self, device_group: DeviceGroup, device: Device):
        """
        Function deletes a device.
        :param device_group: The respective DeviceGroup of the Device
        :param device: The respective Device.
        :return:
        """
        url = self.url + '/iot/devices/' + device.device_id
        headers = {**requtils.HEADER_CONTENT_JSON, **device_group.get_header()}
        response = self.session.request("DELETE", url, headers=headers)
        if response.status_code == 204:
            log.info(f"Device {device.device_id} successfully deleted!")
        else:
            log.warning(f"Device {device.device_id} could not be deleted: {response.text}")

    def get_device(self, device_group: DeviceGroup, device: Device):
        """
        Function gets a device.
        :param device_group:
        :param device:
        :return:
        """
        url = self.url + '/iot/devices/' + device.device_id
        headers = {**requtils.HEADER_CONTENT_JSON, **device_group.get_header()}
        payload = ""
        response = self.session.request("GET", url, data=payload,
                                    headers=headers)
        ok, retstr = requtils.response_ok(response)
        if not ok:
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, retstr)
        else:
            return response.text

    def update_device(self, device_group: DeviceGroup, device: Device, payload: dict):
        """

        :param device_group:
        :param device:
        :param payload:
        :return:
        """
        url = self.url + '/iot/devices/' + device.device_id
        headers = {**requtils.HEADER_CONTENT_JSON, **device_group.get_header()}
        response = self.session.request("PUT", url,
                                    data=payload,
                                    headers=headers)

        ok, retstr = requtils.response_ok(response)
        if not ok:
            level, retstr = requtils.logging_switch(response)
            self.log_switch(level, retstr)
        else:
            log.info(f"Device {device.device_id} successfully updated!")