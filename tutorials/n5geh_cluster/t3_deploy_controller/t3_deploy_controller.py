"""
# # Exercise 5: Virtual Thermal Zone with Control

# Create a virtual IoT device that simulates a heater for a thermal zone.
# The heater is controlled via a simple hysteresis controller (on/off) based on
# the zone temperature.
#
# #### Modularized Steps:
# 1. Platform Cleanup & Restore
# 2. Provisioning the Heater (Adding the new actuator)
# 3. Setting up the Actuator (MQTT Client to receive commands)
# 4. Starting the Periodic Controller (Background thread loop)
# 5. Running the Simulation
# 6. Visualization
"""

import time
import threading
from urllib.parse import urlparse
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import json

# Import from filip
from filip.models.base import DataType
from filip.models.ngsi_v2 import ContextEntity
from filip.models.ngsi_v2.context import NamedContextAttribute
from filip.models.ngsi_v2.subscriptions import Subscription, Notification, Subject
from filip.utils.cleanup import clear_context_broker, clear_iot_agent, clear_quantumleap

# Import from previous tutorials
from tutorials.n5geh_cluster.t2_provision_sensor.t2_provision_sensor import (
    provision_temperature_sensor,
    APIKEY_WS,
    APIKEY_TS,
    fetch_historical_data,
)
from tutorials.n5geh_cluster.init_clients import (
    iota_client,
    cb_client,
    ql_client,
    QL_URL_INTERNAL,
    MQTT_INTERNAL_URL,
)
from tutorials.ngsi_v2.simulation_model import SimulationModel

# ==========================================
# 1. PARAMETERS
# ==========================================
MQTT_BROKER_URL_EXPOSED = "mqtt://mqtt.n5geh.eonerc.rwth-aachen.de:8883"
MQTT_USER = "ebcdev"
MQTT_PW = "ebcdev"

COMMAND_TOPIC = "/json/ebc_dev_apikey1/heater/command"

# Simulation parameters
TEMPERATURE_MAX = 10
TEMPERATURE_MIN = -5
TEMPERATURE_ZONE_START = 20

T_SIM_START = 0
T_SIM_END = 24 * 60 * 60
COM_STEP = 60 * 60 * 0.25  # 15 min steps


# ==========================================
# 2. PROVISIONING (Registering the Heater)
# ==========================================
def provision_heater(entity_type, entity_name):
    """Creates and registers the new Heater device in the Context Broker."""
    print(f"\n[Provisioning] Creating the Heater actuator ({entity_name})...")

    heater = ContextEntity(id=entity_name, type=entity_type)
    t_sim = NamedContextAttribute(name="sim_time", type=DataType.NUMBER)
    ht_on = NamedContextAttribute(name="heater_on", type=DataType.BOOLEAN)

    heater.add_attributes([t_sim, ht_on])
    cb_client.post_entity(entity=heater)

    # Forwarding command to the MQTT broker
    print(f"[Provisioning] Linking '{ht_on.name}' attribute to MQTT topic...")
    cb_client.post_subscription(
        subscription=Subscription(
            subject=Subject(
                **{
                    "entities": [{"id": entity_name}],
                    "condition": {"attrs": [ht_on.name]},
                }
            ),
            notification=Notification(
                **{
                    "mqttCustom": {
                        "url": MQTT_INTERNAL_URL,
                        "topic": COMMAND_TOPIC,
                        "user": MQTT_USER,
                        "passwd": MQTT_PW,
                        "payload": "${" + ht_on.name + "}",
                    }
                }
            ),
            throttling=0,
        )
    )

    # Subscription to save historical state to QuantumLeap
    print(f"[Provisioning] Creating database subscription for {entity_name}...")
    cb_client.post_subscription(
        subscription=Subscription(
            subject=Subject(
                **{
                    "entities": [{"id": entity_name}],
                    "condition": {"attrs": [ht_on.name]},
                }
            ),
            notification=Notification(
                **{"http": {"url": f"{QL_URL_INTERNAL}/v2/notify"}}
            ),
            throttling=0,
        )
    )
    print("[Provisioning] Heater successfully provisioned.")


