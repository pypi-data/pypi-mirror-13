#! /usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import

__version__ = "1.0.1"

api_key = None
api_base = 'https://www.coinsbill.com/api/'

from .client import CoinsBillClient 

from .resource import ( 
    Invoice,
    CoinsBill
    )