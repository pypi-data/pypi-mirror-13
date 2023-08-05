#! /usr/bin/env python
# encoding: utf-8

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup



setup(name='coinsbill',
    version='1.0.1',
    description='Python interaction with the CoinsBill API.',
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