# ==========================================
# 3. ACTUATOR (Receiving Commands)
# ==========================================
def setup_heater_actuator(broker_url, topic, username, password, sim_model):
    """
    Sets up an MQTT client that acts as the physical heater.
    It listens to the command topic and updates the simulation model.
    """
    print(f"\n[Actuator] Connecting physical heater to '{topic}'...")

    mqttc = mqtt.Client(
        protocol=mqtt.MQTTv5, callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )
    mqttc.username_pw_set(username=username, password=password)
    mqttc.tls_set()

    # Define the callback for incoming MQTT commands
    def on_message(client, userdata, msg):
        payload = msg.payload.decode("utf-8").strip().lower()

        # Determine boolean state from payload
        is_on = payload in ["true", "1"]

        # ---> THIS is the missing link! <---
        # Update the simulation model so the heater actually affects the temperature
        sim_model.heater_on = is_on

        state_str = "ON" if is_on else "OFF"
        print(
            f"[Actuator] Physical Heater received command -> Turned {state_str} ({payload})"
        )

    mqttc.on_message = on_message

    url = urlparse(broker_url)
    mqttc.connect(
        host=url.hostname,
        port=url.port,
        keepalive=60,
    )
    mqttc.subscribe(topic)
    mqttc.loop_start()
    return mqttc


# ==========================================
# 4. CONTROLLER (Periodic Hysteresis Loop)
# ==========================================
def run_periodic_controller(stop_event, sensor_id, heater_id, sampling_time_sec):
    """
    Runs continuously in a background thread. It fetches the temperature at a
    set interval and updates the Context Broker to turn the heater on or off.
    """
    print(
        f"\n[Controller] Starting periodic polling loop (Sampling: {sampling_time_sec}s)..."
    )

    new_state = False  # Initial state of the heater
    while not stop_event.is_set():
        try:
            # 1. Fetch current sensor data
            sensor_entity = cb_client.get_entity(
                entity_id=sensor_id, entity_type="TemperatureSensor"
            )
            current_temp = sensor_entity.temperature.value
            print(f"[Controller] pull temperature measurement")

            # 2. On-Off Logic
            if current_temp <= 19:
                new_state = True
            elif current_temp >= 21:
                new_state = False

            # 3. Send command if the required state differs from what we last sent
            print(
                f"[Controller] Temp is {current_temp:.2f}°C. Triggering Heater State -> {new_state}"
            )
            cb_client.update_attribute_value(
                entity_id=heater_id,
                attr_name="heater_on",
                value=new_state,
                forcedUpdate=True,  # This is important to trigger the command
            )
        except Exception as e:
            print(f"[Controller] Error during polling or command update: {e}")

        # Wait for the next sampling cycle
        time.sleep(sampling_time_sec)

    print("[Controller] Loop stopped gracefully.")


# ==========================================
# 5. PUBLISHER (Simulation Loop)
# ==========================================
def run_local_simulation(sim_model, broker_url, username, password, pause_time=1.0):
    """
    Runs the simulation loop locally. It publishes the sensor data via MQTT
    and updates the heater's simulation time directly in the Context Broker.
    """
    print("\n[Simulation] Starting simulation loop...")

    # Setup MQTT client for publishing sensor data to the IoT Agent
    mqttc = mqtt.Client(
        protocol=mqtt.MQTTv5, callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )
    mqttc.username_pw_set(username=username, password=password)
    mqttc.tls_set()

    url = urlparse(broker_url)
    mqttc.connect(
        host=url.hostname,
        port=url.port,
        keepalive=60,
        clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY,
    )
    mqttc.loop_start()

    # Define the IoT Agent ingestion topics for our sensors
    topic_ws = f"/json/{APIKEY_WS}/device:001/attrs"
    topic_ts = f"/json/{APIKEY_TS}/device:002/attrs"

    for t_sim in range(
        sim_model.t_start, sim_model.t_end + int(COM_STEP), int(COM_STEP)
    ):
        # 1. Publish Sensor Data
        mqttc.publish(
            topic_ws,
            json.dumps({"temperature": sim_model.t_amb, "sim_time": sim_model.t_sim}),
        )
        mqttc.publish(
            topic_ts,
            json.dumps({"temperature": sim_model.t_zone, "sim_time": sim_model.t_sim}),
        )

        # 2. Update Heater sim_time (Heater is a pure ContextEntity, so we update CB directly)
        cb_client.update_attribute_value(
            entity_id="urn:ngsi-ld:Heater:001",
            attr_name="sim_time",
            value=sim_model.t_sim,
        )

        # 3. Allow time for the controller thread to poll and the actuator to receive messages
        time.sleep(pause_time)

        # 4. Advance the simulation (now factoring in if heater_on is True/False)
        sim_model.do_step(int(t_sim + COM_STEP))

    mqttc.loop_stop()
    mqttc.disconnect()
    print("[Simulation] Sequence completed.")


