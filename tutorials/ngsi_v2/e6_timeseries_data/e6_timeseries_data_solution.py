"""
# # Exercise 6: Time Series Data

# We now want store our data in the historic data storage and visualize it

# The input sections are marked with 'ToDo'

# #### Steps to complete:
# 1. Set up the missing parameters in the parameter section
# 2. Create a quantumleap client that creates subscription that gets triggered
#    by the updates on your context entities
# 3. Run the simulation
# 4. Retrieve the data via QuantumLeap and visualize it
"""

# ## Import packages
import json
from pathlib import Path
import time
from typing import List
from urllib.parse import urlparse
from uuid import uuid4
import pandas as pd
import paho.mqtt.client as mqtt
from pydantic import TypeAdapter
import matplotlib.pyplot as plt
# import from filip
from filip.clients.ngsi_v2 import \
    ContextBrokerClient, \
    IoTAClient, \
    QuantumLeapClient
from filip.clients.mqtt import IoTAMQTTClient
from filip.models.base import FiwareHeader
from filip.models.ngsi_v2.context import NamedCommand
from filip.models.ngsi_v2.subscriptions import Subscription, Message
from filip.models.ngsi_v2.iot import \
    Device, \
    PayloadProtocol, \
    ServiceGroup
from filip.utils.cleanup import \
    clear_context_broker, \
    clear_iot_agent, \
    clear_quantumleap
# import simulation model
from tutorials.ngsi_v2.simulation_model import SimulationModel

# ## Parameters
# ToDo: Enter your context broker host and port, e.g. http://localhost:1026.
CB_URL = "http://localhost:1026"
# ToDo: Enter your IoT-Agent host and port, e.g. http://localhost:4041.
IOTA_URL = "http://localhost:4041"
# ToDo: Enter your IoT-Agent host and port, e.g. http://localhost:4041.
QL_URL = "http://localhost:8668"
# ToDo: Enter your mqtt broker url, e.g. mqtt://test.mosquitto.org:1883.
MQTT_BROKER_URL_EXPOSED = "mqtt://localhost:1883"
# ToDo: Enter your mqtt broker url, e.g. mqtt://mosquitto:1883.
MQTT_BROKER_URL_INTERNAL = "mqtt://mosquitto:1883"
# ToDo: If required, enter your username and password.
MQTT_USER = ""
MQTT_PW = ""

# ToDo: Change the name of your service to something unique. If you run
#  on a shared instance this is very important in order to avoid user
#  collisions. You will use this service through the whole tutorial.
#  If you forget to change it, an error will be raised!
# FIWARE-Service
SERVICE = 'filip_tutorial'
# FIWARE-Service path
SERVICE_PATH = '/'

# ToDo: Change the APIKEY to something unique. This represents the "token"
#  for IoT devices to connect (send/receive data) with the platform. In the
#  context of MQTT, APIKEY is linked with the topic used for communication.
APIKEY = 'your_apikey'
UNIQUE_ID = str(uuid4())
TOPIC_CONTROLLER = f"fiware_workshop/{UNIQUE_ID}/controller"
print(TOPIC_CONTROLLER)

# path to read json-files from previous exercises
READ_GROUPS_FILEPATH = \
    Path("../e5_iot_thermal_zone_control_solution_groups.json")
READ_DEVICES_FILEPATH = \
    Path("../e5_iot_thermal_zone_control_solution_devices.json")
READ_SUBSCRIPTIONS_FILEPATH = \
    Path("../e5_iot_thermal_zone_control_solution_subscriptions.json")

# opening the files
with (open(READ_GROUPS_FILEPATH, 'r') as groups_file,
      open(READ_DEVICES_FILEPATH, 'r') as devices_file,
      open(READ_SUBSCRIPTIONS_FILEPATH, 'r') as subscriptions_file):
    json_groups = json.load(groups_file)
    json_devices = json.load(devices_file)
    json_subscriptions = json.load(subscriptions_file)

# set parameters for the temperature simulation
TEMPERATURE_MAX = 10  # maximal ambient temperature
TEMPERATURE_MIN = -5  # minimal ambient temperature
TEMPERATURE_ZONE_START = 20  # start value of the zone temperature

T_SIM_START = 0  # simulation start time in seconds
T_SIM_END = 24 * 60 * 60  # simulation end time in seconds
COM_STEP = 60 * 60 * 0.25  # 15 min communication step in seconds

