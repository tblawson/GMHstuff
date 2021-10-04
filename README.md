# GMHstuff
A wrapper around GMH functions defined in GMH3x32E.dll (supplied with all Greisinger 3100N USB-to-serial interface cables). Updated to Python 3.

##Installation
```
pip install https://github.com/tblawson/GMHstuff/archive/master.zip#subdirectory=gmhstuff
```

##Example Usage
```
>>> import gmhstuff
>>> a_thermometer = gmhstuff.GMHSensor(1)  # Create thermometer object at COM1.
>>> a_thermometer.measure('T')
(21.28, '°C')  # Note: the measurement includes units!
``` 
