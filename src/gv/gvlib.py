# Copyright (c) 2015, GreenVulcano Open Source Project. All rights reserved.
#
# This file is part of the GreenVulcano Communication Library for IoT.
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this software. If not, see <http://www.gnu.org/licenses/>.


"""
GreenVulcano Communication Library
Main Library Module

@author: Domenico Barra
@contact: eisenach@gmail.com
@license: LGPL v.3
@change: 2015-07-24 - First version
"""

import abc
from . import mixins

######################################################################
#
######################################################################
class DeviceInfo(object):
    """Holds the info about a specific device (i.e. the piece of hardware
    on which this software is running).
    """
    def __init__(self, id_: str, name: str, ip: str, port: int):
        self.__id = id_
        self.__name = name
        self.__ip = ip
        self.__port = port
    
    @property
    def id(self):
        """The unique ID of the device."""
        return self.__id
    
    @property
    def name(self):
        """The name (better if human-readable) of the device."""
        return self.__name
    
    @property
    def ip(self):
        """The IP address of the device."""
        return self.__ip
    
    @property
    def port(self):
        """The port on which this device wishes to be contacted back."""
        return self.__port


class Callback(object):
    """(Sort of) Prototype for callback functions from the IoT network.
    This is mainly used for type hinting - Python 3.5 is not (yet) widespread
    at the time of writing, so the `typing` module is not available.
    This can easily be replaced by `Callable[[str,bytearray], bytearray]` when
    `typing` becomes available."""
    def __call__(self, topic: str, payload: bytearray) -> bytearray:
        pass


class Transport(object): pass # forward declaration for type hinting in TransportListener


class TransportListener(object):
    """Class to respond to transport events.
    All methods are default-implemented to do nothing.
    If any class wishes to respond to transport events, all it has to do
    is inherit from `TransportListener` and override the relevant methods.
    """

    class Info(object):
        """Carries information about a transport event.
        The only field that will always be expected to be set is `transport`.
        """

        def __init__(self, transport: Transport,
                     topic: str = None, failure_reason: Exception = None):
            """Constructs a new Info object.
            Parameters:
                transport  : the transport that generated the event
                topic (opt): the topic to which the event refers
                failure_reason (opt): only present when the event being
                             processed represents a failure. It carries
                             an `Exception` object.
            """
            self.transport = transport
            self.topic = topic
            self.failure_reason = failure_reason

    def _after_connect(self, info: Info):
        """Called after a successful connection.
        Fields valued in the info object: transport
        """
        pass

    def _after_connection_unsuccessful(self, info: Info):
        """Called after an unsuccessful connection.
        Fields valued in the info object: transport, failure_reason
        """
        pass

    def _before_disconnect(self, info: Info):
        """Called before the transport initiates disconnection.
        Fields valued in the info object: transport
        """
        pass

    def _after_connection_lost(self, info: Info):
        """Called after transport detects lost connection
        Fields valued in the info object: transport, failure_reason
        """
        pass

    def _after_subscribe(self, info: Info):
        """Called after the transport has successfully subscribed to a topic
        Fields valued in the info object: transport, topic
        """
        pass

    def _before_unsubscribe(self, info: Info):
        """Called before the transport unsubscribes from a topic
        Fields valued in the info object: transport, topic
        """
        pass


class Transport(metaclass=abc.ABCMeta):
    """
    Abstract base class for transport implementation.
    """
    class TransportException(Exception):
        ERRORS = {
            "NOT_IMPLEMENTED":
                (-1, 'The requested method is not implemented')}

        """
        Raised by methods of `Transport` when they cannot do their job
        """
        def __init__(self, code: int, reason: str, lookup: str = None):
            
            if lookup:
                code, reason = self.ERRORS[lookup]
            
            Exception.__init__(self, code, reason)
            self.code = code
            self.reason = reason
            
    def __init__(self):
        self.__callbacks = {}
        self.__listeners = set()

    def connect(self):
        try:
            self._handle_connect()
        except Exception as exc:
            self._invoke_listeners(TransportListener._after_connection_unsuccessful,
                                   TransportListener.Info(self, failure_reason=exc))

    def subscribe(self, topic: str, callback: Callback):
        if topic not in self.__callbacks:
            self.__callbacks[topic] = set()
        self.__callbacks[topic].add(callback)
        self._handle_subscription(topic, callback)
        self._invoke_listeners(TransportListener._after_subscribe,
                               TransportListener.Info(self, topic=topic))

    def shutdown(self):
        self._invoke_listeners(TransportListener._before_disconnect,
                               TransportListener.Info(self))
        self._handle_shutdown()

    def callback(self, topic: str, payload: bytearray):
        s = self.__callbacks.get(topic) or self.__EMPTY_SET
        for cb in s:
            payload = cb(payload)

    def add_listener(self, listener: TransportListener):
        self.__listeners.add(listener)

    def remove_listener(self, listener: TransportListener):
        self.__listeners.remove(listener)

    def _invoke_listeners(self, listener_method, info: TransportListener.Info):
        for lst in self.__listeners:
            listener_method(lst, info)

    @abc.abstractclassmethod
    def send(self, service: str, payload: bytearray,
             qos: int = 0, retain: bool = False):
        raise self.TransportException(lookup="NOT_IMPLEMENTED")
    
    @abc.abstractclassmethod
    def poll(self):
        raise self.TransportException(lookup="NOT_IMPLEMENTED")

    @abc.abstractclassmethod
    def _handle_connect(self):
        pass  # no need to complain, just skip

    @abc.abstractclassmethod
    def _handle_shutdown(self):
        pass  # no need to complain, just skip
    
    @abc.abstractclassmethod
    def _handle_subscription(self, topic: str, callback: Callback):
        raise self.TransportException(lookup="NOT_IMPLEMENTED")

    __EMPTY_SET = set()


