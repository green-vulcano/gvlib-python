'''
GreenVulcano Communication Library

@summary: Main Library Package
@organization: GreenVulcano Technologies
@license: GPL v.3
@copyright: 2015, GreenVulcano Technologies
@author: Domenico Barra
@contact: eisenach@gmail.com

@change: 2015-07-24 - First version
'''

from .gvlib import GVComm, DeviceInfo
from .protocols import GVProtocol_v1 as DefaultProtocol
from .transports.rest import RestTransport

