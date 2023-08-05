# encoding: utf-8
#
# Handles devices reporting themselves as USB VID/PID 0C45:7401 (mine also says
# RDing TEMPerV1.2).
#
# Copyright 2012-2014 Philipp Adelt <info@philipp.adelt.net>
#
# This code is licensed under the GNU public license (GPL). See LICENSE.md for
# details.

import usb
import sys
import struct
import os
import re
import logging

VIDPIDS = [
    (0x0c45L, 0x7401L),
]
REQ_INT_LEN = 8
ENDPOINT = 0x82
INTERFACE = 1
CONFIG_NO = 1
TIMEOUT = 5000
USB_PORTS_STR = '^\s*(\d+)-(\d+(?:\.\d+)*)'
CALIB_LINE_STR = USB_PORTS_STR +\
    '\s*:\s*scale\s*=\s*([+|-]?\d*\.\d+)\s*,\s*offset\s*=\s*([+|-]?\d*\.\d+)'
USB_SYS_PREFIX = '/sys/bus/usb/devices/'
COMMANDS = {
    'temp': '\x01\x80\x33\x01\x00\x00\x00\x00',
    'ini1': '\x01\x82\x77\x01\x00\x00\x00\x00',
    'ini2': '\x01\x86\xff\x01\x00\x00\x00\x00',
}
LOGGER = logging.getLogger(__name__)


def readattr(path, name):
    """
    Read attribute from sysfs and return as string
    """
    try:
        f = open(USB_SYS_PREFIX + path + "/" + name)
        return f.readline().rstrip("\n")
    except IOError:
        return None


def find_ports(device):
    """
    Find the port chain a device is plugged on.

    This is done by searching sysfs for a device that matches the device
    bus/address combination.

    Useful when the underlying usb lib does not return device.port_number for
    whatever reason.
    """
    bus_id = device.bus
    dev_id = device.address
    for dirent in os.listdir(USB_SYS_PREFIX):
        matches = re.match(USB_PORTS_STR + '$', dirent)
        if matches:
            bus_str = readattr(dirent, 'busnum')
            if bus_str:
                busnum = float(bus_str)
            else:
                busnum = None
            dev_str = readattr(dirent, 'devnum')
            if dev_str:
                devnum = float(dev_str)
            else:
                devnum = None
            if busnum == bus_id and devnum == dev_id:
                return str(matches.groups()[1])


