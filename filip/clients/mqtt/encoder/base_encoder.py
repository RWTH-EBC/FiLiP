import logging
from abc import ABC
from datetime import datetime
from typing import Dict, Literal, Tuple
from paho.mqtt.client import MQTTMessage
from filip.models.mqtt import IotaMqttMessageType

class BaseEncoder(ABC):
    prefix: str = ''

    def __init__(self):
        # setup logging functionality
        self.logger = logging.getLogger(
            name=f"{self.__class__.__module__}."
                 f"{self.__class__.__name__}")
        self.logger.addHandler(logging.NullHandler())

    def decode_message(self,
                       msg: MQTTMessage,
                       decoder: str = 'utf-8') -> Tuple[str, str, str]:
        topic = msg.topic.strip('/')
        topic = topic.split('/')
        apikey = None
        device_id = None
        payload = msg.payload.decode(decoder)
        if topic[-1] == 'cmd':
            apikey = topic[0]
            device_id = topic[1]

        if any((apikey, device_id, payload)) is None:
            raise ValueError

        return apikey, device_id, payload

    def encode_msg(self,
                   device_id: str,
                   payload: Dict,
                   msg_type: Literal['single', 'multi', 'cmdexe']) -> str:
        raise NotImplementedError

    @classmethod
    def _parse_timestamp(cls, payload: Dict) -> Dict:
        if payload.get('timeInstant', None):
            timestamp = payload['timeInstant']
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(payload["timeInstant"])
            if isinstance(timestamp, datetime):
                payload['timeInstant'] = timestamp.astimezone().isoformat()
            else:
                raise ValueError('Not able to parse datetime')
        return payload

    @classmethod
    def _raise_encoding_error(cls,
                              payload: Dict,
                              msg_type: IotaMqttMessageType):
        """
        Helper function to provide consistent error messages
        Args:
            payload: Invalid message content
            msg_type: Invalid message type

        Returns:
            None

        Raises:
            ValueError
        """
        ValueError(f"Message format not supported! \n "
                   f"Message Type: {msg_type} \n "
                   f"Payload: {payload}")
