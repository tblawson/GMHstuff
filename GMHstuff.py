# -*- coding: utf-8 -*-
"""
GMHstuff.py - required to access dll functions for GMH probes
Created on Wed Jul 29 13:21:22 2015

@author: t.lawson
"""

import os
import ctypes as ct


# os.path.join('C:', 'Users', 't.lawson', 'PycharmProjects', 'GMHstuff2')
# Change PATH to wherever you keep GMH3x32E.dll:
gmhlibpath = 'I:/MSL/Private/Electricity/Ongoing/OHM/Temperature_PRTs/GMHdll'
os.environ['GMHPATH'] = gmhlibpath
GMHpath = os.environ['GMHPATH']
GMHLIB = ct.windll.LoadLibrary(os.path.join('GMHdll', 'GMH3x32E'))  # (os.path.join(GMHpath, 'GMH3x32E'))

# A (useful) subset of Transmit() function calls:
TRANSMIT_CALLS = {'GetValue': 0, 'GetStatus': 3, 'GetTypeCode': 12, 'GetMinRange': 176, 'GetMaxRange': 177,
                  'GetUnitCode': 178, 'GetMeasCode': 180, 'GetDispMinRange': 200, 'GetDispMaxRange': 201,
                  'GetDispUnitCode': 202, 'GetDispDecPoint': 204, 'GetChannelCount': 208, 'GetPowerOffTime': 222,
                  'SetPowerOffTime': 223, 'GetSoftwareInfo': 254}

MEAS_ALIAS = {'T': 'Temperature', 'P': 'Absolute Pressure', 'RH': 'Rel. Air Humidity', 'T_dew': 'Dewpoint Temperature',
              'T_wb': 'Wet Bulb Temperature', 'H_atm': 'Atmospheric Humidity', 'H_abs': 'Absolute Humidity'}

C_LANG_OFFSET = ct.c_int16(4096)  # English language-offset


