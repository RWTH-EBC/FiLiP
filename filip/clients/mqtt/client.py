"""
Implementation of an extended MQTT client that automatically handles the
topic subscription for FIWARE's IoT communication pattern.

Created 21st Oct, 2021

@author: Thomas Storek
"""
import json
import logging
import paho.mqtt.client as mqtt
import warnings
import itertools
from datetime import datetime
from typing import Any, Callable, Dict, List, Literal, Tuple, Type, Union
from filip.clients.mqtt.encoder import BaseEncoder
from filip.models.ngsi_v2.iot import Device, ServiceGroup, TransportProtocol


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
        The client does not sync the device configuration with the IoT-Agent.
        This is up to the user!

    Note:
        The extension does not effect the normal workflow or any other
        functionality known from the original client.

        The client does not yet support the retrieval of command
        configurations via mqtt documented here:
        https://fiware-iotagent-json.readthedocs.io/en/latest/usermanual/index.html#api-overview

    Example:
        This example shows the basic usage of the client. It does not
        demonstrate its whole capabilities. Please check the single methods
        for more details. Please also keep in mind that this still requires
        provisioning of the device in the IoT-Agent and sending the commands
        via the context broker. For more details check the additional example
        section::

            from filip.models.ngsi_v2.iot import Device, DeviceAttribute, DeviceCommand, ServiceGroup
            from filip.clients.mqtt import MQTTClient
            from filip.clients.mqtt.encoder import IoTA_Json

            # create a device configuration
            device_attr = DeviceAttribute(name='temperature',
                                          object_id='t',
                                          type="Number")
            device_command = DeviceCommand(name='heater', type="Boolean")
            device = Device(device_id='MyDevice',
                            entity_name='MyDevice',
                            entity_type='Thing',
                            protocol='IoTA-JSON',
                            transport='MQTT',
                            apikey=YourApiKey,
                            attributes=[device_attr],
                            commands=[device_command])

            service_group = ServiceGroup(apikey="YourApiKey", resource="/iot")

            mqttc = MQTTClient(client_id="YourID",
                               userdata=None,
                               protocol=mqtt.MQTTv5,
                               transport="tcp",
                               devices = [device],
                               service_groups = [service_group],
                               encoder = IoTA_Json)

            # create a callback function that will be called for incoming
            # commands and add it for a single device
            def on_command(client, obj, msg):
                apikey, device_id, payload = client.encoder.decode_message(msg=msg)

                # do_something with the message. For instance write into a queue.

                # acknowledge a command
                client.publish(device_id=device_id,
                               command_name=next(payload.keys())
                               payload=payload)

            mqttc.add_command_callback(on_command)

            # create a non blocking loop
            mqttc.loop_start()

            # publish a multi-measurement for a device
            mqttc.publish(device_id='MyDevice', payload={'t': 50})

            # publish a single measurement for a device
            mqttc.publish(device_id='MyDevice',
                          attribute_name='temperature',
                          payload=50)

            # adding timestamps to measurements using the client


            # adding timestamps to measurements in payload
            from datetime import datetime

            mqttc.publish(device_id='MyDevice',
                          payload={'t': 50,
                                   'timeInstant': datetime.now().astimezone().isoformat()},
                          timestamp=true)

            # stop network loop and disconnect cleanly
            mqttc.loop_stop()
            mqttc.disconnect()


    """
    def __init__(self,
                 client_id="",
                 clean_session=None,
                 userdata=None,
                 protocol=mqtt.MQTTv311,
                 transport="tcp",
                 devices: List[Device] = None,
                 service_groups: List[ServiceGroup] = None,
                 encoder: Type[BaseEncoder] = None):
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
        """
        # initialize parent client
        super().__init__(client_id=client_id,
                         clean_session=clean_session,
                         userdata=userdata,
                         protocol=protocol,
                         transport=transport)

        # setup logging functionality
        self.logger = logging.getLogger(
            name=f"{self.__class__.__module__}."
                 f"{self.__class__.__name__}")
        self.logger.addHandler(logging.NullHandler())
        self.enable_logger(self.logger)

        # create dictionary holding the registered device configurations
        # check if all devices have the right transport protocol
        self.devices: Dict[str, Device]
        if devices:
            for device in devices:
                if device.transport == TransportProtocol.MQTT:
                    self.devices[device.device_id] = device
                else:
                    raise ValueError(f"Unsupported transport protocol found "
                                     f"in device confguration!")
        else:
            self.devices = {}

        # create dictionary holding the registered service groups
        self.service_groups: Dict[Tuple[str, str], ServiceGroup]
        if service_groups:
            self.service_groups = {gr.apikey: gr for gr in service_groups}
        else:
            self.service_groups = {}

        # add encoder for message parsing
        if encoder:
            self.encoder: BaseEncoder = encoder()
        else:
            self.encoder: BaseEncoder = BaseEncoder()


    def __create_topic(self, *,
                       topic_type: Literal['attrs',
                                           'cmd',
                                           'cmdexe',
                                           'configuration'],
                       device: Device,
                       attribute: str = None) -> str:
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
                'configuration' for topic the device can request command
                    configurations on
        Returns:
            string with topic
        """
        if topic_type == 'attrs':
            if attribute:
                attr = next(attr for attr in device.attributes
                            if attr.name == attribute)
                if attr.object_id:
                    attr_suffix = attr.object_id
                else:
                    attr_suffix = attr.name
                topic = '/'.join((self.encoder.prefix,
                                  device.apikey,
                                  device.device_id,
                                  'attrs',
                                  attr_suffix))
            else:
                topic = '/'.join((self.encoder.prefix,
                                  device.apikey,
                                  device.device_id,
                                  'attrs'))
        elif topic_type == 'cmd':
            topic = '/' + '/'.join((device.apikey, device.device_id, 'cmd'))
        elif topic_type == 'cmdexe':
            topic = '/'.join((self.encoder.prefix,
                              device.apikey,
                              device.device_id, 'cmd'))
        elif topic_type == 'configuration':
            topic = '/'.join((self.encoder.prefix,
                              device.apikey,
                              device.device_id, 'configuration'))
        else:
            raise KeyError
        return topic

    def __subscribe_commands(self, *,
                             device: Device = None,
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
        if Device:
            if len(device.commands) > 0:
                if device.apikey in self.service_groups.keys():
                    pass
                # check if matching service group is registered
                else:
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

    def get_service_group(self, apikey: str) -> ServiceGroup:
        """
        Returns registered service group configuration

        Args:
            apikey: Unique APIKey of the service group

        Returns:
            ServiceGroup

        Raises:
            KeyError: if service group not yet registered

        Example::

            from filip.clients.mqtt import MQTTClient

            mqttc = MQTTClient()
            group = mqttc.get_service_group(apikey="MyAPIKEY")
            print(group.json(indent=2))
            print(type(group))
        """
        group = self.service_groups.get(apikey, None)
        if group is None:
            raise KeyError("Service group with apikey %s not found!", apikey)
        return group

    def add_service_group(self, service_group: Union[ServiceGroup, Dict]):
        """
        Registers a device service group with the client

        Args:
            service_group: Service group configuration

        Returns:
            None

        Raises:
            ValueError: if service group already exists
        """
        if isinstance(service_group, dict):
            service_group = ServiceGroup.parse_obj(service_group)
        assert isinstance(service_group, ServiceGroup), \
            "Invalid content for service group!"

        if self.service_groups.get(service_group.apikey, None) is None:
            pass
        else:
            raise ValueError("Service group already exists! %s",
                             service_group.apikey)
        # add service group configuration to the service group list
        self.service_groups[service_group.apikey] = service_group

    def delete_service_group(self, apikey):
        """
        Unregisters a service group and removes
        Args:
            apikey: Unique APIKey of the service group
        Returns:
            None
        """
        group = self.service_groups.pop(apikey, None)
        if group:
            self.logger.info("Successfully unregistered Service Group '%s'!",
                             apikey)
        else:
            self.logger.error("Could not unregister service group '%s'!",
                              apikey)

    def update_service_group(self, service_group: Union[ServiceGroup, Dict]):
        """
        Updates a registered service group configuration. There is no
        opportunity to only partially update the device. Hence, your service
        group model should be complete.

        Args:
            service_group: Service group configuration

        Returns:
            None

        Raises:
            KeyError: if service group not yet registered
        """
        if isinstance(service_group, dict):
            service_group = ServiceGroup.parse_obj(service_group)
        assert isinstance(service_group, Device), "Invalid content for " \
                                                  "service group"

        if self.service_groups.get(service_group.apikey, None) is None:
            raise KeyError("Service group not found! %s",
                             service_group.apikey)
        # add service group configuration to the service group list
        self.service_groups[service_group.apikey] = service_group

    def get_device(self, device_id: str) -> Device:
        """
        Returns the configuration of a registered device.

        Args:
            device_id: Id of the requested device

        Returns:
           Device: Device model of the requested device

        Raises:
            KeyError: if requested device is not registered with the client

        Example::

            from filip.clients.mqtt import MQTTClient

            mqttc = MQTTClient()
            device = mqttc.get_device(device_id="MyDeviceId")
            print(device.json(indent=2))
            print(type(device))
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

        Raises:
            ValueError: if device configuration already exists
        """
        if isinstance(device, dict):
            device = Device.parse_obj(device)
        assert isinstance(device, Device), "Invalid content for device"

        if self.devices.get(device.device_id, None) is None:
            pass
        else:
            raise ValueError("Device already exists! %s", device.device_id)
        # add device configuration to the device list
        self.devices[device.device_id] = device
        # subscribes to the command topic
        self.__subscribe_commands(device=device,
                                  qos=qos,
                                  options=options,
                                  properties=properties)

    def delete_device(self, device_id: str):
        """
        Unregisters a device and removes its subscriptions and callbacks
        Args:
            device_id: id of and IoT device

        Returns:
            None
        """
        device = self.devices.pop(device_id, None)
        if device:
            topic = self.__create_topic(device=device,
                                        topic_type='cmd')
            self.unsubscribe(topic=topic)
            self.message_callback_remove(sub=topic)
            self.logger.info("Successfully unregistered Device '%s'!", device_id)
        else:
            self.logger.error("Could not unregister device '%s'", device_id)

    def update_device(self,
                      device: Union[Device, Dict],
                      qos=0,
                      options=None,
                      properties=None):
        """
        Updates a registered device configuration. There is no opportunity
        to only partially update the device. Hence, your device model should
        be complete.

        Args:
            device: Configuration of an IoT device
            qos: Quality of service can be 0, 1 or 2
            options: MQTT v5.0 subscribe options
            properties: MQTT v5.0 properties

        Returns:
            None

        Raises:
            KeyError: if device not yet registered
        """
        if isinstance(device, dict):
            device = Device.parse_obj(device)
        assert isinstance(device, Device), "Invalid content for device"

        if self.devices.get(device.device_id, None) is None:
            raise KeyError("Device not found! %s", device.device_id)

        # update device configuration in the device list
        self.devices[device.device_id] = device
        # subscribes to the command topic
        self.__subscribe_commands(device=device,
                                  qos=qos,
                                  options=options,
                                  properties=properties)


    def add_command_callback(self, device_id: str, callback: Callable):
        """
        Adds callback function for a device configuration.

        Args:
            device_id:
                id of and IoT device
            callback:
                function that will be called for incoming commands.
                This function should have the following format:

        Example::

            def on_command(client, obj, msg):
                apikey, device_id, payload = client.encoder.decode_message(msg=msg)

                # do_something with the message. For instance write into a queue.

                # acknowledge a command. Here command are usually single
                # messages. The first key is equal to the commands name.
                client.publish(device_id=device_id,
                               command_name=next(payload.keys())
                               payload=payload)

            mqttc.add_command_callback(device_id="MyDevice",
                                       callback=on_command)

        Returns:
            None
        """
        device = self.devices.get(device_id, None)
        if device is None:
            raise KeyError("Device does not exist! %s", device_id)
        self.__subscribe_commands(device=device)
        topic = self.__create_topic(device=device,
                                    topic_type='cmd')
        self.message_callback_add(topic, callback)

    def publish(self,
                topic = None,
                payload: Union[Dict, Any] = None,
                qos: int=0,
                retain: bool=False,
                properties=None,
                device_id: str = None,
                attribute_name: str = None,
                command_name: str = None,
                timestamp: bool = False
                ):
        """
        Publish an MQTT Message to a specified topic. If you want to publish
        a device specific message to a device use the device_id argument for
        multi-measurement. The function will then automatically validate
        against the registered device configuration if the payload keys are
        valid. If you want to publish a single measurement the attribute_name
        argument is required as well.

        Note:
            If the device_id argument is set, the topic argument will be
            ignored.

        Args:
            topic:
                The topic that the message should be published on.
            payload:
                The actual message to send. If not given, or set to None a
                zero length message will be used. Passing an int or float will
                result in the payload being converted to a string
                representing that number. If you wish to send a true
                int/float, use struct.pack() to create the
                payload you require. For publishing to a device use a dict
                containing the object_ids as keys.
            qos:
                The quality of service level to use.
            retain:
                If set to true, the message will be set as the "last known
                good"/retained message for the topic.
            properties:
                (MQTT v5.0 only) the MQTT v5.0 properties to be included.
                Use the Properties class.
            device_id:
                Id of the IoT device you want to publish for. The topics will
                automatically created. If set, the message type will be
                assumed to be multi measurement.
            attribute_name:
                Name of an attribute of the device. Do only use this for
                single measurements. If set, `command_name` must
                be omitted.
            command_name:
                Name of a command of the device that should be acknowledged. If
                set `attribute_name` must be omitted.
            timestamp:
                If `true` the client will generate a valid timestamp based on
                its current system time and added to the multi measurement
                payload. If a `timeInstant` is already contained in the
                message payload.

        Returns:
            None

        Raises:
            KeyError: if device configuration is not registered with client
            ValueError: if the passed arguments are inconsistent or a
                timestamp does not match the ISO 8601 format.
            AssertionError: if the message payload does not match the device
                configuration.
        """
        if device_id:
            device = self.get_device(device_id=device_id)

            # create message for multi measurement payload
            if attribute_name is None and command_name is None:
                assert isinstance(payload, Dict), "Payload must be " \
                                                  "dictionary"
                if timestamp:
                    payload["timeInstant"] = \
                        datetime.now().astimezone().isoformat()

                # validate if dict keys match device configuration
                for key, attr in itertools.product(payload.keys(),
                                                   device.attributes):
                    if key in attr.object_id:
                           pass
                    elif key == attr.name:
                        if attr.object_id:
                            payload[attr.object_id] = payload.pop(key)
                    elif key == 'timeInstant':
                            payload["timeInstant"] = \
                                datetime.fromisoformat(payload["timeInstant"])
                    else:
                        raise KeyError("Attribute key is not allowed for "
                                       "this device")

            # create message for command acknowledgement
            elif attribute_name is None and command_name:
                assert isinstance(payload, Dict), "Payload must be a dictionary"
                assert len(payload.keys()) == 1, \
                        "Cannot acknowledge multiple commands simultaneously"
                assert next(iter(payload.keys())) in \
                       [cmd.name for cmd in device.commands], \
                    "Unknown command for this device!"
                topic = self.__create_topic(device=device, topic_type='cmdexe')
                payload = self.encoder.encode_msg(payload=payload,
                                                  msg_type='cmdexe')

            # create message for single measurement
            elif attribute_name and command_name is None:
                topic = self.__create_topic(device=device,
                                            topic_type='attrs',
                                            attribute=attribute_name)
                payload = self.encoder.encode_msg(payload=payload,
                                                  msg_type='single')
            else:
                raise ValueError("Inconsistent arguments!")

        super().publish(topic=topic,
                        payload=payload,
                        qos=qos,
                        retain=retain,
                        properties=properties)

    def subscribe(self, topic=None, qos=0, options=None, properties=None):
        """
        Extends the normal subscribe function of the paho.mqtt.client.
        If the topic argument is omitted the client will subscribe to all
        registered device command topics.

        Args:
            topic:
                A string specifying the subscription topic to subscribe to.
            qos:
                The desired quality of service level for the subscription.
                Defaults to 0.
            options: Not used.
            properties: Not used.

        Returns:
            None
        """
        if topic:
            super().subscribe(topic=topic,
                              qos=qos,
                              options=options,
                              properties=properties)
        else:
            for device in self.devices:
                self.__subscribe_commands(device=device,
                                          qos=qos,
                                          options=options,
                                          properties=properties)
