# # Exercise 3: Virtual Thermal Zone

# Create a virtual IoT device that simulates the air temperature of a
# thermal zone and publishes it via MQTT. The simulation function is already
# predefined.

# The input sections are marked with 'ToDo'

# #### Steps to complete:
# 1. Set up the missing parameters in the parameter section
# 2. Create an MQTT client using the paho-mqtt package with mqtt.Client()
# 3. Define a callback function that will be executed when the client
#    receives message on a subscribed topic. It should decode your message
#    and store the information for later in our history
# 4. Subscribe to the topic that the device will publish to
# 5. Create a function that publishes the simulated temperature via MQTT as a JSON
# 6. Run the simulation and plot

# ## Import packages
import json
import paho.mqtt.client as mqtt
from pathlib import Path
from pydantic import parse_file_as
import matplotlib.pyplot as plt
import time
from typing import List
from urllib.parse import urlparse
from uuid import uuid4
# import from filip
from filip.clients.ngsi_v2 import ContextBrokerClient, IoTAClient
from filip.clients.mqtt import IoTAMQTTClient
from filip.models.base import DataType, FiwareHeader
from filip.models.ngsi_v2.context import NamedCommand
from filip.models.ngsi_v2.subscriptions import Subscription, Message
from filip.models.ngsi_v2.iot import \
    Device, \
    DeviceCommand, \
    PayloadProtocol, \
    ServiceGroup
from filip.utils.cleanup import clear_context_broker, clear_iot_agent
# import simulation model
from tutorial.simulation_model import SimulationModel

# ## Parameters
# ToDo: Enter your context broker host and port, e.g http://localhost:1026
CB_URL = "http://localhost:1026"
# ToDo: Enter your IoT-Agent host and port, e.g mqtt://localhost:4041
IOTA_URL = "http://localhost:4041"
# ToDo: Enter your mqtt broker url, e.g mqtt://test.mosquitto.org:1883
MQTT_BROKER_URL_EXPOSED = "mqtt://localhost:1883"
# ToDo: Enter your mqtt broker url, e.g mqtt://mosquitto:1883
MQTT_BROKER_URL_INTERNAL = "mqtt://mosquitto:1883"
# FIWARE-Service
SERVICE = 'filip_tutorial'
# FIWARE-Servicepath
# ToDo: Change the name of your service-path to something unique. If you run
#  on a shared instance this very important in order to avoid user
#  collisions. You will use this service path through the whole tutorial.
#  If you forget to change it an error will be raised!
SERVICE_PATH = '/your_path'
APIKEY = SERVICE_PATH.strip('/')
UNIQUE_ID = str(uuid4())
TOPIC_CONTROLLER = f"fiware_workshop/{UNIQUE_ID}/controller"
print(TOPIC_CONTROLLER)
# Path to json-files to store entity data for follow up exercises
READ_GROUPS_FILEPATH = Path("./e4_iot_thermal_zone_sensors_solution_groups.json")
READ_DEVICES_FILEPATH = Path("./e4_iot_thermal_zone_sensors_solution_devices.json")

# set parameters for the temperature simulation
TEMPERATURE_MAX = 10  # maximal ambient temperature
TEMPERATURE_MIN = -5  # minimal ambient temperature
TEMPERATURE_ZONE_START = 20  # start value of the zone temperature

T_SIM_START = 0  # simulation start time in seconds
T_SIM_END = 24 * 60 * 60  # simulation end time in seconds
COM_STEP = 60 * 60 * 0.25 # 15 min communication step in seconds

