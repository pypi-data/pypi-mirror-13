from distutils.core import setup, Extension

ds18b20_arm6 = Extension('r1_ds18b20',
                    libraries= ['rt'],             
                    sources = ['ds18b20pi/r1_ds18b20.c'])       
ds18b20_arm7 = Extension('r2_ds18b20',
                    libraries= ['rt'],
                    sources = ['ds18b20pi/r2_ds18b20.c'])
                    

setup (name = 'ds18b20pi',
       version = '0.3',
       description = 'ds18b20 userspace library for Rapsberry Pi',       
       long_description='''
* no kernel patches needed
* any GPIOs allowed
* any number of GPIOs allowed

Make sure you have:

*build-essential package
*python-dev or python3-dev package
*Raspberry Pi device
*sudo access for the script

Usage:

import time

import ds18b20pi

ds18b20pi.bus.convert(pin)

time.sleep(0.75)

temperatureDict = ds18b20pi.bus.search(pin)
    
The Package is fresh and installation could be buggy,
sorry for any inconvenience.
    ''',
       
       url = 'https://github.com/gladkikhartem/ds18b20pi',
       author='Gladkikh Artem',
       author_email='artem.and.co@gmail.com',
       license='GPL',
       packages=['ds18b20pi'],
       ext_modules = [ds18b20_arm6,ds18b20_arm7])
       
