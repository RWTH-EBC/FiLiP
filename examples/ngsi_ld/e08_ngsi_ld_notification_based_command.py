"""
In e08_ngsi_v2_iota_paho_mqtt, and e09_ngsi_v2_iota_filip_mqtt we have learned
how to set up the communication via MQTT for both sensors and actuators.
The solution was to rely on the IoTAgent. However, practice experiences showed
that for the communication of actuators, i.e. commands, the IoTAgent has some
limitations. For example, the IoTAgent does not support the modification of the
downlink topics and the payload format, and to connect another MQTT Broker, extra
instance of IoTAgent is needed.

Therefore, in this example, we will learn about the alternative of the previous solutions,
 i.e. how to set up the MQTT communication for actuators via Notification.

At the end of this example, you will be able to adjust the payload format to best
suit your actuators' requirements. The default payload format is a quit verbose JSON
object. With the customization, you can simplify the payload format to a simple string.
More information: https://fiware-orion.readthedocs.io/en/3.8.0/orion-api.html#custom-notifications
"""

import json
import time

from filip.clients.ngsi_ld.cb import ContextBrokerLDClient
from filip.models import FiwareLDHeader
from filip.models.ngsi_ld.subscriptions import SubscriptionLD, NotificationParams,Endpoint
from filip.models.ngsi_ld.context import ContextLDEntity
from filip.config import settings
from filip.utils.cleanup import clear_context_broker_ld
import paho.mqtt.client as mqtt
import logging


# Host address of Context Broker
CB_URL = settings.CB_URL
# Host address of the MQTT-Broker
MQTT_BROKER_URL = "mqtt://mosquitto:1883"

# FIWARE-Service
SERVICE = "filip"
# FIWARE-Service path
SERVICE_PATH = "/"

# Setting up logging
logging.basicConfig(
    level="INFO",
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
)

logger = logging.getLogger(__name__)


def set_up_mqtt_actuator(normal_topic: str, custom_topic: str):
    """
    This function sets up the MQTT actuator
    """

    def on_connect(client, userdata, flags, reasonCode, properties=None):
        if reasonCode != 0:
            logger.error(f"Connection failed with error code: " f"'{reasonCode}'")
            raise ConnectionError
        else:
            logger.info("Successfully, connected with result code " + str(reasonCode))
        client.subscribe(mqtt_topic)
        client.subscribe(mqtt_topic_custom)

    def on_subscribe(client, userdata, mid, granted_qos, properties=None):
        logger.info("Successfully subscribed to with QoS: %s", granted_qos)

    def on_message(client, userdata, msg):
        logger.info("Receive MQTT command: " + msg.topic + " " + str(msg.payload))
        if msg.topic == normal_topic:
            data = json.loads(msg.payload)
            data_pretty = json.dumps(data, indent=2)
            print(f"Actuator 1 received raw data: {data_pretty}")
            print(f"Turn toggle to: {data['data'][0]['toggle']['value']}")
            pass
        if msg.topic == custom_topic:
            print(f"Actuator 2 received raw data: {msg.payload}")
            print(f"Turn heat power to: {msg.payload.decode()}")

    def on_disconnect(client, userdata, flags, reasonCode, properties=None):
        logger.info("MQTT client disconnected with reasonCode " + str(reasonCode))

    mqtt_client = mqtt.Client(
        userdata=None,
        protocol=mqtt.MQTTv5,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        transport="tcp",
    )
    # add callbacks to the client
    mqtt_client.on_connect = on_connect
    mqtt_client.on_subscribe = on_subscribe
    mqtt_client.on_message = on_message
    mqtt_client.on_disconnect = on_disconnect

    return mqtt_client


def create_subscription(
    cbc: ContextBrokerLDClient, entity_id: str, notification: NotificationParams
):
    
    sub = SubscriptionLD(id=entity_id, notification=notification, entities=[{"type": "Room"}])
    cbc.post_subscription(sub)


if __name__ == "__main__":
    # FIWARE header
    fiware_header = FiwareLDHeader(ngsild_tenant=SERVICE)

    # Create a Context Broker Client
    cb_client = ContextBrokerLDClient(url=CB_URL, fiware_header=fiware_header)
    clear_context_broker_ld(cb_ld_client=cb_client)

    # Set up a dummy MQTT actuator
    mqtt_topic = "actuator/1"  # Topic for the actuator 1
    mqtt_topic_custom = "actuator/2"  # Topic for the actuator 2 (custom payload)

    actuator_client = set_up_mqtt_actuator(mqtt_topic, mqtt_topic_custom)
    actuator_client.connect("localhost",1883)
    actuator_client.loop_start()

    # Create entities for the actuators
    actuator_1 = ContextLDEntity(
        id="urn:ngsi-ld:actuator1", type="Actuator", toggle={"type": "Property", "value": False}
    )
    cb_client.post_entity(actuator_1)
    actuator_2 = ContextLDEntity(
        id="urn:ngsi-ld:actuator2", type="Actuator", heatPower={"type": "Property", "value": 0}
    )
    cb_client.post_entity(actuator_2)

    # Create a notification for the actuator 1 with normal payload
    notification_normal = NotificationParams(
        endpoint=Endpoint(uri=f'{MQTT_BROKER_URL}/{mqtt_topic}')
    )
    create_subscription(
        cb_client, entity_id=actuator_1.id, notification=notification_normal
    )

    # Create a subscription for the actuator 2 with custom payload
    notification_custom = NotificationParams(
        endpoint=Endpoint(uri=f'{MQTT_BROKER_URL}/{mqtt_topic_custom}',accept="application/json")
    )
    create_subscription(
        cb_client, entity_id=actuator_2.id, notification=notification_custom
    )

    # Send command to actuator 1
    actuator_1.toggle.value = True
    # Update the subscribed entity will trigger the notification
    cb_client.append_entity_attributes(entity=actuator_1)
    time.sleep(2)
    actuator_1.toggle.value = False
    cb_client.append_entity_attributes(entity=actuator_1)
    time.sleep(2)

    # Send command to actuator 2
    actuator_2.heatPower.value = 500
    # Update the subscribed entity will trigger the notification
    cb_client.append_entity_attributes(entity=actuator_1)
    time.sleep(2)

    actuator_2.heatPower.value = 1000
    cb_client.append_entity_attributes(entity=actuator_1)
    time.sleep(2)

    # Clean up
    actuator_client.loop_stop()
    actuator_client.disconnect()

    #gotta sleep here for some reason, otherwise orion restarts ( ikr ?)
    time.sleep(2)
    clear_context_broker_ld(cb_ld_client=cb_client)
