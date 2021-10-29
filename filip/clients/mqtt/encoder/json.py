import json
from typing import Any, Dict, Literal, Tuple
from filip.clients.mqtt.encoder import BaseEncoder

class IoTA_Json(BaseEncoder):
    prefix = '/json'

    @classmethod
    def decode_message(cls, msg, decoder='utf-8') -> Tuple[str, str, Dict]:
        apikey, device_id, payload = super().decode_message(msg=msg,
                                                            decoder=decoder)
        payload = json.loads(payload)
        return apikey, device_id, payload

    @classmethod
    def encode_msg(cls, payload: Any, msg_type: Literal['single',
                                                        'multi',
                                                        'cmdexe'])  \
            -> str:
        if msg_type == 'single':
            return payload
        elif msg_type == 'multi':
            return json.dumps(payload)
        elif msg_type == 'cmdexe':
            return json.dumps(payload)
        cls.__raise_encoding_error(payload=payload, msg_type=msg_type)
