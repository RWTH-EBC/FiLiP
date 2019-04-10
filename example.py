import os
import csv

#import fiwarePy.device as dev
import fiwarePy




if __name__ == "__main__":

    # Read and check configuration

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
