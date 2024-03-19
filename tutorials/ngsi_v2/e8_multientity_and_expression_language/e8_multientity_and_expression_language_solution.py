"""
# # Exercise 8: MultiEntity and Expression Language

# The MultiEntity plugin Allows the devices provisioned in the IoTAgent to map their
attributes to more than one entity, # declaring the target entity through the
Configuration or Device provisioning APIs.

# The IoTAgent Library provides an expression language for measurement transformation,
that can be used to adapt the # information coming from the South Bound APIs to the
information reported to the Context Broker. This is really useful # when you need to
adapt measure.

# There are available two different expression languages jexl and legacy. The
recommended language to use is jexl, # which is newer and most powerful.

# The input sections are marked with 'TODO'

# #### Steps to complete:
# 1. Setting up the expression language jexl
# 2. Applying the expression language to device attributes
# 3. Testing the expression language via MQTT messages
# 4. Applying the expression language to device attributes in a multi-entity scenario
"""
# Import packages
import time

from filip.clients.ngsi_v2 import IoTAClient, ContextBrokerClient
from filip.models.base import FiwareHeader
from filip.models.ngsi_v2.iot import (Device, ServiceGroup, TransportProtocol,
                                      PayloadProtocol, DeviceAttribute,
                                      ExpressionLanguage)
from filip.utils.cleanup import clear_all
from paho.mqtt import client as mqtt_client

# Host address of Context Broker
CB_URL = "http://localhost:1026"

# Host address of IoT-Agent
IOTA_URL = "http://localhost:4041"

# MQTT Broker
MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883

# FIWARE Service
SERVICE = 'filip_tutorial'
SERVICE_PATH = '/'

# ToDo: Change the APIKEY to something unique. This represent the "token"
#  for IoT devices to connect (send/receive data ) with the platform. In the
#  context of MQTT, APIKEY is linked with the topic used for communication.
APIKEY = 'your_apikey'

if __name__ == '__main__':
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
                                  apikey=APIKEY,
                                  expressionLanguage=ExpressionLanguage.JEXL)
    iota_client.post_group(service_group=service_group1)

    # TODO: Create a device with two attributes 'location' and 'fillingLevel' that use
    #  expressions. These attributes are based on the attributes 'longitude',
    #  'latitude' and 'level'. 'location' is an array with 'longitude' and 'latitude'.
    #  'fillingLevel' is 'level' divided by 100
    device1 = Device(device_id="waste_container_001",
                     entity_name="urn:ngsi-ld:WasteContainer:001",
                     entity_type="WasteContainer",
                     transport=TransportProtocol.MQTT,
                     protocol=PayloadProtocol.IOTA_JSON,
                     attributes=[DeviceAttribute(name="latitude", type="Number"),
                                 DeviceAttribute(name="longitude", type="Number"),
                                 DeviceAttribute(name="level", type="Number"),
                                 DeviceAttribute(name="location", type="Array",
                                                 expression="[longitude, latitude]"),
                                 DeviceAttribute(name="fillingLevel", type="Number",
                                                 expression="level / 100")
                                 ]
                     )
    iota_client.post_device(device=device1)

    # TODO: Setting expression language to JEXL at Device level with other attributes.
    #  The attribute 'value' (Number) is itself multiplied by 5. The attribute
    #  'consumption' (String) is the trimmed version of the attribute 'spaces' (String)
    device2 = Device(device_id="waste_container_002",
                     entity_name="urn:ngsi-ld:WasteContainer:002",
                     entity_type="WasteContainer",
                     transport=TransportProtocol.MQTT,
                     protocol=PayloadProtocol.IOTA_JSON,
                     expressionLanguage=ExpressionLanguage.JEXL,
                     attributes=[DeviceAttribute(name="value", type="Number",
                                                 expression="5 * value"),
                                 DeviceAttribute(name="spaces", type="String"),
                                 DeviceAttribute(name="consumption", type="String",
                                                 expression="spaces | trim")
                                 ]
                     )
    iota_client.post_device(device=device2)

    client = mqtt_client.Client()
    client.username_pw_set(username="", password="")
    client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
    client.loop_start()

    # TODO: Publish attributes 'level', 'longitude' and 'latitude' of device1
    client.publish(topic=f'/json/{APIKEY}/{device1.device_id}/attrs',
                   payload='{"level": 99, "longitude": 12.0, "latitude": 23.0}')

    # TODO: Publish attributes 'value' and 'spaces' of device2
    client.publish(topic=f'/json/{APIKEY}/{device2.device_id}/attrs',
                   payload='{"value": 10, "spaces": "     foobar    "}')

    client.disconnect()

    # TODO: Create a weather station device with multi entity attributes (Number). 'v'
    #  is multiplied by 100 and is a standard attribute. 'v1' and 'v2' are multiplied
    #  by 100 and are multi entity attributes of type SubWeatherStation. The name of
    #  each attribute is 'vol'.
    device3 = Device(device_id="weather_station_001",
                     entity_name="urn:ngsi-ld:WeatherStation:001",
                     entity_type="WeatherStation",
                     transport=TransportProtocol.MQTT,
                     protocol=PayloadProtocol.IOTA_JSON,
                     expressionLanguage=ExpressionLanguage.JEXL,
                     attributes=[DeviceAttribute(object_id="v1", name="vol", type="Number",
                                                 expression="v1*100",
                                                 entity_name="urn:ngsi-ld:SubWeatherStation:001",
                                                 entity_type="SubWeatherStation"),
                                 DeviceAttribute(object_id="v2", name="vol", type="Number",
                                                 expression="v2*100",
                                                 entity_name="urn:ngsi-ld:SubWeatherStation:002",
                                                 entity_type="SubWeatherStation"),
                                 DeviceAttribute(object_id="v", name="vol", type="Number",
                                                 expression="v*100")
                                 ]
                     )
    iota_client.post_device(device=device3)

    client = mqtt_client.Client()
    client.username_pw_set(username="", password="")
    client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
    client.loop_start()

    # TODO: Publish values to all attributes of device3
    client.publish(topic=f'/json/{APIKEY}/{device3.device_id}/attrs',
                   payload='{"v1": 10, "v2": 20, "v": 30}')

    client.disconnect()

    time.sleep(2)

    # Printing context entities of OCB
    for context_entity in cb_client.get_entity_list(entity_types=["WasteContainer",
                                                                  "WeatherStation",
                                                                  "SubWeatherStation"]):
        print(context_entity.model_dump_json(indent=4))
