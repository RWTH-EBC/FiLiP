import os
import csv
import iot

import filip
import filip.iot as iot
import filip.orion as orion



if __name__ == "__main__":

    # Read and check configuration
    CONFIG = filip.Config()
    #CONFIG.read_config_file("./config.json")
    ORION_CB = orion.Orion(CONFIG)
    IOTA_JSON = iot.Agent("iota_json", CONFIG)
    IOTA_UL = iot.Agent("iota_ul", CONFIG)

    FIWARE_SERVICE = filip.Fiware_service("test_service", "/iot_ul",
                                          iot_agent="iota_ul", apikey="1234")
    FIWARE_SERVICE.test_apikey()

    room1_a1 = orion.Attribute('temperature', 11, 'Float')
    room1_a2 = orion.Attribute('pressure', 111, 'Integer')
    attributes1 = room1_a1, room1_a2
    room1 = orion.Entity('Room1', 'Room', attributes1)
    device = iot.Device('motion001','Room1', "Thing", transport="MQTT",
                        protocol="PDI-IoTA-UltraLight", timezone="Europe/Berlin")


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
    dev.provision_devices(devices)
