#! /usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import

import os
import io
import json
import requests

from .client import CoinsBillClient

try:
    basestring
except NameError:
    basestring = str

class ListResource(CoinsBillClient):

    def get(self, id=None):
        path = self.ENDPOINT if id is None else '%s/%s' % (self.ENDPOINT, id)

        return self._request('GET', path)

class CreateResource(CoinsBillClient):

    def create(self, **params):
        uri = self.BASE_URL + self.ENDPOINT
        data = dict(**(params or {}))
        r = self._get_response(uri, data)

        return r if r.status_code == 201 else self._get_response(uri, data)

    def _get_response(self, uri, data):
        return self.client.post(uri, data=json.dumps(data))

class UpdateResource(CoinsBillClient):

    def update(self, id=None, **params):
        path = self.ENDPOINT if id is None else '%s/%s' % (self.ENDPOINT, id)
        uri = self.BASE_URL + path
        data = dict(**(params or {}))
        
        r  = self.client.put(uri, data=json.dumps(data))
        return r

    def _get_response(self, uri, data):
        return self.client.post(uri, data=json.dumps(data))

class Invoice(ListResource, CreateResource, UpdateResource):
    """Handle Invoice to the CoinsBill API."""
    ENDPOINT = 'invoice'

class Button(ListResource, CreateResource, UpdateResource):
    """Handle Payment Buttons to the CoinsBill API."""
    ENDPOINT = 'buttons'

class Customer(ListResource):
    """Handle Customer to the CoinsBill API."""
    ENDPOINT = 'customer'

class Settlement(ListResource):
    """Handle Payment Settlement to the CoinsBill API."""
    ENDPOINT = 'settlement'

class Rates(ListResource):
    """Handle Exchange Rates to the CoinsBill API."""
    ENDPOINT = 'rates'

class ResourceMixin(Invoice):
    """Combined Mixin API."""
    pass


class CoinsBill:

    def __init__(self, api_key):
        self.invoice = Invoice(api_key)
        self.button = Button(api_key)
        self.customer = Customer(api_key)
        self.settlement = Settlement(api_key)
        self.rates = Rates(api_key)

    def invoice(self):
        return self.invoice

    def button(self):
        return self.button

    def customer(self):
        return self.customer

    def settlement(self):
        return self.settlement

    def rates(self):
        return self.rates