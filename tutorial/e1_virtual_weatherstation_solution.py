# # Exercise 1: Virtual Weather-Station

# Create a virtual IoT device that simulates the ambient temperature and
# publishes it via MQTT. The simulation function is already predefined.
# This exercise to give a simple introduction to the communication via MQTT.

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

# ## Import packages
import json
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import time
from urllib.parse import urlparse
from uuid import uuid4

# import simulation model
from tutorial.simulation_model import SimulationModel


# ## Parameters
# ToDo: Enter your mqtt broker url and port, e.g mqtt://test.mosquitto.org:1883
MQTT_BROKER_URL = "mqtt://test.mosquitto.org:1883"

# ToDo: Create a unique topic that your weather station will publish on,
#  e.g. by using a uuid
unique_id = str(uuid4())
topic_weather_station = f"fiware_workshop/{unique_id}/weather_station"

# set parameters for the temperature simulation
temperature_max = 10  # maximal ambient temperature
temperature_min = -5  # minimal ambient temperature

t_sim_start = 0  # simulation start time in seconds
t_sim_end = 24 * 60 * 60  # simulation end time in seconds
com_step = 60 * 60 * 0.25  # 15 min communication step in seconds


# ## Main script
if __name__ == '__main__':
    # instantiate simulation model
    sim_model = SimulationModel(t_start=t_sim_start,
                                t_end=t_sim_end,
                                temp_max=temperature_max,
                                temp_min=temperature_min)

    # define lists to store historical data
    history_weather_station = []

    # ToDo: create a MQTTv5 client with paho-mqtt
    mqttc = mqtt.Client(protocol=mqtt.MQTTv5)

    # ToDo: Define a callback function that will be executed when the client
    #  receives message on a subscribed topic. It should decode your message
    #  and store the information for later in our history
    #  Note: do not change function's signature!
    def on_message(client, userdata, msg):
        # decode the payload
        payload = msg.payload.decode('utf-8')
        # ToDo: Parse the payload using the `json` package and write it to
        #  the history
        history_weather_station.append(json.loads(payload))

        return

    # add your callback function to the client. You can either use a global
    # or a topic specific callback with `mqttc.message_callback_add()`
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

    # ToDo: print and subscribe to the weather station topic
    print(f"WeatherStation topic:\n topic_weather_station")
    mqttc.subscribe(topic=topic_weather_station)

    # create a non-blocking thread for mqtt communication
    mqttc.loop_start()

    # ToDo: Create a loop that publishes every second a message to the broker
    #  that holds the simulation time "t_sim" and the corresponding temperature
    #  "t_amb"
    for t_sim in range(sim_model.t_start,
                       int(sim_model.t_end + com_step),
                       int(com_step)):
        # ToDo: publish the simulated ambient temperature
        mqttc.publish(topic=topic_weather_station,
                      payload=json.dumps({"t_amb": sim_model.t_amb,
                                          "t_sim": sim_model.t_sim}))

        # simulation step for next loop
        sim_model.do_step(int(t_sim + com_step))
        time.sleep(1)

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
    plt.show()
