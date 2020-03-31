from filip import iot, config, orion
import json
import os
from pathlib import Path

# ToDo: Rewrite Example, so it matches the orion Example
# ToDo: Change Data Model

def iota_ul(config:config.Config):
    # Creating an Instance of the Context Broker

    print("uno")
    ORION_CB = orion.Orion(CONFIG)


    # Creating an Instance of the IoT-Agent in the UL-Version
    IOTA_UL = iot.Agent("iota", CONFIG)




    # set the service path
    fiware_service = orion.FiwareService("test_service2", "/iot_ul")
    ORION_CB.set_service(fiware_service)
    res=fiware_service.get_header()


    device_group = iot.DeviceGroup(fiware_service,
                                    "http://orion:1026",
                                    iot_agent="iota_ul",
                                    apikey="12345test",
                                   autoprovision=True)

    print(device_group)


    device_group.test_apikey()


    device_ul = iot.Device('urn:Room:002:sensor01','urn:Room:002',
                           "Thing",
                           transport="MQTT", protocol="PDI-IoTA-UltraLight",
                           timezone="Europe/Berlin")

    print(device_ul)

    temp_attr = {"name": "temperature",
            "value_type": "Number",
            "attr_type": "active",
            "attr_value": "12",
            "object_id": "t"}



    device_ul.add_attribute_json(temp_attr)

    press_attr = {"name": "pressure",
            "value_type": "Number",
            "attr_type": "active",
            "object_id": "p"}

    device_ul.add_attribute_json(press_attr)


    name_attr =  {"name": "nice_name",
                   "value_type": "String",
                   "attr_type": "static",
                   "attr_value" : "beautiful attribute!",
                   "object_id": "name"}

    device_ul.add_attribute_json(name_attr)

    # test creating an internal attribute

    internal_attr = {"name": "nice_name_int",
                   "value_type": "String",
                   "attr_type": "internal",
                   "attr_value" : "beautiful attribute!",
                   "object_id": "name"}

    device_ul.add_attribute_json(internal_attr)



    device_ul.delete_attribute("pressure", "active")

    IOTA_UL.post_group(device_group)
    IOTA_UL.update_group(device_group)
    IOTA_UL.get_groups(device_group)
    IOTA_UL.post_device(device_group, device_ul)
    IOTA_UL.update_device(device_group, device_ul, "")
    IOTA_UL.get_device(device_group, device_ul)

    ORION_CB.get_all_entities()
    ORION_CB.get_entity('urn:Room:002')



    IOTA_UL.delete_device(device_group, device_ul)
    IOTA_UL.delete_group(device_group)



def iota_json(config:config.Config):

    # Creating an Instance of the Context Broker

    ORION_CB = orion.Orion(CONFIG)


    # Creating an Instance of the IoT-Agent in the JSON-Version
    IOTA_JSON = iot.Agent("iota", CONFIG)




    # set the service path
    fiware_service = orion.FiwareService("test_service2", "/iot_ul")
    ORION_CB.set_service(fiware_service)
    res=fiware_service.get_header()



    device_group_json = iot.DeviceGroup(fiware_service,
                                         "http://orion:1026",
                                         iot_agent="iota_json", apikey="12345",
                                        timestamp=True, autoprovision=False)




    device_json = iot.Device('urn:Room:002:sensor02','urn:Room:002',
                             "Thing", transport="MQTT",
                             protocol="IoTA-JSON",
                             timezone="Europe/Berlin",
                             timestamp=True,
                             autoprovision=False)

    print(device_json)

    IOTA_JSON.post_group(device_group_json)
    IOTA_JSON.get_groups(device_group_json)
    IOTA_JSON.post_device(device_group_json, device_json)
    IOTA_JSON.update_device(device_group_json, device_json, "")
    IOTA_JSON.get_device(device_group_json, device_json)

    IOTA_JSON.delete_device(device_group_json, device_json)
    IOTA_JSON.delete_group(device_group_json)



