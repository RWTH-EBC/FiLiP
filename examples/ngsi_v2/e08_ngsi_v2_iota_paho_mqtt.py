"""
# This example shows how to provision a virtual iot device in a FIWARE-based
# IoT Platform using FiLiP and PahoMQTT
"""
# ## Import packages
import json
import logging
import random
import time
import paho.mqtt.client as mqtt

from urllib.parse import urlparse
from filip.config import settings
from filip.models import FiwareHeader
from filip.models.ngsi_v2.iot import \
    Device, \
    DeviceAttribute, \
    DeviceCommand, \
    ServiceGroup, \
    StaticDeviceAttribute
from filip.models.ngsi_v2.context import NamedCommand
from filip.clients.ngsi_v2 import HttpClient, HttpClientConfig

# ## Parameters
#
# To run this example you need a working Fiware v2 setup with a
# context-broker, an IoT-Agent and mqtt-broker. Here you can set the
# addresses:
#
# Host address of Context Broker
CB_URL = settings.CB_URL
# Host address of IoT-Agent
IOTA_URL = settings.IOTA_URL
# Host address of the MQTT-Broker
MQTT_BROKER_URL = settings.MQTT_BROKER_URL

# Here you can also change the used Fiware service
# FIWARE-Service
SERVICE = 'filip'
# FIWARE-Service path
SERVICE_PATH = '/example'

# You may also change the ApiKey Information
# ApiKey of the Device
DEVICE_APIKEY = 'filip-example-device'
# ApiKey of the ServiceGroup
SERVICE_GROUP_APIKEY = 'filip-example-service-group'

# Setting up logging
logging.basicConfig(
    level='INFO',
    format='%(asctime)s %(name)s %(levelname)s: %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S')

logger = logging.getLogger(__name__)

