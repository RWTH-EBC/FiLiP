"""
# # Exercise 5: Virtual Thermal Zone with Control

# Create a virtual IoT device that simulates a heater for your
# thermal zone. The heater can be turned on and off via a simple hysteresis
# controller. The devices from e4_iot_thermal_zone_sensors.py will be loaded
# from the stored *.json-files.

# The input sections are marked with 'ToDo'

# #### Steps to complete:
# 1. Set up the missing parameters in the parameter section
# 2. Retrieve the service group and device configurations of already existing
#    devices from the IoT-Agent
# 3. Create a third device configuration for a heater holding a command
#    for turning it `on` and `off` and post it to the server
# 4. Create an MQTT client using the filip.client.mqtt package and register
#    your service group and your devices
# 4. Define a callback function that will be executed when the client
#    receives a command. Decode the message and set the update state in
#    simulation model. Afterwards, acknowledge the command using the api of the
#    IoTAMQTTClient.
# 5. Add the callback for your heater device to the IoTAMQTTClient
# 6. Create an MQTT subscription for asynchronous communication that
#    gets triggered when the temperature attribute changes.
# 7. Write a second callback that represents your controller. It should get
#    triggered when the MQTTClient receives a notification message due to your
#    subscription. Add the callback to your MQTTClient using the original
#    paho-api (`message_callback_add`)
# 8. Run the simulation and plot
"""

# ## Import packages
import json
from pathlib import Path
import time
from typing import List
from urllib.parse import urlparse
from uuid import uuid4
import paho.mqtt.client as mqtt
from pydantic import TypeAdapter
import matplotlib.pyplot as plt

# import from filip
from filip.clients.ngsi_v2 import ContextBrokerClient, IoTAClient
from filip.clients.mqtt import IoTAMQTTClient
from filip.models.base import DataType, FiwareHeader
from filip.models.ngsi_v2.context import NamedCommand
from filip.models.ngsi_v2.subscriptions import Subscription, Message
from filip.models.ngsi_v2.iot import \
    Device, \
    DeviceAttribute, \
    DeviceCommand, \
    PayloadProtocol, \
    ServiceGroup
from filip.utils.cleanup import clear_context_broker, clear_iot_agent
# import simulation model
from tutorials.ngsi_v2.simulation_model import SimulationModel

# ## Parameters
# ToDo: Enter your context broker host and port, e.g http://localhost:1026.
CB_URL = "http://localhost:1026"
# ToDo: Enter your IoT-Agent host and port, e.g http://localhost:4041.
IOTA_URL = "http://localhost:4041"
# ToDo: Enter your mqtt broker url, e.g mqtt://test.mosquitto.org:1883.
MQTT_BROKER_URL_EXPOSED = "mqtt://localhost:1883"
# ToDo: Enter your mqtt broker url, e.g mqtt://mosquitto:1883.
MQTT_BROKER_URL_INTERNAL = "mqtt://mosquitto:1883"
# ToDo: If required, enter your username and password.
MQTT_USER = ""
MQTT_PW = ""

# ToDo: Change the name of your service to something unique. If you run
#  on a shared instance this is very important in order to avoid user
#  collisions. You will use this service through the whole tutorial.
#  If you forget to change it, an error will be raised!
# FIWARE-Service
SERVICE = 'filip_tutorial'
# FIWARE-Service path
SERVICE_PATH = '/'

# ToDo: Change the APIKEY to something unique. This represents the "token"
#  for IoT devices to connect (send/receive data) with the platform. In the
#  context of MQTT, APIKEY is linked with the topic used for communication.
APIKEY = 'your_apikey'
UNIQUE_ID = str(uuid4())
TOPIC_CONTROLLER = f"fiware_workshop/{UNIQUE_ID}/controller"
print(TOPIC_CONTROLLER)
# path to json-files to store entity data for follow up exercises
WRITE_GROUPS_FILEPATH = \
    Path("../e5_iot_thermal_zone_control_solution_groups.json")
WRITE_DEVICES_FILEPATH = \
    Path("../e5_iot_thermal_zone_control_solution_devices.json")
WRITE_SUBSCRIPTIONS_FILEPATH = \
    Path("../e5_iot_thermal_zone_control_solution_subscriptions.json")
