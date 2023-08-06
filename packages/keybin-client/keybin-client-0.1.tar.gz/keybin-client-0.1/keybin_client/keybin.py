from functools import wraps

import requests

from keybin_client import errors


def _ensure_token(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not kwargs.get('token'):
            kwargs['token'] = Keybin.get_token()
        return function(*args, **kwargs)
    return wrapper


def _ensure_configured(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        cls = args[0]
        if not cls.host or not cls.username or not cls.password:
            raise errors.ConfigurationError()
        return function(*args, **kwargs)
    return wrapper


class Keybin:

    host = None
    username = None
    password = None
    client_id = None

    def __init__(self, host, username, password, client_id=None):
        Keybin.configure(host, username, password, client_id)

    @classmethod
    def configure(cls, host, username, password, client_id=None):
        cls.host = host
        cls.username = username
        cls.password = password
        cls.client_id = client_id
        return cls

    @classmethod
    @_ensure_configured
    @errors.error_handler
    def __make_request(cls, method, endpoint, payload=None):
        url = "{}{}".format(cls.host, endpoint)
        resp = requests.request(method, url, json=payload)
        resp.raise_for_status()
        return resp.json()

    @classmethod
    @_ensure_configured
    def get_token(cls, client_id=None):
        payload = {
            'username': cls.username,
            'password': cls.password,
            'client_id': client_id or cls.client_id,
        }
        response_data = cls.__make_request('post', '/token', payload=payload)
        return response_data['token']['token']

    @classmethod
    @_ensure_configured
    @_ensure_token
    def get_keys(cls, token=None):
        endpoint = '/user/{token}/keys'.format(token=token)
        response_data = cls.__make_request('get', endpoint)
        return response_data['keys']

    @classmethod
    @_ensure_configured
    @_ensure_token
    def get_value_for_key(cls, key, token=None):
        endpoint = '/user/{token}/store/{key}'.format(token=token, key=key)
        response_data = cls.__make_request('get', endpoint)
        return response_data['value']

    @classmethod
    @_ensure_configured
    @_ensure_token
    def store_value_for_key(cls, key, value, token=None):
        payload = {
            'value': value
        }
        endpoint = '/user/{token}/store/{key}'.format(token=token, key=key)
        cls.__make_request('post', endpoint, payload=payload)