# ==========================================
# 6. VISUALIZATION
# ==========================================
def plot_results(time_ws, temp_ws, time_ts, temp_ts, time_ht, cmd_ht):
    """Plots the separated time and data arrays from the platform."""
    print("\n[Visualization] Generating plots...")

    # Convert seconds to hours for easier reading
    time_ws_h = [t / 3600 for t in time_ws]
    time_ts_h = [t / 3600 for t in time_ts]
    time_ht_h = [t / 3600 for t in time_ht]

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 12))

    # 1. Weather Station
    ax1.plot(time_ws_h, temp_ws, color="blue", marker="o", markersize=3)
    ax1.set_title("Weather Station (Ambient)")
    ax1.set_ylabel("Temp (°C)")
    ax1.grid(True)

    # 2. Zone Temperature
    ax2.plot(time_ts_h, temp_ts, color="orange", marker="o", markersize=3)
    ax2.set_title("Zone Temperature Sensor")
    ax2.set_ylabel("Temp (°C)")
    ax2.grid(True)

    # 3. Heater State
    # Convert booleans/strings to integer states (1/0) if necessary
    numeric_cmd = [1 if str(state).lower() == "true" else 0 for state in cmd_ht]
    ax3.step(time_ht_h, numeric_cmd, color="red", where="post")
    ax3.set_title("Heater State (Periodic Controller)")
    ax3.set_xlabel("Time (hours)")
    ax3.set_ylabel("State (1=On, 0=Off)")
    ax3.set_yticks([0, 1])
    ax3.grid(True)

    plt.tight_layout()
    plt.show()


# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    # 1. Clear previous states
    print("[Setup] Clearing old platform data...")
    clear_iot_agent(iota_client=iota_client)
    clear_context_broker(cb_client=cb_client)
    clear_quantumleap(ql_client=ql_client)

    # 2. Provision Sensors and Actuator
    provision_temperature_sensor(
        apikey=APIKEY_WS,
        entity_type="WeatherStation",
        device_id="device:001",
        entity_name="urn:ngsi-ld:WeatherStation:001",
    )

    sensor_entity_name = "urn:ngsi-ld:TemperatureSensor:001"
    provision_temperature_sensor(
        apikey=APIKEY_TS,
        entity_type="TemperatureSensor",
        device_id="device:002",
        entity_name=sensor_entity_name,
    )

    heater_entity_name = "urn:ngsi-ld:Heater:001"
    provision_heater(entity_type="Heater", entity_name=heater_entity_name)

    # 3. Setup the physical actuator listener
    sim_model = SimulationModel(
        t_start=T_SIM_START,
        t_end=T_SIM_END,
        temp_max=TEMPERATURE_MAX,
        temp_min=TEMPERATURE_MIN,
        temp_start=TEMPERATURE_ZONE_START,
    )
    # pass sim_model to the actuator
    actuator_mqttc = setup_heater_actuator(
        broker_url=MQTT_BROKER_URL_EXPOSED,
        topic=COMMAND_TOPIC,
        username=MQTT_USER,
        password=MQTT_PW,
        sim_model=sim_model,
    )

    # 4. Start the controller background thread
    controller_stop_event = threading.Event()
    controller_thread = threading.Thread(
        target=run_periodic_controller,
        args=(controller_stop_event, sensor_entity_name, heater_entity_name, 0.5),
    )
    controller_thread.start()

    # 5. Run the primary simulation
    print(
        "\n[Simulation] Simulation started. Watch the Controller and Actuator react..."
    )
    run_local_simulation(
        sim_model=sim_model,
        broker_url=MQTT_BROKER_URL_EXPOSED,
        username=MQTT_USER,
        password=MQTT_PW,
        pause_time=1.0,
    )
    print("\n[Simulation] Simulation sequence completed.")

    # 6. Stop the controller and actuator gracefully
    controller_stop_event.set()
    controller_thread.join()
    actuator_mqttc.loop_stop()
    actuator_mqttc.disconnect()

    print("\n[Data Platform] Allowing 5 seconds for database synchronization...")
    time.sleep(5)

    # 7. Fetch Historical Data
    expected_records = len(
        list(range(T_SIM_START, T_SIM_END + int(COM_STEP), int(COM_STEP)))
    )

    time_ws, temp_ws = fetch_historical_data(
        entity_id="urn:ngsi-ld:WeatherStation:001",
        entity_type="WeatherStation",
        attr_name="temperature",
        last_n=expected_records,
    )

    time_ts, temp_ts = fetch_historical_data(
        entity_id="urn:ngsi-ld:TemperatureSensor:001",
        entity_type="TemperatureSensor",
        attr_name="temperature",
        last_n=expected_records,
    )

    time_ht, cmd_ht = fetch_historical_data(
        entity_id="urn:ngsi-ld:Heater:001",
        entity_type="Heater",
        attr_name="heater_on",
        last_n=expected_records,
    )

    # 8. Plot the complete timeline
    plot_results(time_ws, temp_ws, time_ts, temp_ts, time_ht, cmd_ht)
