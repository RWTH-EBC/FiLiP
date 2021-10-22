import json
from typing import Dict, Tuple
from filip.clients.mqtt.encoder import BaseEncoder

class IoTA_Json(BaseEncoder):
    prefix = '/json'

    @classmethod
    def decode_message(cls, msg, decoder='utf-8') -> Tuple[str, str, Dict]:
        apikey, device_id, payload = super().decode_message(msg=msg,
                                                            decoder=decoder)
        payload = json.loads(msg.payload.decode(decoder))

        return apikey, device_id, payload


    @staticmethod
    def encode_msg(device_id, payload: Dict) -> str:
        return json.dumps(payload)
