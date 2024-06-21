"""
# Examples for subscriptions

# create new subscription following the API Walkthrough example:
# https://fiware-orion.readthedocs.io/en/master/user/walkthrough_apiv2/index.html
"""
# ## Import packages
import logging
import datetime
import time

from filip.models.ngsi_v2.subscriptions import Subscription, Mqtt, Message
from filip.clients.ngsi_v2.cb import ContextBrokerClient
from filip.models.base import FiwareHeader
from filip.models.ngsi_v2.context import ContextEntity
from urllib.parse import urlparse

# ## Parameters
#
# To run this example you need a working Fiware v2 setup with a context-broker
# You can here set the address:
#
# Host address of Context Broker
CB_URL = "http://localhost:1026"

# You can here also change the used Fiware service
# FIWARE-Service
SERVICE = 'filip'
# FIWARE-Servicepath
SERVICE_PATH = '/example'

# MQTT URL for eclipse mosquitto
MQTT_BROKER_URL_INTERNAL = "mqtt://mosquitto:1883"
MQTT_BROKER_URL_EXPOSED = "mqtt://localhost:1883"

# MQTT topic that the subscription will send to
mqtt_topic = ''.join([SERVICE, SERVICE_PATH])

# Setting up logging
logging.basicConfig(
    level='INFO',
    format='%(asctime)s %(name)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    # # 1 Setup Client
    #
    # create the client, for more details view the example: e01_http_clients.py
    fiware_header = FiwareHeader(service=SERVICE,
                                 service_path=SERVICE_PATH)
    cb_client = ContextBrokerClient(url=CB_URL,
                                    fiware_header=fiware_header)

    room_001 = {"id": "urn:ngsi-ld:Room:001",
                "type": "Room",
                "temperature": {"value": 11,
                                "type": "Float"},
                "pressure": {"value": 111,
                             "type": "Integer"}
                }
    room_entity = ContextEntity(**room_001)
    cb_client.post_entity(entity=room_entity, update=True)


    # # 2 Setup a subscription and MQTT notifications
    #
    # Create the data for the subscription. Have a look at the condition and
    # the attribute section. Only a change of the temperature attribute will
    # trigger the subscription and only temperature data will be included
    # into the message.
    # Additionally, you should be aware of the throttling and expiration of a
    # subscription.
    #
    # For more details on subscription you might want to
    # check the Subscription model or the official tutorials.
    sub_example = {
        "description": "Subscription to receive MQTT-Notifications about "
                       "urn:ngsi-ld:Room:001",
        "subject": {
            "entities": [
                {
                    "id": "urn:ngsi-ld:Room:001",
                    "type": "Room"
                }
            ],
            "condition": {
                "attrs": [
                    "temperature"
                ]
            }
        },
        "notification": {
            "mqtt": {
                "url": MQTT_BROKER_URL_INTERNAL,
                "topic": mqtt_topic
            },
            "attrs": [
                "temperature"
            ]
        },
        "expires": datetime.datetime.now() + datetime.timedelta(minutes=15),
        "throttling": 0
    }
    # Generate Subscription object for validation
    sub = Subscription(**sub_example)

    # Posting an example subscription for Room1. Make sure that you store the
    # returned id because you might need for later updates of the subscription.
    sub_id = cb_client.post_subscription(subscription=sub)

    # # 3 setup callbacks and the MQTT client
    #
    # define callbacks for the mqtt client. They will be triggered by
    # different events. Do not change their signature!
    def on_connect(client, userdata, flags, reasonCode, properties=None):
        if reasonCode != 0:
            logger.error(f"Connection failed with error code: "
                         f"'{reasonCode}'")
            raise ConnectionError
        else:
            logger.info("Successfully, connected with result code " + str(
                reasonCode))
        client.subscribe(mqtt_topic)

    def on_subscribe(client, userdata, mid, granted_qos, properties=None):
        logger.info("Successfully subscribed to with QoS: %s", granted_qos)


    def on_message(client, userdata, msg):
        message = Message.parse_raw(msg.payload)
        logger.info("Received this message:\n" + message.json(indent=2))


    def on_disconnect(client, userdata, flags, reasonCode, properties=None):
        logger.info("MQTT client disconnected with reasonCode "
                    + str(reasonCode))

    # MQTT client
    import paho.mqtt.client as mqtt

    mqtt_client = mqtt.Client(userdata=None,
                              protocol=mqtt.MQTTv5,
                              callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                              transport="tcp")
    # add callbacks to the mqtt-client
    mqtt_client.on_connect = on_connect
    mqtt_client.on_subscribe = on_subscribe
    mqtt_client.on_message = on_message
    mqtt_client.on_disconnect = on_disconnect

    # connect to the mqtt-broker to receive the notifications message
    mqtt_url = urlparse(MQTT_BROKER_URL_EXPOSED)
    mqtt_client.connect(host=mqtt_url.hostname,
                        port=mqtt_url.port,
                        keepalive=60,
                        bind_address="",
                        bind_port=0,
                        clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY,
                        properties=None)

    # # 4 send new value via MQTT
    #
    # create a non-blocking thread for mqtt communication
    mqtt_client.loop_start()
    new_value = 55

    cb_client.update_attribute_value(entity_id='urn:ngsi-ld:Room:001',
                                     attr_name='temperature',
                                     value=new_value,
                                     entity_type='Room')
    cb_client.update_attribute_value(entity_id='urn:ngsi-ld:Room:001',
                                     attr_name='pressure',
                                     value=new_value,
                                     entity_type='Room')
    time.sleep(1)

    # # 5 Deleting the example entity and the subscription
    #
    cb_client.delete_subscription(sub_id)
    cb_client.delete_entity(entity_id=room_entity.id,
                            entity_type=room_entity.type)
    # # 6 Clean up (Optional)
    #
    # Close clients
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    cb_client.close()
