#! /usr/bin/env python
# encoding: utf-8

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))


# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='coinsbill',
    version='1.0',
    description='Python interaction with the CoinsBill API.',
    long_description=long_description,
    url='https://www.coinsbill.com/developers',
    author='CoinsBill',
    author_email='support@coinsbill.com',
    license='Apache License, Version 2.0, January 2004',
    packages=['coinsbill', ],
    install_requires=['requests>=2.4.0'],
    keywords = ['coinsbill', 'bitcoin', 'payment'], 
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

