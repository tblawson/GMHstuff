# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 16:58:44 2017

Updated to Python 3.7 17/03/2020

@author: t.lawson
"""

import GMHstuff as GMH


# PORT = 10  # Change this to whatever port Windows assigns to your device
PORT = int(input("COM port number? > "))
GFTB200 = GMH.GMHSensor(PORT)
GFTB200.open_port()
# print('\ndemo status:', GFTB200.demo)  # 'demo = False' means a fully-functional device


# for i in range(GFTB200.chan_count):
#     v = GFTB200.get_meas_attributes(i)
#     print('{}: in {} (ch{})'.format(i, v[1], v[0]))

print('\nBelow is a list of available measurements for this device:')
print('\n{:>20}{:>5}{:>10}{:>15}{:>15}'.format('quantity', 'chan', 'value', 'unit_from_info', 'unit_from_meas'))
for q in GMH.MEAS_ALIAS.keys():
    quantity = GMH.MEAS_ALIAS[q]
    attribs = GFTB200.get_meas_attributes(q)
    measurement = GFTB200.measure(q)  # measurement is a tuple: (<value>, <unit string>)
    val = measurement[0]
    meas_unit = measurement[1]
    print('{:>20}{:>5}{:>10}{:>15}{:>15}'.format(quantity, attribs[0], val, attribs[1], meas_unit))

print(GFTB200.get_meas_attributes('height'))

GFTB200.get_sensor_info()

GFTB200.close()  # Close ALL open COM ports
