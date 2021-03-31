import logging
from iota.client import IoTAClient
from core.models import FiwareHeader
from iota.models import Device, ServiceGroup
from uuid import uuid4

logger = logging.getLogger(__name__)


#
# def iota(config: config.Config):
#     # Creating an Instance of the Context Broker
#     ocb = ContextBroker(config)
#
#     # Creating an Instance of the IoT-Agent in the UL-Version
#     agent = Agent(config)
#
#     # set the service_group path
#     fiware_service = FiwareService("filip",
#                                          "/iot_example")
#     ocb.set_service(fiware_service)
#
#     res = fiware_service.get_header()
#
#     if config.data["iota"]["protocol"] == "IoTA-UL":
#         device_group = DeviceGroup(fiware_service,
#                                    "http://orion:1026",
#                                    apikey="12345test",
#                                    autoprovision=True,
#                                    resource="iot/d")
#         print(device_group)
#
#         device_group.test_apikey()
#
#         print("Device initialization for IoTA-UL Agent")
#         device = Device(device_id='urn:Room:002:sensor01',
#                         entity_name='urn:Room:002',
#                         entity_type="Thing",
#                         transport="MQTT",
#                         protocol="PDI-IoTA-UltraLight",
#                         timezone="Europe/Berlin",
#                         service=fiware_service.name,
#                         service_path=fiware_service.path,
#                         resource="iot/d"
#                         )
#     elif config.data["iota"]["protocol"] == "IoTA-JSON":
#         device_group = DeviceGroup(fiware_service,
#                                    "http://orion:1026",
#                                    apikey="12345test",
#                                    autoprovision=True,
#                                    resource="iot/json")
#         print(device_group)
#
#         device_group.test_apikey()
#
#         print("Device initialization for IoTA-JSON Agent")
#         device = Device(device_id='urn:Room:002:sensor02',
#                         entity_name='urn:Room:002',
#                         entity_type="Thing",
#                         transport="MQTT",
#                         protocol="IoTA-JSON",
#                         timezone="Europe/Berlin",
#                         timestamp=True,
#                         autoprovision=False,
#                         service=fiware_service.name,
#                         service_path=fiware_service.path,
#                         resource = "iot/json"
#                         )
#     else:
#         print(f'{conf["iota"]["protocol"]} - is not a supported protocol.')
#
#     print(device)
#
#     press_attr = {"name": "pressure",
#                   "type": "Number",
#                   "attr_type": "active",
#                   "object_id": "p"}
#
#     device.add_attribute(press_attr)
#
#     # creating attribute using dict/json with prohibited value
#     temp_attr = {"name": "temperature",
#                  "type": "Number",
#                  "attr_type": "active",
#                  "value": "12",
#                  "object_id": "t"}
#
#     device.add_attribute(temp_attr)
#
#     # creating attribute using dict/json but include attr_type as variable
#     name_attr = {"name": "nice_name",
#                  "type": "String",
#                  "value" : "beautiful attribute!",}
#
#     device.add_attribute(name_attr, attr_type="static")
#
#     # creating attribute using dict/json with missing attr_type
#     name_attr = {"name": "very_nice_name",
#                  "type": "String",
#                  "value" : "beautiful attribute!",
#                  "object_id": "name"}
#
#     device.add_attribute(name_attr)
#
#     # creating attribute using variables
#     device.add_attribute(name="Tiger",
#                          attr_type="static",
#                          type="Number",
#                          value=12)
#
#     # creating command
#     device.add_attribute(name = "OpenCages",
#                          type = "String",
#                          attr_type = "command",
#                          value = "Yes",
#                          object_id= "cage")
#
#     # test creating an internal attribute
#     internal_attr = {"name": "nice_name_int",
#                      "type": "String",
#                      "attr_type": "internal",
#                      "value" : "beautiful attribute!",
#                      "object_id": "name"}
#
#     device.add_attribute(internal_attr)
#
#     print(device)
#
#     device.delete_attribute("pressure", "active")
#
#     agent.post_group(device_group)
#     agent.update_group(device_group)
#     agent.get_group_list(device_group)
#     agent.post_device(device_group, device)
#     agent.update_device(device_group, device, {})
#
#     print(agent.get_device(device_group, device))
#     print(ocb.get_all_entities())
#     print(ocb.get_entity('urn:Room:002'))
#
#     agent.delete_device(device_group, device)
#     agent.delete_group(device_group)


def setup():
    logger.info("------Setting up clients------")
    with IoTAClient(fiware_header=FiwareHeader(service='filip',
                                               service_path='/testing')) as \
            iota_client:
        logger.info("IoTA " + iota_client.get_version().__str__() + " at url " +
                    iota_client.base_url)


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
            logger.info("------Getting service groups by resource and API key------")
            logger.info(
                iota_client.get_group(resource=group.resource, apikey=group.apikey))
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

    # # setup logging
    # # before the first initalization the log_config.yaml.example file needs to be
    # modified
    #
    # path_to_config = os.path.join(str(Path().resolve().parent), "config.json")
    # config.setup_logging()
    #
    # # Read and check configuration
    # conf = config.Config(path_to_config)
    #
    # iota(conf)
