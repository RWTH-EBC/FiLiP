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
from pathlib import Path
import time
from urllib.parse import urlparse
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt

# import from filip
from filip.clients.ngsi_v2 import ContextBrokerClient, IoTAClient
from filip.clients.mqtt import IoTAMQTTClient
from filip.models.base import FiwareHeader
from filip.models.ngsi_v2.iot import Device, DeviceAttribute, ServiceGroup
from filip.utils.cleanup import clear_context_broker, clear_iot_agent

# import simulation model
from tutorials.ngsi_v2.simulation_model import SimulationModel

# ## Parameters
# ToDo: Enter your context broker host and port, e.g. http://localhost:1026.
CB_URL = "http://localhost:1026"
# ToDo: Enter your IoT-Agent host and port, e.g. http://localhost:4041.
IOTA_URL = "http://localhost:4041"
# ToDo: Enter your mqtt broker url, e.g. mqtt://test.mosquitto.org:1883.
MQTT_BROKER_URL = "mqtt://localhost:1883"
# ToDo: If required, enter your username and password.
MQTT_USER = ""
MQTT_PW = ""

# ToDo: Change the name of your service to something unique. If you run
#  on a shared instance this is very important in order to avoid user
#  collisions. You will use this service through the whole tutorial.
#  If you forget to change it, an error will be raised!
# FIWARE-Service
SERVICE = "filip_tutorial"
# FIWARE-Service path
SERVICE_PATH = "/"

# ToDo: Change the APIKEY to something unique. This represents the "token"
#  for IoT devices to connect (send/receive data) with the platform. In the
#  context of MQTT, APIKEY is linked with the topic used for communication.
APIKEY = "your_apikey"

# path to json-files to device configuration data for follow-up exercises
WRITE_GROUPS_FILEPATH = Path("../e4_iot_thermal_zone_sensors_solution_groups.json")
WRITE_DEVICES_FILEPATH = Path("../e4_iot_thermal_zone_sensors_solution_devices.json")

# set parameters for the temperature simulation
TEMPERATURE_MAX = 10  # maximal ambient temperature
TEMPERATURE_MIN = -5  # minimal ambient temperature
TEMPERATURE_ZONE_START = 20  # start value of the zone temperature

T_SIM_START = 0  # simulation start time in seconds
T_SIM_END = 24 * 60 * 60  # simulation end time in seconds
COM_STEP = 60 * 60 * 0.25  # 15 min communication step in seconds

