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
```
pip install thermometer

```

basic usage
-----------
```
>>> from thermometer.dallas_18s20 import w1
>>> w = w1.dallas_18s20()
>>> w.get_temps_aliases()
[('870155007fff0c108a', 24.437), ('080255007fff0c10a5', 32.5)]

```


alias usage
-----------
```
>>> from thermometer.dallas_18s20 import w1
>>> w = w1.dallas_18s20()
>>> w.alias('870155007fff0c108a', 'temp1')
>>> w.get_temps_aliases()
[('temp1', 24.437), ('080255007fff0c10a5', 32.5)]

```
