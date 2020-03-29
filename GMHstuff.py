# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 13:21:22 2015

@author: t.lawson
"""
# GMHstuff.py - required to access dll functions for GMH probes

import os
import ctypes as ct

# Change PATH to wherever you keep GMH3x32E.dll: os.path.join('C:', 'Users', 't.lawson', 'PycharmProjects', 'GMHstuff2')
gmhlibpath = 'I:/MSL/Private/Electricity/Ongoing/OHM/Temperature_PRTs/GMHdll'
os.environ['GMHPATH'] = gmhlibpath
GMHpath = os.environ['GMHPATH']
GMHLIB = ct.windll.LoadLibrary(os.path.join('GMHdll', 'GMH3x32E'))  # (os.path.join(GMHpath, 'GMH3x32E'))

# A (useful) subset of Transmit() function calls:
TRANSMIT_CALLS = {'GetValue': 0, 'GetStatus': 3, 'GetType': 12, 'GetMinRange': 176, 'GetMaxRange': 177,
                  'GetUnitCode': 178, 'GetMeasCode': 180, 'GetDispMinRange': 200, 'GetDispMaxRange': 201,
                  'GetDispUnitCode': 202, 'GetDispDecPoint': 204, 'GetChannelCount': 208, 'GetPowerOffTime': 222,
                  'SetPowerOffTime': 223, 'GetSoftwareInfo': 254}

MEAS_ALIAS = {'T': 'Temperature', 'P': 'Absolute Pressure', 'RH': 'Rel. Air Humidity', 'T_dew': 'Dewpoint Temperature',
              'T_wb': 'Wet Bulb Temperature', 'H_atm': 'Atmospheric Humidity', 'H_abs': 'Absolute Humidity'}

C_LANG_OFFSET = ct.c_int16(4096)  # English language-offset

class GMH_Sensor():
    """
    A class to wrap around the low-level functions of GMH3x32E.dll.

    For use with Greisinger GMH devices (GFTB200, etc.).
    """
    def __init__(self, port, demo=True):
        """
        Initiate a GMH sensor object.

        :param port:
            COM port number to which GMH device is attached (via 3100N cable)
        :param demo:
            Describes if this object is NOT capable of operating as a real GMH sensor (default is True) -
            False - the COM port connecting to a real device is open AND that device is turned on and present,
            True - the device is a combination of one or more of:
            * not turned on OR
            * not connected OR
            * not associated with an open COM port.
        """
        self.demo = demo
        self.port = port
        self.c_Prio = ct.c_short()
        self.c_flData = ct.c_double()
        self.c_intData = ct.c_long()
        self.c_meas_str = ct.create_string_buffer(30)
        self.c_unit_str = ct.create_string_buffer(10)

        self.c_error_msg = ct.create_string_buffer(70)
        self.error_msg = '-'
        self.status_msg = '-'
        self.error_code = 0
        self.com_open = False

    def rtncode_to_errmsg(self, rtn_code):
        """
        Translate a function's return code to a message-string.

        Shift return code by language offset,
        Obtain message string (as byte-stream) corresponding to translated code,
        Decode byte-stream to message string,
        print message.

        :argument:
            int
        :returns
            string (Unicode)
        """
        c_msg = ct.create_string_buffer(70)
        c_status = ct.create_string_buffer(70)
        c_translated_code = ct.c_int16(rtn_code + C_LANG_OFFSET.value)
        GMHLIB.GMH_GetErrorMessageRet(c_translated_code, ct.byref(c_msg))
        GMHLIB.GMH_GetStatusMessage(c_translated_code, ct.byref(c_status))
        msg = c_msg.value.decode('ISO-8859-1')
        status = c_status.value.decode('ISO-8859-1')
        if 'EASYBus' in msg:
            return ('OK.', status)
        else:
            return (msg, status)

    def open(self):
        """
        Open a single COM channel to a 3100N GMH adapter cable.

        Only one COM port can be open at a time. Up to 5 GMH devices can be serviced through
        one COM port (but requires special hardware fan-out).

        :returns:
            1 for success,
            -1 for failure.
            0 means sensor is in demo mode and any 'reading' is fake data.
        """

        if self.demo is True:
            print('Open(): demo is True; rtn=0')
            self.com_open = False
            return 0
        else:
            try:
                c_rtn_code = ct.c_int16(GMHLIB.GMH_OpenCom(self.port))
                self.error_code = c_rtn_code.value
                print('open(): calling rtncode_to_errmsg():', self.rtncode_to_errmsg(c_rtn_code.value))
                (self.error_msg, self.status_msg) = self.rtncode_to_errmsg(c_rtn_code.value)
                print('GMH_OpenCom() rtn_code =', self.error_code)
                assert self.error_code >= 0, 'GMHLIB.GMH_OpenCom() failed -> {} {}'.format(self.error_code,
                                                                                           self.error_msg)
            except AssertionError as msg:
                print('open():', msg)
                self.com_open = False
                return -1
            else:
                self.error_code = c_rtn_code.value
                self.com_open = True
                return 1

    def Close(self):
        """
        Close open COM port (only one).

        Note that COM port could still be open even if object is in demo mode.
        :returns 1 if successful, -1 otherwise
        """
        if self.com_open is False:
            pass
        else:
            GMHLIB.GMH_CloseCom()
            self.com_open = False
        return 1

    def transmit(self, chan, func):
        """
        A wrapper for the GMH general-purpose interrogation function GMH_Transmit().

        Runs func on instrument channel chan and updates self.error_code.
        self.error_code is then used to update self.error_msg and self.status_msg.
        :argument
            chan: Measurement channel of GMH device (0-99)
            func: Function-call code (see transmit_calls dict)
        :returns
            1 for success (non-demo mode),
            0 for success (demo mode),
            GMHLIB.GMH_Transmit() return code for failure (any negative value).
        """
        if self.demo is True:
            return 0
        else:
            self.error_code = GMHLIB.GMH_Transmit(chan, func, ct.byref(self.c_Prio),
                                                  ct.byref(self.c_flData),
                                                  ct.byref(self.c_intData))
            (self.error_msg, self.status_msg) = self.rtncode_to_errmsg(self.error_code)
            # print('transmit():', self.error_code, self.error_msg, '...', self.status_msg)
            if self.error_code >= 0:
                return 1
            else:
                return self.error_code

    def get_sensor_info(self):
        """
        Interrogates GMH sensor for measurement capabilities.

        :returns
        self.info - a dictionary keyed by measurement string (eg: 'Temperature').
        Values are tuples: (<address>, <measurement unit>),
        where <address> is an int and <measurement unit> is a (unicode) string.
        """

        channels = []  # Between 1 and 99
        measurements = []  # E.g. 'Temperature', 'Absolute Pressure', ...
        units = []  # E.g. 'deg C', 'hPascal', ...

        if self.demo is True:  # Either COM port not open and/or sensor is missing/turned off
            return {'NO SENSOR': (0, 'NO UNIT')}
        else:  # Fully-operational
            # Get number of measurement channels for this instrument. Write result to self.c_intData:
            self.error_code = self.transmit(1, TRANSMIT_CALLS['GetChannelCount'])
            chan_count = self.c_intData.value
            print('get_sensor_info(): {} channels found'.format(chan_count))

            channel = 0
            while channel <= chan_count:
                print('get_sensor_info(): Verifying channel {}...'.format(channel))
                c_chan = ct.c_short(channel)

                # Write result to self.c_intData:
                self.error_code = self.transmit(c_chan, TRANSMIT_CALLS['GetValue'])
                if self.error_code < 0:
                    print('get_sensor_info(): {:s}...{:s}'.format(self.error_msg, self.status_msg))
                    print('get_sensor_info(): No measurement function at channel {}'.format(channel))
                    channel += 1
                    continue  # Skip to next channel if this one's a dud
                else:
                    self.error_code = self.transmit(c_chan, TRANSMIT_CALLS['GetMeasCode'])
                    if self.c_intData.value == 0:
                        channel += 1
                        continue  # Bail-out if not a valid measurement code
                    c_translated_meas_code = ct.c_int16(self.c_intData.value + C_LANG_OFFSET.value)

                    # Write result to self.c_meas_str:
                    GMHLIB.GMH_GetMeasurement(c_translated_meas_code, ct.byref(self.c_meas_str))
                    measurements.append(self.c_meas_str.value.decode('ISO-8859-1'))

                    # Write result to self.c_intData:
                    self.transmit(c_chan, TRANSMIT_CALLS['GetUnitCode'])
                    c_unit_code = ct.c_int16(self.c_intData.value + C_LANG_OFFSET.value)

                    # Write result to self.c_unit_str:
                    GMHLIB.GMH_GetUnit(c_unit_code, ct.byref(self.c_unit_str))
                    units.append(self.c_unit_str.value.decode('ISO-8859-1'))
                    channels.append(channel)
                    channel += 1

            self.info = dict(zip(measurements, zip(channels, units)))
            return self.info

    def measure(self, meas):
        """
        Make a measurement (temperature, pressure, humidity, etc).

        :argument meas - an alias (as defined in MEAS_ALIAS) for the measurement type.
        meas is one of: 'T', 'P', 'RH', 'T_dew', 't_wb', 'H_atm' or 'H_abs'.

        :returns a tuple: (<measurement as float>, <unit as (unicode) string>)
        """
        if len(self.info) == 0:
            print('Measure(): No measurements available! - Check sensor is connected and ON.')
            return (0, 'NO_UNIT')
        elif MEAS_ALIAS[meas] not in self.info.keys():
            print('Function', meas, 'not available!')
            return (0, 'NO_UNIT')
        else:
            channel = self.info[MEAS_ALIAS[meas]][0]
            c_chan = ct.c_short(channel)
            self.transmit(c_chan, TRANSMIT_CALLS['GetValue'])
            return (self.c_flData.value, self.info[MEAS_ALIAS[meas]][1])
