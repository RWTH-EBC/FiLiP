"""
Created 21st Oct, 2021

@author: Thomas Storek
"""
import logging
import paho.mqtt.client as mqtt
from pydantic import BaseModel, Field, validator, ValidationError
from typing import Any, Callable, Dict, List, Literal, Tuple, Type, Union
from filip.types import AnyMqttUrl
from filip.clients.mqtt.encoder import BaseEncoder
from filip.models.ngsi_v2.iot import Device, ServiceGroup


class MQTTClientConfig(BaseModel):
    url: AnyMqttUrl = Field(
        default=None,
        title='Host',
        description='host is the hostname or IP address '
                    'of the remote broker.'
    )
    host: str = Field(
        default=None,
        title='Host',
        description='host is the hostname or IP address '
                    'of the remote broker.'
    )
    port: int = Field(
        default=1883,
        title='Port',
        ge=0,
        lt=65535,
        description="Network port of the server host to "
                    "connect to. Defaults to 1883. Note "
                    "that the default port for MQTT "
                    "over SSL/TLS is 8883 so if you are "
                    "using tls_set() the port may need "
                    "providing."
    )
    keepalive: int = Field(
        default=60,
        description='Maximum period in seconds between '
                    'communications with the broker. '
                    'If no other messages are being '
                    'exchanged, this controls the '
                    'rate at which the client will '
                    'send ping messages to the '
                    'broker.'
    )
    clean_start: bool = Field(
        default=True,
        description="True, False or "
                    "MQTT_CLEAN_START_FIRST_ONLY."
                    "Sets the MQTT v5.0 clean_start "
                    "flag always, never or on the "
                    "first successful connect "
                    "only, respectively.  "
                    "MQTT session data (such as "
                    "outstanding messages and "
                    "subscriptions) is cleared "
                    "on successful connect when "
                    "the clean_start flag is set."
    )
    qos: int = Field(
        default=0,
        description='Quality of Service',
        ge=0,
        le=2
    )
    connection_timeout: float = Field(
        default=10,
        description="Number of seconds to wait for the initial connection until "
                    "throwing an Error."
    )
    encoder: BaseEncoder = Field(
        default='agentlib',
        title='encoder',
        description="Encoder to be used for "
                    "composing the message format"
    )
    @validator('url', always=True)
    def check_url(cls, url):
        if url is None:
            raise ValueError(
                "You have to pass an url as a parameter "
                "in order for the mqtt communicator to work"
            )
        if url.scheme in ['mqtts', 'mqtt']:
            return url
        if url.scheme is None:
            url.scheme = 'mqtt'
            return url
        raise ValidationError

    @validator('host', always=True)
    def check_host(cls, host, values):
        if host is None and 'url' in values:
            return values['url'].host
        return host

    @validator('port', always=True)
    def check_port(cls, port, values):
        if 'url' in values and values['url'].port:
            return values['url'].port
        return port

    class Config:
        arbitrary_types_allowed = True


