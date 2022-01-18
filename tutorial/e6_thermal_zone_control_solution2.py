# # Exercise 3: Virtual Thermal Zone

# Create a virtual IoT device that simulates the air temperature of a thermal zone and
# publishes it via MQTT. The simulation function is already predefined.

# The input sections are marked with 'ToDo'

# #### Steps to complete:
# 1. Set up the missing parameters in the parameter section
# 2. Create an MQTT client using the paho-mqtt package with mqtt.Client()
# 3. Define a callback function that will be executed when the client
#    receives message on a subscribed topic_weather. It should decode your message
#    and store the information for later in our history
# 4. Subscribe to the topic_weather that the device will publish to
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

# ToDo: Create a topic_weather that your weather station will publish to
topic_weather = "fiware_workshop/<name_surname>/weather_station"
topic_heater = "fiware_workshop/<name_surname>/heater"

signal_start = 0  # start signal of the controller


# ## Simulation model
class Controller:

    def __init__(self, sig_start: int):
        self.sig_start = sig_start
        self.u_low = 19
        self.u_high = 21
        self.current_output = sig_start

    # define the function that returns a virtual ambient temperature depend from the
    # the simulation time using cosinus function
    def do_step(self, temperature: float):
        signal = self.current_output
        if temperature < self.u_low:
            signal = 1
        if temperature > self.u_high:
            signal = 0
        self.current_output = signal
        return self.current_output


# ## Main script
if __name__ == '__main__':
    # instantiate simulation model
    sim_model = Controller(sig_start=signal_start)

    # define lists for storing historical data
    history_ambient = []
    history_room = []

    # ToDo: create a MQTTv5 client with paho-mqtt
    mqttc = mqtt.Client(protocol=mqtt.MQTTv5)


    # ToDo: Define a callback function that will be executed when the client
    #  receives message on a subscribed topic_weather. It should decode your message
    #  and store the information for later in our history
    #  Note: do not change function's signature!
    def on_message(client, userdata, msg):
        payload = msg.payload.decode('utf-8')
        json_payload = json.loads(payload)
        mqttc.publish(topic=topic_heater,
                      payload=json.dumps(
                          {"heater signal": sim_model.do_step(json_payload['room temperature']),
                           "t_sim": json_payload['t_sim']}))


    # add your callback function to the client
    mqttc.on_message = on_message

    # ToDO: connect to the mqtt broker and subscribe to your topic_weather
    mqtt_url = urlparse(MQTT_BROKER_URL)
    mqttc.connect(host=mqtt_url.hostname,
                  port=mqtt_url.port,
                  keepalive=60,
                  bind_address="",
                  bind_port=0,
                  clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY,
                  properties=None)

    mqttc.subscribe(topic=topic_weather)

    # create a non-blocking thread for mqtt communication
    mqttc.loop_start()

    # close the mqtt listening thread
    mqttc.loop_stop()
    # disconnect the mqtt device
    mqttc.disconnect()
