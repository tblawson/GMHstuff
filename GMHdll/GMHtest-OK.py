# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 16:57:22 2015

@author: t.lawson
"""
import ctypes as ct

GMHlib = ct.windll.GMH3x32E
version =  GMHlib.GMH_GetVersionNumber()
print 'dll Version no. = %d (= %s)' % (version,hex(version))

#COM4 = ct.c_short(4)
#COM6 = ct.c_short(6)
open_code = GMHlib.GMH_OpenCom(6)
print '\nopen Com return code = %d' % open_code


Prio = ct.c_short()
flData = ct.c_double() # Don't change this type!! It's the exactly right one!
intData = ct.c_long()
ValFunc = ct.c_short(0) # GetValue()
UnitFunc = ct.c_int16(202) # GetDispUnitCode()

for Address in range(1,30):
    Addr = ct.c_short(Address)
    trans_code = GMHlib.GMH_Transmit(Addr,
                                     ValFunc,
                                     ct.byref(Prio),
                                     ct.byref(flData),
                                     ct.byref(intData))
    if trans_code == 0:
        break
        
print '\nUsing addresses', Addr.value

##--------------------Unit------------------------------

#trans_code = GMHlib.GMH_Transmit(Addr,
#                                 UnitFunc,
#                                 ct.byref(Prio),
#                                 ct.byref(flData),
#                                 ct.byref(intData))
#print '\ntransmit(GetDispUnitCode) return value = %d' % trans_code
##print 'Float Data = %f' % flData.value
##print 'Int data = %d' % intData.value
#
#UnitCode = ct.c_int16(intData.value + 4096)
#UnitStr = ct.c_char_p('')
#
## Convert units code to units string:
#strlen = GMHlib.GMH_GetUnit(UnitCode, UnitStr) # crashes Python.?..
##print'UnitString: %s ' % UnitStr.value
#unit_str = UnitStr.value
#-------------------------------------------------------

#------------------Measure T-------------------------------

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

print 'T = %f' % (Temp)

close_code = GMHlib.GMH_CloseCom()