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
MQTT Transport Implementation

@author: Domenico Barra
@contact: eisenach@gmail.com
@license: LGPL v.3
@change: 2015-07-24 - First version
'''

from ..gvlib import Transport
from ..mixins import _ServerAndPort, _DeviceInfo

import paho.mqtt.client as mqtt


class MqttTransport(Transport, _DeviceInfo, _ServerAndPort):
    def __init__(self, device_info, server, port, clean_session=True, credentials=None, loop_wait_sec=0.1):
        Transport.__init__(self)
        _DeviceInfo.__init__(self, device_info)
        _ServerAndPort.__init__(self, server, port)
        self.__loop_wait_sec = loop_wait_sec
        client = mqtt.Client(device_info.id, clean_session)
        if credentials:
            client.username_pw_set(credentials[0], credentials[1])
        client.on_message = self.__on_message
        client.connect(server, port, bind_address=device_info.ip)
        self.__client = client
            
    
    def send(self, service, payload):
        self.__client.publish(service, payload)
    
    def poll(self):
        self.__client.loop(self.__loop_wait_sec)
        
    def shutdown(self):
        self.__client.disconnect()
        
    def _handle_subscription(self, topic, callback):
        self.__client.subscribe(topic)

    def __on_message(self, client, userdata, msg):
        self.callback(msg.topic, msg.payload)
    
