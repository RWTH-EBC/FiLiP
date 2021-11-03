
from typing import Any, Dict, Literal, Tuple
from filip.clients.mqtt.encoder import BaseEncoder


class Ultralight(BaseEncoder):
    prefix = '/ul'

    def __init__(self):
        super().__init__()

    def decode_message(self, msg, decoder='utf-8') -> Tuple[str, str, Dict]:
        apikey, device_id, payload = super().decode_message(msg=msg,
                                                            decoder=decoder)
        payload = payload.split('@')
        if device_id == payload[0]:
            self.logger.warning("Received invalid command")

        payload = payload[1].split('|')
        payload = {payload[i]: eval(payload[i + 1])
                   for i in range(0, len(payload), 2)}

        return apikey, device_id, payload

    def encode_msg(self, payload: Any, msg_type: Literal['single',
                                                         'multi',
                                                         'cmdexe'])  \
            -> str:
        if msg_type == 'single':
            return payload
        elif msg_type == 'multi':
            payload = super()._parse_timestamp(payload=payload)
            timestamp = str(payload.pop('timeInstant', ''))
            data = '|'.join([f"{key}|{value}" for key, value in
                             payload.items()])
            data = '|'.join([timestamp, data])
            return data
        elif msg_type == 'cmdexe':
            return '|'.join([f"{key}|{value}" for key, value in
                             payload.items()])
        self.__raise_encoding_error(payload=payload, msg_type=msg_type)