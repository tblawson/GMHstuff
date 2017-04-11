# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 13:21:22 2015

@author: t.lawson
"""
# GMHstuff.py - required to access dll functions for GMH probes

import os
import ctypes as ct

# Change PATH to C:\GMH\GMHdll\ (or wherever you've put GMH3x32E.dll):
os.environ['GMHPATH'] = 'C:\Documents and Settings\\t.lawson\My Documents\Python Scripts\High_Res_Bridge\GMHdll'
gmhpath = os.environ['GMHPATH']
GMHLIB = ct.windll.LoadLibrary(os.path.join(gmhpath,'GMH3x32E'))

class GMH_Sensor():
    """
    A class to wrap around the low-level functions of GMH3x32E.dll. 
    For use with most Greisinger GMH devices.
    """
    def __init__(self,port,demo = True):
        self.demo = demo
        self.port = port # COM port of USB 3100N adapter cable
        self.Prio = ct.c_short()
        self.flData = ct.c_double()
        self.intData = ct.c_long()
        self.meas_str = ct.create_string_buffer(30)
        self.unit_str = ct.create_string_buffer(10)
        self.lang_offset = ct.c_int16(4096) # English language-offset
        self.MeasFn = ct.c_short(180) # GetMeasCode()
        self.UnitFn = ct.c_int16(178) # GetUnitCode()
        self.ValFn = ct.c_short(0) # GetValue()
        self.error_msg = ct.create_string_buffer(70)
        self.meas_alias = {'T':'Temperature',
                          'P':'Absolute Pressure',
                          'RH':'Rel. Air Humidity',
                          'T_dew':'Dewpoint Temperature',
                          'T_wb':'Wet Bulb Temperature',
                          'H_atm':'Atmospheric Humidity',
                          'H_abs':'Absolute Humidity'}
        self.Open()
        self.info = self.GetSensorInfo()


    def Open(self):
        if self.demo == True:
            return 1
        else:  
            err_code = GMHLIB.GMH_OpenCom(self.port)
            print 'open() port', self.port,'Return code:',err_code
            return err_code
 
       
    def Close(self):
        if self.demo == True:
            return 1
        else:  
            GMHLIB.GMH_CloseCom()
        return 1
 
   
    def Transmit(self,Addr,Func):
        """
        A wrapper for the GMH general-purpose interrogation function GMH_Transmit().
        """
        if self.demo == True:
            return 1
        else:
            err_code = GMHLIB.GMH_Transmit(Addr,Func,ct.byref(self.Prio),ct.byref(self.flData),ct.byref(self.intData))
            
            self.error_code = ct.c_int16(err_code + self.lang_offset.value)
            GMHLIB.GMH_GetErrorMessageRet(self.error_code, ct.byref(self.error_msg))

            return self.error_code.value
 
   
    def GetSensorInfo(self):
        """
        Interrogates GMH sensor.
        Returns a dictionary keyed by measurement string.
        Values are tuples: (<address>, <measurement unit>),
        where <address> is an int and <measurement unit> is a string.
        """

        addresses = [] # Between 1 and 99
        measurements = [] # E.g. 'Temperature', 'Absolute Pressure', 'Rel. Air Humidity',...
        units = [] # E.g. 'deg C', 'hPascal', '%RH',...
        
        for Address in range(1,100):
            Addr = ct.c_short(Address)
            self.error_code = self.Transmit(Addr,self.MeasFn) # Writes result to self.intData
            if self.intData.value == 0:
                break # Bail-out if we run out of measurement functions
            addresses.append(Address)
    
            meas_code = ct.c_int16(self.intData.value + self.lang_offset.value)
            GMHLIB.GMH_GetMeasurement(meas_code, ct.byref(self.meas_str)) # Writes result to self.meas_str
            measurements.append(self.meas_str.value)
    
            self.Transmit(Addr,self.UnitFn) # Writes result to self.intData
                                     
            unit_code = ct.c_int16(self.intData.value + self.lang_offset.value)
            GMHLIB.GMH_GetUnit(unit_code, ct.byref(self.unit_str)) # Writes result to self.unit_str
            units.append(self.unit_str.value)

        return dict(zip(measurements,zip(addresses,units)))


    def Measure(self, meas):
        """
        Measure either temperature, pressure or %RH, based on parameter meas.
        Returns a tuple: (<Temperature/Pressure/RH as int>, <unit as string>)
        """
        Address = self.info[self.meas_alias[meas]][0]
        Addr = ct.c_short(Address)
        self.Transmit(Addr,self.ValFn)
        return (self.flData.value, self.info[self.meas_alias[meas]][1])
