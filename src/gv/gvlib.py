'''
Created on Jul 21, 2015

@author: Domenico Barra <eisenach@gmail.com>
'''


class DeviceInfo(object):
    '''
    Holds the info about a specific device (i.e. the board on which this
    software is running).
    '''
    def __init__(self, id, name, ip, port):
        self.__id = id
        self.__name = name
        self.__ip = ip
        self.__port = port


    def get_id(self):
        return self.__id


    def get_name(self):
        return self.__name


    def get_ip(self):
        return self.__ip


    def get_port(self):
        return self.__port

    __id = None
    __name = None
    __ip = None
    __port = None
    id = property(get_id, None, None, None)
    name = property(get_name, None, None, None)
    ip = property(get_ip, None, None, None)
    port = property(get_port, None, None, None)
    

        

class GVComm(object):
    '''
    classdocs
    '''


    def __init__(self, device_info, transport):
        '''
        Constructor
        '''
        self.__device_info = device_info
        self.__transport = transport
