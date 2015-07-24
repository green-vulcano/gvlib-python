'''
Created on Jul 24, 2015

@author: Domenico Barra <eisenach@gmail.com>
'''


class _ServerAndPort(object):
    '''
    Mixin to add 'server' and 'port' properties.
    '''
    def __init__(self, server, port):
        self.__server = server
        self.__port = port;
            
    @property
    def server(self): return self.__server
        
    @property
    def port(self): return self.__port
    
    
    
class _DeviceInfo(object):
    '''
    Mixin to add the 'device_info' property.
    '''
    def __init__(self, device_info):
        self.__device_info = device_info
    
    @property
    def device_info(self):
        return self.__device_info
