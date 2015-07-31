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
        
    def _handle_subscription(self, topic, callback):
        self.__client.subscribe(topic)

    def __on_message(self, client, userdata, msg):
        self.callback(msg.topic, msg.payload)
    
