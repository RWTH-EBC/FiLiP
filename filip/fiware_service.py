import random
import string
import filip
import json

class Fiware_service:
    def __init__(self, name: str, path: str, cbroker: str,
                           **kwargs):
        self.name = name
        self.path = path
        self.cbroker = cbroker
        self.agent = kwargs.get("iot-agent", "iota-json")
        self.apikey = kwargs.get("apikey", "12345")
        self.entity_type = kwargs.get("entity_type", "Thing")
        self.resource = kwargs.get("resource","")
        self.devices = []


    def get_header(self) -> dict:
        return {
            "fiware-service": self.name,
            "fiware-servicepath": self.path
        }


    def get_json(self):
        dict = {}
        dict['apikey']= self.apikey
        dict['cbroker'] = self.cbroker
        dict['entity_type']= self.entity_type
        dict['resource'] = self.resource
        return json.dumps(dict, indent=4)

    def generate_apikey(self, length: int = 10):
        """
        This function generates a random key from lowercase letter and
        digit characters
        :ivar length: Number of characters in the key string
        """
        return ''.join(random.choice(
            string.ascii_lowercase + string.digits) for _ in range(
            length))

    def test_apikey(self):
        """
        This function tests if an apikey is defined in the configfile.
        Otherwise it will ask the user to generate one and saves it to the
        configfile in the given sections.
        """
        try:
            if self.apikey == "":
                res = input("[INFO]: No API-Key defined. Do you want to "
                            "generate one? "
                            "y/Y ")
                if res == "y" or res == "Y":
                    res = input("Please specify number of key (default is "
                                "10)? ")
                    if res != 10:
                        self.apikey = self.generate_apikey(int(res))
                    else:
                        self.apikey = self.generate_apikey()
                    #with open(self.path, 'w') as configfile:
                    #    self.config.write(configfile)
                    print("[INFO]: Random Key generated: '" + self.apikey+ "'")
                else:
                    print("[INFO]: Default Key will be used: '1234'!")
            print("[INFO]: API-Key check success! " + self.apikey)
        except Exception:
            print("[ERROR]: API-Key check failed. Please check configuration!")

    def register_device(self, device: filip.iot.Device):
        return

    def get_device(self, device: filip.iot.Device):
        return