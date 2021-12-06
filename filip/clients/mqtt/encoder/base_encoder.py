"""
Abstract class for all IoTA MQTT message encoders
"""
import logging
from abc import ABC
from datetime import datetime
from typing import Dict, Tuple
from paho.mqtt.client import MQTTMessage
from filip.models.mqtt import IoTAMQTTMessageType
from filip.utils import convert_datetime_to_iso_8601_with_z_suffix


class BaseEncoder(ABC):
    """
    Abstract class for all IoTA MQTT message encoders
    """
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
        """
        Decode message for ingoing traffic
        Args:
            msg: Message class
            decoder: encoding identifier

        Returns:
            apikey
            device_id
            payload
        """
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
                   msg_type: IoTAMQTTMessageType) -> str:
        """
        Encode message for outgoing traffic

        Args:
            device_id: id of the iot device
            payload: payload to send
            msg_type: kind of message to send

        """
        raise NotImplementedError

    @classmethod
    def _parse_timestamp(cls, payload: Dict) -> Dict:
        """
        Helper function to parse timestamps

        Args:
            payload: payload to reformat

        Returns:
            Dictionary containing the formatted payload
        """
        if payload.get('timeInstant', None):
            timestamp = payload['timeInstant']
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(payload["timeInstant"])
            if isinstance(timestamp, datetime):
                payload['timeInstant'] = \
                    convert_datetime_to_iso_8601_with_z_suffix(
                        payload['timeInstant'])
            else:
                raise ValueError('Not able to parse datetime')
        return payload

    @classmethod
    def _raise_encoding_error(cls,
                              payload: Dict,
                              msg_type: IoTAMQTTMessageType):
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
