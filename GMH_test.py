# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 16:58:44 2017

Updated to Python 3.7 17/03/2020

@author: t.lawson
"""

import GMHstuff as GMH

PORT = 6  # Change this to whatever port Windows assigns to your device

GFTB200 = GMH.GMH_Sensor(PORT, demo=False)
print('Open() rtn:', GFTB200.Open())
info = GFTB200.GetSensorInfo()
print(info)
print('quantity \t value \t unit_from_info \t unit_from_meas')
for q in GFTB200.meas_alias.keys():
    quantity = GFTB200.meas_alias[q]
    info_unit = info[quantity][1]
    measurement = GFTB200.Measure(q)
    val = measurement[0]
    meas_unit = measurement[1]

    print(quantity, '\t', val, '\t', info_unit, '\t', meas_unit)

# T = GFTB200.Measure('T')
# print(T[0], T[1])
# P = GFTB200.Measure('P')
# print(P[0], P[1])
# RH = GFTB200.Measure('RH')
# print(RH[0], RH[1])
# T_dew = GFTB200.Measure('T_dew')
# print(T_dew[0], T_dew[1])
# T_wb = GFTB200.Measure('T_wb')
# print(T_wb[0], T_wb[1])
# H_abs = GFTB200.Measure('H_abs')
# print(H_abs[0], H_abs[1])
# H_atm = GFTB200.Measure('H_atm')
# print(H_atm[0], H_atm[1])

GFTB200.Close()
