"""
# # Exercise 4: Virtual Thermal Zone

# Create two virtual IoT devices: a temperature sensor for a thermal zone
# and a virtual weather station. Both devices publish their values to
# the FIWARE data platform via MQTT.
#
# #### Modularized Steps:
# 1. Platform Cleanup (Resetting state)
# 2. Provisioning (Registering devices and creating subscriptions)
# 3. Publishing (Running the simulation and sending MQTT data)
# 4. Data Retrieval (Fetching historical data from QuantumLeap)
# 5. Visualization (Plotting the results)
"""

import json
import time
from urllib.parse import urlparse
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt

# Import from filip (FIWARE library)
from filip.models.ngsi_v2.iot import Device, DeviceAttribute, ServiceGroup
from filip.models.ngsi_v2.subscriptions import Subscription, Subject, Notification
from filip.utils.cleanup import clear_context_broker, clear_iot_agent, clear_quantumleap

# Import simulation model & platform clients
from tutorials.ngsi_v2.simulation_model import SimulationModel
from tutorials.n5geh_cluster.init_clients import (
    iota_client,
    cb_client,
    ql_client,
    QL_URL_INTERNAL,
)

# ==========================================
# 1. PARAMETERS
# ==========================================
MQTT_BROKER_URL = "mqtt://mqtt.n5geh.eonerc.rwth-aachen.de:8883"
MQTT_USER = "ebcdev"
MQTT_PW = "ebcdev"

SERVICE = "ebcdev1"
SERVICE_PATH = "/"

APIKEY_WS = "ebc_dev_apikey1"
APIKEY_TS = "ebc_dev_apikey2"

# Simulation parameters
TEMPERATURE_MAX = 10
TEMPERATURE_MIN = -5
TEMPERATURE_ZONE_START = 20

T_SIM_START = 0
T_SIM_END = 24 * 60 * 60
COM_STEP = 60 * 60 * 0.25  # 15 min steps


# ==========================================
# 2. PROVISIONING (Registering Devices)
# ==========================================
def provision_temperature_sensor(apikey, entity_type, device_id, entity_name):
    """
    Helper function to register a device group, the device itself,
    and set up the subscription to save data to the historical database.
    """
    print(f"\n[Provisioning] Setting up {entity_type} ({entity_name})...")

    # 1. Create a service group for this type of sensor
    # The best practice of service is to create a service group for each type of device
    existing_groups = iota_client.get_group_list()
    if entity_type not in [g.entity_type for g in existing_groups]:
        service_group = ServiceGroup(
            apikey=apikey, resource="/iot/json", entity_type=entity_type
        )
        iota_client.post_group(service_group=service_group, update=True)

    # 2. Define the attributes our device will send
    attr_sim_time = DeviceAttribute(name="sim_time", type="Number")
    attr_temperature = DeviceAttribute(name="temperature", type="Number")

    # 3. Create and register the device
    device = Device(
        device_id=device_id,
        entity_name=entity_name,
        entity_type=entity_type,
        protocol="IoTA-JSON",
        transport="MQTT",
        apikey=apikey,
        attributes=[attr_sim_time, attr_temperature],
        commands=[],
    )
    iota_client.post_device(device=device, update=True)

    # 4. Create a subscription so the Context Broker forwards data to QuantumLeap (Historical DB)
    print(f"[Provisioning] Creating database subscription for {entity_type}...")
    cb_client.post_subscription(
        subscription=Subscription(
            subject=Subject(
                # Here idPattern: ".*" + type: "WeatherStation" applies to every entity of this type
                **{"entities": [{"idPattern": ".*", "type": entity_type}]}
            ),
            notification=Notification(
                **{"http": {"url": f"{QL_URL_INTERNAL}/v2/notify"}}
            ),
            throttling=0,
        )
    )


