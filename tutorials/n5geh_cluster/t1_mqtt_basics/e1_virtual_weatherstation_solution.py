"""
# # Exercise 1: Virtual Weather-Station

# Create a virtual IoT device that simulates the ambient temperature and
# publishes it via MQTT.
# This exercise gives a simple introduction to the communication via MQTT.

# #### Steps covered in this modularized version:
# 1. Parameter configuration
# 2. Setup of the MQTT client and connection
# 3. Handling incoming messages (Subscriber)
# 4. Running the simulation and publishing (Publisher)
# 5. Visualizing the results
"""

import json
import time
from urllib.parse import urlparse
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt

# Import simulation model
from tutorials.ngsi_v2.simulation_model import SimulationModel

# ==========================================
# 1. PARAMETERS
# ==========================================
MQTT_BROKER_URL = "mqtt://mqtt.n5geh.eonerc.rwth-aachen.de:8883"
MQTT_USER = "ebcdev"
MQTT_PW = "ebcdev"
# TODO allowed Topics: /json/ebc_dev_apikey<1~5>/#
TOPIC_WEATHER_STATION = "/json/ebc_dev_apikey1/weather_station"

TEMPERATURE_MAX = 10
TEMPERATURE_MIN = -5

T_SIM_START = 0
T_SIM_END = 24 * 60 * 60
COM_STEP = 60 * 60


# ==========================================
# 2. SUBSCRIBER: Callback Function
# ==========================================
def on_message(client, userdata, msg):
    """
    This function is triggered automatically whenever the client receives a
    message on a subscribed topic.
    """
    # Decode the raw byte payload into a string
    payload_str = msg.payload.decode("utf-8")

    # Parse the JSON string back into a Python dictionary
    data = json.loads(payload_str)

    # 'userdata' is our history list passed during client setup
    userdata.append(data)

    # Print statement to show students when data arrives
    print(f"[Subscriber] Received data on '{msg.topic}': {data}")


# ==========================================
# 3. SETUP: Client Configuration
# ==========================================
def setup_mqtt_client(broker_url, username, password, topic, history_list):
    """
    Creates the MQTT client, sets up credentials, assigns the callback,
    and connects to the broker.
    """
    print("\n[Setup] 1. Initializing MQTT Client...")
    mqttc = mqtt.Client(
        protocol=mqtt.MQTTv5, callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )

    # Set credentials and enable secure connection (TLS)
    mqttc.username_pw_set(username=username, password=password)
    mqttc.tls_set()

    # Pass our history list into the client so the callback can access it safely
    mqttc.user_data_set(history_list)

    # Assign the callback function defined above
    mqttc.on_message = on_message

    # Parse URL and connect
    url = urlparse(broker_url)
    print(f"[Setup] 2. Connecting to broker at {url.hostname}:{url.port}...")
    mqttc.connect(
        host=url.hostname,
        port=url.port,
        keepalive=60,
        clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY,
    )

    # Subscribe to the topic to receive the messages we publish
    print(f"[Setup] 3. Subscribing to topic: {topic}\n")
    mqttc.subscribe(topic=topic)

    return mqttc


# ==========================================
# 4. PUBLISHER: Simulation Loop
# ==========================================
def run_simulation_and_publish(mqttc, sim_model, topic, com_step):
    """
    Advances the simulation step-by-step and publishes the current
    temperature to the MQTT broker.
    """
    print("--- Starting Simulation ---")

    # Start a background thread to handle incoming network traffic
    mqttc.loop_start()

    # Loop through the simulation time
    for t_sim in range(
        sim_model.t_start, int(sim_model.t_end + com_step), int(com_step)
    ):
        # Package the data into a dictionary, then convert to a JSON string
        payload_dict = {"t_amb": sim_model.t_amb, "t_sim": sim_model.t_sim}
        payload_json = json.dumps(payload_dict)

        print(f"[Publisher]  Sending simulated data: {payload_json}")

        # Publish to the broker
        mqttc.publish(topic=topic, payload=payload_json)

        # Advance the simulation model and pause briefly for educational effect
        sim_model.do_step(int(t_sim + com_step))
        time.sleep(0.2)

    # Stop the background thread and disconnect gracefully
    mqttc.loop_stop()
    mqttc.disconnect()
    print("--- Simulation Finished & Disconnected ---\n")


# ==========================================
# 5. VISUALIZATION: Plot Results
# ==========================================
def plot_results(history):
    """
    Extracts time and temperature data from the history list and plots it.
    """
    print(f"[Visualization] Plotting {len(history)} received data points...")
    fig, ax = plt.subplots()

    # Convert seconds to hours for the x-axis
    t_simulation = [item["t_sim"] / 3600 for item in history]
    temperature = [item["t_amb"] for item in history]

    ax.plot(t_simulation, temperature, marker="o", linestyle="-")
    ax.set_title("Virtual Weather Station Data over MQTT")
    ax.set_xlabel("Time in h")
    ax.set_ylabel("Ambient Temperature in °C")
    ax.grid(True)

    plt.show()


if __name__ == "__main__":
    # 1. Initialize the shared history list and the simulation model
    history_weather_station = []

    sim_model = SimulationModel(
        t_start=T_SIM_START,
        t_end=T_SIM_END,
        temp_max=TEMPERATURE_MAX,
        temp_min=TEMPERATURE_MIN,
    )

    # 2. Setup the client and connect
    client = setup_mqtt_client(
        broker_url=MQTT_BROKER_URL,
        username=MQTT_USER,
        password=MQTT_PW,
        topic=TOPIC_WEATHER_STATION,
        history_list=history_weather_station,
    )

    # 3. Run the publishing loop
    run_simulation_and_publish(
        mqttc=client,
        sim_model=sim_model,
        topic=TOPIC_WEATHER_STATION,
        com_step=COM_STEP,
    )

    # 4. Display the received data
    plot_results(history=history_weather_station)