# ## Main script
if __name__ == '__main__':
    # create a fiware header object
    fiware_header = FiwareHeader(service=SERVICE,
                                 service_path=SERVICE_PATH)
    # clear the state of your service and scope
    clear_iot_agent(url=IOTA_URL, fiware_header=fiware_header)
    clear_context_broker(url=CB_URL, fiware_header=fiware_header)
    clear_quantumleap(url=QL_URL, fiware_header=fiware_header)

    # instantiate simulation model
    sim_model = SimulationModel(t_start=T_SIM_START,
                                t_end=T_SIM_END,
                                temp_max=TEMPERATURE_MAX,
                                temp_min=TEMPERATURE_MIN,
                                temp_start=TEMPERATURE_ZONE_START)

    # create clients and restore devices and groups from file
    groups = TypeAdapter(List[ServiceGroup]).validate_python(json_groups)
    devices = TypeAdapter(List[Device]).validate_python(json_devices)
    sub = TypeAdapter(List[Subscription]).validate_python(json_subscriptions)[0]
    sub.notification.mqtt.topic = TOPIC_CONTROLLER
    sub.notification.mqtt.user = MQTT_USER
    sub.notification.mqtt.passwd = MQTT_PW
    cbc = ContextBrokerClient(url=CB_URL, fiware_header=fiware_header)
    cbc.post_subscription(subscription=sub)
    iotac = IoTAClient(url=IOTA_URL, fiware_header=fiware_header)
    iotac.post_groups(service_groups=groups)
    iotac.post_devices(devices=devices)

    # get the group and device configurations from the server
    group = iotac.get_group(resource="/iot/json", apikey=APIKEY)
    weather_station = iotac.get_device(device_id="device:001")
    zone_temperature_sensor = iotac.get_device(device_id="device:002")
    heater = iotac.get_device(device_id="device:003")

    # create a MQTTv5 client with paho-mqtt and the known groups and
    # devices.
    mqttc = IoTAMQTTClient(protocol=mqtt.MQTTv5,
                           devices=[weather_station,
                                    zone_temperature_sensor,
                                    heater],
                           service_groups=[group])
    # ToDo: Set user data if required.
    mqttc.username_pw_set(username=MQTT_USER, password=MQTT_PW)
    # Implement a callback function that gets triggered when the
    # command is sent to the device. The incoming command should update the
    # heater attribute of the simulation model
    def on_command(client, obj, msg):
        """
        Callback for incoming commands
        """
        # Decode the message payload using the libraries builtin encoders
        apikey, device_id, payload = \
            client.get_encoder(PayloadProtocol.IOTA_JSON).decode_message(
                msg=msg)

        sim_model.heater_on = payload[heater.commands[0].name]

        # Acknowledge the command. Here commands are usually single
        # messages. The first key is equal to the commands name.
        client.publish(device_id=device_id,
                       command_name=next(iter(payload)),
                       payload=payload)

    # Add the command callback to your MQTTClient. This will get
    # triggered for the specified device_id.
    mqttc.add_command_callback(device_id=heater.device_id,
                               callback=on_command)

    # You need to implement a controller that controls the
    # heater state with respect to the zone temperature. This will be
    # implemented with asynchronous communication using MQTT-Subscriptions
    def on_measurement(client, obj, msg):
        """
        Callback for measurement notifications
        """
        message = Message.model_validate_json(msg.payload)
        updated_zone_temperature_sensor = message.data[0]

        # retrieve the value of temperature attribute
        temperature = updated_zone_temperature_sensor.temperature.value

        update = True
        if temperature <= 19:
            state = 1
        elif temperature >= 21:
            state = 0
        else:
            update = False
        # send the command to the heater entity
        if update:
            command = NamedCommand(name=heater.commands[0].name, value=state)
            cbc.post_command(entity_id=heater.entity_name,
                             entity_type=heater.entity_type,
                             command=command)

    mqttc.message_callback_add(sub=TOPIC_CONTROLLER,
                               callback=on_measurement)

    # ToDo: Create a quantumleap client.
    qlc = QuantumLeapClient(url=QL_URL, fiware_header=fiware_header)

    # ToDo: Create http subscriptions that get triggered by updates of your
    #  device attributes. Note that you can also post the same subscription
    #  by the context broker.
    qlc.post_subscription(entity_id=weather_station.entity_name,
                          entity_type=weather_station.entity_type,
                          cb_url="http://orion:1026",
                          ql_url="http://quantumleap:8668",
                          throttling=0)

    qlc.post_subscription(entity_id=zone_temperature_sensor.entity_name,
                          entity_type=zone_temperature_sensor.entity_type,
                          cb_url="http://orion:1026",
                          ql_url="http://quantumleap:8668",
                          throttling=0)

    qlc.post_subscription(entity_id=heater.entity_name,
                          entity_type=heater.entity_type,
                          cb_url="http://orion:1026",
                          ql_url="http://quantumleap:8668",
                          throttling=0)

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

    # Create a loop that publishes a message every 0.3 seconds to the broker
    # that holds the simulation time "sim_time" and the corresponding
    # temperature "temperature". You may use the `object_id`
    # or the attribute name as key in your payload.
    for t_sim in range(sim_model.t_start,
                       sim_model.t_end + int(COM_STEP),
                       int(COM_STEP)):
        # publish the simulated ambient temperature
        mqttc.publish(device_id=weather_station.device_id,
                      payload={"temperature": sim_model.t_amb,
                               "sim_time": sim_model.t_sim})

        # publish the simulated zone temperature
        mqttc.publish(device_id=zone_temperature_sensor.device_id,
                      payload={"temperature": sim_model.t_zone,
                               "sim_time": sim_model.t_sim})

        # publish the 'sim_time' for the heater device
        mqttc.publish(device_id=heater.device_id,
                      payload={"sim_time": sim_model.t_sim})

        time.sleep(0.3)
        # simulation step for next loop
        sim_model.do_step(int(t_sim + COM_STEP))
        # wait for 0.3 seconds before publishing the next values
        time.sleep(0.3)

    # close the mqtt listening thread
    mqttc.loop_stop()
    # disconnect the mqtt device
    mqttc.disconnect()

    # wait until all data is available
    time.sleep(10)

    # ToDo: Retrieve the historic data from QuantumLeap, convert them to a
    #  pandas dataframe and plot them.
    # retrieve the data for the weather station
    history_weather_station = qlc.get_entity_by_id(
        entity_id=weather_station.entity_name,
        entity_type=weather_station.entity_type,
        last_n=10000
    )

    # convert to pandas dataframe and print it
    history_weather_station = history_weather_station.to_pandas()
    print(history_weather_station)
    # drop unnecessary index levels
    history_weather_station = history_weather_station.droplevel(
        level=("entityId", "entityType"), axis=1)
    history_weather_station['sim_time'] = pd.to_numeric(
        history_weather_station['sim_time'], downcast="float")
    history_weather_station['temperature'] = pd.to_numeric(
        history_weather_station['temperature'], downcast="float")
    # ToDo: Plot the results.
    fig, ax = plt.subplots()
    ax.plot(history_weather_station['sim_time']/60,
            history_weather_station['temperature'])
    ax.title.set_text("Weather Station")
    ax.set_xlabel('time in min')
    ax.set_ylabel('ambient temperature in °C')
    plt.show()

    # ToDo: Retrieve the data for the zone temperature.
    history_zone_temperature_sensor = qlc.get_entity_by_id(
        entity_id=zone_temperature_sensor.entity_name,
        entity_type=zone_temperature_sensor.entity_type,
        last_n=10000
    )

    # ToDo: Convert to pandas dataframe and print it.
    history_zone_temperature_sensor = \
        history_zone_temperature_sensor.to_pandas()
    print(history_zone_temperature_sensor)
    # ToDo: Drop unnecessary index levels.
    history_zone_temperature_sensor = history_zone_temperature_sensor.droplevel(
        level=("entityId", "entityType"), axis=1)
    history_zone_temperature_sensor['sim_time'] = pd.to_numeric(
        history_zone_temperature_sensor['sim_time'], downcast="float")
    history_zone_temperature_sensor['temperature'] = pd.to_numeric(
        history_zone_temperature_sensor['temperature'], downcast="float")
    # ToDo: Plot the results.
    fig2, ax2 = plt.subplots()
    ax2.plot(history_zone_temperature_sensor['sim_time']/60,
             history_zone_temperature_sensor['temperature'])
    ax2.title.set_text("Zone Temperature Sensor")
    ax2.set_xlabel('time in min')
    ax2.set_ylabel('zone temperature in °C')
    plt.show()

    # ToDo: Retrieve the data for the heater.
    history_heater = qlc.get_entity_by_id(
        entity_id=heater.entity_name,
        entity_type=heater.entity_type,
        last_n=10000
    )

    # convert to pandas dataframe and print it
    history_heater = history_heater.to_pandas()
    history_heater = history_heater.replace(' ', 0)
    print(history_heater)

    # ToDo: Drop unnecessary index levels.
    history_heater = history_heater.droplevel(
        level=("entityId", "entityType"), axis=1)
    history_heater['sim_time'] = pd.to_numeric(
        history_heater['sim_time'], downcast="float")
    history_heater['heater_on_info'] = pd.to_numeric(
        history_heater['heater_on_info'], downcast="float")
    # ToDo: Plot the results.
    fig3, ax3 = plt.subplots()
    ax3.plot(history_heater['sim_time']/60,
             history_heater['heater_on_info'])
    ax3.title.set_text("Heater")
    ax3.set_xlabel('time in min')
    ax3.set_ylabel('set point')
    plt.show()

    clear_iot_agent(url=IOTA_URL, fiware_header=fiware_header)
    clear_context_broker(url=CB_URL, fiware_header=fiware_header)
    clear_quantumleap(url=QL_URL, fiware_header=fiware_header)
