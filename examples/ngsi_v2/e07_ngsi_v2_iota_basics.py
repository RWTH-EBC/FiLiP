"""
# # Examples for working with IoT Devices
"""
# ## Import packages
import logging
import json
from filip.clients.ngsi_v2 import IoTAClient
from filip.models.base import FiwareHeader, DataType
from filip.models.ngsi_v2.iot import Device, ServiceGroup, TransportProtocol, \
    StaticDeviceAttribute, DeviceAttribute, LazyDeviceAttribute, DeviceCommand
from uuid import uuid4

# ## Parameters
#
# To run this example you need a working Fiware v2 setup with a context-broker
# and an iota-broker. Here you can set the addresses:
#
# Host address of Context Broker
CB_URL = "http://localhost:1026"
# Host address of IoT-Agent
IOTA_URL = "http://localhost:4041"

# Here you can also change FIWARE service and service path.
# FIWARE-Service
SERVICE = 'filip'
# FIWARE-Service path
SERVICE_PATH = '/example'

# Setting up logging
logging.basicConfig(
    level='INFO',
    format='%(asctime)s %(name)s %(levelname)s: %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S')

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    # # 1 Setup IoTAClient
    #
    # First a client is initialised that provides access to our
    # Fiware-server space.
    #
    # For more details about this step see e01_http_clients.py.

    fiware_header = FiwareHeader(service=SERVICE,
                                 service_path=SERVICE_PATH)

    iota_client = IoTAClient(url=IOTA_URL,
                             fiware_header=fiware_header)

    print(f"IoTA: {json.dumps(iota_client.get_version(), indent=2)}"
          f" located at the url: {iota_client.base_url}")

    # # 2 Device Model
    #
    # ## 2.1 Create a device
    #
    # A device can be created in two ways.
    # For all information about the needed device attributes, please
    # reference the DeviceModel directly.
    #
    # When a device is posted to Fiware, Fiware will automatically create a
    # ContextEntity that symbolises the current device state. Through the
    # ContextBrokerClient and the entity, the state of the device can be seen
    # and manipulated.
    #
    # Dictionary:
    example_device = {"device_id": "sensor008",
                      "service": SERVICE,
                      "service_path": SERVICE_PATH,
                      "entity_name": "sensor1",
                      "entity_type": "Sensor",
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
    device1 = Device(**example_device)

    # Direct Parameters:
    device2 = Device(device_id="sensor009",
                     service=SERVICE,
                     service_path=SERVICE_PATH,
                     entity_name="sensor2",
                     entity_type="Sensor",
                     transport=TransportProtocol.HTTP,
                     endpoint="http://localhost:1234")

    # ## 2.2 Device Attributes
    #
    # You can add attributes to a device, and they will automatically be
    # mirrored to the related context entity.
    # Each attribute needs a unique name.
    #
    # ### 2.2.1 StaticDeviceAttribute
    #
    # These attributes represent static information (such as names) and are
    # mirrored 1:1
    device2.add_attribute(StaticDeviceAttribute(name="address",
                                                type=DataType.TEXT,
                                                value="Lichtenhof 3"))
    # ### 2.2.2 DeviceAttribute
    #
    # These attributes represent live information of the device.
    # The value can be read by accessing the mirrored attribute in the
    # context entity.
    # It is differentiated between two kinds:
    #
    # DeviceAttributes, always keep the value in the context entity up-to-date
    # (polling)
    device2.add_attribute(DeviceAttribute(name="temperature",
                                          object_id="t"))
    # LazyDeviceAttributes, only update the value in the entity if it is
    # accessed (event based)
    device2.add_attribute(LazyDeviceAttribute(name="temperature"))

    # ### 2.2.3 Commands
    #
    # Commands can be executed to let the device execute some action
    device2.add_attribute(DeviceCommand(name="on"))
    # In the context entity three attributes are added for a command:
    #   -   Command (name): used to execute
    #   -   Status (name_status): used to inform about execution status
    #   -   Info/Result (name_info): used to inform about the final result

    # # 3 Interact with Fiware
    #
    # ## 3.1 Upload a new Device
    print(f"Payload that will be sent to the IoT-Agent:\n "
          f"{device2.model_dump_json(indent=2)}")
    iota_client.post_device(device=device2)
    #
    # ## 3.2 Load a specific device as model
    my_device = iota_client.get_device(device_id=device2.device_id)
    #
    # ## 3.3 Load multiple devices
    my_devices = iota_client.get_device_list()
    #
    # ## 3.4 Update a device
    #
    # After changes were made to the device, the simplest way to transfer
    # them to Fiware is through patch_device method:
    iota_client.patch_device(my_device)
    #
    # ## 3.5 Delete a device
    iota_client.delete_device(device_id=device2.device_id)

    # # 4 Service Groups
    #
    # For some services, there will be no need to provision individual devices,
    # but it will make more sense to provision different service groups,
    # each of one mapped to a different type of entity in the context broker
    # https://iotagent-node-lib.readthedocs.io/en/latest/api/index.html#service-group-api

    # ## 4.1. Create a service group
    service_group1 = ServiceGroup(entity_type='Thing',
                                  resource='/iot/json',
                                  apikey=str(uuid4()))
    iota_client.post_groups(service_groups=[service_group1])

    # ## 4.2 Access a service group
    #
    # All groups:
    retrieved_groups = iota_client.get_group_list()
    # a specific group
    my_group = iota_client.get_group(resource='/iot/json',
                                     apikey=service_group1.apikey)

    # ## 4.3 Delete a service group
    iota_client.delete_group(resource='/iot/json',
                             apikey=service_group1.apikey)

    # # 5 Clean up (Optional)
    #
    # Close client
    iota_client.close()