# ## Main script
if __name__ == "__main__":
    # create a fiware header object
    fiware_header = FiwareHeader(service=SERVICE, service_path=SERVICE_PATH)
    # clear the state of your service and scope
    clear_iot_agent(url=IOTA_URL, fiware_header=fiware_header)
    clear_context_broker(url=CB_URL, fiware_header=fiware_header)

    # instantiate simulation model
    sim_model = SimulationModel(
        t_start=T_SIM_START,
        t_end=T_SIM_END,
        temp_max=TEMPERATURE_MAX,
        temp_min=TEMPERATURE_MIN,
        temp_start=TEMPERATURE_ZONE_START,
    )

    # define lists to store historical data
    history_weather_station = []
    history_zone_temperature_sensor = []

    # create a service group with your api key
    service_group = ServiceGroup(apikey=APIKEY, resource="/iot/json")

    # ToDo: Create two IoTA-MQTT devices for the weather station and the zone
    #  temperature sensor. Also add the simulation time as `active attribute`
    #  to each device!
    # create the weather station device
    # create the `sim_time` attribute and add it to the weather station's attributes
    t_sim = DeviceAttribute(name="sim_time", object_id="t_sim", type="Number")

    weather_station = Device(
        device_id="device:001",
        entity_name="urn:ngsi-ld:WeatherStation:001",
        entity_type="WeatherStation",
        protocol="IoTA-JSON",
        transport="MQTT",
        apikey=APIKEY,
        attributes=[t_sim],
        commands=[],
    )

    # create a temperature attribute and add it via the api of the
    # `device`-model. Use the `t_amb` as `object_id`. `object_id` specifies
    # what key will be used in the MQTT Message payload
    t_amb = DeviceAttribute(name="temperature", object_id="t_amb", type="Number")

    weather_station.add_attribute(t_amb)

    # ToDo: Create the zone temperature device and add the `t_sim` attribute upon
    #  creation.
    zone_temperature_sensor = Device(
        device_id="device:002",
        entity_name="urn:ngsi-ld:TemperatureSensor:001",
        entity_type="TemperatureSensor",
        protocol="IoTA-JSON",
        transport="MQTT",
        apikey=APIKEY,
        attributes=[t_sim],
        commands=[],
    )

    # ToDo: Create the temperature attribute. Use the `t_zone` as `object_id`.
    #  `object_id` specifies what key will be used in the MQTT Message payload.
    t_zone = DeviceAttribute(name="temperature", object_id="t_zone", type="Number")

    zone_temperature_sensor.add_attribute(t_zone)

    # ToDo: Create an IoTAClient.
    iotac = IoTAClient(url=IOTA_URL, fiware_header=fiware_header)
    # ToDo: Provision service group and add it to your IoTAMQTTClient.
    iotac.post_group(service_group=service_group, update=True)
    # ToDo: Provision the devices at the IoTA-Agent.
    # provision the weather station device
    iotac.post_device(device=weather_station, update=True)
    # ToDo: Provision the zone temperature device.
    iotac.post_device(device=zone_temperature_sensor, update=True)

    # ToDo: Create a context broker client.
    # ToDo: Check in the context broker whether the entities corresponding to your
    #  devices were correctly created.
    cbc = ContextBrokerClient(url=CB_URL, fiware_header=fiware_header)
    # get weather station entity
    print(
        f"Weather station:\n{cbc.get_entity(weather_station.entity_name).model_dump_json(indent=2)}"
    )
    # ToDo: Get zone temperature sensor entity.
    print(
        f"Zone temperature sensor:\n{cbc.get_entity(zone_temperature_sensor.entity_name).model_dump_json(indent=2)}"
    )

    # ToDo: Create an MQTTv5 client using filip.clients.mqtt.IoTAMQTTClient.
    mqttc = IoTAMQTTClient(protocol=mqtt.MQTTv5)
    # set user data if required
    mqttc.username_pw_set(username=MQTT_USER, password=MQTT_PW)
    # ToDo: Register the service group with your MQTT-Client.
    mqttc.add_service_group(service_group=service_group)
    # ToDo: Register devices with your MQTT-Client.
    # register the weather station
    mqttc.add_device(weather_station)
    # ToDo: Register the zone temperature sensor.
    mqttc.add_device(zone_temperature_sensor)

    # The IoTAMQTTClient automatically creates outgoing topics from the
    # device configuration during runtime. Hence, we need to construct them
    # manually in order to subscribe to them. This is usually not required as
    # only the platform should listen to the incoming traffic.
    # If you want to listen subscribe to the following topics:
    # "/json/<APIKEY>/<weather_station.device_id>/attrs"
    # "/json/<APIKEY>/<zone_temperature_sensor.device_id>/attrs"

    # ToDO: Connect to the MQTT broker and subscribe to your topic.
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
    # subscribe to topics
    # subscribe to all incoming command topics for the registered devices
    mqttc.subscribe()
    # create a non-blocking thread for mqtt communication
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
            device_id=weather_station.device_id,
            payload={"temperature": sim_model.t_amb, "sim_time": sim_model.t_sim},
        )

        # ToDo: Publish the simulated zone temperature.
        mqttc.publish(
            device_id=zone_temperature_sensor.device_id,
            payload={"temperature": sim_model.t_zone, "sim_time": sim_model.t_sim},
        )

        # simulation step for the next loop
        sim_model.do_step(int(t_sim + COM_STEP))
        # wait for one second before publishing the next values
        time.sleep(0.1)

        # get corresponding entities and store the data
        weather_station_entity = cbc.get_entity(
            entity_id=weather_station.entity_name,
            entity_type=weather_station.entity_type,
        )
        # append the data to the local history
        history_weather_station.append(
            {
                "sim_time": weather_station_entity.sim_time.value,
                "temperature": weather_station_entity.temperature.value,
            }
        )

        # ToDo: Get zone temperature sensor and store the data.
        zone_temperature_sensor_entity = cbc.get_entity(
            entity_id=zone_temperature_sensor.entity_name,
            entity_type=zone_temperature_sensor.entity_type,
        )
        history_zone_temperature_sensor.append(
            {
                "sim_time": zone_temperature_sensor_entity.sim_time.value,
                "temperature": zone_temperature_sensor_entity.temperature.value,
            }
        )

    # close the mqtt listening thread
    mqttc.loop_stop()
    # disconnect the mqtt device
    mqttc.disconnect()

    # plot the results
    fig, ax = plt.subplots()
    t_simulation = [item["sim_time"] / 3600 for item in history_weather_station]
    temperature = [item["temperature"] for item in history_weather_station]
    ax.plot(t_simulation, temperature)
    ax.title.set_text("Weather Station")
    ax.set_xlabel("time in h")
    ax.set_ylabel("ambient temperature in °C")

    fig2, ax2 = plt.subplots()
    t_simulation = [item["sim_time"] / 3600 for item in history_zone_temperature_sensor]
    temperature = [item["temperature"] for item in history_zone_temperature_sensor]
    ax2.plot(t_simulation, temperature)
    ax2.title.set_text("Zone Temperature Sensor")
    ax2.set_xlabel("time in h")
    ax2.set_ylabel("zone temperature in °C")

    plt.show()

    # write devices and groups to file and clear server state
    assert (
        WRITE_DEVICES_FILEPATH.suffix == ".json"
    ), f"Wrong file extension! {WRITE_DEVICES_FILEPATH.suffix}"
    WRITE_DEVICES_FILEPATH.touch(exist_ok=True)
    with WRITE_DEVICES_FILEPATH.open("w", encoding="utf-8") as f:
        devices = [item.model_dump() for item in iotac.get_device_list()]
        json.dump(devices, f, ensure_ascii=False, indent=2)

    assert (
        WRITE_GROUPS_FILEPATH.suffix == ".json"
    ), f"Wrong file extension! {WRITE_GROUPS_FILEPATH.suffix}"
    WRITE_GROUPS_FILEPATH.touch(exist_ok=True)
    with WRITE_GROUPS_FILEPATH.open("w", encoding="utf-8") as f:
        groups = [item.model_dump() for item in iotac.get_group_list()]
        json.dump(groups, f, ensure_ascii=False, indent=2)

    clear_iot_agent(url=IOTA_URL, fiware_header=fiware_header)
    clear_context_broker(url=CB_URL, fiware_header=fiware_header)
