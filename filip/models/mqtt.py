"""
Module contains models for MQTT communication with FIWARE's IoT-Agents.
"""
from aenum import Enum


class IoTAMQTTMessageType(str, Enum):
    """
    Options for mqtt message type
    """
    _init_ = 'value __doc__'
    CMD = "cmd", "Command"
    CMDEXE = "cmdexe", "Command acknowledgement"
    MULTI = "multi",  "Multi measurement"
    SINGLE = "single", "Single measurement"
    CONFIG = "configuration", "Configuration message"