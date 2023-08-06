===
python thermometers
===

idea: read data from various thermometers

reality: we have one dallas 18s20 connected via 1wire what is mostly used on  RaspberryPi

PULL REQUEST FOR ANOTHER DEVICES ARE WELCOME

supported logger
----------------

'thermometer.d18s20.w1' write data from thermometer to logger as list of values, this allow to use i.e. fluent for
store data into graphite or another type of data storage.


instalation
------------
'''
pip install thermometer

'''

