"""
# # Exercise 8: MultiEntity and Expression Language

#

# The input sections are marked with 'TODO'

# #### Steps to complete:
# 1.
"""

# Import packages
import logging
import json
import time

from filip.clients.ngsi_v2 import IoTAClient
from filip.models.base import FiwareHeader, DataType
from filip.models.ngsi_v2.iot import Device, ServiceGroup, TransportProtocol, PayloadProtocol, \
    StaticDeviceAttribute, DeviceAttribute, LazyDeviceAttribute, DeviceCommand, ExpressionLanguage
from filip.utils.cleanup import clear_all
from uuid import uuid4
from paho.mqtt import client as mqtt_client

# Host address of Context Broker
CB_URL = "http://localhost:1026"

# Host address of IoT-Agent
IOTA_URL = "http://localhost:4041"

# MQTT Broker
MQTT_BROKER_URL = "127.0.0.1"
MQTT_BROKER_PORT = 1883

# FIWARE Service
SERVICE = 'filip_tutorial'
SERVICE_PATH = '/'

# Local API key
API_KEY = "localapikey"

# Setting up logging
logging.basicConfig(
    level='INFO',
    format='%(asctime)s %(name)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# FIWARE Header
fiware_header = FiwareHeader(service=SERVICE,
                             service_path=SERVICE_PATH)

# Cleanup at the beginning
clear_all(fiware_header=fiware_header, cb_url=CB_URL, iota_url=IOTA_URL)

# IoT Agent Client
iota_client = IoTAClient(url=IOTA_URL,
                         fiware_header=fiware_header)

# TODO: Setting expression language to JEXL at Service Group level
service_group1 = ServiceGroup(entity_type='Thing',
                              resource='/iot/json',
                              apikey=API_KEY,
                              expressionLanguage=ExpressionLanguage.JEXL)
iota_client.post_group(service_group=service_group1)

# TODO: Create a device with two attributes location and fillingLevel that use expressions. These attributes are based
#  on the attributes longitude, latitude and level.
device1 = Device(device_id="waste_container_001",
                 entity_name="urn:ngsi-ld:WasteContainer:001",
                 entity_type="WasteContainer",
                 transport=TransportProtocol.MQTT,
                 protocol=PayloadProtocol.IOTA_JSON,
                 attributes=[DeviceAttribute(name="latitude", type="Number"),
                             DeviceAttribute(name="longitude", type="Number"),
                             DeviceAttribute(name="level", type="Number"),
                             DeviceAttribute(name="location", type="Array", expression="[longitude, latitude]"),
                             DeviceAttribute(name="fillingLevel", type="Number", expression="level / 100")
                             ]
                 )
iota_client.post_device(device=device1)

# TODO: Setting expression language to JEXL at Device level with other attributes
device2 = Device(device_id="waste_container_002",
                 entity_name="urn:ngsi-ld:WasteContainer:002",
                 entity_type="WasteContainer",
                 transport=TransportProtocol.MQTT,
                 protocol=PayloadProtocol.IOTA_JSON,
                 expressionLanguage=ExpressionLanguage.JEXL,
                 attributes=[DeviceAttribute(name="value", type="Number", expression="5 * value"),
                             DeviceAttribute(name="spaces", type="String"),
                             DeviceAttribute(name="consumption", type="String", expression="spaces | trim")
                             ]
                 )
iota_client.post_device(device=device2)

client = mqtt_client.Client()
client.username_pw_set(username="", password="")
client.connect(MQTT_BROKER_URL, MQTT_BROKER_PORT)
client.loop_start()

# TODO: Publish attributes of device1
client.publish(topic=f'/json/{API_KEY}/{device1.device_id}/attrs',
               payload='{"level": 99, "longitude": 12.0, "latitude": 23.0}')

# TODO: Publish attributes of device2
client.publish(topic=f'/json/{API_KEY}/{device2.device_id}/attrs',
               payload='{"value": 10, "spaces": "     foobar    "}')

client.loop_stop()
