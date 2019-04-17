import random
import string
import filip
import json

class FiwareService:
    def __init__(self, name: str, path: str, cbroker: str,
                           **kwargs):
        self.name = name
        self.path = path


    def get_header(self) -> dict:
        return {
            "fiware-service": self.name,
            "fiware-servicepath": self.path
        }




