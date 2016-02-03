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
    """
    Holds the info about a specific device (i.e. the piece of hardware
    on which this software is running).
    """
    def __init__(self, id_, name, ip, port):
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
        
######################################################################
#
######################################################################
class GVComm(mixins._DeviceInfo):
    """
    Main entry point for the GreenVulcano Communication Library for IoT.
    This class is designed to act as a simple Façade: it merely delegates
    the requested actions to the transport and protocol passed to its
    constructor. This gives you a single object to interact with for
    most practical purposes.
    """

    def __init__(self, device_info, transport, protocol):
        """
        Constructor
        """
        mixins._DeviceInfo.__init__(self, device_info)
        self.__transport = transport
        self.__protocol= protocol
        
    def add_device(self, callback=None):
        self.__protocol.add_device()
        if callback:
            topic = self.__protocol.SERVICES["devices_input"] % {'device_id': self.device_info.id}
            self.add_callback(topic, callback)

    def send_status(self, status):
        self.__protocol.send_status(status)
    
    def add_sensor(self, id_, name, type_):
        self.__protocol.add_sensor(id_, name, type_)
    
    def add_actuator(self, id_, name, type_, callback):
        topic = self.__protocol.SERVICES["actuators_input"] % {'device_id': self.device_info.id, 'actuator_id': id_}
        self.__protocol.add_actuator(id_, name, type_)
        self.add_callback(topic, callback) 
    
    def send_data(self, id_, value, qos=0, retain=False):
        self.__protocol.send_data(id_, value, qos, retain)

    def add_callback(self, topic, cb):
        self.__transport.subscribe(topic, cb)
        
    def poll(self):
        self.__transport.poll()

    def connect(self):
        self.__transport.connect()

    def shutdown(self):
        self.__transport.shutdown()

######################################################################
#
######################################################################


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

        def __init__(self, transport, topic=None, failure_reason=None):
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

    def _after_connect(self, info):
        """Called after a successful connection.
        Fields valued in the info object: transport
        """
        pass

    def _after_connection_unsuccessful(self, info):
        """Called after an unsuccessful connection.
        Fields valued in the info object: transport, failure_reason
        """
        pass

    def _before_disconnect(self, info):
        """Called before the transport initiates disconnection.
        Fields valued in the info object: transport
        """
        pass

    def _after_connection_lost(self, info):
        """Called after transport detects lost connection
        Fields valued in the info object: transport, failure_reason
        """
        pass

    def _after_subscribe(self, info):
        """Called after the transport has successfully subscribed to a topic
        Fields valued in the info object: transport, topic
        """
        pass

    def _before_unsubscribe(self, info):
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
        def __init__(self, code, reason, lookup=None):
            
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
    def subscribe(self, topic, callback):
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

    def callback(self, topic, payload):
        s = self.__callbacks.get(topic) or self.__EMPTY_SET
        for cb in s:
            payload = cb(payload)

    def add_listener(self, listener):
        self.__listeners.add(listener)

    def remove_listener(self, listener):
        self.__listeners.remove(listener)

    def _invoke_listeners(self, listener_method, info):
        for lst in self.__listeners:
            listener_method(lst, info)

    @abc.abstractclassmethod
    def send(self, service, payload, qos=0, retain=False):
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
    def _handle_subscription(self, topic, callback):
        raise self.TransportException(lookup="NOT_IMPLEMENTED")

    __EMPTY_SET = set()


class Protocol(metaclass=abc.ABCMeta):
    """Base class for protocol implementations.
    """

    def __init__(self, transport):
        self._transport = transport
        
    @abc.abstractclassmethod
    def add_device(self): pass
    
    @abc.abstractclassmethod
    def add_sensor(self, id_, name, type_): pass
    
    @abc.abstractclassmethod
    def add_actuator(self, id_, name, type_): pass
    
    @abc.abstractclassmethod
    def send_data(self, id_, value, qos=0, retain=False): pass
