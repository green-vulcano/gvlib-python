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

'''
GreenVulcano Communication Library
Main Library Module

@author: Domenico Barra
@contact: eisenach@gmail.com
@license: LGPL v.3
@change: 2015-07-24 - First version
'''

import abc
from . import mixins

######################################################################
#
######################################################################
class DeviceInfo(object):
    '''
    Holds the info about a specific device (i.e. the piece of hardware
    on which this software is running).
    '''
    def __init__(self, id_, name, ip, port):
        self.__id = id_
        self.__name = name
        self.__ip = ip
        self.__port = port
    
    @property
    def id(self):
        '''The unique ID of the device.'''
        return self.__id
    
    @property
    def name(self):
        '''The name (better if human-readable) of the device.''' 
        return self.__name
    
    @property
    def ip(self):
        '''The IP address of the device.'''
        return self.__ip
    
    @property
    def port(self):
        '''The port on which this device wishes to be contacted back.'''
        return self.__port
        
######################################################################
#
######################################################################
class GVComm(mixins._DeviceInfo):
    '''
    Main entry point for the GreenVulcano Communication Library for IoT.
    This class is designed to act as a simple Façade: it merely delegates
    the requested actions to the transport and protocol passed to its
    constructor. This gives you a single object to interact with for
    most practical purposes.
    '''

    def __init__(self, device_info, transport, protocol):
        '''
        Constructor
        '''
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
        
    def shutdown(self):
        self.__transport.shutdown()

######################################################################
#
######################################################################
class Transport(metaclass=abc.ABCMeta):
    '''
    Abstract base class for transport implementation.
    '''
    class TransportException(Exception):
        ERRORS = { "NOT_IMPLEMENTED": 
                  (-1, 'The requested method is not implemented')}

        '''
        Raised by methods of `Transport` when they cannot do their job
        '''
        def __init__(self, code, reason, lookup=None):
            
            if lookup:
                code, reason = self.ERRORS[lookup]
            
            Exception.__init__(self, code, reason)
            self.code = code
            self.reason = reason
            
    def __init__(self):
        self.__callbacks = {}

    def subscribe(self, topic, callback):
        if topic not in self.__callbacks:
            self.__callbacks[topic] = set()
        self.__callbacks[topic].add(callback)
        self._handle_subscription(topic, callback)
    
    def callback(self, topic, payload):
        s = self.__callbacks.get(topic) or self.__EMPTY_SET
        for cb in s:
            payload = cb(payload)

    @abc.abstractclassmethod
    def send(self, service, payload, qos=0, retain=False):
        raise self.TransportException(lookup="NOT_IMPLEMENTED")
    
    @abc.abstractclassmethod
    def poll(self):
        raise self.TransportException(lookup="NOT_IMPLEMENTED")
    
    @abc.abstractclassmethod
    def shutdown(self):
        pass ### no need to complain, just skip
    
    @abc.abstractclassmethod
    def _handle_subscription(self, topic, callback):
        raise self.TransportException(lookup="NOT_IMPLEMENTED")

    __EMPTY_SET = set()

######################################################################
#
######################################################################
class Protocol(metaclass=abc.ABCMeta):
    def __init__(self, transport):
        self._transport = transport
        
    @abc.abstractclassmethod
    def add_device(self): pass
    
    @abc.abstractclassmethod
    def add_sensor(self, id_, name, type_): pass
    
    @abc.abstractclassmethod
    def add_actuator(self, id_, name, type_, topic): pass    
    
    @abc.abstractclassmethod
    def send_data(self, id_, value, qos=0, retain=False): pass
