'''
GreenVulcano Communication Library

@summary: Implementation of mixins used across the library
@organization: GreenVulcano Technologies
@license: GPL v.3
@copyright: 2015, GreenVulcano Technologies
@author: Domenico Barra
@contact: eisenach@gmail.com

@change: 2015-07-24 - First version
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
