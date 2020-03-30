# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 16:57:22 2015

@author: t.lawson
"""
import ctypes as ct

GMHlib = ct.windll.GMH3x32E
version =  GMHlib.GMH_GetVersionNumber()
print 'dll Version no. = %d (= %s)' % (version,hex(version))

COM = ct.c_short(4)
open_code = GMHlib.GMH_OpenCom(COM)
print '\nopen return code = %d' % open_code

Addr = ct.c_short(21)
print '\nUsing address %d' % Addr.value

Prio = ct.c_short()
flData = ct.c_double() # Don't change this type!! It's the exactly right one!
intData = ct.c_long()

#----------------Measurement type--------------------------
#MeasFunc = ct.c_int16(180) # GetMeasCode()
#trans_code = GMHlib.GMH_Transmit(Addr,
#                                 MeasFunc,
#                                 ct.byref(Prio),
#                                 ct.byref(flData),
#                                 ct.byref(intData))
#print '\ntransmit(GetMeasCode) return value = %d' % trans_code
##print 'Float Data = %f' % flData.value
##print 'Int data = %d' % intData.value
#
#MeasCode = ct.c_int16(intData.value + 4096) #intData.value + 4096
#MeasStr = ct.c_char_p('')
#
### Convert 'measurement type' code to 'measurement type' string:
#strlen = GMHlib.GMH_GetMeasurement(MeasCode, MeasStr)
#meas_str = MeasStr.value
#print'MeasString: %s ' % MeasStr.value
#-------------------------------------------------------

##--------------------Unit------------------------------
UnitFunc = ct.c_int16(202) # GetDispUnitCode()
trans_code = GMHlib.GMH_Transmit(Addr,
                                 UnitFunc,
                                 ct.byref(Prio),
                                 ct.byref(flData),
                                 ct.byref(intData))
print '\ntransmit(GetDispUnitCode) return value = %d' % trans_code
#print 'Float Data = %f' % flData.value
#print 'Int data = %d' % intData.value

UnitCode = ct.c_int16(intData.value + 4096)
UnitStr = ct.c_char_p('')

# Convert units code to units string:
strlen = GMHlib.GMH_GetUnit(UnitCode, UnitStr) # crashes Python.?..
#print'UnitString: %s ' % UnitStr.value
unit_str = UnitStr.value
#-------------------------------------------------------

#------------------Measure T-------------------------------

ValFunc = ct.c_short(0) # GetValue()

trans_code = GMHlib.GMH_Transmit(Addr,
                                 ValFunc,
                                 ct.byref(Prio),
                                 ct.byref(flData),
                                 ct.byref(intData))
print '\ntransmit(GetValue) return value = %d' % trans_code
#print 'Float Data = ',flData.value,
#print 'Int data = %d' % intData.value
Temp = flData.value
#--------------------------------------------------

print 'T = %f %s' % (Temp, unit_str)

close_code = GMHlib.GMH_CloseCom()