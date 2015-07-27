'''
GreenVulcano Communication Library

@summary: Rest Transport Implementation
@organization: GreenVulcano Technologies
@license: GPL v.3
@copyright: 2015, GreenVulcano Technologies
@author: Domenico Barra
@contact: eisenach@gmail.com

@change: 2015-07-24 - First version
'''

from ..gvlib import Transport
from ..mixins import _ServerAndPort, _DeviceInfo

import httplib2

class RestTransport(Transport, _DeviceInfo, _ServerAndPort):
    def __init__(self, device_info, server, port,
                 credentials=None, use_https=False, timeout=None):
        _DeviceInfo.__init__(self, device_info)
        _ServerAndPort.__init__(self, server, port)
        self.__use_https = use_https
        self.__http = httplib2.Http(timeout=timeout)
        if credentials:
            self.__http.add_credentials(credentials[0], credentials[1])
    
    def send(self, service, payload):
        resp, cont = self.__http.request(
                "%s//%s:%d/%s" % (
                                "https" if self.__use_https else "http",
                                self.server, self.port, service),
                method="POST",
                body=payload,
                headers = {
                    "Content-Type" : "application/json; charset=utf-8",
                    "Host"         : self.device_info.ip,
                    "Connection"   : "close" ## TODO: CHANGE THIS!
                })
        if resp.status < 200 or resp.status > 299:
            raise self.TransportException(resp.status, resp.reason)
    
    def poll(self):
        Transport.poll(self)
    
