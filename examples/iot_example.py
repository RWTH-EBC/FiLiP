from filip import iot, orion, config


def read_config(path_to_config:str="/Users/Felix/restructuring/config.json"):
    """
    Function creates an instance of  the CONFIG so it can be passed to different Classes
    :param path_to_config: path to a config, describing the ports
    :return: Instance of the config
    """
    # Reading the config

    CONFIG = config.Config(path_to_config)

    return CONFIG


def create_cb(path_to_config:str="/Users/Felix/restructuring/config.json"):
    """
    Function creates an instance of the context broker
    :param path_to_config: path to a config, describing the ports
    :return: Instance of the Context Broker
    """
    # Reading the config
    CONFIG = config.Config(path_to_config)


    # creating an instance of the ORION context broker
    ORION_CB = orion.Orion(CONFIG)



    return ORION_CB





def create_device(transport:str = "MQTT",
                  protocol:str="PDI-IoTA-UltraLight",
                  timezone:str = "Europe/Berlin"):

    device = iot.Device(device_id='urn:Room:002:sensor01',
                        entity_name='urn:Room:002', entity_type="Thing",
                        transport=transport, protocol=protocol,
                        timezone=timezone)

    temp_attr = {"name": "temperature",
            "value_type": "Number",
            "attr_type": "active",
            "attr_value": "12",
            "object_id": "t"}


    device.add_attribute_json(temp_attr)

    press_attr = {"name": "pressure",
            "value_type": "Number",
            "attr_type": "active",
            "object_id": "p"}

    device.add_attribute_json(press_attr)


    name_attr =  {"name": "nice_name",
                   "value_type": "String",
                   "attr_type": "static",
                   "attr_value" : "beautiful attribute!",
                   "object_id": "name"}

    device.add_attribute_json(name_attr)

    return device

def create_device_group(fiware_service:object, cb_host:str,
                        devices:list, apikey="12345"):
    """

    :param fiware_service:
    :param cb_host:
    :param devices:
    :return:
    """

    device_group = iot.DeviceGroup(fiware_service=fiware_service, cb_host=cb_host, devices=devices)

    return device_group


def create_second_device(transport:str = "MQTT",
                  protocol:str="PDI-IoTA-UltraLight",
                  timezone:str = "Europe/Berlin"):

    device = iot.Device(device_id='urn:Room:002:sensor02',
                        entity_name='urn:Room:002', entity_type="Thing",
                        transport=transport, protocol=protocol,
                        timezone=timezone)

    temp_attr = {"name": "temperature",
            "value_type": "Number",
            "attr_type": "active",
            "attr_value": "15",
            "object_id": "t"}


    device.add_attribute_json(temp_attr)

    press_attr = {"name": "pressure",
            "value_type": "Number",
            "attr_type": "active",
            "object_id": "p"}

    device.add_attribute_json(press_attr)


    name_attr =  {"name": "nice_name",
                   "value_type": "String",
                   "attr_type": "static",
                   "attr_value" : "beautiful attribute!",
                   "object_id": "name"}

    device.add_attribute_json(name_attr)

    return device

if __name__ == "__main__":

    # Read and check configuration
    CONFIG = config.Config("config.json")

    # Creating an Instance of the Context Broker
    ORION_CB = create_cb()

    # check whether the context broker works:
    ORION_CB.sanity_check()


    # Creating an Instance of the IoT-Agent in the JSON-Version
    IOTA_JSON = iot.Agent("iota_json", CONFIG)

    # Creating an Instance of the IoT-Agent in the UL-Version
    IOTA_UL = iot.Agent("iota_ul", CONFIG)




    # set the service path
    fiware_service = orion.FiwareService("test_service2", "/iota")
    ORION_CB.set_service(fiware_service)
    res = fiware_service.get_header()


    # create a device

    device_1 = create_device()

    # create a device group

    cb_host = "http://orion:1026"

    iot_agent = "iota_ul"

    device_group = create_device_group(fiware_service=fiware_service, cb_host=cb_host,
                                       devices=[device_1])

    # Test the device group
    device_group.test_apikey()

    IOTA_JSON.post_group(device_group)

    IOTA_JSON.post_device(device=device_1, device_group=device_group)

    """ 
    device_group_json = iot.DeviceGroup(fiware_service,
                                         "http://orion:1026",
                                         iot_agent="iota_json", apikey="12345")

    device_group = iot.DeviceGroup(fiware_service,
                                    "http://orion:1026",
                                    iot_agent="iota_ul",
                                    apikey="12345test")
    device_group.test_apikey()

    device_ul = iot.Device('urn:Room:002:sensor01','urn:Room:002',
                           "Thing",
                           transport="MQTT", protocol="PDI-IoTA-UltraLight",
                           timezone="Europe/Berlin")

    '''

    device_ul.add_attribute("temperature", attr_type="active",
                            value_type="Number", object_id="t")
                            
                            
    device_ul.add_attribute("pressure", attr_type="active",
                            value_type="Number", object_id="p")


    device_ul.add_attribute("nice_name", attr_type="static",
                            value_type="String", object_id="name",
                            attr_value="beautiful attribute!")

    
    '''
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



    device_ul.delete_attribute("pressure", "active")


    device_json = iot.Device('urn:Room:002:sensor02','urn:Room:002',
                             "Thing", transport="MQTT",
                             protocol="IoTA-JSON",
                             timezone="Europe/Berlin")
    
    print(device_ul.get_json())

    print(device_json.get_json())

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

    print(ORION_CB.get_all_entities(), "These are all Entities")
    ORION_CB.get_entity('urn:Room:002')
    #ORION_CB.delete('urn:Room:002')


    #IOTA_JSON.delete_device(device_group_json, device_json)
    #IOTA_JSON.delete_group(device_group_json)

    #IOTA_UL.delete_device(device_group, device_ul)
    #IOTA_UL.delete_group(device_group)


    """
