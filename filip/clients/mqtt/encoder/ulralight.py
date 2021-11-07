from pydantic import validate_arguments
from typing import Any, Dict, Tuple, Union
from filip.clients.mqtt.encoder import BaseEncoder
from filip.models.mqtt import IoTAMQTTMessageType

class Ultralight(BaseEncoder):
    prefix = '/ul'

    def __init__(self):
        super().__init__()

    @staticmethod
    @validate_arguments
    def __eval_value(value: Union[bool, float, str]):
        return value

    def decode_message(self, msg, decoder='utf-8') -> Tuple[str, str, Dict]:
        apikey, device_id, payload = super().decode_message(msg=msg,
                                                            decoder=decoder)
        payload = payload.split('@')
        if not device_id == payload[0]:
            self.logger.warning("Received invalid command")

        payload = payload[1].split('|')
        payload = {payload[i]: self.__eval_value(payload[i + 1])
                   for i in range(0, len(payload), 2)}

        return apikey, device_id, payload

    def encode_msg(self,
                   device_id: str,
                   payload: Any,
                   msg_type: IoTAMQTTMessageType) -> str:
        if msg_type == IoTAMQTTMessageType.SINGLE:
            return payload
        elif msg_type == IoTAMQTTMessageType.MULTI:
            payload = super()._parse_timestamp(payload=payload)
            timestamp = str(payload.pop('timeInstant', ''))
            data = '|'.join([f"{key}|{value}" for key, value in
                             payload.items()])
            data = '|'.join([timestamp, data]).strip('|')
            return data
        elif msg_type == IoTAMQTTMessageType.CMDEXE:
            for key, value in payload.items():
                if isinstance(value, bool):
                    value = str(value).lower()
                elif isinstance(value, (float, int)):
                    value = str(value)
                elif isinstance(value, str):
                    pass
                else:
                    raise ValueError("Cannot parse command acknowledgement!")
                return f"{device_id}@{key}|{value}"
        super()._raise_encoding_error(payload=payload, msg_type=msg_type)