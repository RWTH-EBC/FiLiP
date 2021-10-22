import json
from typing import Dict
from filip.clients.mqtt.encoder import BaseEncoder

class IoTA_Ultralight(BaseEncoder):
    prefix = '/ul'

    @staticmethod
    def decode_m(msg) -> Dict:
        return json.loads(msg.payload)

    @staticmethod
    def encode_msg(payload: Dict) -> str:
        return json.dumps(payload)