from distutils.core import setup, Extension

ds18b20_arm6 = Extension('r1_ds18b20',
                    libraries= ['rt'],             
                    sources = ['ds18b20pi/r1_ds18b20.c'])       
ds18b20_arm7 = Extension('r2_ds18b20',
                    libraries= ['rt'],
                    sources = ['ds18b20pi/r2_ds18b20.c'])
                    

setup (name = 'ds18b20pi',
       version = '0.1',
       description = 'ds18b20 userspace library for Rapsberry Pi',       
       long_description=''' 
       This library is userspace and doesn't need any kernel patches or modifications
       
       You are free to use any GPIOs available. (GPIOs are numbered in BCM format)
       You are free to use multiple GPIOs at the same time.
       
       Make sure you have compiler,  python-dev  or python3-dev package installed, so that
       Distutils could compile C extension modules.
       
       Usage:
       
       import time
       import ds18b20pi
       ds18b20pi.bus.convert(pin)
       time.sleep(0.75)
       for id, temperature in ds18b20pi.bus.search(pin).iteritems():
            print(id,temperature)
       ''',
       
       url = 'https://github.com/gladkikhartem/ds18b20pi',
       author='Gladkikh Artem',
       author_email='artem.and.co@gmail.com',
       license='GPL',
       packages=['ds18b20pi'],
       ext_modules = [ds18b20_arm6,ds18b20_arm7])
       
