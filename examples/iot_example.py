import logging
import json
from filip.clients.ngsi_v2 import IoTAClient
from filip.models.base import FiwareHeader
from filip.models.ngsi_v2.iot import Device, ServiceGroup
from uuid import uuid4

logger = logging.getLogger(__name__)


def setup():
    logger.info("------Setting up clients------")
    with IoTAClient(fiware_header=FiwareHeader(service='filip',
                                               service_path='/testing')) as \
            iota_client:
        logger.info("IoTA " + json.dumps(iota_client.get_version(), indent=2)
                    + " at url " + iota_client.base_url)


def create_device():
    example_device = {"device_id": "sensor004",
                      "service": "",
                      "service_path": "/",
                      "entity_name": "sensor1",
                      "entity_type": "all",
                      "timezone": 'Europe/Berlin',
                      "timestamp": True,
                      "apikey": "1234",
                      "protocol": "IoTA-UL",
                      "transport": "MQTT",
                      "lazy": [],
                      "commands": [],
                      "attributes": [],
                      "static_attributes": [],
                      "internal_attributes": [],
                      "explicitAttrs": False,
                      "ngsiVersion": "v2"}
    post_device = Device(**example_device)
    with IoTAClient(fiware_header=FiwareHeader(service='filip',
                                               service_path='/testing')) as \
            iota_client:
        logger.info("------Posting example device------")
        iota_client.post_device(device=post_device)
    return post_device


def create_service_group():
    with IoTAClient(fiware_header=FiwareHeader(service='filip',
                                               service_path='/testing')) as \
            iota_client:
        service_group1 = ServiceGroup(entity_type='Thing',
                                      resource='/iot/json',
                                      apikey=str(uuid4()))
        service_group2 = ServiceGroup(entity_type='OtherThing',
                                      resource='/iot/json',
                                      apikey=str(uuid4()))
        logger.info("------Creating example service groups------")
        iota_client.post_groups(service_groups=[service_group1,
                                                service_group2])


def filter_service_group():
    with IoTAClient(fiware_header=FiwareHeader(service='filip',
                                               service_path='/testing')) as \
            iota_client:
        retrieved_groups = iota_client.get_group_list()
        logger.info("------Get all service groups------")
        logger.info(retrieved_groups)
        for group in retrieved_groups:
            logger.info("------Getting service groups "
                        "by resource and API key------")
            logger.info(
                iota_client.get_group(resource=group.resource,
                                      apikey=group.apikey).json(indent=2))
        return retrieved_groups


def delete_service_group(groups_to_delete):
    with IoTAClient(fiware_header=FiwareHeader(service='filip',
                                               service_path='/testing')) as \
            iota_client:
        logger.info("------Deleting all example service groups------")
        for gr in groups_to_delete:
            iota_client.delete_group(resource=gr.resource,
                                     apikey=gr.apikey)


def filter_device():
    with IoTAClient(fiware_header=FiwareHeader(service='filip',
                                               service_path='/testing')) as \
            iota_client:
        retrieved_devices = iota_client.get_device_list()
        logger.info("------Getting all example devices------")
        logger.info(devices)
        # for device in retrieved_devices:
        # logger.info("------Getting devices by id------")
        # iota_client.get_device(device_id=device.device_id)
        # This is not working because of parsing error in iota client
        return retrieved_devices


def delete_device(device_id):
    with IoTAClient(fiware_header=FiwareHeader(service='filip',
                                               service_path='/testing')) as \
            iota_client:
        logger.info("------Deleting example device from device registry------")
        iota_client.delete_device(device_id=device_id)
        # logger.info("------Deleting entities from context broker------")
    # with ContextBrokerClient(fiware_header=FiwareHeader(service='filip',
    #                                                     service_path='/testing')) as \
    #         cb_client:
    #     cb_client.delete_entity(entity_id=device.entity_name,
    #     entity_type=device.entity_type)


if __name__ == "__main__":
    setup()
    device = create_device()
    create_service_group()
    groups = filter_service_group()
    devices = filter_device()
    delete_service_group(groups)
    delete_device(device.device_id)
