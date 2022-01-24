# # Exercise 4: Virtual Thermal Zone

# Create two virtual IoT device. One of them represents the temperature
# sensor for the air temperature of a the thermal zone, whereas the second
# represents a virtual weather station. Both devices publish there values to
# the platform via MQTT. Use the simulation model of
# e1_virtual_weatherstation.py
#
# The input sections are marked with 'ToDo'
#
# #### Steps to complete:
# 1. Set up the missing parameters in the parameter section
# 2. Create a service group and two devices
# 3. Provision the service group and the devices
# 4. Create an MQTT client using the filip.client.mqtt package and register
#    your service group and your devices
# 5. Check if the IoT-Agent correctly creates the corresponding entities
# 5. Create a function that publishes the simulated temperature via MQTT,
#    retrieves the entity data after each message and writes the values to a
#    history
# 6. Run the simulation and plot the results

# ## Import packages
import json
import paho.mqtt.client as mqtt
from pathlib import Path
from pydantic import parse_file_as
import matplotlib.pyplot as plt
import time
from typing import List
from urllib.parse import urlparse
# import from filip
from filip.clients.ngsi_v2 import ContextBrokerClient, IoTAClient
from filip.clients.mqtt import IoTAMQTTClient
from filip.models.base import FiwareHeader
from filip.models.ngsi_v2.context import ContextEntity
from filip.models.ngsi_v2.iot import Device, DeviceAttribute, ServiceGroup
from filip.utils.cleanup import clear_context_broker, clear_iot_agent
# import simulation model
from tutorial.simulation_model import SimulationModel

# ## Parameters
# ToDo: Enter your context broker host and port, e.g http://localhost:1026
CB_URL = "http://localhost:1026"
# ToDo: Enter your IoT-Agent host and port, e.g mqtt://localhost:4041
IOTA_URL = "http://localhost:4041"
# ToDo: Enter your mqtt broker url, e.g mqtt://test.mosquitto.org:1883
MQTT_BROKER_URL = "mqtt://localhost:1883"
# FIWARE-Service
SERVICE = 'filip_tutorial'
# FIWARE-Servicepath
# ToDo: Change the name of your service-path to something unique. If you run
#  on a shared instance this very important in order to avoid user
#  collisions. You will use this service path through the whole tutorial.
#  If you forget to change it an error will be raised!
SERVICE_PATH = '/your_path'
APIKEY = SERVICE_PATH.strip('/')

# Path to json-files to store entity data for follow up exercises
write_groups_filepath = Path("./e4_iot_thermal_zone_sensors_groups.json")
write_devices_filepath = Path("./e4_iot_thermal_zone_sensors_devices.json")

# set parameters for the temperature simulation
temperature_max = 10  # maximal ambient temperature
temperature_min = -5  # minimal ambient temperature
temperature_zone_start = 20  # start value of the zone temperature

t_sim_start = 0  # simulation start time in seconds
t_sim_end = 24 * 60 * 60  # simulation end time in seconds
com_step = 60 * 60 * 0.25  # 15 min communication step in seconds

