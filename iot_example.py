import os
import csv
import filip.iot as iot
import json
import filip
import filip.orion as orion
import filip.config as config



if __name__ == "__main__":

    # Read and check configuration
    CONFIG = config.Config("config - Kopie.json")
    ORION_CB = orion.Orion(CONFIG)
    IOTA_JSON = iot.Agent("iota_json", CONFIG)
    IOTA_UL = iot.Agent("iota_ul", CONFIG)
    fiware_service = orion.FiwareService("test_service2", "/iot_ul")
    ORION_CB.set_service(fiware_service)
    res=fiware_service.get_header()

    device_group_json = filip.iot.DeviceGroup(fiware_service,
                                         "http://orion:1026",
                                         iot_agent="iota_ul", apikey="12345")

    device_group = filip.iot.DeviceGroup(fiware_service,
                                         "http://orion:1026",
                                         iot_agent="iota_ul",
                                         apikey="12345test")
    device_group.test_apikey()

    device_ul = iot.Device('urn:Room:002:sensor01','urn:Room:002',
                           "Thing",
                           transport="MQTT", protocol="PDI-IoTA-UltraLight",
                           timezone="Europe/Berlin")
    attr1 = iot.Attribute("temperature", attr_type="active",
                          value_type="Number", object_id="t")
    attr2 = iot.Attribute("pressure", attr_type="active",
                          value_type="Number", object_id="p")
    attr3 = iot.Attribute("nice_name", attr_type="static",
                          value_type="String", object_id="name",
                          attr_value="beautiful attribute!")
    print(attr1.get_json)
    device_ul.add_attribute(attr1)
    device_ul.add_attribute(attr2)
    device_ul.add_attribute(attr3)

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
