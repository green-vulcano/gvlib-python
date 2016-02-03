# gvlib-python
GreenVulcano Communication Library - Python version

## Requirements
This library is developed with a Python 3.x orientation. This means that
you can probably run it on Python 2.7, although we didn't run an
extensive test campaign to prove it.
The libraries on which the GreenVulcano Communication Library depends
are listed in the `requirements.txt` file.

## Setup
As for any Python-based installation, it's strongly suggested that you
set up your own, dedicated environment using `virtualenv`.
Once created, you can run `pip` to configure the environment in order
to meet the library requirements.
The most basic setup scenario would go like this.

```
eisenach@v-dev-kubu-1:~/tools/venv$ pyvenv myenv
eisenach@v-dev-kubu-1:~/tools/venv$ . myenv/bin/activate
(myenv) eisenach@v-dev-kubu-1:~/tools/venv$ pip install -r ~/git/gvlib-python/requirements.txt

    [... omissis ...]

(myenv) eisenach@v-dev-kubu-1:~/tools/venv$ 
```

As of writing, there is no "site" setup available for gvlib-python, but we
count on having it soon (volunteers welcome, it's a fairly simple task!)

## License
Copyright (c) 2015, GreenVulcano Open Source Project. All rights reserved.

The GreenVulcano Communication Library for IoT is free software: you can
redistribute it and/or modify it under the terms of the GNU Lesser General
Public License as published by the Free Software Foundation, either version 3
of the License, or (at your option) any later version.
This software is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License
for more details.
You should have received a copy of the GNU Lesser General Public License
along with this software. If not, see <http://www.gnu.org/licenses/>.

## Usage
The GreenVulcano Communication Library has been designed with simplicity in mind:
if you are looking for down-to-the-metal, finest-grained control on what you send
and receive, you are probably better off using the underlying protocols directly.

You may want to set up a simple client node as follows (note: parameters are always
specified as keywords for clarity, but you can use the positional convention):

```python
from gv import GVComm, DeviceInfo, DefaultProtocol
from gv.transports.mqtt import MqttTransport


def servo_fun(payload):
    value = int(payload)
    print("moving servo to", value)
    ### actually move the servo here!


me = DeviceInfo(id_="111", name="gv-raspi-111", ip="10.0.2.15", port=9999)
mqtt = MqttTransport(device_info=me, server="10.0.2.1", port=1883)
proto = DefaultProtocol(transport=mqtt, device_info=me)

comm = GVComm(device_info=me, transport=mqtt, protocol=proto)
comm.connect()

comm.add_device()
comm.add_sensor(id_="s1", name="temp-1", type_="temperature")
comm.add_actuator(id_="a1", name="servo-1", type_="servo", callback=servo_fun)

while True:
    comm.poll() ### this will call servo_fun if the server sends
                ### anything on topic '/test/topic/a1'
    val = read_temperature()
    if val > 100:
    	break
    comm.send_sensor_data(id_="s1", value=val)
    
    
comm.shutdown() ### propagates the command to all other objects
    
```