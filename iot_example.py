import os
import csv
import iot
import json
import filip
import filip.orion as orion




if __name__ == "__main__":

    # Read and check configuration
    CONFIG = filip.Config()
    #CONFIG.read_config_file("./config.json")
    ORION_CB = orion.Orion(CONFIG)
    IOTA_JSON = iot.Agent("iota_json", CONFIG)
    IOTA_UL = iot.Agent("iota_ul", CONFIG)
    fiware_service = orion.FiwareService("test_service", "/iot_ul")
    res=fiware_service.get_header()
    device_group = filip.iot.DeviceGroup(fiware_service.name,
                                         fiware_service.path,
                                          "http://orion:1026",
                                         iot_agent="iota_ul", \
                                                       apikey="12345")
    device_group.test_apikey()

    device_ul = iot.Device('urn:Room:001:sensor01','urn:Room:001',
                           "Thing",
                           transport="MQTT", protocol="PDI-IoTA-UltraLight",
                           timezone="Europe/Berlin")
    device_json = iot.Device('urn:Room:001:sensor01','urn:Room:001', "Thing",
                           transport="MQTT", protocol="IoTA-JSON",
                           timezone="Europe/Berlin")
    #attribute = iot.Attribute(name= "test", )
    print(device_ul.get_json())
    #print(device_json.get_json())
    IOTA_JSON.post_group(device_group)
    IOTA_JSON.get_groups(device_group)
    IOTA_JSON.post_device(device_group, device_json)
    IOTA_JSON.update_device(device_group, device_json, "")
    IOTA_JSON.get_device(device_group, device_json)
    ORION_CB.get_all_entities(fiware_service)
    ORION_CB.get_entity(fiware_service, 'urn:Room:001')
    #iot.Attribute()

    IOTA_JSON.delete_device(device_group, device_json)
    IOTA_JSON.delete_group(device_group)


    #attr1 = orion.Attribute('temperature', 11, 'Float')
    #attr2 = orion.Attribute('pressure', 111, 'Integer')
    #attributes = attr1, attr2
    #room_ul = orion.Entity('urn:Room:001', 'Room', attributes)
    #room_json= orion.Entity('urn:Room:002', 'Room', attributes)


    #IOTA_UL.post_device(device_ul)
    #IOTA_JSON.post_device(device_json)
    # config = conf.Config(config_path, config_section)
    # CONFIG.read
    # a = CONFIG.CONFIG_PATH





    # CONFIG_PATH = os.getenv("CONFIG_PATH", 'conf.ini')
    # ORION_URL = os.getenv("ORION_URL", "http://localhost:1028/")
    # IOTA_URL = os.getenv("IOTA_URL", "http://localhost:1026/")
    # QUANTUM_URL = os.getenv("QUANTUM_URL", "http://localhost:8668/")

    # CONFIG.check_config()

    # Register a service configuration
    # iota.register_configuration(config.fiware_service,
    #                           config.fiware_service_path,
    #                          apikey=config.apikey)

    # demo using fismep project files, adjust this to your needs!
'''
    devices = []
    with open('example.csv', encoding='UTF-8') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=';')

        for row in reader:
            device_id = "sensor" + row["ID_SENSOR"]
            entity_id = "fismep:sensor:" + row["ID_SENSOR"]
            device = dev.Device(device_id, entity_id, "Sensor")
            # TODO we can specify unit and  description as static attribute, BUT
            # they then will be appended to each updateContext request
            # -> send them directly to the context broker!
            devices.append(device)

    print("[INFO] Loaded {} devices".format(len(devices)))
    #dev.provision_devices(devices)
    '''
