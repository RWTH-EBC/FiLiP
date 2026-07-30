"""
# # Exercise 4: Virtual Thermal Zone

# Create two virtual IoT devices. One of them represents the temperature
# sensor for the air temperature of a thermal zone, whereas the second
# represents a virtual weather station. Both devices publish their values to
# the platform via MQTT. Use the simulation model of
# e1_virtual_weatherstation.py
#
# The input sections are marked with 'ToDo'
#
# #### Steps to complete:
# 1. Set up the missing parameters in the parameter section
# 2. Create a service group and two corresponding devices
# 3. Provision the service group and the devices
# 4. Create an MQTT client using the filip.client.mqtt package and register
#    your service group and your devices
# 5. Check if the IoT-Agent correctly creates the corresponding entities
# 5. Create a function that publishes the simulated temperature via MQTT,
#    retrieves the entity data after each message and writes the values to a
#    history
# 6. Run the simulation and plot the results
"""

# ## Import packages
import json
import time
from urllib.parse import urlparse
import paho.mqtt.client as mqtt

# import from filip
from filip.models.ngsi_v2.iot import Device, DeviceAttribute, ServiceGroup
from filip.utils.cleanup import clear_context_broker, clear_iot_agent

# import simulation model
from tutorials.ngsi_v2.simulation_model import SimulationModel
from tutorials.n5geh_cluster.init_clients import iota_client, cb_client, ql_client

# ## Parameters


MQTT_BROKER_URL = "mqtt://mqtt.n5geh.eonerc.rwth-aachen.de:8883"
MQTT_USER = "ebcdev"
MQTT_PW = "ebcdev"

# TODO available SERVICE: ebcdev1 - ebcdev5
# FIWARE-Service
SERVICE = "ebcdev1"
# FIWARE-Service path
SERVICE_PATH = "/"

# TODO available APIKEY: ebc_dev_apikey1 - ebc_dev_apikey5
APIKEY_WS = "ebc_dev_apikey1"
APIKEY_TS = "ebc_dev_apikey2"

# path to json-files to device configuration data for follow-up exercises

# set parameters for the temperature simulation
TEMPERATURE_MAX = 10  # maximal ambient temperature
TEMPERATURE_MIN = -5  # minimal ambient temperature
TEMPERATURE_ZONE_START = 20  # start value of the zone temperature

T_SIM_START = 0  # simulation start time in seconds
T_SIM_END = 24 * 60 * 60  # simulation end time in seconds
COM_STEP = 60 * 60 * 0.25  # 15 min communication step in seconds


def provision_weather_station():
    # create a service group for a type of sensors
    service_group_ws = ServiceGroup(
        apikey=APIKEY_WS, resource="/iot/json", entity_type="WeatherStation"
    )

    # ToDo: Create two IoTA-MQTT devices for the weather station and the zone
    #  temperature sensor. Also add the simulation time as `active attribute`
    #  to each device!
    # create the weather station device
    # create the `sim_time` attribute and add it to the weather station's attributes
    t_sim = DeviceAttribute(name="sim_time", type="Number")

    weather_station = Device(
        device_id="device:001",
        entity_name="urn:ngsi-ld:WeatherStation:001",
        entity_type="WeatherStation",
        protocol="IoTA-JSON",
        transport="MQTT",
        apikey=APIKEY_WS,
        attributes=[t_sim],
        commands=[],
    )

    # create a temperature attribute and add it via the api of the
    # `device`-model. Use the `t_amb` as `object_id`. `object_id` specifies
    # what key will be used in the MQTT Message payload
    t_amb = DeviceAttribute(name="temperature", type="Number")

    weather_station.add_attribute(t_amb)

    iota_client.post_group(service_group=service_group_ws, update=True)
    iota_client.post_device(device=weather_station, update=True)


def provision_room_temperature_sensor():
    # create a service group for a type of sensors
    service_group_ts = ServiceGroup(
        apikey=APIKEY_WS, resource="/iot/json", entity_type="TemperatureSensor"
    )

    # create the `sim_time` attribute and add it to the weather station's attributes
    t_sim = DeviceAttribute(name="sim_time", type="Number")

    # ToDo: Create the zone temperature device and add the `t_sim` attribute upon
    #  creation.
    zone_temperature_sensor = Device(
        device_id="device:002",
        entity_name="urn:ngsi-ld:TemperatureSensor:001",
        entity_type="TemperatureSensor",
        protocol="IoTA-JSON",
        transport="MQTT",
        apikey=APIKEY_TS,
        attributes=[t_sim],
        commands=[],
    )

    # ToDo: Create the temperature attribute. Use the `t_zone` as `object_id`.
    #  `object_id` specifies what key will be used in the MQTT Message payload.
    t_zone = DeviceAttribute(name="temperature", type="Number")

    zone_temperature_sensor.add_attribute(t_zone)

    # ToDo: Provision service group and add it to your IoTAMQTTClient.
    iota_client.post_group(service_group=service_group_ts, update=True)
    # ToDo: Provision the devices at the IoTA-Agent.
    # provision the weather station device
    # ToDo: Provision the zone temperature device.
    iota_client.post_device(device=zone_temperature_sensor, update=True)


