from filip import config, orion
from filip.iota.agent import Agent
from filip.iota.device_group import DeviceGroup
from filip.iota.device import Device
import os
from pathlib import Path

# ToDo: Rewrite Example, so it matches the orion Example
# ToDo: Change Data Model

def iota(config:config.Config):
    # Creating an Instance of the Context Broker
    ocb = orion.Orion(config)

    # Creating an Instance of the IoT-Agent in the UL-Version
    agent = Agent(config)

    # set the service path
    fiware_service = orion.FiwareService("filip",
                                         "/iot_example")
    ocb.set_service(fiware_service)

    res = fiware_service.get_header()

    device_group = DeviceGroup(fiware_service,
                               "http://orion:1026",
                               apikey="12345test",
                               autoprovision=True,
                               resource=)

    print(device_group)

    device_group.test_apikey()

    if config.data["iota"]["protocol"] == "IoTA-UL":
        device_group = DeviceGroup(fiware_service,
                                   "http://orion:1026",
                                   apikey="12345test",
                                   autoprovision=True,
                                   resource="iot/d")
        print(device_group)

        device_group.test_apikey()

        print("Device initialization for IoTA-UL Agent")
        device = Device(device_id='urn:Room:002:sensor01',
                        entity_name='urn:Room:002',
                        entity_type="Thing",
                        transport="MQTT",
                        protocol="PDI-IoTA-UltraLight",
                        timezone="Europe/Berlin",
                        service=fiware_service.name,
                        service_path=fiware_service.path,
                        resource="iot/d"
                        )
    elif config.data["iota"]["protocol"] == "IoTA-JSON":
        device_group = DeviceGroup(fiware_service,
                                   "http://orion:1026",
                                   apikey="12345test",
                                   autoprovision=True,
                                   resource="iot/json")
        print(device_group)

        device_group.test_apikey()


        print("Device initialization for IoTA-JSON Agent")
        device = Device(device_id='urn:Room:002:sensor02',
                        entity_name='urn:Room:002',
                        entity_type="Thing",
                        transport="MQTT",
                        protocol="IoTA-JSON",
                        timezone="Europe/Berlin",
                        timestamp=True,
                        autoprovision=False,
                        service=fiware_service.name,
                        service_path=fiware_service.path,
                        resource = "iot/json"
                        )
    else:
        print(f'{conf["iota"]["protocol"]} - is not a supported protocol.')

    print(device)

    press_attr = {"name": "pressure",
                  "type": "Number",
                  "attr_type": "active",
                  "object_id": "p"}

    device.add_attribute(press_attr)

    # creating attribute using dict/json with prohibited value
    temp_attr = {"name": "temperature",
                 "type": "Number",
                 "attr_type": "active",
                 "value": "12",
                 "object_id": "t"}

    device.add_attribute(temp_attr)

    # creating attribute using dict/json but include attr_type as variable
    name_attr = {"name": "nice_name",
                 "type": "String",
                 "value" : "beautiful attribute!",}

    device.add_attribute(name_attr, attr_type="static")

    # creating attribute using dict/json with missing attr_type
    name_attr = {"name": "very_nice_name",
                 "type": "String",
                 "value" : "beautiful attribute!",
                 "object_id": "name"}

    device.add_attribute(name_attr)

    # creating attribute using variables
    device.add_attribute(name="Tiger",
                         attr_type="static",
                         type="Number",
                         value=12)

    # creating command
    device.add_attribute(name = "OpenCages",
                         type = "String",
                         attr_type = "command",
                         value = "Yes",
                         object_id= "cage")

    # test creating an internal attribute
    internal_attr = {"name": "nice_name_int",
                     "type": "String",
                     "attr_type": "internal",
                     "value" : "beautiful attribute!",
                     "object_id": "name"}

    device.add_attribute(internal_attr)

    print(device)

    device.delete_attribute("pressure", "active")

    agent.post_group(device_group)
    agent.update_group(device_group)
    agent.get_groups(device_group)
    agent.post_device(device_group, device)
    agent.update_device(device_group, device, {})

    print(agent.get_device(device_group, device))
    print(ocb.get_all_entities())
    print(ocb.get_entity('urn:Room:002'))

    agent.delete_device(device_group, device)
    agent.delete_group(device_group)


if __name__ == "__main__":
    # setup logging
    # before the first initalization the log_config.yaml.example file needs to be modified

    path_to_config = os.path.join(str(Path().resolve().parent), "config.json")
    config.setup_logging()

    # Read and check configuration
    conf = config.Config(path_to_config)

    iota(conf)