class TemperDevice(object):
    """
    A TEMPer USB thermometer.
    """
    def __init__(self, device, sensor_count=1):
        self.set_sensor_count(sensor_count)

        self._device = device
        self._bus = device.bus
        self._ports = getattr(device, 'port_number', None)
        if self._ports == None:
            self._ports = find_ports(device)
        self.set_calibration_data()
        LOGGER.debug('Found device | Bus:{0} Ports:{1}'.format(
            self._bus, self._ports))

    def set_calibration_data(self, scale=None, offset=None):
        """
        Set device calibration data based on settings in /etc/temper.conf.
        """
        if scale is not None and offset is not None:
            self._scale = scale
            self._offset = offset
        elif scale is None and offset is None:
            self._scale = 1.0
            self._offset = 0.0
            try:
                f = open('/etc/temper.conf', 'r')
            except IOError:
                f = None
            if f:
                lines = f.read().split('\n')
                f.close()
                for line in lines:
                    matches = re.match(CALIB_LINE_STR, line)
                    if matches:
                        bus = int(matches.groups()[0])
                        ports = matches.groups()[1]
                        scale = float(matches.groups()[2])
                        offset = float(matches.groups()[3])
                        if str(ports) == str(self._ports):
                            self._scale = scale
                            self._offset = offset
        else:
            raise RuntimeError("Must set both scale and offset, or neither")

    def set_sensor_count(self, count):
        """
        Set number of sensors on the device.

        To do: revamp /etc/temper.conf file to include this data.
        """
        # Currently this only supports 1 and 2 sensor models.
        # If you have the 8 sensor model, please contribute to the
        # discussion here: https://github.com/padelt/temper-python/issues/19
        if count not in [1, 2,]:
            raise ValueError('Only sensor_count of 1 or 2 supported')

        self._sensor_count = int(count)

    def get_ports(self):
        """
        Get device USB ports.
        """
        if self._ports:
            return self._ports
        return '' 

    def get_bus(self):
        """
        Get device USB bus.
        """
        if self._bus:
            return self._bus
        return ''

    def get_data(self):
        """
        Get data from the USB device.
        """
        try:
            # Take control of device if required
            if self._device.is_kernel_driver_active:
                LOGGER.debug('Taking control of device on bus {0} ports '
                    '{1}'.format(self._bus, self._ports))
                for interface in [0, 1]:
                    try:
                        self._device.detach_kernel_driver(interface)
                    except usb.USBError as err:
                        LOGGER.debug(err)
                self._device.set_configuration()
                # Prevent kernel message:
                # "usbfs: process <PID> (python) did not claim interface x before use"
                for interface in [0, 1]:
                    usb.util.claim_interface(self._device, interface)
                    usb.util.claim_interface(self._device, interface)

                # Turns out we don't actually need that ctrl_transfer.
                # Disabling this reduces number of USBErrors from ~7/30 to 0!
                #self._device.ctrl_transfer(bmRequestType=0x21, bRequest=0x09,
                #    wValue=0x0201, wIndex=0x00, data_or_wLength='\x01\x01',
                #    timeout=TIMEOUT)


            # Turns out a whole lot of that magic seems unnecessary.
            #self._control_transfer(COMMANDS['temp'])
            #self._interrupt_read()
            #self._control_transfer(COMMANDS['ini1'])
            #self._interrupt_read()
            #self._control_transfer(COMMANDS['ini2'])
            #self._interrupt_read()
            #self._interrupt_read()

            # Get temperature
            self._control_transfer(COMMANDS['temp'])
            data = self._interrupt_read()

            # Seems unneccessary to reset each time
            # Also ends up hitting syslog with this kernel message each time:
            # "reset low speed USB device number x using uhci_hcd"
            # self._device.reset()

            # Be a nice citizen and undo potential interface claiming.
            # Also see: https://github.com/walac/pyusb/blob/master/docs/tutorial.rst#dont-be-selfish
            usb.util.dispose_resources(self._device)
            return data
        except usb.USBError as err:
            # Catch the permissions exception and add our message
            if "not permitted" in str(err):
                raise Exception(
                    "Permission problem accessing USB. "
                    "Maybe I need to run as root?")
            else:
                LOGGER.error(err)
                raise

    def get_temperature(self, format='celsius', sensor=0):
        """
        Get device temperature reading.
        """
        results = self.get_temperatures(sensors=[sensor,])

        if format == 'celsius':
            return results[sensor]['temperature_c']
        elif format == 'fahrenheit':
            return results[sensor]['temperature_f']
        elif format == 'millicelsius':
            return results[sensor]['temperature_mc']
        else:
            raise ValueError("Unknown format")

    def get_temperatures(self, sensors=None):
        """
        Get device temperature reading.

        Params:
        - sensors: optional list of sensors to get a reading for, examples:
          [0,] - get reading for sensor 0
          [0, 1,] - get reading for sensors 0 and 1
          None - get readings for all sensors
        """
        _sensors = sensors
        if _sensors is None:
            _sensors = range(0, self._sensor_count)

        if not set(_sensors).issubset(range(0, self._sensor_count)):
            raise ValueError(
                'Some or all of the sensors in the list %s are out of range '
                'given a sensor_count of %d.  Valid range: %s' % (
                    _sensors,
                    self._sensor_count,
                    range(0, self._sensor_count),
                )
            )

        data = self.get_data()

        results = {}

        # Interpret device response
        for sensor in _sensors:
            offset = (sensor + 1) * 2
            data_s = "".join([chr(byte) for byte in data])
            value = (struct.unpack('>h', data_s[offset:(offset + 2)])[0])
            celsius = value / 256.0
            celsius = celsius * self._scale + self._offset
            results[sensor] = {
                'ports': self.get_ports(),
                'bus': self.get_bus(),
                'sensor': sensor,
                'temperature_f': celsius * 1.8 + 32.0,
                'temperature_c': celsius,
                'temperature_mc': celsius * 1000,
                'temperature_k': celsius + 273.15,
            }

        return results

    def _control_transfer(self, data):
        """
        Send device a control request with standard parameters and <data> as
        payload.
        """
        LOGGER.debug('Ctrl transfer: {0}'.format(data))
        self._device.ctrl_transfer(bmRequestType=0x21, bRequest=0x09,
            wValue=0x0200, wIndex=0x01, data_or_wLength=data, timeout=TIMEOUT)

    def _interrupt_read(self):
        """
        Read data from device.
        """
        data = self._device.read(ENDPOINT, REQ_INT_LEN, timeout=TIMEOUT)
        LOGGER.debug('Read data: {0}'.format(data))
        return data

    def close(self):
        """Does nothing in this device. Other device types may need to do cleanup here."""
        pass


class TemperHandler(object):
    """
    Handler for TEMPer USB thermometers.
    """

    def __init__(self):
        self._devices = []
        for vid, pid in VIDPIDS:
            self._devices += [TemperDevice(device) for device in \
                usb.core.find(find_all=True, idVendor=vid, idProduct=pid)]
	LOGGER.info('Found {0} TEMPer devices'.format(len(self._devices)))

    def get_devices(self):
        """
        Get a list of all devices attached to this handler
        """
        return self._devices