# path to read json-files from previous exercises
READ_GROUPS_FILEPATH = \
    Path("../e4_iot_thermal_zone_sensors_solution_groups.json")
READ_DEVICES_FILEPATH = \
    Path("../e4_iot_thermal_zone_sensors_solution_devices.json")

# opening the files
with (open(READ_GROUPS_FILEPATH, 'r') as groups_file,
      open(READ_DEVICES_FILEPATH, 'r') as devices_file):
    json_groups = json.load(groups_file)
    json_devices = json.load(devices_file)

# set parameters for the temperature simulation
TEMPERATURE_MAX = 10  # maximal ambient temperature
TEMPERATURE_MIN = -5  # minimal ambient temperature
TEMPERATURE_ZONE_START = 20  # start value of the zone temperature

T_SIM_START = 0  # simulation start time in seconds
T_SIM_END = 24 * 60 * 60  # simulation end time in seconds
COM_STEP = 60 * 60 * 0.25  # 15 min communication step in seconds

# ## Main script
if __name__ == '__main__':
    # create a fiware header object
    fiware_header = FiwareHeader(service=SERVICE,
                                 service_path=SERVICE_PATH)
    # clear the state of your service and scope
    clear_iot_agent(url=IOTA_URL, fiware_header=fiware_header)
    clear_context_broker(url=CB_URL, fiware_header=fiware_header)

    # instantiate simulation model
    sim_model = SimulationModel(t_start=T_SIM_START,
                                t_end=T_SIM_END,
                                temp_max=TEMPERATURE_MAX,
                                temp_min=TEMPERATURE_MIN,
                                temp_start=TEMPERATURE_ZONE_START)

    # define lists to store historical data
    history_weather_station = []
    history_zone_temperature_sensor = []
    history_heater = []

    # create clients and also restore devices and groups from file
    groups = TypeAdapter(List[ServiceGroup]).validate_python(json_groups)
    devices = TypeAdapter(List[Device]).validate_python(json_devices)
    cbc = ContextBrokerClient(url=CB_URL, fiware_header=fiware_header)
    iotac = IoTAClient(url=IOTA_URL, fiware_header=fiware_header)
    iotac.post_groups(service_groups=groups)
    iotac.post_devices(devices=devices)

    # ToDo: Get the device configurations from the server.
    weather_station = iotac.get_device(device_id="device:001")
    zone_temperature_sensor = iotac.get_device(device_id="device:002")

    # ToDo: Get the service group configurations from the server.
    group = iotac.get_group(resource="/iot/json", apikey=APIKEY)

    # ToDo: Create an additional device holding a command attribute and
    #  post it to the IoT-Agent. It should be mapped to the `type` heater.
    # create the sim_time attribute and add it during device creation
    t_sim = DeviceAttribute(name='sim_time',
                            object_id='t_sim',
                            type="Number")

    # ToDo: Create the command attribute of name `heater_on` (currently it is
    #  not possible to add metadata here).
    cmd = DeviceCommand(name="heater_on",
                        type=DataType.BOOLEAN)

    # ToDo: Create the device configuration and send it to the server.
    heater = Device(device_id="device:003",
                    entity_name="urn:ngsi-ld:Heater:001",
                    entity_type="Heater",
                    apikey=APIKEY,
                    attributes=[t_sim],
                    commands=[cmd],
                    transport='MQTT',
                    protocol='IoTA-JSON')

    iotac.post_device(device=heater)

    # ToDo: Check the entity that corresponds to your device.
    heater_entity = cbc.get_entity(entity_id=heater.entity_name,
                                   entity_type=heater.entity_type)
    print(f"Your device entity before running the simulation: \n "
          f"{heater_entity.model_dump_json(indent=2)}")

    # create a MQTTv5 client with paho-mqtt and the known groups and devices.
    mqttc = IoTAMQTTClient(protocol=mqtt.MQTTv5,
                           devices=[weather_station,
                                    zone_temperature_sensor,
                                    heater],
                           service_groups=[group])
    # set user data if required
    mqttc.username_pw_set(username=MQTT_USER, password=MQTT_PW)

    # ToDo: Implement a callback function that gets triggered when the
    #  command is sent to the device. The incoming command should update the
    #  heater attribute of the simulation model.
    def on_command(client, obj, msg):
        """
        Callback for incoming commands
        """
        # decode the message payload using the libraries builtin encoders
        apikey, device_id, payload = \
            client.get_encoder(PayloadProtocol.IOTA_JSON).decode_message(
                msg=msg)
        # map the command value to the simulation
        sim_model.heater_on = payload[cmd.name]

        # ToDo: Acknowledge the command. In this case commands are usually single
        #   messages. The first key is equal to the commands name.
        client.publish(device_id=device_id,
                       command_name=next(iter(payload)),
                       payload=payload)

    # ToDo: Add the command callback to your MQTTClient. This will get
    #  triggered for the specified device_id.
    mqttc.add_command_callback(device_id=heater.device_id,
                               callback=on_command)

    # ToDO: Create an MQTT subscription for asynchronous communication that
    #  gets triggered when the temperature attribute changes.
    subscription = {
        "description": "Subscription to receive MQTT-Notifications about "
                       "urn:ngsi-ld:ThermalZone:001",
        "subject": {
            "entities": [
                {
                    "id": zone_temperature_sensor.entity_name,
                    "type": zone_temperature_sensor.entity_type
                }
            ],
        },
        "notification": {
            "mqtt": {
                "url": MQTT_BROKER_URL_INTERNAL,
                "topic": TOPIC_CONTROLLER,
                "user": MQTT_USER,
                "passwd": MQTT_PW
            }
        },
        "throttling": 0
    }
    # generate Subscription object for validation and post it
    subscription = Subscription(**subscription)
    subscription_id = cbc.post_subscription(subscription=subscription)

    # ToDo: You need to implement a controller that controls the
    #  heater state with respect to the zone temperature. This will be
    #  implemented with asynchronous communication using MQTT-Subscriptions.
    def on_measurement(client, obj, msg):
        """
        Callback for measurement notifications
        """
        message = Message.model_validate_json(msg.payload)
        updated_zone_temperature_sensor = message.data[0]

        # ToDo: Retrieve the value of temperature attribute.
        temperature = updated_zone_temperature_sensor.temperature.value

        update = True
        if temperature <= 19:
            state = 1
        elif temperature >= 21:
            state = 0
        else:
            update = False

        # ToDo: Send the command to the heater entity.
        if update:
            command = NamedCommand(name=cmd.name, value=state)
            cbc.post_command(entity_id=heater.entity_name,
                             entity_type=heater.entity_type,
                             command=command)

    mqttc.message_callback_add(sub=TOPIC_CONTROLLER,
                               callback=on_measurement)

    # connect to the mqtt broker and subscribe to your topic
    mqtt_url = urlparse(MQTT_BROKER_URL_EXPOSED)
    mqttc.connect(host=mqtt_url.hostname,
                  port=mqtt_url.port,
                  keepalive=60,
                  bind_address="",
                  bind_port=0,
                  clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY,
                  properties=None)
    # subscribe to topics
    # subscribe to all incoming command topics for the registered devices
    mqttc.subscribe()
    mqttc.subscribe(topic=TOPIC_CONTROLLER)

    # create a non-blocking thread for mqtt communication
    mqttc.loop_start()

    # ToDo: Create a loop that publishes a message every 100 milliseconds
    #  to the broker that holds the simulation time "sim_time" and the
    #  corresponding temperature "temperature". You may use the `object_id`
    #  or the attribute name as key in your payload.
    for t_sim in range(sim_model.t_start,
                       sim_model.t_end + int(COM_STEP),
                       int(COM_STEP)):
        # publish the simulated ambient temperature
        mqttc.publish(device_id=weather_station.device_id,
                      payload={"temperature": sim_model.t_amb,
                               "sim_time": sim_model.t_sim})

        # publish the simulated zone temperature
        mqttc.publish(device_id=zone_temperature_sensor.device_id,
                      payload={"temperature": sim_model.t_zone,
                               "sim_time": sim_model.t_sim})

        # publish the 'sim_time' for the heater device
        mqttc.publish(device_id=heater.device_id,
                      payload={"sim_time": sim_model.t_sim})

        time.sleep(0.1)
        # simulation step for next loop
        sim_model.do_step(int(t_sim + COM_STEP))
        # wait for 0.1 second before publishing the next values
        time.sleep(0.1)

        # get corresponding entities and write values to history
        weather_station_entity = cbc.get_entity(
            entity_id=weather_station.entity_name,
            entity_type=weather_station.entity_type
        )
        # append the data to the local history
        history_weather_station.append(
            {"sim_time": weather_station_entity.sim_time.value,
             "temperature": weather_station_entity.temperature.value})

        # get zone temperature sensor and write values to history
        zone_temperature_sensor_entity = cbc.get_entity(
            entity_id=zone_temperature_sensor.entity_name,
            entity_type=zone_temperature_sensor.entity_type
        )
        history_zone_temperature_sensor.append(
            {"sim_time": zone_temperature_sensor_entity.sim_time.value,
             "temperature": zone_temperature_sensor_entity.temperature.value})

        # get zone temperature sensor and write values to history
        heater_entity = cbc.get_entity(
            entity_id=heater.entity_name,
            entity_type=heater.entity_type)
        history_heater.append(
            {"sim_time": heater_entity.sim_time.value,
             "on_off": heater_entity.heater_on_info.value})

    # close the mqtt listening thread
    mqttc.loop_stop()
    # disconnect the mqtt device
    mqttc.disconnect()

    print(cbc.get_entity(entity_id=heater.entity_name,
                         entity_type=heater.entity_type).model_dump_json(indent=2))

    # plot results
    fig, ax = plt.subplots()
    t_simulation = [item["sim_time"]/60 for item in history_weather_station]
    temperature = [item["temperature"] for item in history_weather_station]
    ax.plot(t_simulation, temperature)
    ax.title.set_text("Weather Station")
    ax.set_xlabel('time in min')
    ax.set_ylabel('ambient temperature in °C')
    plt.show()

    fig2, ax2 = plt.subplots()
    t_simulation = [item["sim_time"]/60 for item in history_zone_temperature_sensor]
    temperature = [item["temperature"] for item in
                   history_zone_temperature_sensor]
    ax2.plot(t_simulation, temperature)
    ax2.title.set_text("Zone Temperature Sensor")
    ax2.set_xlabel('time in min')
    ax2.set_ylabel('zone temperature in °C')
    plt.show()

    fig3, ax3 = plt.subplots()
    t_simulation = [item["sim_time"]/60 for item in history_heater]
    on_off = [item["on_off"] for item in history_heater]
    ax3.plot(t_simulation, on_off)
    ax3.title.set_text("Heater")
    ax3.set_xlabel('time in min')
    ax3.set_ylabel('on/off')
    plt.show()

    # write devices and groups to file and clear server state
    assert WRITE_DEVICES_FILEPATH.suffix == '.json', \
        f"Wrong file extension! {WRITE_DEVICES_FILEPATH.suffix}"
    WRITE_DEVICES_FILEPATH.touch(exist_ok=True)
    with WRITE_DEVICES_FILEPATH.open('w', encoding='utf-8') as f:
        devices = [item.model_dump() for item in iotac.get_device_list()]
        json.dump(devices, f, ensure_ascii=False, indent=2)

    assert WRITE_GROUPS_FILEPATH.suffix == '.json', \
        f"Wrong file extension! {WRITE_GROUPS_FILEPATH.suffix}"
    WRITE_GROUPS_FILEPATH.touch(exist_ok=True)
    with WRITE_GROUPS_FILEPATH.open('w', encoding='utf-8') as f:
        groups = [item.model_dump() for item in iotac.get_group_list()]
        json.dump(groups, f, ensure_ascii=False, indent=2)

    assert WRITE_SUBSCRIPTIONS_FILEPATH.suffix == '.json', \
        f"Wrong file extension! {WRITE_SUBSCRIPTIONS_FILEPATH.suffix}"
    WRITE_SUBSCRIPTIONS_FILEPATH.touch(exist_ok=True)
    with WRITE_SUBSCRIPTIONS_FILEPATH.open('w', encoding='utf-8') as f:
        subs = [item.model_dump() for item in cbc.get_subscription_list()]
        json.dump(subs, f, ensure_ascii=False, indent=2)

    clear_iot_agent(url=IOTA_URL, fiware_header=fiware_header)
    clear_context_broker(url=CB_URL, fiware_header=fiware_header)
