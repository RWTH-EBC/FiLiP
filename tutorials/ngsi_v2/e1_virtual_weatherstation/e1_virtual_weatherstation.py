"""
# # Exercise 1: Virtual Weather-Station

# Create a virtual IoT device that simulates the ambient temperature and
# publishes it via MQTT. The simulation function is already predefined.
# This exercise gives a simple introduction to the communication via MQTT.

# The input sections are marked with 'ToDo'

# #### Steps to complete:
# 1. Set up the missing parameters in the parameter section
# 2. Create an MQTT client using the paho-mqtt package with mqtt.Client()
# 3. Define a callback function that will be executed when the client
#    receives message on a subscribed topic. It should decode your message
#    and store the information for later in our history
#    `history_weather_station`
# 4. Subscribe to the topic that the device will publish to
# 5. Create a function that publishes the simulated temperature `t_amb` and
#    the corresponding simulation time `t_sim `via MQTT as a JSON
# 6. Run the simulation and plot
"""

# ## Import packages
import json
import time
from urllib.parse import urlparse
from uuid import uuid4
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt

# import simulation model
from tutorials.ngsi_v2.simulation_model import SimulationModel

# ## Parameters
# ToDo: Enter your mqtt broker url and port, e.g. mqtt://test.mosquitto.org:1883.
MQTT_BROKER_URL = "mqtt://test.mosquitto.org:1883"
# ToDo: If required, enter your username and password.
MQTT_USER = ""
MQTT_PW = ""

# ToDo: Create a unique topic that your weather station will publish on,
#  e.g. by using a uuid.
UNIQUE_ID = str(uuid4())
TOPIC_WEATHER_STATION = f"fiware_workshop/{UNIQUE_ID}/weather_station"

# set parameters for the temperature simulation
TEMPERATURE_MAX = 10  # maximal ambient temperature
TEMPERATURE_MIN = -5  # minimal ambient temperature

T_SIM_START = 0  # simulation start time in seconds
T_SIM_END = 24 * 60 * 60  # simulation end time in seconds
COM_STEP = 60 * 60  # 60 min communication step in seconds

# ## Main script
if __name__ == '__main__':
    # instantiate simulation model
    sim_model = SimulationModel(t_start=T_SIM_START,
                                t_end=T_SIM_END,
                                temp_max=TEMPERATURE_MAX,
                                temp_min=TEMPERATURE_MIN)

    # define a list for storing historical data
    history_weather_station = []

    # ToDo: Create an MQTTv5 client with paho-mqtt.
    mqttc = ...
    # set user data if required
    mqttc.username_pw_set(username=MQTT_USER, password=MQTT_PW)

    # ToDo: Define a callback function that will be executed when the client
    #  receives message on a subscribed topic. It should decode your message
    #  and store the information for later in our history.
    #  Note: Do not change the function's signature!
    def on_message(client, userdata, msg):
        """
        Callback function for incoming messages
        """
        # decode the payload
        payload = msg.payload.decode('utf-8')
        # ToDo: Parse the payload using the `json` package and write it to
        #  the history.
        ...

        pass

    # add your callback function to the client. You can either use a global
    # or a topic specific callback with `mqttc.message_callback_add()`
    mqttc.on_message = on_message

    # ToDo: Connect to the mqtt broker and subscribe to your topic.
    mqtt_url = urlparse(MQTT_BROKER_URL)
    ...







    # ToDo: Print and subscribe to the weather station topic.
    print(f"WeatherStation topic:\n {TOPIC_WEATHER_STATION}")
    mqttc.subscribe(topic=TOPIC_WEATHER_STATION)

    # create a non-blocking thread for mqtt communication
    mqttc.loop_start()

    # ToDo: Create a loop that publishes every 20 milliseconds a message to the broker
    #  that holds the simulation time "t_sim" and the corresponding temperature
    #  "t_amb".
    for t_sim in range(sim_model.t_start,
                       int(sim_model.t_end + COM_STEP),
                       int(COM_STEP)):
        # ToDo: Publish the simulated ambient temperature.
        ...



        # simulation step for next loop
        sim_model.do_step(int(t_sim + COM_STEP))
        time.sleep(0.2)

    # close the mqtt listening thread
    mqttc.loop_stop()
    # disconnect the mqtt device
    mqttc.disconnect()

    # plot results
    fig, ax = plt.subplots()
    t_simulation = [item["t_sim"]/3600 for item in history_weather_station]
    temperature = [item["t_amb"] for item in history_weather_station]
    ax.plot(t_simulation, temperature)
    ax.set_xlabel('time in h')
    ax.set_ylabel('ambient temperature in °C')
    plt.show()
