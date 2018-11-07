# Impedance_raspi_ad5933
Python module for AD5933, using smbus on raspi. 

This repository contains code that is not tested, will not be updated and should be completely rewritten.

## Code example
The example below is not tested. And probably won't work.  
```
import pyAD5933

sensor = AD5933(16.0)
sensor.init()
sensor.set_PGA_gain(5)
sensor.set_ex_voltage(4)
sensor.set_settling_time(255, 2)
sensor.make_inp_measure(1e3, 9, 1e3)
temperature = sensor.make_temp_measure()
```