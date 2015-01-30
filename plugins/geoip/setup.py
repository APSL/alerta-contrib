#!/usr/bin/env python

from setuptools import setup, find_packages

version = '0.1.0'

setup(
    name="alerta-geoip",
    version=version,
    description='Alerta plugin for GeoIP Lookup',
    url='https://github.com/alerta/alerta-contrib',
    license='Apache License 2.0',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    packages=find_packages(),
    py_modules=['geoip'],
    install_requires=[
        'requests',
        'alerta-server'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'alerta.plugins': [
            'geoip = geoip:GeoLocation'
        ]
    }
)
