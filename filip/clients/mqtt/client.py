"""
Created 21st Oct, 2021

@author: Thomas Storek
"""
import logging
import paho.mqtt.client as mqtt
from pydantic import BaseModel, Field, validator, ValidationError
from typing import Any, Callable, Dict, List, Literal, Type, Union
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
    subtopics: Union[List[str], str] = Field(
        default=[],
        description="Topics to that the agent subscribes"
    )
    prefix: str = Field(
        default="/agentlib",
        description="Prefix for MQTT-Topic"
    )
    qos: int = Field(
        default=0,
        description='Quality of Service',
        ge=0,
        le=2
    )
    encoder: Encoder = Field(
        default='agentlib',
        title='encoder',
        description="Encoder to be used for "
                    "composing the message format"
    )
    connection_timeout: float = Field(
        default=10,
        description="Number of seconds to wait for the initial connection until "
                    "throwing an Error."
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
            parent

        Raises:
            Value Error
        """
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
        if devices:
            self.devices = {dev.device_id: dev for dev in devices}
        else:
            self.devices = {}

        if service_groups:
            self.service_groups = {(gr.apikey, gr.resource): gr
                                   for gr in service_groups}
        else:
            self.service_groups = {}

        self.encoder: BaseEncoder = encoder()


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

    def get_topics(self, device_id: str) -> Dict:
        device = self.devices[device_id]
        topics = {'attrs': '/'.join((self.encoder.prefix, device.apikey,
                                     device_id, 'attrs')),
                  'cmd': '/' + '/'.join((device.apikey, device.device_id, 'cmd')),
                  'cmdexe': '/'.join((self.encoder.prefix, device.apikey,
                                    device_id, 'cmd'))}
        return topics

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

    def add_device(self, device: Union[Device, Dict]):
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
        if self.is_connected():
            self.subscribe(self.get_topics(device_id=de)['cmd'])

    def add_command_callback(self, device_id, callback: Callable):
        assert device_id.get(device_id, None) is not None, "Device does not " \
                                                           "exist!"
        topic = self.devices[device_id]
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


    def on_connect(self, mqttc, obj, flags, rc):
        print("rc: "+str(rc))

    def on_connect_fail(self, mqttc, obj):
        print("Connect failed")

    def on_message(self, mqttc, obj, msg):
        print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        print(self.encoder.decode_msg(msg))

    def on_publish(self, mqttc, obj, mid):
        print("mid: "+str(mid))

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: "+str(mid)+" "+str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        print(string)

    def run(self):
        self.connect("mqtt.eclipseprojects.io", 1883, 60)
        #self.subscribe("$SYS/#", 0)
        for device in self.devices.values():
            topic = f"/{'/'.join((device.apikey, device.device_id, 'attrs'))}"
            self.subscribe(topic)

        rc = 0
        while rc == 0:
            rc = self.loop()
        return rc

    def stop(self):
        self.loop_stop()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    device = Device(device_id="device_id",
                    apikey="apikey",
                    entity_name="device_name",
                    entity_type="device_type",
                    transport="MQTT")
    from filip.clients.mqtt.encoder import IoTAJsonEncoder
    mqttc = MQTTClient(client_id="test", devices=[device], encoder=IoTAJsonEncoder)
    print(mqttc.get_topics(device_id=device.device_id))

    rc = mqttc.run()
    print("rc: " + str(rc))