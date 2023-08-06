#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='androidicon',
    packages=['androidicon'],
    version='1.0.0',
    description='Create Android icons',
    author='Carlo Eduardo Rodriguez Espino',
    author_email='carloeduardorodriguez@gmail.com',
    url='https://github.com/CarloRodriguez/androidicon',
    download_url='https://github.com/CarloRodriguez/androidicon/archive/master.zip',
    keywords=['android', 'icon', 'icons', 'resize'],
    install_requires=[
        'Pillow',
    ]
)
