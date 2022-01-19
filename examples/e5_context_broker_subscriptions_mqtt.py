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
MQTT_BROKER_URL = "mqtt://mosquitto:1883"

MQTT_BROKER_URL_LOCAL = "mqtt://localhost:1883"
# MQTT topic
mqtt_topic = ''.join([SERVICE,
                          SERVICE_PATH])

# Setting up logging
logging.basicConfig(
    level='INFO',
    format='%(asctime)s %(name)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # # 1 Setup Client
    #
    # create the client, for more details view the example: e1_http_clients.py
    fiware_header = FiwareHeader(service=SERVICE,
                                 service_path=SERVICE_PATH)
    cb_client = ContextBrokerClient(url=CB_URL,
                                    fiware_header=fiware_header)

    # # 2 Setup a subscription and MQTT notifications
    #
    sub_example = {
        "description": "A subscription to get info about Room1",
        "subject": {
            "entities": [
                {
                    "id": "Room1",
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
            "mqtt":
                Mqtt(url=MQTT_BROKER_URL, topic=mqtt_topic)
            ,
            "attrs": [
                "temperature"
            ]
        },
        "expires": datetime.datetime.now() + datetime.timedelta(minutes=15),
        "throttling": 0
    }
    sub = Subscription(**sub_example)

    # setup MQTT notifications
    # notification = sub.notification.copy(
    #     update={'http': None, 'mqtt': Mqtt(url=MQTT_BROKER_URL,
    #                                        topic=mqtt_topic)})
    # subscription = sub.copy(
    #     update={'notification': notification,
    #             'description': 'MQTT test subscription',
    #             'expires': None})

    # Posting an example subscription for Room1
    sub_id = cb_client.post_subscription(subscription=sub)

    # # 3 setup callbacks and the MQTT client
    #
    # callbacks
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
        sub_message = Message.parse_raw(msg.payload)
        logger.info("Received this message: " + str(sub_message))


    def on_disconnect(client, userdata, reasonCode, properties=None):
        logger.info("MQTT client disconnected with reasonCode "
                    + str(reasonCode))

    # MQTT client
    import paho.mqtt.client as mqtt

    mqtt_client = mqtt.Client(userdata=None,
                              protocol=mqtt.MQTTv5,
                              transport="tcp")
    # add callbacks to the client
    mqtt_client.on_connect = on_connect
    mqtt_client.on_subscribe = on_subscribe
    mqtt_client.on_message = on_message
    mqtt_client.on_disconnect = on_disconnect

    # connect to the server
    mqtt_url = urlparse(MQTT_BROKER_URL_LOCAL)
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

    print(cb_client.get_entity_list())

    cb_client.update_attribute_value(entity_id='Room1',
                                     attr_name='temperature',
                                     value=new_value,
                                     entity_type='Room')
    cb_client.update_attribute_value(entity_id='Room1',
                                     attr_name='pressure',
                                     value=new_value,
                                     entity_type='Room')

    print(cb_client.get_entity_list())
    time.sleep(1)

    # # 5 Deleting the example subscription
    #
    cb_client.delete_subscription(sub_id)

    # # 6 Clean up (Optional)
    #
    # Close clients
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    cb_client.close()
