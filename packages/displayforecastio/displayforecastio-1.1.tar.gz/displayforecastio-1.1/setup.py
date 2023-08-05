#!/usr/bin/env python

from setuptools import setup, find_packages

REQUIREMENTS = [line.strip() for line in
                open("requirements.txt").readlines()]
setup(
    name='displayforecastio',
    version='1.1',
    author='Matt Bachmann',
    url='https://github.com/Bachmann1234/displayforecastio',
    description='Display the current weather in your terminal',
    license='Apache 2.0',
    packages=find_packages(),
    install_requires=REQUIREMENTS,
    entry_points={
        'console_scripts': ['forecastio = displayforecastio.app:run'],
    }
)
