"""
# # Exercise 7: Semantic IoT Systems
#
# We now want to add a semantic meaning to our measurements. Therefore we
# semantically connect to the context entities that we created in
# `e3_context_entities.py`

# The input sections are marked with 'ToDo'

# #### Steps to complete:
# 1. Set up the missing parameters in the parameter section
# 2. Add relationships that connect the weather station to the building,
#    and vice versa
# 3. Add relationships that connect the thermal zone temperature sensor and
#    the heater to the building, and vice versa
# 4. Retrieve all entities and print them
# 5. Congratulations you are now ready to build your own semantic systems for
#    advanced semantic functions check on our semantics examples
"""

# ## Import packages
from pathlib import Path
from typing import List
from pydantic import parse_file_as

# import from filip
from filip.clients.ngsi_v2 import \
    ContextBrokerClient, \
    IoTAClient
from filip.models.base import FiwareHeader
from filip.models.ngsi_v2.context import \
    ContextEntity, \
    NamedContextAttribute
from filip.models.ngsi_v2.iot import \
    Device, \
    ServiceGroup, \
    StaticDeviceAttribute
from filip.utils.cleanup import \
    clear_context_broker, \
    clear_iot_agent

# ## Parameters
# ToDo: Enter your context broker host and port, e.g http://localhost:1026
CB_URL = "http://localhost:1026"
# ToDo: Enter your IoT-Agent host and port, e.g http://localhost:4041
IOTA_URL = "http://localhost:4041"

# FIWARE-Service
SERVICE = 'filip_tutorial'
# FIWARE-Servicepath
# ToDo: Change the name of your service-path to something unique. If you run
#  on a shared instance this very important in order to avoid user
#  collisions. You will use this service path through the whole tutorial.
#  If you forget to change it an error will be raised!
SERVICE_PATH = '/your_path'
APIKEY = SERVICE_PATH.strip('/')

# Path to read json-files from previous exercises
READ_GROUPS_FILEPATH = \
    Path("e5_iot_thermal_zone_control_solution_groups.json")
READ_DEVICES_FILEPATH = \
    Path("e5_iot_thermal_zone_control_solution_devices.json")
READ_ENTITIES_FILEPATH = \
    Path("e3_context_entities_solution_entities.json")

# ## Main script
if __name__ == '__main__':
    # create a fiware header object
    fiware_header = FiwareHeader(service=SERVICE,
                                 service_path=SERVICE_PATH)
    # clear the state of your service and scope
    clear_iot_agent(url=IOTA_URL, fiware_header=fiware_header)
    clear_context_broker(url=CB_URL, fiware_header=fiware_header)

    # Create clients and restore devices and groups from file
    groups = parse_file_as(List[ServiceGroup], READ_GROUPS_FILEPATH)
    devices = parse_file_as(List[Device], READ_DEVICES_FILEPATH)
    entities = parse_file_as(List[ContextEntity], READ_ENTITIES_FILEPATH)
    cbc = ContextBrokerClient(url=CB_URL, fiware_header=fiware_header)
    for entity in entities:
        cbc.post_entity(entity=entity)

    iotac = IoTAClient(url=IOTA_URL, fiware_header=fiware_header)
    iotac.post_groups(service_groups=groups)
    iotac.post_devices(devices=devices)

    # ToDo: Retrieve all iot resources from the IoT-Agent
    # Get the group and device configurations from the server
    group = iotac.get_group(resource="/iot/json", apikey=APIKEY)
    weather_station = iotac.get_device(device_id="device:001")
    zone_temperature_sensor = iotac.get_device(device_id="device:002")
    heater = iotac.get_device(device_id="device:003")

    # ToDo: Get context entities from the Context Broker
    #  (exclude the IoT device ones)
    building = cbc.get_entity(entity_id="urn:ngsi-ld:building:001",
                              entity_type="Building")
    thermal_zone = cbc.get_entity(entity_id="ThermalZone:001",
                                  entity_type="ThermalZone")

    # ToDo: Semantically connect the weather station and the building. By
    #  adding a `hasWeatherStation` attribute of type `Relationship`. For the
    #  connection from the weather station to the building add a static
    #  attribute to the weather station

    # create the context attribute for the building and add it to the
    # building entity
    has_weather_station = NamedContextAttribute(
        name="hasWeatherStation",
        type="Relationship",
        value=weather_station.entity_name)
    building.add_attributes(attrs=[has_weather_station])

    # create a static attribute that connects the weather station to the
    # building
    cbc.update_entity(entity=building)

    ref_building = StaticDeviceAttribute(name="refBuilding",
                                         type="Relationship",
                                         value=building.id)
    weather_station.add_attribute(ref_building)
    iotac.update_device(device=weather_station)

    # ToDo: Semantically connect the zone temperature sensor and the thermal
    #  zone by adding a `hasTemperatureSensor` attribute of type
    #  `Relationship` to the thermal zone entity.
    #  For the connection from the sensor to the zone add a static
    #  attribute to the temperature sensor device

    # ToDo: create the context attribute for the thermal zone and add it to the
    #   thermal zone entity
    has_sensor = NamedContextAttribute(
        name="hasTemperatureSensor",
        type="Relationship",
        value=zone_temperature_sensor.entity_name)
    thermal_zone.add_attributes(attrs=[has_sensor])

    # ToDo: create a static attribute that connects the zone temperature zone to
    #  the thermal zone
    cbc.update_entity(entity=thermal_zone)

    ref_thermal_zone = StaticDeviceAttribute(name="refThermalZone",
                                             type="Relationship",
                                             value=thermal_zone.id)
    zone_temperature_sensor.add_attribute(ref_thermal_zone)
    iotac.update_device(device=zone_temperature_sensor)

    # ToDo: Semantically connect the zone temperature sensor and the thermal
    #  zone by adding a `hasTemperatureSensor` attribute of type
    #  `Relationship` to the thermal zone entity.
    #  For the connection from the sensor to the zone add a static
    #  attribute to the temperature sensor device

    # ToDo: create the context attribute for the thermal zone and add it to the
    #   thermal zone entity
    has_heater = NamedContextAttribute(
        name="hasHeater",
        type="Relationship",
        value=heater.entity_name)
    thermal_zone.add_attributes(attrs=[has_heater])

    # ToDo: create a static attribute that connects the zone temperature zone to
    #  the thermal zone
    cbc.update_entity(entity=thermal_zone)

    ref_thermal_zone = StaticDeviceAttribute(name="refThermalZone",
                                             type="Relationship",
                                             value=thermal_zone.id)
    heater.add_attribute(ref_thermal_zone)
    iotac.update_device(device=heater)

    # ToDo: Retrieve all ContextEntites and print them
    entities = cbc.get_entity_list()
    for entity in entities:
        print(entity.json(indent=2))

    clear_iot_agent(url=IOTA_URL, fiware_header=fiware_header)
    clear_context_broker(url=CB_URL, fiware_header=fiware_header)