if __name__ == "__main__":
    # setup logging
    # before the first initalization the log_config.yaml.example file needs to be modified



    path_to_config = os.path.join(str(Path().resolve().parent), "config.json")
    config.setup_logging()
    # Read and check configuration
    CONFIG = config.Config(path_to_config)

    with open(path_to_config) as f:
        data = json.loads(f.read())


    if data["iota"]["protocol"] == "IoTA-UL":
        print("Ultralight Agent")
        iota_ul(CONFIG)

    elif data["iota"]["protocol"] == "IoTA-JSON":
        print("JSON Agent")
        iota_json(CONFIG)

    else:
        print(f'{data["iota"]["protocol"]} - is not a supported protocol.')


    '''
    # Creating an Instance of the Context Broker

    ORION_CB = orion.Orion(CONFIG)


    # Creating an Instance of the IoT-Agent in the UL-Version
    IOTA_UL = iot.Agent("iota", CONFIG)
    
    IOTA_UL.test_connection(CONFIG)


    # Creating an Instance of the IoT-Agent in the JSON-Version
    IOTA_JSON = iot.Agent("iota", CONFIG)


    # set the service path
    fiware_service = orion.FiwareService("test_service2", "/iot_ul")
    ORION_CB.set_service(fiware_service)
    res=fiware_service.get_header()

    device_group_json = iot.DeviceGroup(fiware_service,
                                         "http://orion:1026",
                                         iot_agent="iota_json", apikey="12345",
                                        timestamp=True, autoprovision=False)

    device_group = iot.DeviceGroup(fiware_service,
                                    "http://orion:1026",
                                    iot_agent="iota_ul",
                                    apikey="12345test",
                                   autoprovision=True)

    print(device_group)


    device_group.test_apikey()

    device_ul = iot.Device('urn:Room:002:sensor01','urn:Room:002',
                           "Thing",
                           transport="MQTT", protocol="PDI-IoTA-UltraLight",
                           timezone="Europe/Berlin")

    print(device_ul)

    """

    device_ul.add_attribute("temperature", attr_type="active",
                            value_type="Number", object_id="t")
                            
                            
    device_ul.add_attribute("pressure", attr_type="active",
                            value_type="Number", object_id="p")


    device_ul.add_attribute("nice_name", attr_type="static",
                            value_type="String", object_id="name",
                            attr_value="beautiful attribute!")

    
    """
    temp_attr = {"name": "temperature",
            "value_type": "Number",
            "attr_type": "active",
            "attr_value": "12",
            "object_id": "t"}



    device_ul.add_attribute_json(temp_attr)

    press_attr = {"name": "pressure",
            "value_type": "Number",
            "attr_type": "active",
            "object_id": "p"}

    device_ul.add_attribute_json(press_attr)


    name_attr =  {"name": "nice_name",
                   "value_type": "String",
                   "attr_type": "static",
                   "attr_value" : "beautiful attribute!",
                   "object_id": "name"}

    device_ul.add_attribute_json(name_attr)

    # test creating an internal attribute

    internal_attr = {"name": "nice_name_int",
                   "value_type": "String",
                   "attr_type": "internal",
                   "attr_value" : "beautiful attribute!",
                   "object_id": "name"}

    device_ul.add_attribute_json(internal_attr)



    device_ul.delete_attribute("pressure", "active")


    device_json = iot.Device('urn:Room:002:sensor02','urn:Room:002',
                             "Thing", transport="MQTT",
                             protocol="IoTA-JSON",
                             timezone="Europe/Berlin",
                             timestamp=True,
                             autoprovision=False)

    print(device_json)

    IOTA_JSON.post_group(device_group_json)
    IOTA_JSON.get_groups(device_group_json)
    IOTA_JSON.post_device(device_group_json, device_json)
    IOTA_JSON.update_device(device_group_json, device_json, "")
    IOTA_JSON.get_device(device_group_json, device_json)

    IOTA_UL.post_group(device_group)
    IOTA_UL.update_group(device_group)
    IOTA_UL.get_groups(device_group)
    IOTA_UL.post_device(device_group, device_ul)
    IOTA_UL.update_device(device_group, device_ul, "")
    IOTA_UL.get_device(device_group, device_ul)

    ORION_CB.get_all_entities()
    ORION_CB.get_entity('urn:Room:002')



    

    IOTA_UL.delete_device(device_group, device_ul)
    IOTA_UL.delete_group(device_group)
    

    '''
