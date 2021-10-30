"""
This example shows how to provision a virtual iot device in a FIWARE-based
IoT Platform using FiLiP and PahoMQTT
"""
import json
import logging
import random
import time
import paho.mqtt.client as mqtt

from urllib.parse import urlparse

from filip.models import FiwareHeader
from filip.models.ngsi_v2.iot import \
    Device, \
    DeviceAttribute, \
    DeviceCommand, \
    ServiceGroup, \
    StaticDeviceAttribute
from filip.models.ngsi_v2.context import NamedCommand
from filip.clients.ngsi_v2 import HttpClient, HttpClientConfig


# Setting up logging
logging.basicConfig(
    level='INFO',
    format='%(asctime)s %(name)s %(levelname)s: %(message)s')
logger = logging.getLogger('filip-iot-example')

# Before running the example you should set some global variables
# Please, enter your URLs here!
CB_URL = "http://yourHost:yourPort"
IOTA_URL = "http://yourHost:yourPort"
MQTT_BROKER_URL = "//yourHost:yourPort"
DEVICE_APIKEY = 'filip-iot-example-device'
SERVICE_GROUP_APIKEY= 'filip-iot-example-service-group'
FIWARE_SERVICE = 'filip'
FIWARE_SERVICE_PATH = '/iot_examples'