class MQTTClient(mqtt.Client):
    """
    This class is an extension to the MQTT client from the well established
    Eclipse Paho™ MQTT Python Client. The official documentation is located
    here: https://github.com/eclipse/paho.mqtt.python

    The class adds additional functions to facilitate the communication to
    FIWARE's IoT-Agent via MQTT. It magically generates and subscribes to all
    important topics that are necessary to establish a
    bi-directional communication with the IoT-Agent.

    Note:
        The extension does not effect the normal workflow or any other
        functionality known from the original client.
    """
    def __init__(self,
                 client_id="",
                 clean_session=None,
                 userdata=None,
                 protocol=mqtt.MQTTv311,
                 transport="tcp",
                 devices: List[Device]=None,
                 service_groups: List[ServiceGroup]=None,
                 encoder: Type[BaseEncoder]=None):
        """
        Args:


        Raises:
            Value Error
        """
        # setup logging functionality
        self.logger = logging.getLogger(
            name=f"{self.__class__.__module__}."
                 f"{self.__class__.__name__}")
        self.logger.addHandler(logging.NullHandler())
        super().__init__(client_id=client_id,
                         clean_session=clean_session,
                         userdata=userdata,
                         protocol=protocol,
                         transport=transport)
        self.enable_logger(self.logger)

        # create dictionary holding the registered device configurations
        self.devices: Dict[str, Device]
        if devices:
            self.devices = {dev.device_id: dev for dev in devices}
        else:
            self.devices = {}

        # create dictionary holding the registered service groups
        service_groups: Dict[Tuple(str, str), ServiceGroup]
        if service_groups:
            self.service_groups = {(gr.apikey, gr.resource): gr
                                   for gr in service_groups}
        else:
            self.service_groups = {}

        # add encoder for message parsing
        self.encoder: BaseEncoder = encoder() or BaseEncoder()

    def __create_topic(self,
                       device: Device,
                       topic_type: Literal['attrs', 'cmd', 'cmdexe']) -> \
            Union[str, List[str]]:
        """

        Args:
            device:
            topic_type:

        Returns:

        # TODO: create also direct topic for non-multimeasure
        """
        topic = None
        if topic_type == 'attrs':
            topic = ['/'.join((self.encoder.prefix,
                               device.apikey,
                               device.device_id, 'attrs'))]
        elif topic_type == 'cmd':
            topic = '/' + '/'.join((device.apikey, device.device_id, 'cmd'))
        elif topic_type == 'cmdexe':
            '/'.join((self.encoder.prefix,
                      device.apikey,
                      device.device_id, 'cmd'))
        else:
            raise KeyError
        return topic


    def __subscribe_commands(self,
                             device: Device=None,
                             qos=0,
                             options=None,
                             properties=None):
        """

        Args:
            device:
            qos:
            options:
            properties:

        Returns:

        """
        apikeys = [gr.apikey for gr in self.service_groups.values()]
        if Device:
            if len(device.commands) > 0:
                if not device.apikey in apikeys:
                    self.logger.warning("Could not find matching service group! "
                                        "Commands may not be received "
                                        "correctly!")
                    topic = self.__create_topic(device=device,
                                                topic_type='cmd')
                    super().subscribe(topic=topic,
                                      qos=qos,
                                      options=options,
                                      properties=properties)
        else:
            for device in self.devices.values():
                self.__subscribe_commands(device=device,
                                          qos=qos,
                                          options=options,
                                          properties=properties)

    def get_device(self, device_id: str) -> Device:
        """
        Returns the configuration of a registered device.

        Args:
            device_id: Id of the requested device

        Returns:
           Device: Device model of the requested device

        Raises:
            KeyError: If requested device is not registered with the client

        Example::

            >>> device = mqttc.get_device(device_id="MyDeviceId")
            >>> print(device.json(indent=2))
            >>> print(type(device))
        """
        return self.devices[device_id]

    def add_device(self,
                   device: Union[Device, Dict],
                   qos=0,
                   options=None,
                   properties=None):
        """
        Registers a device config with the mqtt client. Subsequently,
        the client will magically subscribe to the corresponding topics based
        on the device config and any matching registered service group config
        if exists.

        Note:
            To register the device config only with this client is not
            sufficient for data streaming the configuration also needs to be
            registered with IoTA-Agent.

        Args:
            device: IoT Device configuration

        Returns:
            None
        """
        if isinstance(device, dict):
            device = Device.parse_obj(device)
        assert isinstance(device, Device), "Invalid content for device"

        self.devices[device.device_id] = device
        print(self.is_connected())
        #if self.is_connected():
        if True:
            self.__subscribe_commands(device=device,
                                      qos=qos,
                                      options=options,
                                      properties=properties)

    def add_command_callback(self, device_id, callback: Callable):
        """

        Args:
            device_id:
            callback:

        Returns:

        """
        assert device_id.get(device_id, None) is not None, "Device does not " \
                                                           "exist!"
        topic = self.__create_topic(self.devices[device_id], topic_type='cmd')
        self.message_callback_add(topic, Callable)

    def publish(self,
                topic = None,
                payload: Union[Dict, Any] = None,
                qos: int=0,
                retain: bool=False,
                properties=None,
                device_id: str = None):
        if device_id:
            device = self.devices[device_id]
            if isinstance(payload, Dict):
                topic = '/'.join([device.apikey, device.device_id, 'attrs'])
        super().publish(topic=topic,
                        payload=payload,
                        qos=qos,
                        retain=retain,
                        properties=properties)

    def subscribe(self, topic=None, qos=0, options=None, properties=None):
        if topic:
            super().subscribe(topic=topic,
                              qos=qos,
                              options=options,
                              properties=properties)
        else:
            self.__subscribe_commands(device=device,
                                      qos=qos,
                                      options=options,
                                      properties=properties)



