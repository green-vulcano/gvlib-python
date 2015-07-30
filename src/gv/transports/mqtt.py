'''
GreenVulcano Communication Library

@summary: MQTT Transport Implementation
@organization: GreenVulcano Technologies
@license: GPL v.3
@copyright: 2015, GreenVulcano Technologies
@author: Domenico Barra
@contact: eisenach@gmail.com

@change: 2015-07-24 - First version
'''

from ..gvlib import Transport
from ..mixins import _ServerAndPort, _DeviceInfo

import mosquitto


#TODO - implement
class MqttTransport(Transport, _DeviceInfo, _ServerAndPort):
    def __init__(self, device_info, server, port, credentials=None):
        _DeviceInfo.__init__(self, device_info)
        _ServerAndPort.__init__(self, server, port)
        if credentials:
            pass 
    
    def send(self, service, payload):
        Transport.send(self, service, payload)
    
    def poll(self):
        Transport.poll(self)
    
