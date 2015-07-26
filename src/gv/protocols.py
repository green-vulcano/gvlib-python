'''
GreenVulcano Communication Library

@summary: Implementation of GreenVulcano protocols
@organization: GreenVulcano Technologies
@license: GPL v.3
@copyright: 2015, GreenVulcano Technologies
@author: Domenico Barra
@contact: eisenach@gmail.com

@change: 2015-07-24 - First version
'''


from .gvlib import Protocol
from .mixins import _DeviceInfo


class GVProtocol_v1(Protocol, _DeviceInfo):
    '''
    Version 1 of the GreenVulcano Protocol for IoT communication
    '''
    
    SERVICES = {
        'devices'  : '/devices',
        'sensors'  : '/devices/%(device_id)s/sensors',
        'actuators': '/devices/%(device_id)s/actuators',
        'data'     : '/devices/%(device_id)s/sensors/%(sensor_id)s/data',
        'status'   : '/status'
    }
    
    def __init__(self, transport, device_info):
        Protocol.__init__(self, transport)
        _DeviceInfo.__init__(self, device_info)
    
    def send_device_info(self):
        payload = '{"id": "%s", "nm": "%s", "ip": "%s", "prt": "%d"}' % (
                self.device_info.id, self.device_info.name,
                self.device_info.ip, self.device_info.port)
        self._transport.send(self.SERVICES['devices'], payload)


    def send_sensor_config(self, id_, name, type_):
        payload =  '{"id": "%d", "nm": "%s", "tp": "%s"}' % (id_, name, type_)
        self._transport.send( self.SERVICES['sensors'] % {
                    'device_id': self.device_info.id }, payload )

    def send_actuator_config(self, id_, name, type_, topic):
        payload =  '{"id": "%d", "nm": "%s", "tp": "%s", "to": "%s"}' % (
                    id_, name, type_)
        self._transport.send( self.SERVICES['actuators'] % {
                    'device_id': self.device_info.id }, payload )
    
    def send_sensor_data(self, id_, val):
        payload = '{"id": "%d", value: "%s"}' % (id_, str(val))
        self._transport.send( self.SERVICES['data'] % {
                    'device_id': self.device_info.id,
                    'sensor_id': id_ }, payload )
        
