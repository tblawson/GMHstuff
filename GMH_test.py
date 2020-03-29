# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 16:58:44 2017

Updated to Python 3.7 17/03/2020

@author: t.lawson
"""

import GMHstuff as GMH

PORT =  int(input("COM port number? > "))
# PORT = 10  # Change this to whatever port Windows assigns to your device

GFTB200 = GMH.GMH_Sensor(PORT, demo=False)
GFTB200.open()
GFTB200.get_sensor_info()
for k in GFTB200.info.keys():
    print(k, '(', GFTB200.info[k][0], ')', GFTB200.info[k][1])

print('{:>20}{:>10}{:>15}{:>15}'.format('quantity', 'value', 'unit_from_info', 'unit_from_meas'))
for q in GMH.MEAS_ALIAS.keys():
    quantity = GMH.MEAS_ALIAS[q]
    info_unit = GFTB200.info[quantity][1]
    measurement = GFTB200.measure(q)
    val = measurement[0]
    meas_unit = measurement[1]

    print('{:>20}{:>10}{:>15}{:>15}'.format(quantity, val, info_unit, meas_unit))

# T = GFTB200.measure('T')
# print(T[0], T[1])
# P = GFTB200.measure('P')
# print(P[0], P[1])
# RH = GFTB200.measure('RH')
# print(RH[0], RH[1])
# T_dew = GFTB200.measure('T_dew')
# print(T_dew[0], T_dew[1])
# T_wb = GFTB200.measure('T_wb')
# print(T_wb[0], T_wb[1])
# H_abs = GFTB200.measure('H_abs')
# print(H_abs[0], H_abs[1])
# H_atm = GFTB200.measure('H_atm')
# print(H_atm[0], H_atm[1])

GFTB200.Close()
