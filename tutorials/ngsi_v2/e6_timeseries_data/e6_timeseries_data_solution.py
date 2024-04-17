"""
# # Exercise 6: Time Series Data

# We now want store our data in the historic data storage and visualize it

# The input sections are marked with 'ToDo'

# #### Steps to complete:
# 1. Set up the missing parameters in the parameter section
# 2. Create a quantumleap client that create subscription that get triggered
#    by the updates on your context entities
# 3. Run the simulation
# 4. Retrieve the data via QuantumLeap and visualize it
"""

# ## Import packages
from pathlib import Path
import time
from typing import List
from urllib.parse import urlparse
from uuid import uuid4
import pandas as pd
import paho.mqtt.client as mqtt
from pydantic import parse_file_as
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
# ToDo: Enter your context broker host and port, e.g http://localhost:1026
CB_URL = "http://localhost:1026"
# ToDo: Enter your IoT-Agent host and port, e.g http://localhost:4041
IOTA_URL = "http://localhost:4041"
# ToDo: Enter your IoT-Agent host and port, e.g http://localhost:4041
QL_URL = "http://localhost:8668"
# ToDo: Enter your mqtt broker url, e.g mqtt://test.mosquitto.org:1883
MQTT_BROKER_URL_EXPOSED = "mqtt://localhost:1883"
# ToDo: Enter your mqtt broker url, e.g mqtt://mosquitto:1883
MQTT_BROKER_URL_INTERNAL = "mqtt://mosquitto:1883"
# ToDo: If required enter your username and password
MQTT_USER = ""
MQTT_PW =  ""

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

# Path to read json-files from previous exercises
READ_GROUPS_FILEPATH = \
    Path("../e5_iot_thermal_zone_control_solution_groups.json")
READ_DEVICES_FILEPATH = \
    Path("../e5_iot_thermal_zone_control_solution_devices.json")
