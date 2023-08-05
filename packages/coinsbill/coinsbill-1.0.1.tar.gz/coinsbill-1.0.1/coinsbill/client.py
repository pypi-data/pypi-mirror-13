import json

from base import APIClient


class CoinsBillError(Exception):
    STATUS_MAP = {
        200: "OK: Success",
        202: "Accepted: Your request was accepted and the user was queued for processing.",
        401: "Not Authorized: either you need to provide authentication credentials, or the credentials provided aren't valid.",
        403: "Bad Request: your request is invalid, and we'll return an error message that tells you why. This is the status code returned if you've exceeded the rate limit (see below).",
        404: "Not Found: either you're requesting an invalid URI or the resource in question doesn't exist (ex: no such user in our system).",
        500: "Internal Server Error: we did something wrong.",
        501: "Not implemented.",
        502: "Bad Gateway: returned if CoinsBill is down or being upgraded.",
        503: "Service Unavailable: the CoinsBill servers are up, but are overloaded with requests. Try again later.",
    }

    def __init__(self, status, response=None):
        self.status = status
        self.response = response

    def __str__(self):
        return "%s (%s)" % (self.status, self.STATUS_MAP.get(self.status, 'Unknown error.'))

    def __repr__(self):
        return "%s(status=%s)" % (self.__class__.__name__, self.status)


class CoinsBillClient(APIClient):
    """
    """
    
    def _handle_response(self, response):
        if response.status_code > 299:
            raise CoinsBillError(response.status_code, response=response)

        return super(CoinsBillClient, self)._handle_response(response)

    def call(self, path, **params):
        return self._request('GET', path, params=params)

    



