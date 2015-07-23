'''
Created on Jul 21, 2015

@author: Domenico Barra <eisenach@gmail.com>
'''

import abc

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


        

class GVComm(object):
    '''
    Main entry point for GVLib.
    '''


    def __init__(self, device_info, transport):
        '''
        Constructor
        '''
        self.__device_info = device_info
        self.__transport = transport



class Transport(metaclass=abc.ABCMeta):
    '''
    Abstract base class for transport implementation.
    '''
    def __init__(self, device_info):
        self.__device_info = device_info
    
    @property
    def device_info(self): return self.__device_info


class _ServerAndPort(object):
    def __init__(self, server, port):
        self.__server = server
        self.__port = port;
        
    @property
    def server(self): return self.__server
    
    @property
    def port(self): return self.__port
    
    

class RestTransport(Transport, _ServerAndPort):
    def __init__(self, device_info, server, port):
        Transport.__init__(self, device_info)
        _ServerAndPort.__init__(self, server, port)
