#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='androidicon',
    packages=['androidicon'],
    version='1.0.3',
    description='Create Android icons',
    author='Carlo Eduardo Rodriguez Espino',
    author_email='carloeduardorodriguez@gmail.com',
    url='https://github.com/CarloRodriguez/androidicon',
    download_url='https://github.com/CarloRodriguez/androidicon/archive/master.zip',
    keywords='android icon icons resize',
    license='GPL',
    entry_points={
        'console_scripts': [
            'androidicon = androidicon.__main__:main'
        ]
    },
    install_requires=[
        'Pillow',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 2.7',
    ],
)
