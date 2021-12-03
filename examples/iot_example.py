"""
# Examples for working with IoT Devices
"""

import json
from filip.clients.ngsi_v2 import IoTAClient
from filip.models.base import FiwareHeader, DataType
from filip.models.ngsi_v2.iot import Device, ServiceGroup, TransportProtocol, \
    StaticDeviceAttribute, DeviceAttribute, LazyDeviceAttribute, DeviceCommand
from uuid import uuid4


"""
To run this example you need a working Fiware v2 setup with a context-broker 
and an iota-broker. You can here set the addresses:
"""
cb_url = "http://localhost:1026"
iota_url = "http://localhost:4041"

"""
You can here also change the used Fiware service
"""
service='filip'
service_path='/example_iot'


if __name__ == "__main__":

    # # 1. Setup IoTAClient
    #
    # First a client is initialised that provides as access to our
    # Fiware-server space. For more details on this step see:
    # Example: client_example.py
    iota_client =  IoTAClient(
        url=iota_url,
        fiware_header=FiwareHeader(service=service,service_path=service_path))

    print("IoTA " + json.dumps(iota_client.get_version(), indent=2)
          + " at url " + iota_client.base_url)

    # # 2. Device Model
    #
    # ## 2.1 Create a device
    #
    # A device can be created in two ways
    # For all information about the needed device attributes, please
    # reference the DeviceModel directly.
    #
    # When a device is posted to Fiware, Fiware will automatically create a
    # ContextEntity that symbolises the current device state. Through the
    # ContextBrokerClient an the entity the state of the device can be seen
    # and manipulated.
    #
    # Dictionary:
    example_device = {"device_id": "sensor008",
                      "service": service,
                      "service_path": service_path,
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
                     service=service,
                     service_path=service_path,
                     entity_name="sensor2",
                     entity_type="Sensor",
                     transport=TransportProtocol.HTTP,
                     endpoint="http://localhost:1234")

    # ## 2.2. Device Attributes
    #
    # To a device attributes can be added, they will automatically be
    # mirrored to the related context entity.
    # Each attribute needs a unique name.
    #
    # ### 2.2.1. StaticDeviceAttribute
    #
    # These attributes represent static information (as names) and are
    # mirrored 1:1
    device2.add_attribute(StaticDeviceAttribute(name="address",
                                                type=DataType.TEXT,
                                                value="Lichtenhof 3"))
    # ### 2.2.2. DeviceAttribute
    #
    # These attributes represent a live information of the device.
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
    device2.add_attribute(LazyDeviceAttribute(name="temperature",
                                              object_id="t"))

    # ### 2.2.3. Commands
    #
    # Commands can be executed to let the device execute some action
    device2.add_attribute(DeviceCommand(name="on"))
    # In the context entity three attributes are added for a command:
    #   -   Command (name): used to execute
    #   -   Status (name_status): used to inform about execution status
    #   -   Info/Result (name_info): used to inform about the final result

    # 3. Interact with Fiware
    #
    # 3.1. Upload a new Device
    iota_client.post_device(device=device2)
    #
    # 3.2. Load a specific device as model
    my_device = iota_client.get_device(device_id="sensor009")
    #
    # 3.3. Load multiple devices
    my_devices = iota_client.get_device_list()
    #
    # 3.4. Update a device
    #
    # After changes were made to the device, the simplest way to transfer
    # them to Fiware is:
    iota_client.patch_device(my_device)
    #
    # 3.5. Delete a device
    iota_client.delete_device(device_id="sensor009")

    # 4. Service Groups
    #
    #For some services, there will be no need to provision individual devices,
    # but it will make more sense to provision different service groups,
    # each of one mapped to a different type of entity in the context broker
    # https://iotagent-node-lib.readthedocs.io/en/latest/api/index.html#service-group-api

    # 4.1. Create a service group
    service_group1 = ServiceGroup(entity_type='Thing',
                                      resource='/iot/json',
                                      apikey=str(uuid4()))
    iota_client.post_groups(service_groups=[service_group1])

    # 4.2. Access a service group
    #
    # All groups:
    retrieved_groups = iota_client.get_group_list()
    # a specific group
    my_group = iota_client.get_group(resource='/iot/json',apikey=service_group1)

    # 4.3 Delete a service group
    iota_client.delete_group(resource='/iot/json', apikey=service_group1)

    # # 5. Clean up (Optional)
    #
    # Close client
    iota_client.close()
