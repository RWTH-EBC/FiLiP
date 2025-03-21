"""
# # Exercise 7: Semantic IoT Systems
#
# We now want to add a semantic meaning to our measurements. Therefore we
# semantically connect the context entities that we created in
# `e3_context_entities.py`

# The input sections are marked with 'ToDo'

# #### Steps to complete:
# 1. Set up the missing parameters in the parameter section
# 2. Add relationships that connect the weather station to the building,
#    and vice versa
# 3. Add relationships that connect the thermal zone temperature sensor and
#    the heater to the building, and vice versa
# 4. Retrieve all entities and print them
# 5. Congratulations! You are now ready to build your own semantic systems. For
#    advanced semantic functions check on our semantics examples
"""

# ## Import packages
import json
from pathlib import Path
from typing import List
from pydantic import TypeAdapter

# import from filip
from filip.clients.ngsi_v2 import ContextBrokerClient, IoTAClient
from filip.models.base import FiwareHeader
from filip.models.ngsi_v2.base import NamedMetadata
from filip.models.ngsi_v2.context import ContextEntity, NamedContextAttribute
from filip.models.ngsi_v2.iot import Device, ServiceGroup, StaticDeviceAttribute
from filip.models.ngsi_v2.units import Unit
from filip.utils.cleanup import clear_context_broker, clear_iot_agent

# ## Parameters
# ToDo: Enter your context broker host and port, e.g. http://localhost:1026.
CB_URL = "http://localhost:1026"
# ToDo: Enter your IoT-Agent host and port, e.g. http://localhost:4041.
IOTA_URL = "http://localhost:4041"

# ToDo: Change the name of your service to something unique. If you run
#  on a shared instance this very is important in order to avoid user
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

# path to read json-files from previous exercises
READ_GROUPS_FILEPATH = Path("../e5_iot_thermal_zone_control_solution_groups.json")
READ_DEVICES_FILEPATH = Path("../e5_iot_thermal_zone_control_solution_devices.json")
READ_ENTITIES_FILEPATH = Path("../e3_context_entities_solution_entities.json")

# opening the files
with open(READ_GROUPS_FILEPATH, "r") as groups_file, open(
    READ_DEVICES_FILEPATH, "r"
) as devices_file, open(READ_ENTITIES_FILEPATH, "r") as entities_file:
    json_groups = json.load(groups_file)
    json_devices = json.load(devices_file)
    json_entities = json.load(entities_file)

