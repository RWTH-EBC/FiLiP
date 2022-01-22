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
import numpy as np
import time
from math import cos
from typing import List
from urllib.parse import urlparse
from filip.clients.ngsi_v2 import ContextBrokerClient, IoTAClient
from filip.clients.mqtt import IoTAMQTTClient
from filip.models.base import FiwareHeader
from filip.models.ngsi_v2.context import ContextEntity
from filip.utils.cleanup import clear_context_broker, clear_iot_agent

# ## Parameters
# ## Parameters
# ToDo: Enter your context broker host and port, e.g http://localhost:1026
CB_URL = "http://localhost:1026"
# ToDo: Enter your mqtt broker url and port, e.g mqtt://test.mosquitto.org:1883
MQTT_BROKER_URL = "mqtt://localhost:1883"
# FIWARE-Service
SERVICE = 'filip_tutorial'
# FIWARE-Servicepath
# ToDo: Change the name of your service-path to something unique. If you run
#  on a shared instance this very important in order to avoid user
#  collisions. You will use this service path through the whole tutorial.
#  If you forget to change it an error will be raised!
SERVICE_PATH = '/your_path'

# Path to json-files to store entity data for follow up exercises
read_entities_filepath = Path("./e3_context_entities_solution_entities.json")
write_entities_filepath = Path("./e4_iot_thermal_zone_sensors_entities.json")
write_groups_filepath = Path("./e4_iot_thermal_zone_sensors_groups.json")
write_devices_filepath = Path("./e4_iot_thermal_zone_sensors_devices.json")

# set parameters for the temperature simulation
temperature_max = 10  # maximal ambient temperature
temperature_min = -5  # minimal ambient temperature
temperature_room_start = 20  # start value of the room temperature

t_sim_start = 0  # simulation start time in seconds
t_sim_end = 24 * 60 * 60  # simulation end time in seconds
sim_step = 1  # simulation step in seconds
com_step = 60 * 60  # communication step in seconds


# ## Simulation model
class SimulationModel:

    def __init__(self,
                 t_start: int,
                 t_end: int,
                 dt: int,
                 temp_max: float,
                 temp_min: float,
                 temp_start: float):
        self.t_start = t_start
        self.t_end = t_end
        self.dt = dt
        self.temp_max = temp_max
        self.temp_min = temp_min
        self.temp_start = temp_start
        self.kA = 120
        self.C_p = 612.5 * 1000
        self.Q_h = 1000
        self.t_sim = self.t_start
        self.t_amb = temp_min
        self.t_zone = temp_start
        self.heater_on: bool = False

    # define the function that returns a virtual ambient temperature depend from the
    # the simulation time using cosinus function
    def do_step(self, t_sim: int):
        for t in range(self.t_sim, t_sim, self.dt):
            self.t_zone = self.t_zone + \
                          self.dt * (self.kA * (self.t_amb - self.t_zone) +
                          self.heater_on * self.Q_h) / self.C_p

            self.t_amb = -(self.temp_max - self.temp_min) / 2 * \
                    cos(2 * np.pi * t /(24 * 60 * 60)) + \
                    self.temp_min + (self.temp_max - self.temp_min) / 2

        self.t_sim = t_sim

        return self.t_sim, self.t_amb, self, self.t_zone


# ## Main script
if __name__ == '__main__':
    # create a fiware header object
    fiware_header = FiwareHeader(service=SERVICE,
                                 service_path=SERVICE_PATH)
    # clear the state of your service and scope
    clear_context_broker(url=CB_URL, fiware_header=fiware_header)
    # restore data from json-file
    entities = parse_file_as(List[ContextEntity],
                             path=read_entities_filepath)
    # create a context broker client and add the fiware_header
    cb_client = ContextBrokerClient(url=CB_URL, fiware_header=fiware_header)
    cb_client.update(entities=entities, action_type='append')

    # check if successfully restored
    print(cb_client.get_entity_list())



    # instantiate simulation model
    sim_model = SimulationModel(t_start=t_sim_start,
                                t_end=t_sim_end,
                                dt=sim_step,
                                temp_max=temperature_max,
                                temp_min=temperature_min,
                                temp_start=temperature_room_start)

    # define lists for storing historical data
    history_weather_station = []
    history_zone_temperature_sensor = []

    topic_zone_temperature_sensor = "/json/apikey/zone_temperature_sensor/attrs"
    topic_weather_station = "/json/apikey/weather_station/attrs"

    # ToDo: create a MQTTv5 client with paho-mqtt
    mqttc = IoTAMQTTClient(protocol=mqtt.MQTTv5)


    # ToDo: Define a callback function that will be executed when the client
    #  receives message on a subscribed topic. It should decode your message
    #  and store the information for later in our history
    #  Note: do not change function's signature!
    def on_message_weather_station(client, userdata, msg):
        payload = msg.payload.decode('utf-8')
        json_payload = json.loads(payload)
        history_weather_station.append(json_payload)

    def on_message_zone_temperature_sensor(client, userdata, msg):
        payload = msg.payload.decode('utf-8')
        json_payload = json.loads(payload)
        history_zone_temperature_sensor.append(json_payload)


    # add your callback function to the client
    mqttc.message_callback_add(sub=topic_weather_station,
                               callback=on_message_weather_station)
    mqttc.message_callback_add(sub=topic_zone_temperature_sensor,
                               callback=on_message_zone_temperature_sensor)

    # ToDO: connect to the mqtt broker and subscribe to your topic
    mqtt_url = urlparse(MQTT_BROKER_URL)
    mqttc.connect(host=mqtt_url.hostname,
                  port=mqtt_url.port,
                  keepalive=60,
                  bind_address="",
                  bind_port=0,
                  clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY,
                  properties=None)

    mqttc.subscribe()
    mqttc.subscribe(topic_weather_station)
    mqttc.subscribe(topic_zone_temperature_sensor)


    # create a non-blocking thread for mqtt communication
    mqttc.loop_start()

    # ToDo: Create a loop that publishes every second a message to the broker
    #  that holds the simulation time "t_sim" and the corresponding temperature
    #  "temperature" the loop should
    for t_sim in range(sim_model.t_start, sim_model.t_end + com_step, com_step):
        mqttc.publish(topic=topic_weather_station,
                      payload=json.dumps({"t_amb": sim_model.t_amb,
                                          "t_sim": sim_model.t_sim}))
        mqttc.publish(topic=topic_zone_temperature_sensor,
                      payload=json.dumps({"t_zone": sim_model.t_zone,
                                          "t_sim": sim_model.t_sim}))
        time.sleep(1)
        sim_model.do_step(t_sim+com_step)

    # close the mqtt listening thread
    mqttc.loop_stop()
    # disconnect the mqtt device
    mqttc.disconnect()

    # plot results
    fig, ax = plt.subplots()
    t_simulation = [item["t_sim"] for item in history_weather_station]
    temperature = [item["t_amb"] for item in history_weather_station]
    ax.plot(t_simulation, temperature)
    ax.set_xlabel('time in s')
    ax.set_ylabel('ambient temperature in °C')

    fig2, ax2 = plt.subplots()
    t_simulation = [item["t_sim"] for item in history_zone_temperature_sensor]
    temperature = [item["t_zone"] for item in history_zone_temperature_sensor]
    ax2.plot(t_simulation, temperature)
    ax2.set_xlabel('time in s')
    ax2.set_ylabel('zone temperature in °C')

    plt.show()
