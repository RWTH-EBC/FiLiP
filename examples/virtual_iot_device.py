"""
This example shows how to provision a virtual iot device in a FIWARE-based
IoT Platform using FiLiP and PahoMQTT
"""
import logging
from filip.models import FiwareHeader
from filip.models.ngsi_v2.iot import \
    Device, \
    DeviceCommand, \
    DeviceAttribute, \
    StaticDeviceAttribute
from filip.clients.ngsi_v2 import HttpClient


# Setting up logging
logging.basicConfig(
    level='INFO',
    format='%(asctime)s %(name)s %(levelname)s: %(message)s')

# First we create our device configuration using the models provided for
# filip.models.ngsi_v2.iot

# creating an attribute for incoming measurements from e.g. a sensor we do
# add the metadata for units here using the unit models
attr = DeviceAttribute(name='temperature',
                       object_id='t',
                       type="Number",
                       metadata={"unit": {"unitCode": "CEL"}})

# creating a static attribute that holds additional information
static_attr = StaticDeviceAttribute(name='info',
                                    type="Text",
                                    value="Filip example for virtual IoT "
                                          "device")
# creating a command that the IoT device will liston to
command = DeviceCommand(name='valve_opening')

device = Device(device_id='MyDevice',
                entity_name='MyDevice',
                entity_type='Thing',
                transport='MQTT',
                apikey='filip_example',
                attributes=[attr],
                static_attributes=[static_attr],
                commands=[command])

# This will print our configuration
print("This is our device configuration: \n" + device.json(indent=2))

# Send device configuration to FIWARE via the IoT-Agent. We use the general
# ngsiv2 httpClient for this.
# This will automatically create an data entity in the context broker and
# make the device with it. The name of the entity will be our device_id in
# this case for more complex configuration you need to set the entity_name
# and entity_type in the previous Device-Model

# create a fiware header
fiware_header = FiwareHeader(service='filip', service_path='/iot_examples')

# create the Http client node that once sent the device cannot be posted again
# and you need to use the update command
client = HttpClient(fiware_header=fiware_header)
#client.iota.post_device(device=device)

# check if the data entity is created in the context broker
entity = client.cb.get_entity(entity_id=device.device_id,
                              entity_type=device.entity_type)
print("This is our data entity belonging to our device: \n" +
      entity.json(indent=2))

# cleanup the server and delete everything
client.iota.delete_device(device_id=device.device_id)
client.cb.delete_entity(entity_id=device.device_id,
                        entity_type=device.entity_type)
