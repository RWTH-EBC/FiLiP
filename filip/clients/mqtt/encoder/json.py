import json
from datetime import datetime
from typing import Any, Dict, Literal, Tuple
from filip.clients.mqtt.encoder import BaseEncoder

class Json(BaseEncoder):
    prefix = '/json'

    def __init__(self):
        super().__init__()

    def decode_message(self, msg, decoder='utf-8') -> Tuple[str, str, Dict]:
        apikey, device_id, payload = super().decode_message(msg=msg,
                                                            decoder=decoder)
        payload = json.loads(payload)
        return apikey, device_id, payload

    def encode_msg(self,
                   device_id,
                   payload: Any,
                   msg_type: Literal['single', 'multi', 'cmdexe']) -> str:
        if msg_type == 'single':
            return payload
        elif msg_type == 'multi':
            payload = super()._parse_timestamp(payload=payload)
            return json.dumps(payload, default=str)
        elif msg_type == 'cmdexe':
            return json.dumps(payload)
        super()._raise_encoding_error(payload=payload, msg_type=msg_type)
