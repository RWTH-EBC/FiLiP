# # Exercise 2: Virtual Weather-Station

# Create a virtual IoT device that simulates the ambient temperature and
# publishes it via MQTT. The simulation function is already predefined.
# The virtual device does not only

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
import matplotlib.pyplot as plt
import numpy as np
import time
from math import cos
from urllib.parse import urlparse

# ## Parameters
# ToDo: Enter your mqtt broker url and port, e.g mqtt://test.mosquitto.org:1883
MQTT_BROKER_URL = "mqtt://test.mosquitto.org:1883"

# ToDo: Create a topic that your weather station will publish to
topic = "fiware_workshop/<name_surname>/weather_station"

# set parameters for the temperature simulation
temp_max = 10 # maximal ambient temperature
temp_min = -5 # minimal ambient temperature

t_start = 0 # simulation start time in seconds
t_end = 24 * 60 * 60 # simulation end time in seconds
dt = 60 * 60 # simulation step in seconds

# ## Simulation model
# define the function that returns a virtual ambient temperature depend from the
# the simulation time using cosinus function
def simulate_temperature(t_sim: float):
    return -(temp_max - temp_min) / 2 * cos(2 * np.pi * t_sim / (24 * 60 * 60)) \
           + temp_min + (temp_max - temp_min) / 2


# ## Main script
if __name__ == '__main__':
    # define a list for storing historical data
    history = []

    # ToDo: create a MQTTv5 client with paho-mqtt
    mqttc = mqtt.Client(protocol=mqtt.MQTTv5)

    # ToDo: Define a callback function that will be executed when the client
    #  receives message on a subscribed topic. It should decode your message
    #  and store the information for later in our history
    #  Note: do not change function's signature!
    def on_message(client, userdata, msg):
        payload = msg.payload.decode('utf-8')
        history.append(json.loads(payload))

    # add your callback function to the client
    mqttc.on_message = on_message

    # ToDO: connect to the mqtt broker and subscribe to your topic
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
    for t_sim in range(t_start, t_end, dt):
        mqttc.publish(topic=topic,
                      payload=json.dumps(
                          {"temperature": simulate_temperature(t_sim),
                           "t_sim": t_sim}))
        time.sleep(1)

    # close the mqtt listening thread
    mqttc.loop_stop()
    # disconnect the mqtt device
    mqttc.disconnect()

    # plot results
    fig, ax = plt.subplots()
    t_sim = [item["t_sim"] for item in history]
    temperature = [item["temperature"] for item in history]
    ax.plot(t_sim, temperature)
    ax.set_xlabel('time in s')
    ax.set_ylabel('temperature in °C')
    plt.show()
