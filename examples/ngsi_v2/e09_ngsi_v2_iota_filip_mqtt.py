"""
# This example shows in more detail how to interact with a device over MQTT
# using FiLiP's IoTA-MQTT Client. This client comes along with a convenient
# API for handling MQTT communication with FIWARE's IoT-Agent
"""
# ## Import packages
import logging
import random
import time
import paho.mqtt.client as mqtt

from urllib.parse import urlparse
from filip.clients.mqtt import IoTAMQTTClient
from filip.models import FiwareHeader
from filip.models.ngsi_v2.iot import \
    Device, \
    DeviceAttribute, \
    DeviceCommand, \
    ServiceGroup, \
    PayloadProtocol
from filip.models.ngsi_v2.context import NamedCommand

# ## Parameters
#
# To run this example you need a working Fiware v2 setup with a
# context-broker, an IoT-Agent and mqtt-broker. You can here set the
# addresses:
#
# Host address of Context Broker
CB_URL = "http://localhost:1026"
# Host address of IoT-Agent
IOTA_URL = "http://localhost:4041"
# Host address of the MQTT-Broker
MQTT_BROKER_URL = "mqtt://localhost:1883"

# You can here also change the used Fiware service
# FIWARE-Service
SERVICE = 'filip'
# FIWARE-Servicepath
SERVICE_PATH = '/example'

# You may also change the ApiKey Information
# ApiKey of the ServiceGroup
SERVICE_GROUP_APIKEY = 'filip-example-service-group'


# Setting up logging
logging.basicConfig(
    level='INFO',
    format='%(asctime)s %(name)s %(levelname)s: %(message)s')

logger = logging.getLogger(__name__)

