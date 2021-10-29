from abc import ABC, abstractmethod
from typing import Dict, Literal, Tuple
from paho.mqtt.client import MQTTMessage


class BaseEncoder(ABC):
    prefix: str = ''

    @abstractmethod
    @classmethod
    def decode_message(cls,
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

    @abstractmethod
    @classmethod
    def encode_msg(cls, payload: Dict, msg_type: Literal['single',
                                                         'multi',
                                                         'cmdexe']) \
            -> str:
        raise NotImplementedError

    @classmethod
    def __raise_encoding_error(cls, payload: Dict,
                               msg_type: Literal['single', 'multi', 'cmdexe']):
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

