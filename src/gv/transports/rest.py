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
Rest Transport Implementation

@author: Domenico Barra
@contact: eisenach@gmail.com
@license: LGPL v.3
@change: 2015-07-24 - First version
'''

from ..gvlib import Transport
from ..mixins import _ServerAndPort, _DeviceInfo

import httplib2

class RestTransport(Transport, _DeviceInfo, _ServerAndPort):
    def __init__(self, device_info, server, port,
                 credentials=None, use_https=False, timeout=None):
        Transport.__init__(self)
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
        
    def shutdown(self):
        Transport.shutdown(self) # no specific shutdown handling
        
    ### Polling and topic subscription is not (yet) supported via REST
    
    def poll(self):
        Transport.poll(self)
        
    def _handle_subscription(self, topic, callback):
        Transport._handle_subscription(self, topic, callback)