# ## Main script
if __name__ == "__main__":
    # create a fiware header object
    fiware_header = FiwareHeader(service=SERVICE, service_path=SERVICE_PATH)
    # clear the state of your service and scope
    clear_iot_agent(url=IOTA_URL, fiware_header=fiware_header)
    clear_context_broker(url=CB_URL, fiware_header=fiware_header)

    # create clients and restore devices and groups from file
    groups = TypeAdapter(List[ServiceGroup]).validate_python(json_groups)
    devices = TypeAdapter(List[Device]).validate_python(json_devices)
    entities = TypeAdapter(List[ContextEntity]).validate_python(json_entities)
    cbc = ContextBrokerClient(url=CB_URL, fiware_header=fiware_header)
    for entity in entities:
        cbc.post_entity(entity=entity)

    iotac = IoTAClient(url=IOTA_URL, fiware_header=fiware_header)
    iotac.post_groups(service_groups=groups)
    iotac.post_devices(devices=devices)

    # ToDo: Retrieve all iot resources from the IoT-Agent.
    # get the group and device configurations from the server
    group = iotac.get_group(resource="/iot/json", apikey=APIKEY)
    weather_station = iotac.get_device(device_id="device:001")
    zone_temperature_sensor = iotac.get_device(device_id="device:002")
    heater = iotac.get_device(device_id="device:003")

    # ToDo: Get context entities from the Context Broker
    #  (exclude the IoT device ones).
    building = cbc.get_entity(
        entity_id="urn:ngsi-ld:building:001", entity_type="Building"
    )
    thermal_zone = cbc.get_entity(
        entity_id="ThermalZone:001", entity_type="ThermalZone"
    )

    # ToDo: Semantically connect the weather station and the building. By
    #  adding a `hasWeatherStation` attribute of type `Relationship`. For the
    #  connection from the weather station to the building add a static
    #  attribute to the weather station.

    # create the context attribute for the building and add it to the
    # building entity
    has_weather_station = NamedContextAttribute(
        name="hasWeatherStation", type="Relationship", value=weather_station.entity_name
    )
    building.add_attributes(attrs=[has_weather_station])

    # create a static attribute that connects the weather station to the
    # building
    cbc.update_entity(entity=building)

    ref_building = StaticDeviceAttribute(
        name="refBuilding", type="Relationship", value=building.id
    )
    weather_station.add_attribute(ref_building)
    iotac.update_device(device=weather_station)

    # ToDo: Semantically connect the zone temperature sensor and the thermal
    #  zone by adding a `hasTemperatureSensor` attribute of type
    #  `Relationship` to the thermal zone entity.
    #  For the connection from the sensor to the zone add a static
    #  attribute to the temperature sensor device.

    # ToDo: Create a context attribute for the thermal zone and add it to the
    #   thermal zone entity.
    has_sensor = NamedContextAttribute(
        name="hasTemperatureSensor",
        type="Relationship",
        value=zone_temperature_sensor.entity_name,
    )
    thermal_zone.add_attributes(attrs=[has_sensor])

    # ToDo: Create a static attribute that connects the zone temperature zone to
    #  the thermal zone.
    cbc.update_entity(entity=thermal_zone)

    ref_thermal_zone = StaticDeviceAttribute(
        name="refThermalZone", type="Relationship", value=thermal_zone.id
    )
    zone_temperature_sensor.add_attribute(ref_thermal_zone)
    iotac.update_device(device=zone_temperature_sensor)

    # ToDo: Semantically connect the zone temperature sensor and the thermal
    #  zone by adding a `hasTemperatureSensor` attribute of type
    #  `Relationship` to the thermal zone entity.
    #  For the connection from the sensor to the zone add a static
    #  attribute to the temperature sensor device.

    # ToDo: Create a context attribute for the thermal zone and add it to the
    #   thermal zone entity.
    has_heater = NamedContextAttribute(
        name="hasHeater", type="Relationship", value=heater.entity_name
    )
    thermal_zone.add_attributes(attrs=[has_heater])

    # ToDo: Create a static attribute that connects the zone temperature zone to
    #  the thermal zone.
    cbc.update_entity(entity=thermal_zone)

    ref_thermal_zone = StaticDeviceAttribute(
        name="refThermalZone", type="Relationship", value=thermal_zone.id
    )
    heater.add_attribute(ref_thermal_zone)
    iotac.update_device(device=heater)

    # ToDo: Add unit metadata to the temperature and sim_time attributes of
    #  all devices. Here we use unit code information. If you can not find
    #  your unit code, you can use our unit models for help.
    # get code from Unit model for seconds
    code = Unit(name="second [unit of time]").code
    # add metadata to sim_time attribute of the all devices
    metadata_sim_time = NamedMetadata(name="unitCode", type="Text", value=code)
    attr_sim_time = weather_station.get_attribute(attribute_name="sim_time")
    attr_sim_time.metadata = metadata_sim_time
    weather_station.update_attribute(attribute=attr_sim_time)
    zone_temperature_sensor.update_attribute(attribute=attr_sim_time)
    heater.update_attribute(attribute=attr_sim_time)

    # ToDo: Get code from Unit model for degree celsius.
    code = Unit(name="degree Celsius").code
    # ToDo: Add metadata to temperature attribute of the weather
    #  station and the zone temperature sensor.
    metadata_t_amb = NamedMetadata(name="unitCode", type="Text", value=code)
    attr_t_amb = weather_station.get_attribute(attribute_name="temperature")
    attr_t_amb.metadata = metadata_t_amb
    weather_station.update_attribute(attribute=attr_t_amb)

    metadata_t_zone = NamedMetadata(name="unitCode", type="Text", value=code)
    attr_t_zone = zone_temperature_sensor.get_attribute(attribute_name="temperature")
    attr_t_zone.metadata = metadata_t_zone
    zone_temperature_sensor.update_attribute(attribute=attr_t_zone)

    # Currently adding metadata via updating does not work perfectly,
    # therefore, we delete and update them.
    iotac.delete_device(device_id=weather_station.device_id)
    iotac.post_device(device=weather_station)
    iotac.delete_device(device_id=zone_temperature_sensor.device_id)
    iotac.post_device(device=zone_temperature_sensor)
    iotac.delete_device(device_id=heater.device_id)
    iotac.post_device(device=heater)

    # ToDo: Retrieve all Context Entities and print them.
    entities = cbc.get_entity_list()
    for entity in entities:
        print(entity.model_dump_json(indent=2))

    clear_iot_agent(url=IOTA_URL, fiware_header=fiware_header)
    clear_context_broker(url=CB_URL, fiware_header=fiware_header)