if __name__ == '__main__':
    # Since we want to use the multi-tenancy concept of fiware we always start
    # with create a fiware header
    fiware_header = FiwareHeader(service=FIWARE_SERVICE,
                                 service_path=FIWARE_SERVICE_PATH)

    # First we create our device configuration using the models provided for
    # filip.models.ngsi_v2.iot

    # creating an attribute for incoming measurements from e.g. a sensor we do
    # add the metadata for units here using the unit models. You will later
    # notice that the library automatically will augment the provided
    # information about units.
    device_attr1 = DeviceAttribute(name='temperature',
                                   object_id='t',
                                   type="Number",
                                   metadata={"unit":
                                                 {"type": "Unit",
                                                  "value": {
                                                      "name": {
                                                          "type": "Text",
                                                          "value": "degree "
                                                                   "Celsius"}
                                                  }}
                                             })

    # creating a static attribute that holds additional information
    static_device_attr = StaticDeviceAttribute(name='info',
                                               type="Text",
                                               value="Filip example for virtual "
                                                     "IoT device")
    # creating a command that the IoT device will liston to
    device_command = DeviceCommand(name='heater', type="Boolean")

    # NOTE: You need to know that if you define an apikey for a single device it
    # will be only used for outgoing traffic. This is does not become very clear
    # in the official documentation.
    # https://fiware-iotagent-json.readthedocs.io/en/latest/usermanual/index.html
    device = Device(device_id='MyDevice',
                    entity_name='MyDevice',
                    entity_type='Thing2',
                    protocol='IoTA-JSON',
                    transport='MQTT',
                    apikey=DEVICE_APIKEY,
                    attributes=[device_attr1],
                    static_attributes=[static_device_attr],
                    commands=[device_command])

    # You can also add additional attributes via the Device API
    device_attr2 = DeviceAttribute(name='humidity',
                                   object_id='h',
                                   type="Number",
                                   metadata={"unitText":
                                                 {"value": "percent",
                                                  "type": "Text"}})

    device.add_attribute(attribute=device_attr2)

    # This will print our configuration that we will send
    logger.info("This is our device configuration: \n" + device.json(indent=2))

    # Send device configuration to FIWARE via the IoT-Agent. We use the general
    # ngsiv2 httpClient for this.
    # This will automatically create an data entity in the context broker and
    # make the device with it. The name of the entity will be our device_id in
    # this case for more complex configuration you need to set the entity_name
    # and entity_type in the previous Device-Model

    # in order to change the apikey of out devices for incoming data we need to
    # create a service group that our device weill be we attached to
    # NOTE: This is important in order to adjust the apikey for incoming traffic.
    service_group = ServiceGroup(service=fiware_header.service,
                                 subservice=fiware_header.service_path,
                                 apikey=SERVICE_GROUP_APIKEY,
                                 resource='/iot/json')

    # create the Http client node that once sent the device cannot be posted again
    # and you need to use the update command
    config=HttpClientConfig(cb_url=CB_URL, iota_url=IOTA_URL)
    client = HttpClient(fiware_header=fiware_header, config=config)
    client.iota.post_group(service_group=service_group, update=True)
    client.iota.post_device(device=device, update=True)

    time.sleep(1)

    # check if the device is correctly configured. You will notice that
    # unfortunately the iot API does not return all the metadata. However,
    # it will still appear in the context-entity
    device = client.iota.get_device(device_id=device.device_id)
    logger.info(f"{device.json(indent=2)}")

    # check if the data entity is created in the context broker
    entity = client.cb.get_entity(entity_id=device.device_id,
                                  entity_type=device.entity_type)
    logger.info("This is our data entity belonging to our device: \n" +
                entity.json(indent=2))

    # create a mqtt client that we use as representation of an IoT device
    # following the official documentation of Paho-MQTT.
    # https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php

    # NOTE: Since Paho-MQTT is no requirement to the library at current stage
    # you probably need need to install it first.
    #
    #   pip install paho-mqtt
    #

    # WE USE THE IMPLEMENTATION OF MQTTv5 which slightly different from former
    # versions. Especially, the arguments of the well-known function have
    # change a little. It's now more verbose than it used to be. Furthermore,
    # you have to handle the properties argument.

    # The callback for when the mqtt client receives a CONNACK response from the
    # server. All callbacks need to have this specific arguments, Otherwise the
    # client will not be able to execute them.
    def on_connect(client, userdata, flags, reasonCode, properties=None):
        if reasonCode != 0:
            logger.error(f"Connection failed with error code: '{reasonCode}'")
            raise ConnectionError
        else:
            logger.info("Successfully, connected with result code "+str(
                reasonCode))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        # We do subscribe to the topic that the platform will publish our
        # commands on
        client.subscribe(f"/{device.apikey}/{device.device_id}/cmd")

    # Callback when the command topic is successfully subscribed
    def on_subscribe(client, userdata, mid, granted_qos, properties=None):
        logger.info("Successfully subscribed to with QoS: %s", granted_qos)

    # The callback for when the device receives a PUBLISH  message like a command
    # from the server. Here, the received command will be printed and an
    # command-acknowledge will be sent to the platform.

    # NOTE: We need to use the apikey of the service-group to send the message to
    # the platform
    def on_message(client, userdata, msg):
        logger.info(msg.topic+" "+str(msg.payload))
        data = json.loads(msg.payload)
        res = {k: v for k, v in data.items()}
        print(msg.payload)
        client.publish(topic=f"/json/{service_group.apikey}"
                             f"/{device.device_id}/cmdexe",
                       payload=json.dumps(res))

    def on_disconnect(client, userdata, reasonCode):
        logger.info("MQTT client disconnected" + str(reasonCode))

    mqtt_client = mqtt.Client(client_id="filip-iot-example",
                              userdata=None,
                              protocol=mqtt.MQTTv5,
                              transport="tcp")
    # add our callbacks to the client
    mqtt_client.on_connect = on_connect
    mqtt_client.on_subscribe = on_subscribe
    mqtt_client.on_message = on_message
    mqtt_client.on_disconnect = on_disconnect
    # connect to the server
    mqtt_url = urlparse(MQTT_BROKER_URL)
    mqtt_client.connect(host=mqtt_url.hostname,
                        port=mqtt_url.port,
                        keepalive=60,
                        bind_address="",
                        bind_port=0,
                        clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY,
                        properties=None)
    # create a non-blocking thread for mqtt communication
    mqtt_client.loop_start()

    for attr in device.attributes:
        payload = json.dumps({attr.object_id: random.randint(0,9)})
        logger.info("Send data to platform:" + payload)
        mqtt_client.publish(
            topic=f"/json/{service_group.apikey}/{device.device_id}/attrs",
            payload=json.dumps({attr.object_id: random.randint(0,9)}))

    time.sleep(1)
    entity = client.cb.get_entity(entity_id=device.device_id,
                                  entity_type=device.entity_type)
    logger.info("This is updated entity status after measurements are "
                "received: \n" + entity.json(indent=2))

    # create and send a command via the context broker
    for i in range(10):
        if i % 2 == 1:
            value = True
        else:
            value = False
            
        context_command = NamedCommand(name=device_command.name,
                                       value=value)
        client.cb.post_command(entity_id=entity.id,
                               entity_type=entity.type,
                               command=context_command)

        time.sleep(1)
        # check the entity the command attribute should now show the PENDING
        entity = client.cb.get_entity(entity_id=device.device_id,
                                      entity_type=device.entity_type)
        logger.info("This is updated entity status after the command was sent "
                    "and the acknowledge message was received: "
                    "\n" + entity.json(indent=2))

    # close the mqtt listening thread
    mqtt_client.loop_stop()
    # disconnect the mqtt device
    mqtt_client.disconnect()

    # cleanup the server and delete everything
    client.iota.delete_device(device_id=device.device_id)
    client.iota.delete_group(resource=service_group.resource,
                             apikey=service_group.apikey)
    client.cb.delete_entity(entity_id=entity.id,
                            entity_type=entity.type)
