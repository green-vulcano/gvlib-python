'''
Created on Jul 24, 2015

@author: Domenico Barra <eisenach@gmail.com>
'''

from ..gvlib import Transport
from ..mixins import _ServerAndPort

class RestTransport(Transport, _ServerAndPort):
    def __init__(self, device_info, server, port):
        _ServerAndPort.__init__(self, server, port)