if __name__ == '__main__':
    import time
    # setup logging
    logging.basicConfig(level=logging.DEBUG)

    # create a device configuration
    # creating a command that the IoT device will liston to
    from filip.models.ngsi_v2.iot import DeviceCommand
    command = DeviceCommand(name='heater', type="Boolean")
    device = Device(device_id="device_id",
                    apikey="apikey",
                    entity_name="device_name",
                    entity_type="device_type",
                    transport="MQTT",
                    commands=[command])

    from filip.clients.mqtt.encoder import IoTA_Json
    mqttc = MQTTClient(client_id="test",
                       devices=[device],
                       encoder=IoTA_Json)

    # demonstrate normal client behavior
    # For additional examples on how to use the client please check:
    # https://github.com/eclipse/paho.mqtt.python/tree/master/examples
    # define callbacks methods
    def on_connect(mqttc, obj, flags, rc):
        print("rc: "+str(rc))

    def on_connect_fail(mqttc, obj):
        print("Connect failed")

    def on_message(mqttc, obj, msg):
        print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        #print(mqttc.encoder.decode_msg(msg))

    def on_publish(mqttc, obj, mid):
        print("mid: "+str(mid))

    def on_subscribe(mqttc, obj, mid, granted_qos):
        print("Subscribed: "+str(mid)+" "+str(granted_qos))

    def on_log(mqttc, obj, level, string):
        print(string)

    # add callbacks to the client
    mqttc.on_connect = on_connect
    mqttc.on_connect_fail = on_connect_fail
    mqttc.on_message = on_message
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    mqttc.on_log = on_log

    first_topic = "/filip/testing/first"
    second_topic = "/filip/testing/second"
    mqttc.connect("mqtt.eclipseprojects.io", 1883, 60)
    mqttc.subscribe(first_topic)

    # create a non blocking loop
    mqttc.loop_start()

    mqttc.publish(topic=first_topic, payload="first")

    # add additional subscription to connection
    mqttc.subscribe(topic=second_topic)
    mqttc.publish(topic=second_topic, payload="second")

    time.sleep(5)
    # stop network loop and disconnect cleanly
    mqttc.loop_stop()
    mqttc.disconnect()

    # demonstrate magic FIWARE behavior
    mqttc.connect("mqtt.eclipseprojects.io", 1883, 60)
    mqttc.subscribe()
    print(mqttc.is_connected())
    # create a non blocking loop
    mqttc.loop_start()
    topic = '/' + '/'.join((device.apikey, device.device_id, 'cmd'))
    mqttc.publish(topic=topic, payload="test_cmd")

    # add additional device
    other_device = Device(device_id="other_device",
                    apikey="apikey",
                    entity_name="other_device_name",
                    entity_type="other_device_type",
                    transport="MQTT",
                    commands=[command])
    mqttc.add_device(device=device)

    topic = '/' + '/'.join((other_device.apikey, other_device.device_id, 'cmd'))
    time.sleep(5)
    mqttc.publish(topic=topic, payload="other_test_cmd")

    time.sleep(5)
    # stop network loop and disconnect cleanly
    mqttc.loop_stop()
    mqttc.disconnect()