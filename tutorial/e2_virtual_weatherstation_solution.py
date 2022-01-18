# # Exercise 2: Virtual Weather-Station

# Create a virtual IoT device that simulates the ambient temperature and
# publishes it via MQTT. The simulation function is already predefined.
# The virtual device does not only

# The input sections are marked with 'ToDo'

# #### Steps to complete:
# 1. Set up the missing parameters in the parameter section
# 2. Create an MQTT client using the paho-mqtt package with mqtt.Client()
# 3. Define a callback function that will be executed when the client
#    receives message on a subscribed topic_one. It should decode your message
#    and store the information for later in our history
# 4. Subscribe to the topic_one that the device will publish to
# 5. Create a function that publishes the simulated temperature via MQTT as a JSON
# 6. Run the simulation and plot

# ## Import packages
import json
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import numpy as np
import time
from math import cos
from urllib.parse import urlparse

# ## Parameters
# ToDo: Enter your mqtt broker url and port, e.g mqtt://test.mosquitto.org:1883
MQTT_BROKER_URL = "mqtt://test.mosquitto.org:1883"

# ToDo: Create a topic_one that your weather station will publish to
topic = "fiware_workshop/<name_surname>/weather_station"

# set parameters for the temperature simulation
temperature_max = 10  # maximal ambient temperature
temperature_min = -5  # minimal ambient temperature

t_sim_start = 0  # simulation start time in seconds
t_sim_end = 24 * 60 * 60  # simulation end time in seconds
sim_step = 1  # simulation step in seconds
com_step = 60 * 60  # communication step in seconds


# ## Simulation model
class SimulationModel:

    def __init__(self, t_start: int, t_end: int, dt: int, temp_max: float, temp_min: float):
        self.t_start = t_start
        self.t_end = t_end
        self.dt = dt
        self.temp_max = temp_max
        self.temp_min = temp_min
        self.current_time = self.t_start
        self.current_output = temp_min

    # define the function that returns a virtual ambient temperature depend from the
    # the simulation time using cosinus function
    def do_step(self, t_sim: float):
        t = self.current_output
        while self.current_time <= t_sim:
            if self.current_time != 0:
                t = -(self.temp_max - self.temp_min) / 2 * cos(2 * np.pi * self.current_time /
                                                               (24 * 60 * 60)) + self.temp_min + \
                    (self.temp_max - self.temp_min) / 2
            self.current_time = self.current_time + self.dt
        self.current_output = t
        return self.current_output


# ## Main script
if __name__ == '__main__':
    # instantiate simulation model
    sim_model = SimulationModel(t_start=t_sim_start, t_end=t_sim_end, dt=sim_step,
                                temp_max=temperature_max, temp_min=temperature_min)

    # define a list for storing historical data
    history = []

    # ToDo: create a MQTTv5 client with paho-mqtt
    mqttc = mqtt.Client(protocol=mqtt.MQTTv5)


    # ToDo: Define a callback function that will be executed when the client
    #  receives message on a subscribed topic_one. It should decode your message
    #  and store the information for later in our history
    #  Note: do not change function's signature!
    def on_message(client, userdata, msg):
        payload = msg.payload.decode('utf-8')
        history.append(json.loads(payload))


    # add your callback function to the client
    mqttc.on_message = on_message

    # ToDO: connect to the mqtt broker and subscribe to your topic_one
    mqtt_url = urlparse(MQTT_BROKER_URL)
    mqttc.connect(host=mqtt_url.hostname,
                  port=mqtt_url.port,
                  keepalive=60,
                  bind_address="",
                  bind_port=0,
                  clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY,
                  properties=None)

    mqttc.subscribe(topic=topic)

    # create a non-blocking thread for mqtt communication
    mqttc.loop_start()

    # ToDo: Create a loop that publishes every second a message to the broker
    #  that holds the simulation time "t_sim" and the corresponding temperature
    #  "temperature" the loop should
    for t_simulation in range(sim_model.t_start, sim_model.t_end + com_step, com_step):
        mqttc.publish(topic=topic,
                      payload=json.dumps(
                          {"temperature": sim_model.do_step(t_simulation),
                           "t_sim": t_simulation}))
        time.sleep(1)

    # close the mqtt listening thread
    mqttc.loop_stop()
    # disconnect the mqtt device
    mqttc.disconnect()

    # plot results
    fig, ax = plt.subplots()
    t_simulation = [item["t_sim"] for item in history]
    temperature = [item["temperature"] for item in history]
    ax.plot(t_simulation, temperature)
    ax.set_xlabel('time in s')
    ax.set_ylabel('temperature in °C')
    plt.show()