READ_SUBSCRIPTIONS_FILEPATH = \
    Path("../e5_iot_thermal_zone_control_solution_subscriptions.json")

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
    clear_quantumleap(url=QL_URL, fiware_header=fiware_header)

    # instantiate simulation model
    sim_model = SimulationModel(t_start=T_SIM_START,
                                t_end=T_SIM_END,
                                temp_max=TEMPERATURE_MAX,
                                temp_min=TEMPERATURE_MIN,
                                temp_start=TEMPERATURE_ZONE_START)

    # Create clients and restore devices and groups from file
    groups = parse_file_as(List[ServiceGroup], READ_GROUPS_FILEPATH)
    devices = parse_file_as(List[Device], READ_DEVICES_FILEPATH)
    sub = parse_file_as(List[Subscription], READ_SUBSCRIPTIONS_FILEPATH)[0]
    sub.notification.mqtt.topic = TOPIC_CONTROLLER
    sub.notification.mqtt.user = MQTT_USER
    sub.notification.mqtt.passwd = MQTT_PW
    cbc = ContextBrokerClient(url=CB_URL, fiware_header=fiware_header)
    cbc.post_subscription(subscription=sub)
    iotac = IoTAClient(url=IOTA_URL, fiware_header=fiware_header)
    iotac.post_groups(service_groups=groups)
    iotac.post_devices(devices=devices)

    # Get the group and device configurations from the server
    group = iotac.get_group(resource="/iot/json", apikey=APIKEY)
    weather_station = iotac.get_device(device_id="device:001")
    zone_temperature_sensor = iotac.get_device(device_id="device:002")
    heater = iotac.get_device(device_id="device:003")

    # create a MQTTv5 client with paho-mqtt and the known groups and
    #  devices.
    mqttc = IoTAMQTTClient(protocol=mqtt.MQTTv5,
                           devices=[weather_station,
                                    zone_temperature_sensor,
                                    heater],
                           service_groups=[group])
    # ToDo: set user data if required
    mqttc.username_pw_set(username=MQTT_USER, password=MQTT_PW)
    # Implement a callback function that gets triggered when the
    #  command is sent to the device. The incoming command schould update the
    #  heater attribute of the simulation model
    def on_command(client, obj, msg):
        """
        Callback for incoming commands
        """
        # Decode the message payload using the libraries builtin encoders
        apikey, device_id, payload = \
            client.get_encoder(PayloadProtocol.IOTA_JSON).decode_message(
                msg=msg)

        sim_model.heater_on = payload[heater.commands[0].name]

        # acknowledge the command. Here command are usually single
        #   messages. The first key is equal to the commands name.
        client.publish(device_id=device_id,
                       command_name=next(iter(payload)),
                       payload=payload)

    # Add the command callback to your MQTTClient. This will get
    #  triggered for the specified device_id
    mqttc.add_command_callback(device_id=heater.device_id,
                               callback=on_command)

    # You need to implement a controller that controls the
    #  heater state with respect to the zone temperature. This will be
    #  implemented with asynchronous communication using MQTT-Subscriptions
    def on_measurement(client, obj, msg):
        """
        Callback for measurement notifications
        """
        message = Message.parse_raw(msg.payload)
        updated_zone_temperature_sensor = message.data[0]

        # retrieve the value of temperature attribute
        temperature = updated_zone_temperature_sensor.temperature.value

        # device if you want update your command
        # Note that this could also be substitute by a conditional
        # subscription
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

    # ToDo: create a quantumleap client
    qlc = QuantumLeapClient(url=QL_URL, fiware_header=fiware_header)

    # ToDO: create a http subscriptions that get triggered by updates of your
    #  device attributes. Note that you can only post the subscription
    #  to the context broker.
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

    # Create a loop that publishes every second a message to the broker
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

        # publish the simulated zone temperature
        mqttc.publish(device_id=zone_temperature_sensor.device_id,
                      payload={"temperature": sim_model.t_zone,
                               "simtime": sim_model.t_sim})

        # publish the 'simtime' for the heater device
        mqttc.publish(device_id=heater.device_id,
                      payload={"simtime": sim_model.t_sim})

        time.sleep(1)
        # simulation step for next loop
        sim_model.do_step(int(t_sim + COM_STEP))
        # wait for one second before publishing the next values
        time.sleep(1)

    # close the mqtt listening thread
    mqttc.loop_stop()
    # disconnect the mqtt device
    mqttc.disconnect()

    # wait until all data is available
    time.sleep(10)

    # ToDo: Retrieve the historic data from QuantumLeap, convert them to a
    #  pandas dataframe and plot them
    # Retrieve the data for the weather station
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
    history_weather_station['simtime'] = pd.to_numeric(
        history_weather_station['simtime'], downcast="float")
    history_weather_station['temperature'] = pd.to_numeric(
        history_weather_station['temperature'], downcast="float")
    # ToDo: plot the results
    fig, ax = plt.subplots()
    ax.plot(history_weather_station['simtime'],
            history_weather_station['temperature'])
    ax.set_xlabel('time in s')
    ax.set_ylabel('ambient temperature in °C')
    plt.show()

    # ToDo: Retrieve the data for the zone temperature
    history_zone_temperature_sensor = qlc.get_entity_by_id(
        entity_id=zone_temperature_sensor.entity_name,
        entity_type=zone_temperature_sensor.entity_type,
        last_n=10000
    )

    # ToDo: convert to pandas dataframe and print it
    history_zone_temperature_sensor = \
        history_zone_temperature_sensor.to_pandas()
    print(history_zone_temperature_sensor)
    # ToDo: drop unnecessary index levels
    history_zone_temperature_sensor = history_zone_temperature_sensor.droplevel(
        level=("entityId", "entityType"), axis=1)
    history_zone_temperature_sensor['simtime'] = pd.to_numeric(
        history_zone_temperature_sensor['simtime'], downcast="float")
    history_zone_temperature_sensor['temperature'] = pd.to_numeric(
        history_zone_temperature_sensor['temperature'], downcast="float")
    # ToDo: plot the results
    fig2, ax2 = plt.subplots()
    ax2.plot(history_zone_temperature_sensor['simtime'],
             history_zone_temperature_sensor['temperature'])
    ax2.set_xlabel('time in s')
    ax2.set_ylabel('zone temperature in °C')
    plt.show()

    # ToDo: Retrieve the data for the heater
    history_heater = qlc.get_entity_by_id(
        entity_id=heater.entity_name,
        entity_type=heater.entity_type,
        last_n=10000
    )

    # convert to pandas dataframe and print it
    history_heater = history_heater.to_pandas()
    history_heater = history_heater.replace(' ', 0)
    print(history_heater)

    # ToDo: drop unnecessary index levels
    history_heater = history_heater.droplevel(
        level=("entityId", "entityType"), axis=1)
    history_heater['simtime'] = pd.to_numeric(
        history_heater['simtime'], downcast="float")
    history_heater['heater_on_info'] = pd.to_numeric(
        history_heater['heater_on_info'], downcast="float")
    # ToDo: plot the results
    fig3, ax3 = plt.subplots()
    ax3.plot(history_heater['simtime'],
             history_heater['heater_on_info'])
    ax3.set_xlabel('time in s')
    ax3.set_ylabel('set point')
    plt.show()

    clear_iot_agent(url=IOTA_URL, fiware_header=fiware_header)
    clear_context_broker(url=CB_URL, fiware_header=fiware_header)
    clear_quantumleap(url=QL_URL, fiware_header=fiware_header)
