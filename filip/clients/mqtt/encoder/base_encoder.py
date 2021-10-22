from abc import ABC
from typing import Any, Dict, Tuple
from paho.mqtt.client import MQTTMessage


class BaseEncoder(ABC):
    prefix: str = ''

    @classmethod
    def decode_message(cls,
                       msg: MQTTMessage,
                       decoder: str = 'utf-8') -> Tuple[str, str, Dict]:
        topic = msg.topic.split('/')
        apikey = None
        device_id = None
        payload = {}
        if topic[0] == cls.prefix and topic[-1]('/cmd'):
            apikey = topic[1]
            device_id = topic[2]

        if any((apikey, device_id, payload)) is None:
            raise ValueError

        return apikey, device_id, payload

    @classmethod
    def encode_msg(cls, device_id: str, payload: Dict) -> str:
        return NotImplemented
