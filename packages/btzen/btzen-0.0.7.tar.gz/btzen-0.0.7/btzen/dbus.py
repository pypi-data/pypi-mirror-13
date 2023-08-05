#
# BTZen - Bluetooh Smart sensor reading library.
#
# Copyright (C) 2015 by Artur Wroblewski <wrobell@pld-linux.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
D-Bus support classes and functions.
"""

import dbus


class Proxy:
    """
    D-Bus object proxy to expose properties via simple attribute access.
    """
    def __init__(self, obj, iface):
        self._obj = obj
        self._iface = iface
        self._properties = dbus.Interface(obj, 'org.freedesktop.DBus.Properties')


    def __getattr__(self, name):
        return self._properties.Get(self._iface, name)
        

def get_device(bus, mac):
    bus_name = 'org.bluez'
    path = '/org/bluez/hci0/dev_{}'.format(mac.replace(':', '_'))
    proxy = bus.get_object(bus_name, path)
    device = dbus.Interface(proxy, dbus_interface='org.bluez.Device1')
    return Proxy(device, 'org.bluez.Device1')


def load_object(bus, path, iface):
    proxy = bus.get_object('org.bluez', path)
    return Proxy(dbus.Interface(proxy, iface), iface)


def load_objects(bus, paths, iface):
    return (load_object(bus, p, iface) for p in paths)


def get_services(bus, device):
    return load_objects(bus, device.GattServices, 'org.bluez.GattService1')


def get_characteristics(bus, service):
    return load_objects(bus, service.Characteristics, 'org.bluez.GattCharacteristic1')


def get_descriptors(bus, characteristics):
    return load_objects(bus, characteristics.Descriptors, 'org.bluez.GattDescriptor1')


def find_sensor(bus, device, uuid):
    items = (c for s in get_services(bus, device) for c in get_characteristics(bus, s))
    return next((c for c in items if c.UUID == uuid), None)


# vim: sw=4:et:ai
