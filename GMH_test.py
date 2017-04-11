# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 16:58:44 2017

@author: t.lawson
"""

import GMHstuff as GMH

GFTB200 = GMH.GMH_Sensor(6, demo = False)
print '\nSensor info:\n',GFTB200.info,'\n'
T = GFTB200.Measure('T')
print T[0],T[1]
P = GFTB200.Measure('P')
print P[0],P[1]
RH = GFTB200.Measure('RH')
print RH[0],RH[1]
T_dew = GFTB200.Measure('T_dew')
print T_dew[0],T_dew[1]
T_wb = GFTB200.Measure('T_wb')
print T_wb[0],T_wb[1]
H_abs = GFTB200.Measure('H_abs')
print H_abs[0],H_abs[1]
H_atm = GFTB200.Measure('H_atm')
print H_atm[0],H_atm[1]

GFTB200.Close()