# ## Main script
if __name__ == '__main__':
    # create a fiware header object
    fiware_header = FiwareHeader(service=SERVICE,
                                 service_path=SERVICE_PATH)
    # clear the state of your service and scope
    clear_context_broker(url=CB_URL, fiware_header=fiware_header)
    clear_iot_agent(url=IOTA_URL, fiware_header=fiware_header)

    # instantiate simulation model
    sim_model = SimulationModel(t_start=t_sim_start,
                                t_end=t_sim_end,
                                temp_max=temperature_max,
                                temp_min=temperature_min,
                                temp_start=temperature_zone_start)

    # define lists to store historical data
    history_weather_station = []
    history_zone_temperature_sensor = []

    # Create a service group and add it to your
    service_group = ServiceGroup(apikey=APIKEY,
                                 resource="/iot/json")

    # ToDo: create two IoTA-MQTT devices for the weather station and the zone
    #  temperature sensor. Also add the simulation time as `active attribute`
    #  to each device!
    #
    # create the weather station device
    # create the simtime attribute and add during device creation
    t_sim = DeviceAttribute(name='simtime',
                            object_id='t_sim',
                            type="Number")

    weather_station = Device(device_id='device:001',
                             entity_name='urn:ngsi-ld:WeatherStation:001',
                             entity_type='WeatherStation',
                             protocol='IoTA-JSON',
                             transport='MQTT',
                             apikey=APIKEY,
                             attributes=[t_sim],
                             commands=[])

    # create a temperature attribute and add it via the api of the
    # `device`-model. Use the 't_amb' as `object_id`. `object_id` specifies
    # what key will be used in the MQTT Message payload
    t_amb = DeviceAttribute(name='temperature',
                            object_id='t_amb',
                            type="Number")

    weather_station.add_attribute(t_amb)

    # ToDo: create the zone temperature device add the t_sim attribute upon
    #  creation
    zone_temperature_sensor = Device(device_id='device:002',
                                     entity_name='urn:ngsi-ld:TemperatureSensor:001',
                                     entity_type='TemperatureSensor',
                                     protocol='IoTA-JSON',
                                     transport='MQTT',
                                     apikey=APIKEY,
                                     attributes=[t_sim],
                                     commands=[])
    # ToDo: Create the temperature attribute. Use the 't_zone' as `object_id`.
    #  `object_id` specifies what key will be used in the MQTT Message payload
    t_zone = DeviceAttribute(name='temperature',
                             object_id='t_zone',
                             type="Number")
    zone_temperature_sensor.add_attribute(t_zone)

    # ToDo: Create an IoTAClient
    iotac = IoTAClient(url=IOTA_URL, fiware_header=fiware_header)
    # ToDo: Provision service group and add it to your IoTAMQTTClient
    iotac.post_group(service_group=service_group, update=True)
    # ToDo: Provision the devices at the IoTA-Agent
    # provision the WeatherStation device
    iotac.post_device(device=weather_station, update=True)
    # ToDo: provision the zone temperature device
    iotac.post_device(device=zone_temperature_sensor, update=True)

    # ToDo: Check in the context broker if the entities corresponding to your
    #  devices where correctly created
    # ToDo: Create a context broker client
    cbc = ContextBrokerClient(url=CB_URL, fiware_header=fiware_header)
    # Get WeatherStation entity
    print(cbc.get_entity(weather_station.entity_name).json(indent=2))
    # Get ZoneTemperatureSensor entity
    print(cbc.get_entity(zone_temperature_sensor.entity_name).json(indent=2))

    # ToDo: create an MQTTv5 client using filip.clients.mqtt.IoTAMQTTClient
    mqttc = IoTAMQTTClient(protocol=mqtt.MQTTv5)
    mqttc.add_service_group(service_group=service_group)
    # ToDo: Register devices with your MQTT-Client
    # register the weather station
    mqttc.add_device(weather_station)
    # ToDo: register the zone temperature sensor
    mqttc.add_device(zone_temperature_sensor)

    # The IoTAMQTTClient automatically creates the outgoing topics from the
    # device configuration during runtime. Hence, we need to construct them
    # manually in order to subscribe to them. This is usually  not required as
    # only the platform should listen to incoming traffic.
    # if you want to listen subscribe to the following topics:
    # "/json/<APIKEY>/<weather_station.device_id>/attrs"
    # "/json/<APIKEY>/<zone_temperature_sensor.device_id>/attrs"

    # ToDO: connect to the mqtt broker and subscribe to your topic
    mqtt_url = urlparse(MQTT_BROKER_URL)
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

    # create a non-blocking thread for mqtt communication
    mqttc.loop_start()

    # ToDo: Create a loop that publishes every second a message to the broker
    #  that holds the simulation time "simtime" and the corresponding
    #  temperature "temperature" the loop should. You may use the `object_id`
    #  or the attribute name as key in your payload.
    for t_sim in range(sim_model.t_start,
                       sim_model.t_end + int(com_step),
                       int(com_step)):
        # publish the simulated ambient temperature
        mqttc.publish(device_id=weather_station.device_id,
                      payload={"temperature": sim_model.t_amb,
                               "simtime": sim_model.t_sim})

        # ToDo: publish the simulated zone temperature
        mqttc.publish(device_id=zone_temperature_sensor.device_id,
                      payload={"temperature": sim_model.t_zone,
                               "simtime": sim_model.t_sim})
        # simulation step for next loop
        sim_model.do_step(int(t_sim + com_step))
        # wait for one second before publishing the next values
        time.sleep(1)

        # Get corresponding entities and write values to history
        weather_station_entity = cbc.get_entity(weather_station.entity_name)
        history_weather_station.append(
            {"simtime": weather_station_entity.simtime.value,
             "temperature": weather_station_entity.temperature.value})

        # ToDo: Get ZoneTemperatureSensor and write values to history
        zone_temperature_sensor_entity = cbc.get_entity(
            zone_temperature_sensor.entity_name)
        history_zone_temperature_sensor.append(
            {"simtime": zone_temperature_sensor_entity.simtime.value,
             "temperature": zone_temperature_sensor_entity.temperature.value})

    # close the mqtt listening thread
    mqttc.loop_stop()
    # disconnect the mqtt device
    mqttc.disconnect()

    # plot results
    fig, ax = plt.subplots()
    t_simulation = [item["simtime"] for item in history_weather_station]
    temperature = [item["temperature"] for item in history_weather_station]
    ax.plot(t_simulation, temperature)
    ax.set_xlabel('time in s')
    ax.set_ylabel('ambient temperature in °C')

    fig2, ax2 = plt.subplots()
    t_simulation = [item["simtime"] for item in history_zone_temperature_sensor]
    temperature = [item["temperature"] for item in
                   history_zone_temperature_sensor]
    ax2.plot(t_simulation, temperature)
    ax2.set_xlabel('time in s')
    ax2.set_ylabel('zone temperature in °C')

    plt.show()
