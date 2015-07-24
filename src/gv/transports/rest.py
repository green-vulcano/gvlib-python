'''
Created on Jul 24, 2015

@author: Domenico Barra <eisenach@gmail.com>
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
        return resp['status']

    def poll(self):
        return Transport.poll(self)

        
    
