"""
Implementation of an extended MQTT client that automatically handles the
topic subscription for FIWARE's IoT communication pattern.
"""
import itertools
import logging
import warnings
from datetime import datetime
from typing import Any, Callable, Dict, List, Tuple, Union

import paho.mqtt.client as mqtt

from filip.clients.mqtt.encoder import BaseEncoder, Json, Ultralight
from filip.models.mqtt import IoTAMQTTMessageType
from filip.models.ngsi_v2.iot import \
    Device, \
    PayloadProtocol, \
    ServiceGroup, \
    TransportProtocol


class IoTAMQTTClient(mqtt.Client):
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
                               _devices = [device],
                               service_groups = [service_group])

            # create a callback function that will be called for incoming
            # commands and add it for a single device
            def on_command(client, obj, msg):
                apikey, device_id, payload = \
                    client.get_encoder().decode_message(msg=msg)

                # do_something with the message.
                # For instance write into a queue.

                # acknowledge a command
                client.publish(device_id=device_id,
                               command_name=next(iter(payload))
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
                 callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                 devices: List[Device] = None,
                 service_groups: List[ServiceGroup] = None,
                 custom_encoder: Dict[str, BaseEncoder] = None):
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
                _devices id.
            service_groups:
                List of service group configurations that will be registered
                with the client. These should be known upon subscribing
                because the client will check for a matching service group if
                this is not known or registered with the IoT-Agent service
                the receiving of commands will fail. Please check the
                official documentation of the IoT-Agents API for more details.
            custom_encoder:
                Custom encoder class that will automatically parse the supported
                payload formats to a dictionary and vice versa. This
                essentially saves boiler plate code.
        """
        # initialize parent client
        super().__init__(client_id=client_id,
                         clean_session=clean_session,
                         userdata=userdata,
                         protocol=protocol,
                         callback_api_version=callback_api_version,
                         transport=transport)

        # setup logging functionality
        self.logger = logging.getLogger(
            name=f"{self.__class__.__name__}")
        self.logger.addHandler(logging.NullHandler())
        self.enable_logger(self.logger)

        # create dictionary holding the registered service groups
        self.service_groups: Dict[Tuple[str, str], ServiceGroup]
        if service_groups:
            self.service_groups = {gr.apikey: gr for gr in service_groups}
        else:
            self.service_groups = {}

        # create dictionary holding the registered device configurations
        # check if all _devices have the right transport protocol
        self._devices: Dict[str, Device] = {}
        if devices:
            self.devices = devices

        # create dict with available encoders
        self._encoders = {'IoTA-JSON': Json(),
                          'PDI-IoTA-UltraLight': Ultralight()}

        # add custom encoder for message parsing
        if custom_encoder:
            self.add_encoder(custom_encoder)

    @property
    def devices(self):
        """
        Returns as list of all registered device configurations
        Returns:

        """
        return list(self._devices.values())

    @devices.setter
    def devices(self, devices: List[Device]):
        """
        Sets list of device configurations

        Args:
            devices: List of device configurations

        Returns:
            None

        Raises:
            ValueError: if duplicate device id was found
        """
        for device in devices:
            try:
                self.add_device(device=device)
            except ValueError:
                raise ValueError(f"Duplicate device_id: {device.device_id}")

    def get_encoder(self, encoder: Union[str, PayloadProtocol]):
        """
        Returns the encoder by key

        Args:
            encoder: encoder name

        Returns:
            Subclass of Baseencoder
        """
        return self._encoders.get(encoder)

    def add_encoder(self, encoder: Dict[str, BaseEncoder]):
        for value in encoder.values():
            assert isinstance(value, BaseEncoder), \
                f"Encoder must be a subclass of {type(BaseEncoder)}"

        self._encoders.update(encoder)

    def __validate_device(self, device: Union[Device, Dict]) -> Device:
        """
        Validates configuration of an IoT Device

        Args:
            device: device model to check on

        Returns:
            Device: validated model

        Raises:
            AssertionError: for faulty configurations
        """
        if isinstance(device, dict):
            device = Device.model_validate(device)

        assert isinstance(device, Device), "Invalid device configuration!"

        assert device.transport == TransportProtocol.MQTT, \
            "Unsupported transport protocol found in device configuration!"

        if device.apikey in self.service_groups.keys():
            pass
        # check if matching service group is registered
        else:
            msg = "Could not find matching service group! " \
                  "Communication may not work correctly!"
            self.logger.warning(msg=msg)
            warnings.warn(message=msg)

        return device

    def __create_topic(self,
                       *,
                       topic_type: IoTAMQTTMessageType,
                       device: Device,
                       attribute: str = None) -> str:
        """
        Creates a topic for a device configuration based on the requested
        topic type.

        Args:
            device:
                Configuration of an IoT device
            topic_type:
                type of the topic to be created,
                'multi' for topics that the device is suppose to publish on.
                'single' for topics that the device is suppose to publish on.
                'cmd' for topic the device is expecting its commands on.
                'cmdexe' for topic the device can acknowledge its commands on.
                'configuration' for topic the device can request command
                    configurations on
            attribute:
                attribute needs to be set for single measurements
        Returns:
            string with topic

        Raises:
            KeyError:
                If unknown message type is used
            ValueError:
                If attribute name is missing for single measurements
        """
        if topic_type == IoTAMQTTMessageType.MULTI:
            topic = '/'.join((self._encoders[device.protocol].prefix,
                              device.apikey,
                              device.device_id,
                              'attrs'))
        elif topic_type == IoTAMQTTMessageType.SINGLE:
            if attribute:
                attr = next(attr for attr in device.attributes
                            if attr.name == attribute)
                if attr.object_id:
                    attr_suffix = attr.object_id
                else:
                    attr_suffix = attr.name
                topic = '/'.join((self._encoders[device.protocol].prefix,
                                  device.apikey,
                                  device.device_id,
                                  'attrs',
                                  attr_suffix))
            else:
                raise ValueError("Missing argument name for single measurement")
        elif topic_type == IoTAMQTTMessageType.CMD:
            topic = '/' + '/'.join((device.apikey, device.device_id, 'cmd'))
        elif topic_type == IoTAMQTTMessageType.CMDEXE:
            topic = '/'.join((self._encoders[device.protocol].prefix,
                              device.apikey,
                              device.device_id,
                              'cmdexe'))
        elif topic_type == IoTAMQTTMessageType.CONFIG:
            topic = '/'.join((self._encoders[device.protocol].prefix,
                              device.apikey,
                              device.device_id,
                              'configuration'))
        else:
            raise KeyError("topic_type not supported")
        return topic

    def __subscribe_commands(self, *,
                             device: Device = None,
                             qos=0,
                             options=None,
                             properties=None):
        """
        Subscribes commands based on device configuration. If device argument is
        omitted the function will subscribe to all topics of already registered
        _devices.
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
                topic = self.__create_topic(device=device,
                                            topic_type=IoTAMQTTMessageType.CMD)
                super().subscribe(topic=topic,
                                  qos=qos,
                                  options=options,
                                  properties=properties)
        else:
            # call itself but with device argument for all registered _devices
            for device in self._devices.values():
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
            service_group = ServiceGroup.model_validate(service_group)
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
            raise KeyError("Device not found!")

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
            service_group = ServiceGroup.model_validate(service_group)
        assert isinstance(service_group, ServiceGroup), \
            "Invalid content for service group"

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
        return self._devices[device_id]

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
        device = self.__validate_device(device=device)

        if self._devices.get(device.device_id, None) is None:
            pass
        else:
            raise ValueError("Device already exists! %s", device.device_id)
        # add device configuration to the device list
        self._devices[device.device_id] = device
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
        device = self._devices.pop(device_id, None)
        if device:
            topic = self.__create_topic(device=device,
                                        topic_type=IoTAMQTTMessageType.CMD)
            self.unsubscribe(topic=topic)
            self.message_callback_remove(sub=topic)
            self.logger.info("Successfully unregistered Device '%s'!",
                             device_id)
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
        device = self.__validate_device(device=device)

        if self._devices.get(device.device_id, None) is None:
            raise KeyError("Device not found! %s", device.device_id)

        # update device configuration in the device list
        self._devices[device.device_id] = device
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
                apikey, device_id, payload = \
                    client.encoder.decode_message(msg=msg)

                # do_something with the message.
                # For instance write into a queue.

                # acknowledge a command. Here command are usually single
                # messages. The first key is equal to the commands name.
                client.publish(device_id=device_id,
                               command_name=next(iter(payload)),
                               payload=payload)

            mqttc.add_command_callback(device_id="MyDevice",
                                       callback=on_command)

        Returns:
            None
        """
        device = self._devices.get(device_id, None)
        if device is None:
            raise KeyError("Device does not exist! %s", device_id)
        self.__subscribe_commands(device=device)
        topic = self.__create_topic(device=device,
                                    topic_type=IoTAMQTTMessageType.CMD)
        self.message_callback_add(topic, callback)

    def publish(self,
                topic=None,
                payload: Union[Dict, Any] = None,
                qos: int = 0,
                retain: bool = False,
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
                utc and added to the multi measurement payload.
                If a `timeInstant` is already contained in the
                message payload it will not overwritten.

        Returns:
            None

        Raises:
            KeyError: if device configuration is not registered with client
            ValueError: if the passed arguments are inconsistent or a
                timestamp does not match the ISO 8601 format.
            AssertionError: if the message payload does not match the device
                configuration.
        """

        # TODO: time stamps are not tested yet

        if device_id:
            device = self.get_device(device_id=device_id)

            # create message for multi measurement payload
            if attribute_name is None and command_name is None:
                assert isinstance(payload, dict), \
                    "Payload must be a dictionary"

                if timestamp and 'timeInstant' not in payload.keys():
                    payload["timeInstant"] = datetime.utcnow()
                # validate if dict keys match device configuration

                msg_payload = payload.copy()
                for key in payload.keys():
                    for attr in device.attributes:
                        if key in attr.object_id or key == 'timeInstant':
                            break
                        elif key == attr.name:
                            if attr.object_id:
                                msg_payload[attr.object_id] = \
                                    msg_payload.pop(key)
                            break
                    else:
                        err_msg = f"Attribute key '{key}' is not allowed " \
                                  f"in the message payload for this " \
                                  f"device configuration with device_id " \
                                  f"'{device_id}'"
                        raise KeyError(err_msg)
                topic = self.__create_topic(
                    device=device,
                    topic_type=IoTAMQTTMessageType.MULTI)
                payload = self._encoders[device.protocol].encode_msg(
                    device_id=device_id,
                    payload=payload,
                    msg_type=IoTAMQTTMessageType.MULTI)

            # create message for command acknowledgement
            elif attribute_name is None and command_name:
                assert isinstance(payload, Dict), "Payload must be a dictionary"
                assert len(payload.keys()) == 1, \
                    "Cannot acknowledge multiple commands simultaneously"
                assert next(iter(payload.keys())) in \
                       [cmd.name for cmd in device.commands], \
                    "Unknown command for this device!"
                topic = self.__create_topic(
                    device=device,
                    topic_type=IoTAMQTTMessageType.CMDEXE)
                payload = self._encoders[device.protocol].encode_msg(
                    device_id=device_id,
                    payload=payload,
                    msg_type=IoTAMQTTMessageType.CMDEXE)

            # create message for single measurement
            elif attribute_name and command_name is None:
                topic = self.__create_topic(
                    device=device,
                    topic_type=IoTAMQTTMessageType.SINGLE,
                    attribute=attribute_name)
                payload = self._encoders[device.protocol].encode_msg(
                    device_id=device_id,
                    payload=payload,
                    msg_type=IoTAMQTTMessageType.SINGLE)
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
            for device in self._devices.values():
                self.__subscribe_commands(device=device,
                                          qos=qos,
                                          options=options,
                                          properties=properties)
