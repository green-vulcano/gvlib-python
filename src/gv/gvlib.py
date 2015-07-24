'''
Created on Jul 21, 2015

@author: Domenico Barra <eisenach@gmail.com>
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

    def __init__(self, device_info, transport):
        '''
        Constructor
        '''
        mixins._DeviceInfo.__init__(self, device_info)
        self.__transport = transport


class Transport(metaclass=abc.ABCMeta):
    '''
    Abstract base class for transport implementation.
    '''
    @abc.abstractclassmethod
    def send(self, service, payload): pass
    
    @abc.abstractclassmethod
    def poll(self): pass


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
