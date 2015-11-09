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
from ..protocols import GVProtocol_v1

import paho.mqtt.client as mqtt

######################################################################
#
######################################################################
class MqttTransport(Transport, _DeviceInfo, _ServerAndPort):
    
    def __init__(self, device_info, server, port, clean_session=True, credentials=None, loop_wait_sec=0.1):
        self.__device_info = device_info
        self.__server = server
        self.__port = port
        self.__clean_session = clean_session
        self.__credentials = credentials
        self.__loop_wait_sec = loop_wait_sec
        
        Transport.__init__(self)
        _DeviceInfo.__init__(self, device_info)
        _ServerAndPort.__init__(self, server, port)
        
        client = mqtt.Client(device_info.id, clean_session)
        
        topic = GVProtocol_v1.SERVICES['status'] %{'device_id': device_info.id}
        payload = '{"st":false}'
        client.will_set(topic, payload, 1, True)
        
        if credentials:
            client.username_pw_set(credentials[0], credentials[1])
            
        client.on_message = self.__on_message
        client.on_connect = self.__on_connect
        client.connect(server, port, bind_address=device_info.ip)        
        
        self.__client = client      

    def send(self, service, payload, qos=0, retain=False):
        self.__client.publish(service, payload, qos, retain)
    
    def poll(self):
        self.__client.loop(self.__loop_wait_sec)
        
    def shutdown(self):
        self.__client.disconnect()
        
    def _handle_subscription(self, topic, callback):
        self.__client.subscribe(topic)
        
    def __on_connect(self, client, userdata, flags, rc):
        '''
        Called when the broker responds to our connection request.        
        client: the client instance for this callback
        userdata: the private user data as set in Client() or userdata_set()
        flags: response flags sent by the brokerConnected with result code "+str(rc)
        rc: the connection result
            0: Connection successful 
            1: Connection refused - incorrect protocol version 
            2: Connection refused - invalid client identifier 
            3: Connection refused - server unavailable 
            4: Connection refused - bad username or password 
            5: Connection refused - not authorised
        '''
        if rc == 0:
            topic = GVProtocol_v1.SERVICES['status'] %{'device_id': self.__device_info.id}
            payload = '{"st":true}'
            self.send(topic, payload, 1, True)
        else:
            print("Not connected. Cause: " + str(rc))

    def __on_message(self, client, userdata, msg):
        self.callback(msg.topic, msg.payload)