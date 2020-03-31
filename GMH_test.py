# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 16:58:44 2017

Updated to Python 3.7 17/03/2020

@author: t.lawson
"""

import GMHstuff as GMH
import time

PORT = int(input("COM port number? > "))
# PORT = 10  # Change this to whatever port Windows assigns to your device

GFTB200 = GMH.GMH_Sensor(PORT)
time.sleep(1)
print('return from open() =', GFTB200.open_port())
print('\n')
for k in GFTB200.info.keys():
    v = GFTB200.info[k]
    print('{}: in {} (ch{})'.format(k, v[1], v[0]))
print('\ndemo status:', GFTB200.demo)
print('\n{:>20}{:>10}{:>15}{:>15}'.format('quantity', 'value', 'unit_from_info', 'unit_from_meas'))
for q in GMH.MEAS_ALIAS.keys():
    quantity = GMH.MEAS_ALIAS[q]
    info_unit = GFTB200.info[quantity][1]
    measurement = GFTB200.measure(q)
    val = measurement[0]
    meas_unit = measurement[1]

    print('{:>20}{:>10}{:>15}{:>15}'.format(quantity, val, info_unit, meas_unit))

GFTB200.close()