if __name__ == '__main__':

    # # 1 FiwareHeader
    # Since we want to use the multi-tenancy concept of fiware we always start
    # with creating a fiware header
    fiware_header = FiwareHeader(service=SERVICE,
                                 service_path=SERVICE_PATH)

    # # 2 Setup
    #
    # ## 2.1 Device creation
    #
    # First we create our device configuration using the models provided for
    # filip.models.ngsi_v2.iot

    # Creating an attribute for incoming measurements from e.g. a sensor. We
    # add the metadata for units using the unit models. You will later
    # notice that the library automatically augments the provided
    # information about units.
    device_attr1 = DeviceAttribute(name='temperature',
                                   object_id='t',
                                   type="Number",
                                   metadata={"unit":
                                                 {"type": "Unit",
                                                  "value": {
                                                      "name": "degree Celsius"
                                                 }
                                                  }
                                             })

    # creating a static attribute that holds additional information
    static_device_attr = StaticDeviceAttribute(name='info',
                                               type="Text",
                                               value="Filip example for "
                                                     "virtual IoT device")
    # creating a command that the IoT device will liston to
    device_command = DeviceCommand(name='heater')

    # NOTE: You need to know that if you define an apikey for a single device it
    # will be only used for outgoing traffic. This is not clearly defined
    # in the official documentation.
    # https://fiware-iotagent-json.readthedocs.io/en/latest/usermanual/index.html
    device = Device(device_id='urn:ngsi-ld:device:001',
                    entity_name='urn:ngsi-ld:device:001',
                    entity_type='Thing',
                    protocol='IoTA-JSON',
                    transport='MQTT',
                    apikey=DEVICE_APIKEY,
                    attributes=[device_attr1],
                    static_attributes=[static_device_attr],
                    commands=[device_command])

    # you can also add additional attributes via the Device API
    device_attr2 = DeviceAttribute(name='humidity',
                                   object_id='h',
                                   type="Number",
                                   metadata={"unitText":
                                                 {"value": "percent",
                                                  "type": "Text"}})

    device.add_attribute(attribute=device_attr2)

    # this will print our configuration that we will send
    logging.info("This is our device configuration: \n" + device.model_dump_json(indent=2))

    # ## 2.2 Device Provision
    #
    # Send the device configuration to FIWARE via the IoT-Agent. We use the general
    # ngsiv2 httpClient.
    # This will automatically create a data entity in the context broker and
    # make the device with it. The id of the entity in the context broker will
    # be our entity_name of the device in this case.
    # For more complex configuration you need to set the entity_name
    # and entity_type in the previous Device-Model.

    # In order to change the apikey of our devices for incoming data we need to
    # create a service group that our device will be we attached to.
    # NOTE: This is important in order to adjust the apikey for incoming traffic.
    service_group = ServiceGroup(service=fiware_header.service,
                                 subservice=fiware_header.service_path,
                                 apikey=SERVICE_GROUP_APIKEY,
                                 resource='/iot/json')

    # Create the Http client node that once sent, the device can't be posted
    # again, and you need to use the update command.
    config = HttpClientConfig(cb_url=CB_URL, iota_url=IOTA_URL)
    client = HttpClient(fiware_header=fiware_header, config=config)
    client.iota.post_group(service_group=service_group, update=True)
    client.iota.post_device(device=device, update=True)

    # ## 2.3 Check for correctness
    # Check if the device is correctly configured. You will notice that
    # unfortunately the iot API does not return all the metadata. However,
    # it will still appear in the context-entity.
    device = client.iota.get_device(device_id=device.device_id)
    logging.info(f"{device.model_dump_json(indent=2)}")

    # check if the data entity is created in the context broker
    entity = client.cb.get_entity(entity_type=device.entity_type,
                                  entity_id=device.device_id)
    logging.info("This is our data entity in the context broker belonging to our device: \n" +
                 entity.model_dump_json(indent=2))

    # # 3 MQTT Client
    #
    # Create a mqtt client that we use as representation of an IoT device
    # following the official documentation of Paho-MQTT.
    # https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php

    # We use the implementation of MQTTv5 which is slightly different from former
    # versions. Especially the arguments of the well-known function have
    # changed. It's now more verbose than it used to be. Furthermore,
    # you have to handle the 'properties' argument.

    # The callback for when the mqtt client receives a CONNACK response from the
    # server. All callbacks need to have this specific arguments, Otherwise the
    # client will not be able to execute them.
    def on_connect(client, userdata, flags, reason_code, properties=None):
        if reason_code != 0:
            logger.error(f"MQTT Client failed to connect with the error code: '{reason_code}'")
            raise ConnectionError
        else:
            logger.info(f"MQTT Client successfully connected with the reason code: {reason_code}")

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        # We do subscribe to the topic that the platform will publish our
        # commands on
        client.subscribe(f"/{device.apikey}/{device.device_id}/cmd")

    # Callback when the command topic is successfully subscribed
    def on_subscribe(client, userdata, mid, granted_qos, properties=None):
        logger.info(f"MQTT Client successfully subscribed: {granted_qos[0]}")

    # The callback for when the device receives a PUBLISH message like a
    # command from the server. Here, the received command will be printed and a
    # command-acknowledge will be sent to the platform.

    # NOTE: We need to use the apikey of the service-group to send the message
    # to the platform
    def on_message(client, userdata, msg):
        logger.info(msg.topic + " " + str(msg.payload))
        data = json.loads(msg.payload)
        res = {k: v for k, v in data.items()}
        print(f"MQTT Client on_message payload: {msg.payload}")
        client.publish(topic=f"/json/{service_group.apikey}"
                             f"/{device.device_id}/cmdexe",
                       payload=json.dumps(res))

    def on_disconnect(client, userdata, reason_code, properties):
        logger.info(f"MQTT Client disconnected with the reason code: {reason_code}")

    mqtt_client = mqtt.Client(client_id="filip-iot-example",
                              userdata=None,
                              protocol=mqtt.MQTTv5,
                              transport="tcp")
    # bind callbacks to the client
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
        random_number = random.randint(0, 9)
        payload = json.dumps({attr.object_id: random_number})
        logger.info("Send data to platform:" + payload)
        mqtt_client.publish(
            topic=f"/json/{service_group.apikey}/{device.device_id}/attrs",
            payload=payload)

    time.sleep(1)
    entity = client.cb.get_entity(entity_id=device.device_id,
                                  entity_type=device.entity_type)
    logger.info("This is updated entity status after measurements are "
                "received: \n" + entity.model_dump_json(indent=2))

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
                    "\n" + entity.model_dump_json(indent=2))

    # close the mqtt listening thread
    mqtt_client.loop_stop()
    # disconnect the mqtt device
    mqtt_client.disconnect()

    # # 4 Cleanup the server and delete everything
    #
    client.iota.delete_device(device_id=device.device_id)
    client.iota.delete_group(resource=service_group.resource,
                             apikey=service_group.apikey)
    client.cb.delete_entity(entity_id=entity.id,
                            entity_type=entity.type)
