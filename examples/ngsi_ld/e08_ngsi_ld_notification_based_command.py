"""
In this example, we will learn how to set up the MQTT communication for actuators 
via Notification.

At the end of this example, you will be able to customize the payload format. 
As opposed to v2, ld notification only allow a limited number of formats: normalized and
keyValues. 
More information: 
https://fiware-tutorials.readthedocs.io/en/latest/ld-subscriptions-registrations.html#using-subscriptions-with-ngsi-ld
"""

import json
import time

from filip.clients.ngsi_ld.cb import ContextBrokerLDClient
from filip.models import FiwareLDHeader
from filip.models.ngsi_ld.subscriptions import (
    SubscriptionLD,
    NotificationParams,
    Endpoint,
)
from filip.models.ngsi_ld.context import ContextLDEntity
from filip.config import settings
from filip.utils.cleanup import clear_context_broker_ld
import paho.mqtt.client as mqtt
import logging


# Host address of Context Broker
LD_CB_URL = settings.LD_CB_URL
# Host address of the MQTT-Broker
MQTT_BROKER_URL = settings.LD_MQTT_BROKER_URL
MQTT_BROKER_URL_INTERNAL = "mqtt://mqtt-broker-ld:1883"  # TODO need to be changed if the host name is not "mqtt-broker-ld"

# NGSI-LD Tenant
NGSILD_TENANT = "filip"
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
            print(f"Turn toggle to: {data['body']['data'][0]['toggle']['value']}")
            pass
        if msg.topic == custom_topic:
            data = json.loads(msg.payload)
            # print(f"Actuator 2 received raw data: {msg.payload}")
            print(
                f"Turn heat power to: {data['body']['data'][0]['heatPower']}"
            )

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

    sub = SubscriptionLD(
        id=f"sub:{entity_id}",
        watchedAttributes=["toggle", "heatPower"],  # TODO hard code
        notification=notification,
        entities=[{"type": "Actuator", "id": entity_id}],
    )
    cbc.post_subscription(sub)


if __name__ == "__main__":
    # FIWARE header
    fiware_header = FiwareLDHeader(ngsild_tenant=NGSILD_TENANT)

    # Create a Context Broker Client
    cb_ld_client = ContextBrokerLDClient(url=LD_CB_URL, fiware_header=fiware_header)
    clear_context_broker_ld(cb_ld_client=cb_ld_client)

    # Set up a dummy MQTT actuator
    mqtt_topic = "actuator/1"  # Topic for the actuator 1
    mqtt_topic_custom = "actuator/2"  # Topic for the actuator 2 (custom payload)

    actuator_client = set_up_mqtt_actuator(mqtt_topic, mqtt_topic_custom)
    actuator_client.connect(MQTT_BROKER_URL.host, MQTT_BROKER_URL.port)
    actuator_client.loop_start()

    # Create entities for the actuators
    actuator_1 = ContextLDEntity(
        id="urn:ngsi-ld:actuator1",
        type="Actuator",
        toggle={"type": "Property", "value": False},
    )
    cb_ld_client.post_entity(actuator_1)
    actuator_2 = ContextLDEntity(
        id="urn:ngsi-ld:actuator2",
        type="Actuator",
        heatPower={"type": "Property", "value": 0},
    )
    cb_ld_client.post_entity(actuator_2)

    # Create a notification for the actuator 1 with normal payload
    notification_normal = NotificationParams(
        attributes=["toggle"],
        endpoint=Endpoint(
            uri=f"{MQTT_BROKER_URL_INTERNAL}/{mqtt_topic}",
        ),
        # accept="application/json"),
        format="normalized",  # Use normalized format for the payload
    )
    create_subscription(
        cb_ld_client, entity_id=actuator_1.id, notification=notification_normal
    )

    # Create a subscription for the actuator 2 with custom payload
    notification_custom = NotificationParams(
        attributes=["heatPower"],
        endpoint=Endpoint(
            uri=f"{MQTT_BROKER_URL_INTERNAL}/{mqtt_topic_custom}",
        ),
        # accept="application/json"),
        format="keyValues",  # Use keyValues format for the payload
    )
    create_subscription(
        cb_ld_client, entity_id=actuator_2.id, notification=notification_custom
    )

    # Send command to actuator 1
    actuator_1.toggle.value = True
    # Update the subscribed entity will trigger the notification
    cb_ld_client.append_entity_attributes(entity=actuator_1)
    time.sleep(2)
    actuator_1.toggle.value = False
    cb_ld_client.append_entity_attributes(entity=actuator_1)
    time.sleep(2)

    # Send command to actuator 2
    actuator_2.heatPower.value = 500
    # Update the subscribed entity will trigger the notification
    cb_ld_client.append_entity_attributes(entity=actuator_2)
    time.sleep(2)

    actuator_2.heatPower.value = 1000
    cb_ld_client.append_entity_attributes(entity=actuator_2)
    time.sleep(2)

    # Clean up
    actuator_client.loop_stop()
    actuator_client.disconnect()

    time.sleep(2)
    clear_context_broker_ld(cb_ld_client=cb_ld_client)
