# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 13:21:22 2015

@author: t.lawson
"""
# GMHstuff.py - required to access dll functions for GMH probes

import os
import ctypes as ct

# Change PATH to wherever you keep GMH3x32E.dll:
gmhlibpath = 'I:\MSL\Private\Electricity\Ongoing\OHM\Temperature_PRTs\GMHdll'
os.environ['GMHPATH'] = gmhlibpath
GMHpath = os.environ['GMHPATH']
GMHLIB = ct.windll.LoadLibrary(os.path.join(GMHpath, 'GMH3x32E'))


class GMH_Sensor():
    """
    A class to wrap around the low-level functions of GMH3x32E.dll.
    For use with most Greisinger GMH devices.
    """
    def __init__(self, port, demo=True):
        self.demo = demo
        self.port = port  # COM port of USB 3100N adapter cable
        self.c_Prio = ct.c_short()
        self.c_flData = ct.c_double()
        self.c_intData = ct.c_long()
        self.c_meas_str = ct.create_string_buffer(30)
        self.c_unit_str = ct.create_string_buffer(10)
        self.c_lang_offset = ct.c_int16(4096)  # English language-offset
        self.c_MeasFn = ct.c_short(180)  # GetMeasCode()
        self.c_UnitFn = ct.c_int16(178)  # GetUnitCode()
        self.c_ValFn = ct.c_short(0)  # GetValue()
        self.c_error_msg = ct.create_string_buffer(70)
        self.error_msg = '-'
        self.error_code = 0
        self.is_open = False
        self.meas_alias = {'T': 'Temperature',
                           'P': 'Absolute Pressure',
                           'RH': 'Rel. Air Humidity',
                           'T_dew': 'Dewpoint Temperature',
                           'T_wb': 'Wet Bulb Temperature',
                           'H_atm': 'Atmospheric Humidity',
                           'H_abs': 'Absolute Humidity'}

    def Open(self):
        """
        Open a single communication channel to a GMH sensor.
        Only one GMH sensor can be open at a time.

        :return: 1 for success, -1 for failure.
        0 means sensor is in demo mode and any 'reading' is fake data.
        Any negative value indicates failure to open.
        """

        if self.demo is True:
            print('Open(): demo is True; rtn=0')
            self.is_open = False
            return 0
        else:
            try:
                c_rtn_code = ct.c_int16(GMHLIB.GMH_OpenCom(self.port))
                c_translated_rtn_code = ct.c_int16(c_rtn_code.value + self.c_lang_offset.value)
                GMHLIB.GMH_GetErrorMessageRet(c_translated_rtn_code, ct.byref(self.c_error_msg))
                self.error_msg = self.c_error_msg.value
                print('GMH_OpenCom() c_rtn_code =', c_rtn_code.value)
                assert c_rtn_code.value >= 0, 'GMHLIB.GMH_OpenCom() failed'
            except AssertionError as msg:
                print(msg, 'with rtn_code', c_rtn_code.value, self.error_msg)
                self.is_open = False
                return -1
            else:
                self.error_msg = self.c_error_msg.value
                # print('Open(): demo is False; rtn=', c_rtn_code.value, self.error_msg)
                self.error_code = c_rtn_code.value
                self.is_open = True
                return 1

    def Close(self):
        if self.demo is True:
            pass
        else:
            GMHLIB.GMH_CloseCom()
        return 1

    def Transmit(self, Addr, Func):
        """
        A wrapper for the GMH general-purpose
        interrogation function GMH_Transmit().
        """
        if self.demo is True:
            return 1
        else:
            rtn_code = GMHLIB.GMH_Transmit(Addr, Func, ct.byref(self.c_Prio),
                                           ct.byref(self.c_flData),
                                           ct.byref(self.c_intData))

            c_translated_rtn_code = ct.c_int16(rtn_code + self.c_lang_offset.value)
            GMHLIB.GMH_GetErrorMessageRet(c_translated_rtn_code,
                                          ct.byref(self.c_error_msg))

            return rtn_code

    def GetSensorInfo(self):
        """
        Interrogates GMH sensor.
        Returns a dictionary keyed by measurement string.
        Values are tuples: (<address>, <measurement unit>),
        where <address> is an int and <measurement unit> is a string.
        """

        addresses = []  # Between 1 and 99
        measurements = []  # E.g. 'Temperature', 'Absolute Pressure', ...
        units = []  # E.g. 'deg C', 'hPascal', ...

        for Address in range(1, 100):
            c_Addr = ct.c_short(Address)

            # Write result to self.c_intData:
            self.error_code = self.Transmit(c_Addr, self.c_MeasFn)
            if self.c_intData.value == 0:
                break  # Bail-out if we run out of measurement functions
            addresses.append(Address)

            c_meas_code = ct.c_int16(self.c_intData.value +
                                     self.c_lang_offset.value)

            # Write result to self.c_meas_str:
            GMHLIB.GMH_GetMeasurement(c_meas_code, ct.byref(self.c_meas_str))
            measurements.append(self.c_meas_str.value.decode('ISO-8859-1'))

            # Write result to self.c_intData:
            self.Transmit(c_Addr, self.c_UnitFn)

            c_unit_code = ct.c_int16(self.c_intData.value +
                                     self.c_lang_offset.value)

            # Write result to self.c_unit_str:
            GMHLIB.GMH_GetUnit(c_unit_code, ct.byref(self.c_unit_str))
            units.append(self.c_unit_str.value.decode('ISO-8859-1'))

        self.info = dict(zip(measurements, zip(addresses, units)))
        return self.info

    def Measure(self, meas):
        """
        Measure parameter meas (temperature, pressure or humidity).
        Returns a tuple: (<Temperature/Pressure/RH as int>, <unit as string>)
        meas is one of: 'T', 'P', 'RH', 'T_dew', 't_wb', 'H_atm' or 'H_abs'.
        """
        if len(self.info) == 0:
            print('Measure(): No measurements available! - Check sensor is connected and ON.')
            return (0, 'NO_UNIT')
        if self.meas_alias[meas] not in self.info.keys():
            print('Function', meas, 'not available!')
            return (0, 'NO_UNIT')
        else:
            Address = self.info[self.meas_alias[meas]][0]
            Addr = ct.c_short(Address)
            self.Transmit(Addr, self.c_ValFn)
            return (self.c_flData.value, self.info[self.meas_alias[meas]][1])