if __name__ == '__main__':

    # # 1 Setup
    #
    # ## 1.1 FiwareHeader
    #
    # Since we want to use the multi-tenancy concept of fiware we always start
    # with create a fiware header
    fiware_header = FiwareHeader(service=SERVICE,
                                 service_path=SERVICE_PATH)

    # ## 1.2 Device configuration
    #
    service_group_json = ServiceGroup(
        apikey=SERVICE_PATH.strip('/'),
        resource="/iot/json")
    service_group_ul = ServiceGroup(
        apikey=SERVICE_PATH.strip('/'),
        resource="/iot/d")

    device_attr = DeviceAttribute(name='temperature',
                                  object_id='t',
                                  type="Number")
    device_command = DeviceCommand(name='heater', type="Boolean")

    device_json = Device(device_id='my_json_device',
                         entity_name='my_json_device',
                         entity_type='Thing',
                         protocol='IoTA-JSON',
                         transport='MQTT',
                         apikey=service_group_json.apikey,
                         attributes=[device_attr],
                         commands=[device_command])

    device_ul = Device(device_id='my_ul_device',
                       entity_name='my_ul_device',
                       entity_type='Thing',
                       protocol='PDI-IoTA-UltraLight',
                       transport='MQTT',
                       apikey=service_group_ul.apikey,
                       attributes=[device_attr],
                       commands=[device_command])

    # ## 1.3 IoTAMQTTClient
    #
    mqttc = IoTAMQTTClient()

    def on_connect(mqttc, obj, flags, rc, properties=None):
        mqttc.logger.info("rc: " + str(rc))

    def on_connect_fail(mqttc, obj):
        mqttc.logger.info("Connect failed")

    def on_publish(mqttc, obj, mid,rc,properties=None):
        mqttc.logger.info("mid: " + str(mid))

    def on_subscribe(mqttc, obj, mid, granted_qos,properties=None):
        mqttc.logger.info("Subscribed: " + str(mid)
                          + " " + str(granted_qos))

    def on_log(mqttc, obj, level, string):
        mqttc.logger.info(string)


    mqttc.on_connect = on_connect
    mqttc.on_connect_fail = on_connect_fail
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    mqttc.on_log = on_log

    # # 2 Normal client behaviour
    #
    # this section demonstrates normal client behavior
    # For additional examples on how to use the client please check:
    # https://github.com/eclipse/paho.mqtt.python/tree/master/examples
    #
    first_topic = f"/filip/{SERVICE_PATH.strip('/')}/first"
    second_topic = f"/filip/{SERVICE_PATH.strip('/')}/second"
    first_payload = "filip_test_1"
    second_payload = "filip_test_2"


    def on_message_first(mqttc, obj, msg, properties=None):
        pass
        # do something

    def on_message_second(mqttc, obj, msg, properties=None):
        pass
        # do something


    mqttc.message_callback_add(sub=first_topic,
                               callback=on_message_first)
    mqttc.message_callback_add(sub=second_topic,
                               callback=on_message_second)
    mqtt_broker_url = urlparse(MQTT_BROKER_URL)

    mqttc.connect(host=mqtt_broker_url.hostname,
                  port=mqtt_broker_url.port,
                  keepalive=60,
                  bind_address="",
                  bind_port=0,
                  clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY,
                  properties=None)
    mqttc.subscribe(topic=first_topic)

    # create a non blocking loop
    mqttc.loop_start()
    mqttc.publish(topic=first_topic, payload="filip_test")

    # add additional subscription to connection
    mqttc.subscribe(topic=second_topic)
    mqttc.publish(topic=second_topic, payload="filip_test")

    # remove subscriptions and callbacks
    mqttc.message_callback_remove(first_topic)
    mqttc.message_callback_remove(second_topic)
    mqttc.unsubscribe(first_topic)
    mqttc.unsubscribe(second_topic)

    # stop network loop and disconnect cleanly
    # close the mqtt listening thread
    mqttc.loop_stop()
    # disconnect the mqtt device
    mqttc.disconnect()

    # # 3 Devices provisioning
    #
    # ## 3.1 Service groups
    #
    # ### 3.1.1 create service Groups
    #
    mqttc.add_service_group(service_group=service_group_json)

    # ### 3.1.2 Interact with service groups
    #
    mqttc.get_service_group(service_group_json.apikey)
    mqttc.update_service_group(service_group=service_group_json)

    # ### 3.1.2 Delete service groups
    #
    mqttc.delete_service_group(apikey=service_group_json.apikey)

    # ## 3.2 Devices
    #
    # ### 3.2.1 Create Device
    #
    mqttc.add_device(device=device_json)

    # ### 3.2.2 Interact with device
    #
    mqttc.get_device(device_json.device_id)
    mqttc.update_device(device=device_json)

    # ### 3.2.3 Delete device
    #
    mqttc.delete_device(device_id=device_json.device_id)

    # # 4 Commands
    #
    # This example is written for the JSON MQTT client, but it can be easily
    # adapted for Ultralight, by changing all JSON/json variable name parts
    # with the corresponding UL/ul parts
    #
    # ## 4.1 Setup MQTT client
    #
    # small clean up
    for group in mqttc.service_groups:
        mqttc.delete_service_group(group.apikey)

    for device in mqttc.devices:
        mqttc.delete_device(device.device_id)


    def on_command(client, obj, msg):
        apikey, device_id, payload = \
            client.get_encoder(PayloadProtocol.IOTA_JSON).decode_message(
                msg=msg)

        # acknowledge a command. Here command are usually single
        # messages. The first key is equal to the commands name.
        client.publish(device_id=device_id,
                       command_name=next(iter(payload)),
                       payload=payload)


    mqttc.add_service_group(service_group_json)
    mqttc.add_device(device_json)
    mqttc.add_command_callback(device_id=device_json.device_id,
                               callback=on_command)

    from filip.clients.ngsi_v2 import HttpClient, HttpClientConfig

    httpc_config = HttpClientConfig(cb_url=CB_URL,
                                    iota_url=IOTA_URL)
    httpc = HttpClient(fiware_header=fiware_header,
                       config=httpc_config)
    httpc.iota.post_group(service_group=service_group_json, update=True)
    httpc.iota.post_device(device=device_json, update=True)

    mqtt_broker_url = urlparse(MQTT_BROKER_URL)

    mqttc.connect(host=mqtt_broker_url.hostname,
                  port=mqtt_broker_url.port,
                  keepalive=60,
                  bind_address="",
                  bind_port=0,
                  clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY,
                  properties=None)
    mqttc.subscribe()
    mqttc.loop_start()

    # ## 4.2 Command
    #
    entity = httpc.cb.get_entity(entity_id=device_json.device_id,
                                 entity_type=device_json.entity_type)
    context_command = NamedCommand(name=device_json.commands[0].name,
                                   value=False)

    httpc.cb.post_command(entity_id=entity.id,
                          entity_type=entity.type,
                          command=context_command)

    time.sleep(2)

    entity = httpc.cb.get_entity(entity_id=device_json.device_id,
                                 entity_type=device_json.entity_type)

    # The entity.heater_status.value should now have the status ok
    print(entity.heater_status.value)

    # ## 4.3 Publish
    #
    payload = random.randrange(0, 100, 1) / 1000
    mqttc.publish(device_id=device_json.device_id,
                  payload={device_json.attributes[0].object_id: payload})
    time.sleep(1)
    entity = httpc.cb.get_entity(entity_id=device_json.device_id,
                                 entity_type=device_json.entity_type)

    # Set Temperature Value
    print(entity.temperature.value)

    payload = random.randrange(0, 100, 1) / 1000
    mqttc.publish(device_id=device_json.device_id,
                  attribute_name="temperature",
                  payload=payload)
    time.sleep(1)
    entity = httpc.cb.get_entity(entity_id=device_json.device_id,
                                 entity_type=device_json.entity_type)
    # Changed Temperature Value
    print(entity.temperature.value)

    # ## 4.4 Close Client

    # stop network loop and disconnect cleanly
    # close the mqtt listening thread
    mqttc.loop_stop()
    # disconnect the mqtt device
    mqttc.disconnect()