# ## Main script
if __name__ == '__main__':
    # create a fiware header object
    fiware_header = FiwareHeader(service=SERVICE,
                                 service_path=SERVICE_PATH)
    # clear the state of your service and scope
    clear_iot_agent(url=IOTA_URL, fiware_header=fiware_header)
    clear_context_broker(url=CB_URL, fiware_header=fiware_header)


    # instantiate simulation model
    sim_model = SimulationModel(t_start=T_SIM_START,
                                t_end=T_SIM_END,
                                temp_max=TEMPERATURE_MAX,
                                temp_min=TEMPERATURE_MIN,
                                temp_start=TEMPERATURE_ZONE_START)

    # define lists to store historical data
    history_weather_station = []
    history_zone_temperature_sensor = []

    # Create clients and restore devices and groups from file
    groups = parse_file_as(List[ServiceGroup], READ_GROUPS_FILEPATH)
    devices = parse_file_as(List[Device], READ_DEVICES_FILEPATH)
    cbc = ContextBrokerClient(url=CB_URL, fiware_header=fiware_header)
    iotac = IoTAClient(url=IOTA_URL, fiware_header=fiware_header)
    iotac.post_groups(service_groups=groups)
    iotac.post_devices(devices=devices)

    # ToDo: Get the device configurations from the server
    weather_station = iotac.get_device(device_id="device:001")
    zone_temperature_sensor = iotac.get_device(device_id="device:002")

    # ToDo: Get the service group configurations from the server
    group = iotac.get_group(resource="/iot/json", apikey=APIKEY)

    # ToDo: Create and additional device holding a command attribute and
    #  post it to the IoT-Agent. It should be mapped to the `type` heater

    # ToDo: create the command attribute of name `heater_on`
    cmd = DeviceCommand(name="heater_on",
                        type=DataType.BOOLEAN)

    # ToDo: create the device configuration and send it to the server
    heater = Device(device_id="device:003",
                    entity_name="urn:ngsi-ld:Heater:001",
                    entity_type="Heater",
                    apikey=APIKEY,
                    commands=[cmd],
                    transport='MQTT',
                    protocol='IoTA-JSON')

    iotac.post_device(device=heater)

    # ToDo: create a MQTTv5 client with paho-mqtt and the known groups and
    #  devices.
    mqttc = IoTAMQTTClient(protocol=mqtt.MQTTv5,
                           devices=[weather_station,
                                    zone_temperature_sensor,
                                    heater],
                           service_groups=[group])

    # ToDo: Implement a callback function that gets triggered when the
    #  command is sent to the device. The incoming command schould update the
    #  heater attribute of the simulation model
    def on_command(client, obj, msg):
        # Decode the message payload using the libraries builtin encoders
        apikey, device_id, payload = \
            client.get_encoder(PayloadProtocol.IOTA_JSON).decode_message(
                msg=msg)

        sim_model.heater_on = payload[cmd.name]

        # ToDo: acknowledge the command. Here command are usually single
        #   messages. The first key is equal to the commands name.
        client.publish(device_id=device_id,
                       command_name=next(iter(payload)),
                       payload=payload)

    # ToDo: Add the command callback to your MQTTClient
    mqttc.add_command_callback(device_id=heater.device_id,
                               callback=on_command)

    # ToDo: Addtionally you need to implement a controller that controls the
    #  heater state with respect to the zone temperature. This will be
    #  implemented with asynchronous communication using MQTT-Subscriptions
    def on_measurement(client, obj, msg):
        message = Message.parse_raw(msg.payload)
        updated_zone_temperature_sensor = message.data[0]

        # ToDo: retrieve the value of temperature attribute
        temperature = updated_zone_temperature_sensor.temperature.value

        # ToDo: device if you want update your command
        #   Note that this could also be substitute by a conditional
        #   subscription
        update = True
        if temperature <= 19:
            state = 1
        elif temperature >= 21:
            state = 0
        else:
            update = False
        # ToDo: send the command to the heater entity
        if update:
            command = NamedCommand(name=cmd.name, value=state)
            cbc.post_command(entity_id=heater.entity_name,
                             entity_type=heater.entity_type,
                             command=command)

    mqttc.message_callback_add(sub=TOPIC_CONTROLLER,
                               callback=on_measurement)

    # create a subscription for asynchronous communication
    subscription = {
        "description": "Subscription to receive MQTT-Notifications about "
                       "urn:ngsi-ld:ThermalZone:001",
        "subject": {
            "entities": [
                {
                    "id": zone_temperature_sensor.entity_name,
                    "type": zone_temperature_sensor.entity_type
                }
            ],
        },
        "notification": {
            "mqtt": {
                "url": MQTT_BROKER_URL_INTERNAL,
                "topic": TOPIC_CONTROLLER
            }
        },
        "throttling": 0
    }
    # Generate Subscription object for validation
    subscription = Subscription(**subscription)
    subscription_id = cbc.post_subscription(subscription=subscription)

    # connect to the mqtt broker and subscribe to your topic
    mqtt_url = urlparse(MQTT_BROKER_URL_EXPOSED)
    mqttc.connect(host=mqtt_url.hostname,
                  port=mqtt_url.port,
                  keepalive=60,
                  bind_address="",
                  bind_port=0,
                  clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY,
                  properties=None)
    # subscribe to topics
    # subscribe to all incoming command topics for the registered devices
    mqttc.subscribe()
    mqttc.subscribe(topic=TOPIC_CONTROLLER)







    # create a non-blocking thread for mqtt communication
    mqttc.loop_start()

    # ToDo: Create a loop that publishes every second a message to the broker
    #  that holds the simulation time "simtime" and the corresponding
    #  temperature "temperature" the loop should. You may use the `object_id`
    #  or the attribute name as key in your payload.
    for t_sim in range(sim_model.t_start,
                       sim_model.t_end + int(COM_STEP),
                       int(COM_STEP)):
        # publish the simulated ambient temperature
        mqttc.publish(device_id=weather_station.device_id,
                      payload={"temperature": sim_model.t_amb,
                               "simtime": sim_model.t_sim})

        # ToDo: publish the simulated zone temperature
        mqttc.publish(device_id=zone_temperature_sensor.device_id,
                      payload={"temperature": sim_model.t_zone,
                               "simtime": sim_model.t_sim})

        time.sleep(0.5)
        # simulation step for next loop
        sim_model.do_step(int(t_sim + COM_STEP))
        # wait for one second before publishing the next values
        time.sleep(0.5)

        # Get corresponding entities and write values to history
        weather_station_entity = cbc.get_entity(weather_station.entity_name)
        # append the data to the local history
        history_weather_station.append(
            {"simtime": weather_station_entity.simtime.value,
             "temperature": weather_station_entity.temperature.value})

        # Get ZoneTemperatureSensor and write values to history
        zone_temperature_sensor_entity = cbc.get_entity(
            zone_temperature_sensor.entity_name)
        history_zone_temperature_sensor.append(
            {"simtime": zone_temperature_sensor_entity.simtime.value,
             "temperature": zone_temperature_sensor_entity.temperature.value})

    # close the mqtt listening thread
    mqttc.loop_stop()
    # disconnect the mqtt device
    mqttc.disconnect()

    print(cbc.get_entity(entity_id=heater.entity_name,
                         entity_type=heater.entity_type).json(indent=2))

    # plot results
    fig, ax = plt.subplots()
    t_simulation = [item["simtime"] for item in history_weather_station]
    temperature = [item["temperature"] for item in history_weather_station]
    ax.plot(t_simulation, temperature)
    ax.set_xlabel('time in s')
    ax.set_ylabel('ambient temperature in °C')

    fig2, ax2 = plt.subplots()
    t_simulation = [item["simtime"] for item in history_zone_temperature_sensor]
    temperature = [item["temperature"] for item in
                   history_zone_temperature_sensor]
    ax2.plot(t_simulation, temperature)
    ax2.set_xlabel('time in s')
    ax2.set_ylabel('zone temperature in °C')

    plt.show()

    clear_iot_agent(url=IOTA_URL, fiware_header=fiware_header)
    clear_context_broker(url=CB_URL, fiware_header=fiware_header)