class Protocol(metaclass=abc.ABCMeta):
    """Base class for protocol implementations.
    """

    def __init__(self, transport: Transport):
        self._transport = transport
        
    @abc.abstractclassmethod
    def add_device(self): pass
    
    @abc.abstractclassmethod
    def add_sensor(self, id_: str, name: str, type_: str): pass
    
    @abc.abstractclassmethod
    def add_actuator(self, id_: str, name: str, type_: str): pass
    
    @abc.abstractclassmethod
    def send_data(self, id_: str, value: str,
                  qos: int = 0, retain: bool = False): pass


class GVComm(mixins._DeviceInfo):
    """Main entry point for the GreenVulcano Communication Library for IoT.
    This class is designed to act as a simple Façade: it merely delegates
    the requested actions to the transport and protocol passed to its
    constructor. This gives you a single object to interact with for
    most practical purposes.
    """

    def __init__(self, device_info: DeviceInfo,
                 transport: Transport, protocol: Protocol):
        """Constructor"""
        mixins._DeviceInfo.__init__(self, device_info)
        self.__transport = transport
        self.__protocol= protocol

    def add_device(self, callback: Callback = None):
        """Registers the current device to the IoT network.
        :param callback: the function to be called when receiving system-level
                         communications directed to the current device
                         (e.g. sleep, wake up, ...)
        """
        self.__protocol.add_device()
        if callback:
            topic = self.__protocol.SERVICES["devices_input"] % {'device_id': self.device_info.id}
            self.add_callback(topic, callback)

    def send_status(self, status: str):
        """Sends the status of the current device to the IoT network.
        :param status: the status to send. May be a bool for online-offline
                       or a string representing a custom status (e.g. "DEMO")
        """
        self.__protocol.send_status(status)

    def add_sensor(self, id_: str, name: str, type_: str):
        """Registers a new sensing capability for this device.
        :param id_: the id of the sensor
        :param name: the (human-readable) name of the sensor
        :param type_: The type of the sensor
        """
        self.__protocol.add_sensor(id_, name, type_)

    def add_actuator(self, id_: str, name: str, type_: str, callback: Callback):
        """Registers a new actuator for this device.
        :param id_: the id of the actuator
        :param name: the (human-readable) name of the actuator
        :param type_: the type of the actuator
        :param callback: the function to call in order to receive
                         commands for the actuator
        """
        topic = self.__protocol.SERVICES["actuators_input"] % {'device_id': self.device_info.id, 'actuator_id': id_}
        self.__protocol.add_actuator(id_, name, type_)
        self.add_callback(topic, callback)

    def send_data(self, id_: str, value: str, qos=0, retain=False):
        """
        :param id_: the id of the sensor
        :param value: the value of the reading
        :param qos: quality of service for the delivery of the message:
                    0 = at most once
                    1 = at least once
                    2 = exactly once
        :param retain: `True` if the message must be retained
                       for durable subscribers, `False` otherwise
        """
        self.__protocol.send_data(id_, value, qos, retain)

    def add_callback(self, topic, cb: Callback):
        """Registers a callback for data received on a topic.
        :param topic: the topic through which data are expected
        :param cb: the function to call when data are received
        """
        self.__transport.subscribe(topic, cb)

    def poll(self):
        """Fetches new data from the IoT network.
        Only needed for non-reactive transports (e.g. REST over simple
        HTTP(S)),
        """
        self.__transport.poll()

    def connect(self):
        """Connects to the IoT network."""
        self.__transport.connect()

    def shutdown(self):
        """Disconnects from the IoT network."""
        self.__transport.shutdown()