def publish_temperature_data():
    # instantiate simulation model
    sim_model = SimulationModel(
        t_start=T_SIM_START,
        t_end=T_SIM_END,
        temp_max=TEMPERATURE_MAX,
        temp_min=TEMPERATURE_MIN,
        temp_start=TEMPERATURE_ZONE_START,
    )

    # IoTagent Ingress topic conventions f"/json/{APIKEY}/{DEVICE_ID}/attrs"
    TOPIC_WEATHER_STATION = f"/json/{APIKEY_WS}/device:001/attrs"
    TOPIC_ZONE_TEMPERATURE_SENSOR = f"/json/{APIKEY_TS}/device:002/attrs"

    mqttc = mqtt.Client(
        protocol=mqtt.MQTTv5, callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )
    # set user data if required
    mqttc.username_pw_set(username=MQTT_USER, password=MQTT_PW)
    mqttc.tls_set()
    mqtt_url = urlparse(MQTT_BROKER_URL)
    mqttc.connect(
        host=mqtt_url.hostname,
        port=mqtt_url.port,
        keepalive=60,
        bind_address="",
        bind_port=0,
        clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY,
        properties=None,
    )

    mqttc.loop_start()

    # ToDo: Create a loop that publishes a message every 100 milliseconds
    #  to the broker that holds the simulation time `sim_time` and the
    #  corresponding temperature `temperature`. You may use the `object_id`
    #  or the attribute name as a key in your payload.
    for t_sim in range(
        sim_model.t_start, sim_model.t_end + int(COM_STEP), int(COM_STEP)
    ):
        # publish the simulated ambient temperature
        mqttc.publish(
            topic=TOPIC_WEATHER_STATION,
            payload=json.dumps(
                {"temperature": sim_model.t_amb, "sim_time": sim_model.t_sim}
            ),
        )

        # ToDo: Publish the simulated zone temperature.
        mqttc.publish(
            topic=TOPIC_ZONE_TEMPERATURE_SENSOR,
            payload=json.dumps(
                {"temperature": sim_model.t_zone, "sim_time": sim_model.t_sim}
            ),
        )

        # simulation step for the next loop
        sim_model.do_step(int(t_sim + COM_STEP))
        # wait for one second before publishing the next values
        time.sleep(0.1)

        # # get corresponding entities and store the data
        # weather_station_entity = cb_client.get_entity(
        #     entity_id=weather_station.entity_name,
        #     entity_type=weather_station.entity_type,
        # )
        # # append the data to the local history
        # history_weather_station.append(
        #     {
        #         "sim_time": weather_station_entity.sim_time.value,
        #         "temperature": weather_station_entity.temperature.value,
        #     }
        # )
        #
        # # ToDo: Get zone temperature sensor and store the data.
        # zone_temperature_sensor_entity = cb_client.get_entity(
        #     entity_id=zone_temperature_sensor.entity_name,
        #     entity_type=zone_temperature_sensor.entity_type,
        # )
        # history_zone_temperature_sensor.append(
        #     {
        #         "sim_time": zone_temperature_sensor_entity.sim_time.value,
        #         "temperature": zone_temperature_sensor_entity.temperature.value,
        #     }
        # )

    # close the mqtt listening thread
    mqttc.loop_stop()
    # disconnect the mqtt device
    mqttc.disconnect()


# ## Main script
if __name__ == "__main__":
    # clear the state of your service and scope
    clear_iot_agent(iota_client=iota_client)
    clear_context_broker(cb_client=cb_client)

    # provision the devices
    provision_weather_station()
    provision_room_temperature_sensor()

    # start simulation
    publish_temperature_data()

    time.sleep(5)

    # get history
    last_n = len(list(range(T_SIM_START, T_SIM_END + int(COM_STEP), int(COM_STEP))))

    entity_ws = cb_client.get_entity(
        entity_id="urn:ngsi-ld:WeatherStation:001", entity_type="WeatherStation"
    )
    entity_ts = cb_client.get_entity(
        entity_id="urn:ngsi-ld:TemperatureSensor:001", entity_type="TemperatureSensor"
    )

    history_ws = ql_client.get_entity_by_id(
        entity_id="urn:ngsi-ld:WeatherStation:001",
        entity_type="WeatherStation",
        last_n=last_n,
    )
    history_ts = ql_client.get_entity_by_id(
        entity_id="urn:ngsi-ld:TemperatureSensor:001",
        entity_type="TemperatureSensor",
        last_n=last_n,
    )

    # plot the results
    # fig, ax = plt.subplots()
    # t_simulation = [item["sim_time"] / 3600 for item in history_weather_station]
    # temperature = [item["temperature"] for item in history_weather_station]
    # ax.plot(t_simulation, temperature)
    # ax.title.set_text("Weather Station")
    # ax.set_xlabel("time in h")
    # ax.set_ylabel("ambient temperature in °C")
    #
    # fig2, ax2 = plt.subplots()
    # t_simulation = [item["sim_time"] / 3600 for item in history_zone_temperature_sensor]
    # temperature = [item["temperature"] for item in history_zone_temperature_sensor]
    # ax2.plot(t_simulation, temperature)
    # ax2.title.set_text("Zone Temperature Sensor")
    # ax2.set_xlabel("time in h")
    # ax2.set_ylabel("zone temperature in °C")
    #
    # plt.show()
