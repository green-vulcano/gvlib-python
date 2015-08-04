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
Implementation of mixins used across the library

@author: Domenico Barra
@contact: eisenach@gmail.com
@license: LGPL v.3
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