class GMHSensor:
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
        self.com_open = False
        self.error_msg = '-'
        self.status_msg = '-'
        self.error_code = 0
        self.type_str = '-'
        self.chan_count = 0

        # All ctypes objects have a c_ suffix:
        self.c_Prio = ct.c_short()
        self.c_flData = ct.c_double()
        self.c_intData = ct.c_long()
        self.c_meas_str = ct.create_string_buffer(30)
        self.c_unit_str = ct.create_string_buffer(10)
        self.c_type_str = ct.create_string_buffer(30)
        self.c_status_msg = ct.create_string_buffer(70)
        self.c_error_msg = ct.create_string_buffer(70)

        self._info = {}  # Don't access directly - use get functions

    @staticmethod
    def rtncode_to_errmsg(rtn_code):
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
        # c_status = ct.create_string_buffer(70)
        c_translated_code = ct.c_int16(rtn_code + C_LANG_OFFSET.value)
        GMHLIB.GMH_GetErrorMessageRet(c_translated_code, ct.byref(c_msg))
        # GMHLIB.GMH_GetStatusMessage(c_translated_code, ct.byref(c_status))
        msg = c_msg.value.decode('ISO-8859-1')
        # status = c_status.value.decode('ISO-8859-1')
        if 'EASYBus' in msg:
            return 'OK.'  # , status)
        else:
            return msg  # , status)

    def open_port(self):
        """
        Open a single COM port for a 3100N GMH adapter cable.

        Only one COM port can be open at a time. Up to 5 GMH devices can be serviced through
        one COM port (but requires special hardware fan-out).

        :returns:
            1 for success,
            -1 for failure.
        """
        try:
            c_rtn_code = ct.c_int16(GMHLIB.GMH_OpenCom(self.port))
            self.error_code = c_rtn_code.value
            self.error_msg = self.rtncode_to_errmsg(c_rtn_code.value)
            assert self.error_code >= 0, 'GMHLIB.GMH_OpenCom() failed'
        except AssertionError as msg:
            print('open_port()_except:', msg, '{} "{}"'.format(self.error_code, self.error_msg))
            self.com_open = False
            return -1
        else:
            self.error_code = c_rtn_code.value
            self.com_open = True
            # print('open_port(): calling get_sensor_info()...')
            self.get_sensor_info()
            return 1

    def close(self):
        """
        Close open COM port (only one).

        Note that COM port could still be open even if object is in demo mode.
        :returns 1 if successful, -1 otherwise
        """
        if self.com_open is False:
            return 0
        else:
            GMHLIB.GMH_CloseCom()
            self.com_open = False
        return 1

    def transmit(self, c_chan, c_func):
        """
        A wrapper for the GMH general-purpose interrogation function GMH_Transmit().

        Runs func on instrument channel chan and updates self.error_code.
        self.error_code is then used to update self.error_msg and self.status_msg.
        :argument
            chan: Measurement channel of GMH device (0-99)
            func: Function-call code (see transmit_calls dict)
        :returns
            1 for success (non-demo mode),
            -1 for GMHLIB.GMH_Transmit() failure
        """
        # if self.demo is True:
        #     return 0
        # else:
        try:
            self.error_code = GMHLIB.GMH_Transmit(c_chan, c_func, ct.byref(self.c_Prio),
                                                  ct.byref(self.c_flData),
                                                  ct.byref(self.c_intData))
            self.error_msg = self.rtncode_to_errmsg(self.error_code)
            assert self.error_code >= 0, 'GMH_Transmit({}) failed'.format(c_func)
        except AssertionError as msg:
            print('transmit({})_except:'.format(c_func), msg, '{} "{}"'.format(self.error_code, self.error_msg))
            return -1
        else:
            # print('transmit({})_else: GMH_Transmit() return: {} "{}"'.format(c_func, self.error_code,
            #                                                                  self.error_msg))
            return 1

    def get_type(self):
        # Get instrument type code -> self.c_intData:
        c_chan = ct.c_int16(1)
        c_func = ct.c_int16(TRANSMIT_CALLS['GetTypeCode'])
        self.transmit(c_chan, c_func)
        c_translated_type_code = ct.c_int16(self.c_intData.value + C_LANG_OFFSET.value)
        # Interpret type code to type string:
        try:
            c_rtn_len = ct.c_byte(GMHLIB.GMH_GetType(c_translated_type_code, ct.byref(self.c_type_str)))
            self.error_code = c_rtn_len.value
            self.type_str = self.c_type_str.value.decode('ISO-8859-1')
            assert self.error_code >= 1, 'GMHLIB.GMH_GetType() failed'
        except AssertionError as msg:
            print('get_type():', msg, '{} "{}"'.format(self.error_code, self.type_str))
            self.type_str = 'UNKNOWN instrument type.'
        else:
            print('get_type(): Sensor type = {}'.format(self.type_str))

    def get_num_chans(self):
        # Get number of measurement channels for this instrument -> self.c_intData:
        c_chan = ct.c_int16(1)
        c_func = ct.c_int16(TRANSMIT_CALLS['GetChannelCount'])
        self.error_code = self.transmit(c_chan, c_func)
        self.chan_count = self.c_intData.value
        print('get_num_chans(): {} channels found'.format(self.chan_count))

    def get_status(self, chan):
        # Get instrument status code -> self.c_intData:
        c_chan = ct.c_int16(chan)
        c_func = ct.c_int16(TRANSMIT_CALLS['GetStatus'])
        self.error_code = self.transmit(c_chan, c_func)
        c_translated_status_code = ct.c_int16(self.c_intData.value + C_LANG_OFFSET.value)
        # Interpret status code -> status string:
        GMHLIB.GMH_GetStatusMessage(c_translated_status_code, ct.byref(self.c_status_msg))
        self.status_msg = self.c_status_msg.value.decode('ISO-8859-1')

    def get_sensor_info(self):
        """
        Interrogates GMH sensor for measurement capabilities.

        Only runs if self.info is empty.

        :returns
        self.info - a dictionary keyed by measurement string (eg: 'Temperature').
        Values are tuples: (<address>, <measurement unit>),
        where <address> is an int and <measurement unit> is a (unicode) string.
        """
        channels = []  # Between 1 and 99
        measurements = []  # E.g. 'Temperature', 'Absolute Pressure', ...
        units = []  # E.g. 'deg C', 'hPascal', ...
        statuses = []

        if len(self._info) > 0:  # Device info already determined.
            print('\nget_sensor_info(): device info already determined.')
            return self._info
        else:
            # Find all channel-independent parameters
            self.get_type()
            self.get_num_chans()
            if self.chan_count == 0:
                return {'NO SENSOR': (0, 'NO UNIT')}
            else:
                # Visit all the channels and note their capabilities:
                channel = 0
                while channel <= self.chan_count:
                    print('\nget_sensor_info(): Testing channel {}...'.format(channel))
                    c_chan = ct.c_int16(channel)
                    # Try reading a value, Write result to self.c_intData:
                    c_func = ct.c_int16(TRANSMIT_CALLS['GetValue'])
                    self.error_code = self.transmit(c_chan, c_func)
                    if self.error_code < 0:
                        print('get_sensor_info(): No measurement function at channel {}'.format(channel))
                        channel += 1
                        continue  # Skip to next channel if this one has no value to read
                    else:  # Successfully got a dummy value
                        c_func = ct.c_int16(TRANSMIT_CALLS['GetMeasCode'])
                        self.error_code = self.transmit(c_chan, c_func)
                        if self.c_intData.value < 0:
                            print('get_sensor_info(): transmit() failure to get meas code.')
                            channel += 1
                            continue  # Bail-out if not a valid measurement code

                        # Now we have a valid measurement code...
                        c_translated_meas_code = ct.c_int16(self.c_intData.value + C_LANG_OFFSET.value)
                        # Write result to self.c_meas_str:
                        GMHLIB.GMH_GetMeasurement(c_translated_meas_code, ct.byref(self.c_meas_str))
                        measurements.append(self.c_meas_str.value.decode('ISO-8859-1'))

                        # Get instrument status code -> self.c_intData:
                        self.get_status(channel)
                        statuses.append(self.status_msg)
                        # print('get_sensor_info(): Status: {}'.format(self.status_msg))

                        c_func = ct.c_int16(TRANSMIT_CALLS['GetUnitCode'])
                        self.transmit(c_chan, c_func)
                        c_unit_code = ct.c_int16(self.c_intData.value + C_LANG_OFFSET.value)
                        # Write result to self.c_unit_str:
                        GMHLIB.GMH_GetUnit(c_unit_code, ct.byref(self.c_unit_str))
                        units.append(self.c_unit_str.value.decode('ISO-8859-1'))
                        channels.append(channel)
                        channel += 1

                        self.demo = False  # If we've got this far we must have a fully-functioning instrument.
                        # print('get_sensor_info(): demo mode = {}'.format(self.demo))
                self._info = dict(zip(measurements, zip(channels, units)))
                return self._info

    def get_meas_attributes(self, meas):
        """
        Look up attributes associated with a type of measurement.

        :param meas: Measurement-type alias (any key in MEAS_ALIAS dict) - a (unicode) string,
        :return: Tuple consisting of the device channel (int) and measurement unit (unicode).
        """
        fail_rtn = (0, 'NO_UNIT')
        try:
            measurement = MEAS_ALIAS[meas]
        except KeyError as msg:
            print('{} - No known alias for {}.'.format(msg, meas))
            return fail_rtn
        else:
            try:
                chan_unit_str = self._info[measurement]
            except KeyError as msg:
                print("{} - measurement {} doesn't exist for this device.".format(msg, meas))
                return fail_rtn
            else:
                return chan_unit_str

    def measure(self, meas):
        """
        Make a measurement (temperature, pressure, humidity, etc).

        :argument meas - an alias (as defined in MEAS_ALIAS) for the measurement type.
        meas is one of: 'T', 'P', 'RH', 'T_dew', 't_wb', 'H_atm' or 'H_abs'.

        :returns a tuple: (<measurement as float>, <unit as (unicode) string>)
        """
        if len(self._info) == 0:
            print('Measure(): No measurements available! - Check sensor is connected and ON.')
            return 0, 'NO_UNIT'
        elif MEAS_ALIAS[meas] not in self._info.keys():
            print('Function', meas, 'not available!')
            return 0, 'NO_UNIT'
        else:
            channel = self._info[MEAS_ALIAS[meas]][0]
            c_chan = ct.c_short(channel)
            c_func = ct.c_int16(TRANSMIT_CALLS['GetValue'])
            self.transmit(c_chan, c_func)
            return self.c_flData.value, self._info[MEAS_ALIAS[meas]][1]
