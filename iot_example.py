import filip.iot as iot
import filip.orion as orion
import filip.config as config

# ToDo: Rewrite Example, so it matches the orion Example
# ToDo: Change Data Model




if __name__ == "__main__":

    # Read and check configuration
    CONFIG = config.Config("config.json")

    # Creating an Instance of the Context Broker
    ORION_CB = orion.Orion(CONFIG)


    # Creating an Instance of the IoT-Agent in the UL-Version
    IOTA_UL = iot.Agent("iota_ul", CONFIG)


    # Creating an Instance of the IoT-Agent in the JSON-Version
    IOTA_JSON = iot.Agent("iota_json", CONFIG)

    # set the service path
    fiware_service = orion.FiwareService("test_service2", "/iot_ul")
    ORION_CB.set_service(fiware_service)
    res=fiware_service.get_header()

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

    
    '''
    temp_attr = {"name": "temperature",
            "value_type": "Number",
            "attr_type": "active",
            "attr_value": "12",
            "object_id": "t"}
            
    

    device_ul.add_attribute_json(temp_attr)
    


    device_ul.add_attribute("pressure", attr_type="active",
                            value_type="Number", object_id="p")


    device_ul.add_attribute("nice_name", attr_type="static",
                            value_type="String", object_id="name",
                            attr_value="beautiful attribute!")


    #device_ul.delete_attribute("pressure", "active")


    device_json = iot.Device('urn:Room:002:sensor02','urn:Room:002',
                             "Thing", transport="MQTT",
                             protocol="IoTA-JSON",
                             timezone="Europe/Berlin")
    
    print(device_ul.get_json())
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



    IOTA_JSON.delete_device(device_group_json, device_json)
    IOTA_JSON.delete_group(device_group_json)

    IOTA_UL.delete_device(device_group, device_ul)
    IOTA_UL.delete_group(device_group)
    

