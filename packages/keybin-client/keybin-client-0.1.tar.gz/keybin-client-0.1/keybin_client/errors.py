import logging
from functools import wraps

import requests


def error_handler(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except requests.HTTPError as he:
            logging.exception("Error occurred while calling remote endpoint")
            res = he.response
            url = res.url
            if res.status_code == 403:
                raise AuthenticationError(url)
            if res.status_code == 404:
                raise NotFoundError(url)
            if res.status_code == 500:
                raise ServerError(url)
            raise KeybinError(url)

    return wrapper


class ConfigurationError(Exception):
    def __init__(self):
        message = ("Client is not configured properly, please call "
                   "keybin_client.init(...)")
        super(ConfigurationError, self).__init__(message)


class KeybinError(Exception):
    def __init__(self, url):
        self.message = 'An unknown error occurred with URL [{}]'.format(url)


class AuthenticationError(KeybinError):
    def __init__(self, url):
        self.message = ('Error occurred while trying to authenticate '
                        'with URL [{}]'.format(url))


class NotFoundError(KeybinError):
    def __init__(self, url):
        self.message = ('Could not find specified resource '
                        'with URL [{}]'.format(url))


class ServerError(KeybinError):
    def __init__(self, url):
        self.message = ('Server error occurred on remote '
                        'endpoint with URL [{}]'.format(url))
