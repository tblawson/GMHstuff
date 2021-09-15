# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 16:58:44 2017

Updated to Python 3.7 17/03/2020

@author: t.lawson
"""

import gmhstuff as gmh


# PORT = 10  # Change this to whatever port Windows assigns to your device
PORT = int(input("COM port number? > "))
GFTB200 = gmh.GMHSensor(PORT)
GFTB200.open_port()
# print('\ndemo status:', GFTB200.demo)  # 'demo = False' means a fully-functional device

print('\nBelow is a list of available measurements for this device:')
print('\n{:>20}{:>5}{:>10}{:>15}{:>15}'.format('quantity', 'chan', 'value', 'unit_from_info', 'unit_from_meas'))
for q in gmh.MEAS_ALIAS.keys():
    quantity = gmh.MEAS_ALIAS[q]
    attribs = GFTB200.get_meas_attributes(q)
    measurement = GFTB200.measure(q)  # measurement is a tuple: (<value>, <unit string>)
    val = measurement[0]
    meas_unit = measurement[1]
    print('{:>20}{:>5}{:>10}{:>15}{:>15}'.format(quantity, attribs[0], val, attribs[1], meas_unit))

print('\nMeas attributes:',GFTB200.get_meas_attributes('P'))

print('\nTemperature:', GFTB200.measure('T'))

print('\nDisp unit:', GFTB200.get_disp_unit(3))

print('\nPower off time: {} mins'.format(GFTB200.get_power_off_time()))
print('\nSet power off time to {} mins:'.format(GFTB200.set_power_off_time(1)))
print('\nPower off time: {} mins'.format(GFTB200.get_power_off_time()))

vers, id = GFTB200.get_sw_info()
print('\nSoftware info: v{}.{}'.format(vers, id))

GFTB200.get_sensor_info()

GFTB200.close()  # Close ALL open COM ports
