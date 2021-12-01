"""
Json encoder class for all IoTA-JSON MQTT message encoders
"""
import json
from typing import Any, Dict, Tuple
from filip.clients.mqtt.encoder import BaseEncoder
from filip.models.mqtt import IoTAMQTTMessageType


class Json(BaseEncoder):
    """
    Json encoder class for all IoTA-JSON MQTT message encoders
    """
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
                   msg_type: IoTAMQTTMessageType) -> str:
        if msg_type == IoTAMQTTMessageType.SINGLE:
            return payload
        elif msg_type == IoTAMQTTMessageType.MULTI:
            payload = super()._parse_timestamp(payload=payload)
            return json.dumps(payload, default=str)
        elif msg_type == IoTAMQTTMessageType.CMDEXE:
            return json.dumps(payload)
        super()._raise_encoding_error(payload=payload, msg_type=msg_type)
