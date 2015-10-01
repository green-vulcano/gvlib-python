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
Implementation of GreenVulcano protocols

@author: Domenico Barra
@contact: eisenach@gmail.com
@license: LGPL v.3
@change: 2015-07-24 - First version
'''


from .gvlib import Protocol
from .mixins import _DeviceInfo

######################################################################
#
######################################################################
class GVProtocol_v1(Protocol, _DeviceInfo):
    '''
    Version 1 of the GreenVulcano Protocol for IoT communication
    '''
        
    SERVICES = {
        'devices'  : '/devices/%(device_id)s',
        'devices_input'  : '/devices/%(device_id)s/input',
        'sensors'  : '/devices/%(device_id)s/sensors/%(sensor_id)s',
        'actuators': '/devices/%(device_id)s/actuators/%(actuator_id)s',
        'actuators_input': '/devices/%(device_id)s/actuators/%(actuator_id)s/input',
        'data'     : '/devices/%(device_id)s/sensors/%(sensor_id)s/output',
        'status'   : '/devices/%(device_id)s/status'
    }
    
    def __init__(self, transport, device_info):
        Protocol.__init__(self, transport)
        _DeviceInfo.__init__(self, device_info)
    
    def add_device(self):
        topic = self.SERVICES['devices'] %{'device_id': self.device_info.id}
        payload = '{"nm":"%s","ip":"%s","prt":"%d"}' % (self.device_info.name, self.device_info.ip, self.device_info.port)        
        self._transport.send(topic, payload)
        
    def send_status(self, status):
        payload =  '{"status": "%s"}' % (istatus)
        topic = self.SERVICES['status'] % {'device_id': self.device_info.id }
        self._transport.send(topic, payload)

    def add_sensor(self, id_, name, type_):
        topic = self.SERVICES['sensors'] % {'device_id': self.device_info.id, 'sensor_id': id_}
        payload =  '{"nm":"%s","tp":"%s"}' % (name, type_)
        self._transport.send(topic, payload)

    def add_actuator(self, id_, name, type_):
        topic = self.SERVICES['actuators'] % {'device_id': self.device_info.id, 'actuator_id': id_}
        payload =  '{"nm":"%s","tp":"%s"}' % (name, type_)
        self._transport.send(topic, payload)
    
    def send_data(self, id_, val):
        topic = self.SERVICES['data'] % {'device_id': self.device_info.id, 'sensor_id': id_}
        payload = '{value:"%s"}' % (str(val))
        self._transport.send(topic, payload)