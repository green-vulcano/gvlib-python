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
    Subclasses of `Transport` can benefit from several "reasonable" default
    implementations, so that they only have to specify any specialized
    behavior in order to meet a specific transport convention.

    *** NOTE ***
    It is important that `Transport` implementation *do not* automatically
    connect upon construction. The reason for this is that objects constructed
    after the transport may want to register as listeners *before* the
    connection is attempted. Therefore, the only way to establish a connection
    should be (so far) to call the method `connect()`.
    """

    class TransportException(Exception):
        """Raised by methods of `Transport` when they cannot do their job."""
        ERRORS = {
            "NOT_IMPLEMENTED":
                (-1, 'The requested method is not implemented')}

        def __init__(self, code: int, reason: str, lookup: str = None):
            
            if lookup:
                code, reason = self.ERRORS[lookup]
            
            Exception.__init__(self, code, reason)
            self.code = code
            self.reason = reason

    def __init__(self):
        """Base class constructor."""
        self.__callbacks = {}
        self.__listeners = set()

    def connect(self):
        """Initiates a connection to the IoT network.
        This method delegates connection to the subclass' implementation
        of `_handle_connect()`, then invokes
        `TransportListener._after_connect(...)` or
        `TransportListener._after_connection_unsuccesful(...)` depending
        on the connection result."""
        try:
            self._handle_connect()
            self._invoke_listeners(TransportListener._after_connect,
                                   TransportListener.Info(self))
        except Exception as exc:
            self._invoke_listeners(TransportListener._after_connection_unsuccessful,
                                   TransportListener.Info(self, failure_reason=exc))

    def subscribe(self, topic: str, callback: Callback):
        """Subscribes to a topic with a specific callback function.
        This method delegates connection to the subclass' implementation
        of `_handle_subscription(...)`, then invokes
        `TransportListener._after_subscribe(...)` in case of success.
        :param topic: the topic to subscribe to
        :param callback: the function to call when data are received
               on the specified topic
        """
        if topic not in self.__callbacks:
            self.__callbacks[topic] = set()
        self.__callbacks[topic].add(callback)
        self._handle_subscription(topic, callback)
        self._invoke_listeners(TransportListener._after_subscribe,
                               TransportListener.Info(self, topic=topic))

    def shutdown(self):
        """Shuts down the connection to the IoT network.
        This method invokes `TransportListener._before_disconnect(...)`,
        then delegates to the subclass' implementation of
        `_handle_shutdown()`.
        """
        self._invoke_listeners(TransportListener._before_disconnect,
                               TransportListener.Info(self))
        self._handle_shutdown()

    def callback(self, topic: str, payload: bytearray):
        """Invokes the callbacks registered for a specific topic
        subscription with the provided data.
        :param topic: the topic for which to invoke callbacks
        :param payload: the data to pass to the callback chain
        """
        s = self.__callbacks.get(topic) or self.__EMPTY_SET
        for cb in s:
            payload = cb(payload)

    def add_listener(self, listener: TransportListener):
        """Registers a new `TransportListener` for this transport.
        Listeners can only be registered once for each transport
        (i.e. two calls to this method will not result in the
        listener being called twice).
        :param listener: the listener to register
        """
        self.__listeners.add(listener)

    def remove_listener(self, listener: TransportListener):
        """Unregisters a `TransportListener` for this transport.
        :param listener: the listener to unregister.
        """
        self.__listeners.remove(listener)

    def _invoke_listeners(self, listener_method, info: TransportListener.Info):
        """Convenience method to invoke a method on all transport listeners.
        :param listener_method: the method to invoke on all listeners
        :param info: the information object to pass to the listeners
        """
        for lst in self.__listeners:
            listener_method(lst, info)

    @abc.abstractclassmethod
    def send(self, service: str, payload: bytearray,
             qos: int = 0, retain: bool = False):
        """Sends data to a specific service.
        :param service: the service to invoke on the receiver's side
        :param payload: the data to send
        :param qos: quality of service for the delivery of the message:
                    0 = at most once
                    1 = at least once
                    2 = exactly once
        :param retain: `True` if the message must be retained
                       for durable subscribers, `False` otherwise
        """
        raise self.TransportException(lookup="NOT_IMPLEMENTED")
    
    @abc.abstractclassmethod
    def poll(self):
        """Fetches new data from the IoT network.
        If data are available, calls the appropriate callbacks
        (using the `Transport.callback(...)` method). Only needed
        for non-reactive transports (e.g. REST over simple HTTP(S)).
        """
        raise self.TransportException(lookup="NOT_IMPLEMENTED")

    @abc.abstractclassmethod
    def _handle_connect(self):
        """To be implemented by subclasses to handle specific details
         of the connection establishment for the given transport.
        """
        pass  # no need to complain, just skip

    @abc.abstractclassmethod
    def _handle_shutdown(self):
        """To be implemented by subclasses to handle specific details
         of the connection shutdown for the given transport.
        """
        pass  # no need to complain, just skip
    
    @abc.abstractclassmethod
    def _handle_subscription(self, topic: str, callback: Callback):
        """To be implemented by subclasses to handle the specific details
        of topic subscription for the given transport.
        :param topic: the topic to subscribe to
        :param callback: the callback to invoke when data are received for
                         the specified topic
        """
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
        If data are available, calls the appropriate callbacks.
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