# ==========================================
# 3. PUBLISHER (Simulate & Send Data)
# ==========================================
def run_simulation_and_publish(pause_time=0.1):
    """
    Runs the temperature simulation and publishes the data for both
    devices to the IoT Agent via MQTT.
    """
    print("\n[Publisher] Initializing simulation and MQTT client...")

    sim_model = SimulationModel(
        t_start=T_SIM_START,
        t_end=T_SIM_END,
        temp_max=TEMPERATURE_MAX,
        temp_min=TEMPERATURE_MIN,
        temp_start=TEMPERATURE_ZONE_START,
    )

    # IoTagent Ingress topic conventions: /json/{APIKEY}/{DEVICE_ID}/attrs
    topic_ws = f"/json/{APIKEY_WS}/device:001/attrs"
    topic_ts = f"/json/{APIKEY_TS}/device:002/attrs"

    # Setup MQTT Client
    mqttc = mqtt.Client(
        protocol=mqtt.MQTTv5, callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )
    mqttc.username_pw_set(username=MQTT_USER, password=MQTT_PW)
    mqttc.tls_set()

    url = urlparse(MQTT_BROKER_URL)
    mqttc.connect(
        host=url.hostname,
        port=url.port,
        keepalive=60,
        clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY,
    )

    mqttc.loop_start()

    print("[Publisher] Starting to publish data...")
    for t_sim in range(
        sim_model.t_start, sim_model.t_end + int(COM_STEP), int(COM_STEP)
    ):
        # Publish Weather Station data
        mqttc.publish(
            topic=topic_ws,
            payload=json.dumps(
                {"temperature": sim_model.t_amb, "sim_time": sim_model.t_sim}
            ),
        )

        # Publish Zone Temperature data
        mqttc.publish(
            topic=topic_ts,
            payload=json.dumps(
                {"temperature": sim_model.t_zone, "sim_time": sim_model.t_sim}
            ),
        )

        print(f"[Publisher] Sent data for sim_time: {sim_model.t_sim}s")

        sim_model.do_step(int(t_sim + COM_STEP))
        time.sleep(pause_time)  # Brief pause to allow platform processing

    mqttc.loop_stop()
    mqttc.disconnect()
    print("[Publisher] Simulation finished. MQTT disconnected.")


# ==========================================
# 4. DATA RETRIEVAL
# ==========================================
def fetch_historical_data(entity_id, entity_type, attr_name, last_n):
    """
    Retrieves the stored history from the QuantumLeap time-series database
    and neatly unpacks it into lists for plotting.
    """
    print(f"\n[Data Platform] Fetching history for {entity_id}...")

    # Query QuantumLeap
    history = ql_client.get_entity_by_id(
        entity_id=entity_id,
        entity_type=entity_type,
        last_n=last_n,
    )

    # Extract specific attributes from the returned data structure
    temperatures = [
        attr.values for attr in history.attributes if attr.attrName == attr_name
    ][0]
    sim_times = [
        attr.values for attr in history.attributes if attr.attrName == "sim_time"
    ][0]

    print(f"[Data Platform] Successfully retrieved {len(temperatures)} records.")
    return sim_times, temperatures


# ==========================================
# 5. VISUALIZATION
# ==========================================
def plot_results(time_ws, temp_ws, time_ts, temp_ts):
    """Plots the historical data retrieved from the platform."""
    print("\n[Visualization] Generating plots...")

    # Convert seconds to hours for easier reading
    time_ws_hours = [t / 3600 for t in time_ws]
    time_ts_hours = [t / 3600 for t in time_ts]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))

    # Weather Station Plot
    ax1.plot(time_ws_hours, temp_ws, marker="o", color="blue")
    ax1.set_title("Weather Station (Ambient)")
    ax1.set_xlabel("Time (hours)")
    ax1.set_ylabel("Temperature (°C)")
    ax1.grid(True)

    # Zone Temperature Plot
    ax2.plot(time_ts_hours, temp_ts, marker="o", color="orange")
    ax2.set_title("Thermal Zone (Indoor)")
    ax2.set_xlabel("Time (hours)")
    ax2.set_ylabel("Temperature (°C)")
    ax2.grid(True)

    plt.tight_layout()
    plt.show()


# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    # 1. Clean previous state to avoid conflicts
    print("[Setup] Clearing old platform data...")
    clear_iot_agent(iota_client=iota_client)
    clear_context_broker(cb_client=cb_client)
    clear_quantumleap(ql_client=ql_client)

    # 2. Provision devices in the FIWARE platform
    provision_temperature_sensor(
        apikey=APIKEY_WS,
        entity_type="WeatherStation",
        device_id="device:001",
        entity_name="urn:ngsi-ld:WeatherStation:001",
    )
    provision_temperature_sensor(
        apikey=APIKEY_TS,
        entity_type="TemperatureSensor",
        device_id="device:002",
        entity_name="urn:ngsi-ld:TemperatureSensor:001",
    )

    # 3. Run simulation and send data
    run_simulation_and_publish()

    # Wait a few seconds to ensure the database has finished writing all records
    print("\n[Wait] Giving the database 5 seconds to process incoming records...")
    time.sleep(5)

    # 4. Fetch the data back from the platform
    # Calculate how many records we expect based on simulation length
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

    # 5. Plot the retrieved data
    plot_results(time_ws, temp_ws, time_ts, temp_ts)
