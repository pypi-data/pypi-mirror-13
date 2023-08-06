#!/usr/bin/env python
from setuptools import setup

setup(
    name='Greg',
    version='0.4.6',
    install_requires=['feedparser'],
    description='A command-line podcast aggregator',
    author='Manolo Martínez',
    author_email='manolo@austrohungaro.com',
    url='https://github.com/manolomartinez/greg',
    packages=['greg'],
    entry_points={'console_scripts': ['greg = greg.gregparser:main']},
    package_data={'greg': ['data/*.conf']},
    license='GPLv3'
)
