"""
Created 21st Oct, 2021

@author: Thomas Storek
"""
import logging
import paho.mqtt.client as mqtt
import warnings
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
            client_id:
                Unique client id string used when connecting
                to the broker. If client_id is zero length or None, then the
                behaviour is defined by which protocol version is in use. If
                using MQTT v3.1.1, then a zero length client id will be sent
                to the broker and the broker will generate a random for the
                client. If using MQTT v3.1 then an id will be randomly
                generated. In both cases, clean_session must be True.
                If this is not the case a ValueError will be raised.
            clean_session:
                boolean that determines the client type. If True,
                the broker will remove all information about this client when it
                disconnects. If False, the client is a persistent client and
                subscription information and queued messages will be retained
                when the client disconnects.
                Note that a client will never discard its own outgoing
                messages on disconnect. Calling connect() or reconnect() will
                cause the messages to be resent.  Use reinitialise() to reset
                a client to its original state. The clean_session argument
                only applies to MQTT versions v3.1.1 and v3.1. It is not
                accepted if the MQTT version is v5.0 - use the clean_start
                argument on connect() instead.
            userdata:
                defined data of any type that is passed as the "userdata"
                parameter to callbacks. It may be updated at a later point
                with the user_data_set() function.
            protocol:
                explicit setting of the MQTT version to use for this client.
                Can be paho.mqtt.client.MQTTv311 (v3.1.1),
                paho.mqtt.client.MQTTv31 (v3.1) or paho.mqtt.client.MQTTv5
                (v5.0), with the default being v3.1.1.
            transport:
                Set to "websockets" to use WebSockets as the transport
                mechanism. Set to "tcp" to use raw TCP, which is the default.
            devices:
                List of device configurations that will be registered
                with the client. Consequently, the client will be able to
                subscribe to all registered device topics. Furthermore,
                after registration messages can simply published by the
                devices id.
            service_groups:
                List of service group configurations that will be registered
                with the client. These should be known upon subscribing
                because the client will check for a matching service group if
                this is not known or registered with the IoT-Agent service
                the receiving of commands will fail. Please check the
                official documentation of the IoT-Agents API for more details.
            encoder:
                Encoder class that will automatically parse the supported
                payload formats to a dictionary and vice versa. This
                essentially saves boiler plate code.

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
        service_groups: Dict[Tuple[str, str], ServiceGroup]
        if service_groups:
            self.service_groups = {(gr.apikey, gr.resource): gr
                                   for gr in service_groups}
        else:
            self.service_groups = {}

        # add encoder for message parsing
        self.encoder: BaseEncoder = encoder() or BaseEncoder()

    def __create_topic(self,
                       device: Device,
                       topic_type: Literal['attrs',
                                           'cmd',
                                           'cmdexe']) -> \
            Union[str, List[str]]:
        """
        Creates a topic for a device configuration based on the requested
        topic type.
        Args:
            device: Configuration of an IoT device
            topic_type:
                type of the topic to be created,
                'attrs' for topics that the device is suppose to publish on.
                'cmd' for topic the device is expecting its commands on.
                'cmdexe' for topic the device can acknowledge its commands on.
        Returns:
            string with topic
        # TODO: create also direct topic for non-multi-measurements
        # TODO: add configuration topic
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
        Subscribes commands based on device configuration. If device argument is
        omitted the function will subscribe to all topics of already registered
        devices.
        Additionally, it will also check if a matching service group is
        registered with the client. If nor a warning will be raised.

        Args:
            device: Configuration of an IoT device
            qos: Quality of service can be 0, 1 or 2
            options: MQTT v5.0 subscribe options
            properties: MQTT v5.0 properties

        Returns:
            None
        """
        apikeys = [gr.apikey for gr in self.service_groups.values()]

        if Device:
            if len(device.commands) > 0:
                # check if matching service group is registered
                if not device.apikey in apikeys:
                    msg = "Could not find matching service group! Commands " \
                          "may not be received correctly!"
                    self.logger.warning(msg=msg)
                    warnings.warn(message=msg)
                topic = self.__create_topic(device=device,
                                            topic_type='cmd')
                super().subscribe(topic=topic,
                                  qos=qos,
                                  options=options,
                                  properties=properties)
        else:
            # call itself but with device argument for all registered devices
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
            device: Configuration of an IoT device
            qos: Quality of service can be 0, 1 or 2
            options: MQTT v5.0 subscribe options
            properties: MQTT v5.0 properties

        Returns:
            None
        """
        if isinstance(device, dict):
            device = Device.parse_obj(device)
        assert isinstance(device, Device), "Invalid content for device"

        # add device configuration to the device list
        self.devices[device.device_id] = device
        # subscribes to the command topic
        self.__subscribe_commands(device=device,
                                  qos=qos,
                                  options=options,
                                  properties=properties)

    def add_command_callback(self, device_id, callback: Callable):
        """

        Args:
            device_id: id of and IoT device
            callback:

        Returns:
            None
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
                device_id: str = None,
                attribute: str = None):
        """

        Args:
            topic:
            payload:
            qos:
            retain:
            properties:
            device_id:

        Returns:

        """
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
    #print(mqttc.is_connected())
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
    mqttc.add_device(device=other_device)
    time.sleep(5)
    topic = '/' + '/'.join((other_device.apikey, other_device.device_id, 'cmd'))
    #mqttc.subscribe(topic=topic)
    mqttc.publish(topic=topic, payload="other_test_cmd")

    time.sleep(5)
    # stop network loop and disconnect cleanly
    mqttc.loop_stop()
    mqttc.disconnect()