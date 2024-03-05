"""
# # Exercise 8: MultiEntity and Expression Language

#

# The input sections are marked with 'TODO'

# #### Steps to complete:
# 1.
"""
# Import packages
import logging
import time

from filip.clients.ngsi_v2 import IoTAClient, ContextBrokerClient
from filip.models.base import FiwareHeader
from filip.models.ngsi_v2.iot import (Device, ServiceGroup, TransportProtocol, PayloadProtocol, DeviceAttribute,
                                      ExpressionLanguage)
from filip.utils.cleanup import clear_all
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
fiware_header = FiwareHeader(service=SERVICE, service_path=SERVICE_PATH)

# Cleanup at the beginning
clear_all(fiware_header=fiware_header, cb_url=CB_URL, iota_url=IOTA_URL)

# IoT Agent and OCB Client
iota_client = IoTAClient(url=IOTA_URL, fiware_header=fiware_header)
cb_client = ContextBrokerClient(url=CB_URL, fiware_header=fiware_header)

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

# time.sleep(2)

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

client.disconnect()

# TODO: Create a weather station device with multi entity attributes
device3 = Device(device_id="weather_station_001",
                 entity_name="urn:ngsi-ld:WeatherStation:001",
                 entity_type="WeatherStation",
                 transport=TransportProtocol.MQTT,
                 protocol=PayloadProtocol.IOTA_JSON,
                 expressionLanguage=ExpressionLanguage.JEXL,
                 attributes=[DeviceAttribute(object_id="v1", name="vol", type="Number", expression="v1*100",
                                             entity_name="urn:ngsi-ld:SubWeatherStation:001",
                                             entity_type="SubWeatherStation"),
                             DeviceAttribute(object_id="v2", name="vol", type="Number", expression="v2*100",
                                             entity_name="urn:ngsi-ld:SubWeatherStation:002",
                                             entity_type="SubWeatherStation"),
                             DeviceAttribute(object_id="v", name="vol", type="Number", expression="v*100")
                             ]
                 )
iota_client.post_device(device=device3)

# time.sleep(2)

client = mqtt_client.Client()
client.username_pw_set(username="", password="")
client.connect(MQTT_BROKER_URL, MQTT_BROKER_PORT)
client.loop_start()

# TODO: Publish values to (multi entity) attributes of device3
client.publish(topic=f'/json/{API_KEY}/{device3.device_id}/attrs',
               payload='{"v1": 10, "v2": 20, "v": 30}')

client.disconnect()

time.sleep(2)

# Printing context entities of OCB
for context_entity in cb_client.get_entity_list(entity_types=["WasteContainer", "WeatherStation", "SubWeatherStation"]):
    logger.info(context_entity.model_dump_json(indent=4))
