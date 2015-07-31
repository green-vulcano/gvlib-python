'''
GreenVulcano Communication Library

@summary: Main Library Module
@organization: GreenVulcano Technologies
@license: GPL v.3
@copyright: 2015, GreenVulcano Technologies
@author: Domenico Barra
@contact: eisenach@gmail.com

@change: 2015-07-24 - First version
'''


import abc

from . import mixins

class DeviceInfo(object):
    '''
    Holds the info about a specific device (i.e. the board on which this
    software is running).
    '''
    def __init__(self, id_, name, ip, port):
        self.__id = id_
        self.__name = name
        self.__ip = ip
        self.__port = port
    
    @property
    def id(self): return self.__id
    
    @property
    def name(self): return self.__name
    
    @property
    def ip(self): return self.__ip
    
    @property
    def port(self): return self.__port

        

class GVComm(mixins._DeviceInfo):
    '''
    Main entry point for GVLib.
    '''

    def __init__(self, device_info, transport, protocol):
        '''
        Constructor
        '''
        mixins._DeviceInfo.__init__(self, device_info)
        self.__transport = transport
        self.__protocol= protocol
 
    def send_device_info(self):
        self.__protocol.send_device_info()
    
    def send_sensor_config(self, id_, name, type_):
        self.__protocol.send_sensor_config(id_, name, type_)
    
    def send_actuator_config(self, id_, name, type_, topic, callback=None):
        self.__protocol.send_actuator_config(id_, name, type_, topic)
        if callback:
            self.add_callback(topic, callback) 
    
    def send_sensor_data(self, id_, value):
        self.__protocol.send_sensor_data(id_, value)

    def add_callback(self, topic, cb):
        self.__transport.subscribe(topic, cb)
        
    def poll(self):
        self.__transport.poll()
        
    def shutdown(self):
        pass




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
    def send(self, service, payload):
        raise self.TransportException(lookup="NOT_IMPLEMENTED")
    
    @abc.abstractclassmethod
    def poll(self):
        raise self.TransportException(lookup="NOT_IMPLEMENTED")
    
    @abc.abstractclassmethod
    def _handle_subscription(self, topic, callback):
        raise self.TransportException(lookup="NOT_IMPLEMENTED")

    __EMPTY_SET = set()



class Protocol(metaclass=abc.ABCMeta):
    def __init__(self, transport):
        self._transport = transport
        
    @abc.abstractclassmethod
    def send_device_info(self): pass
    
    @abc.abstractclassmethod
    def send_sensor_config(self, id_, name, type_): pass
    
    @abc.abstractclassmethod
    def send_actuator_config(self, id_, name, type_, topic): pass    
    
    @abc.abstractclassmethod
    def send_sensor_data(self, id_, value): pass
