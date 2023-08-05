from __future__ import unicode_literals
import functools
import json
import re
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode
try:
    unicode = unicode
except NameError:
    # 'unicode' is undefined, must be Python 3
    str = str
    unicode = str
    bytes = bytes
    basestring = (str, bytes)
else:
    # 'unicode' exists, must be Python 2
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring
from .constants import *


__all__ = (
    'default_handle_response',
    'prepare_url',
    'prepare_base_url',
    'prepare_json_data',
    'check_kwargs',
)


def _handle_json_response(resp):
    return json.loads(resp)


def prepare_json_data(data):
    try:
        return json.dumps(data)
    except (TypeError, ValueError):
        return data


def default_handle_response(resp):
    return _handle_json_response(resp)


def prepare_url(base_url, path, url_params=None):
    """Prepare url from path and params"""
    if url_params is None:
        url_params = {}
    url = '{0}{1}'.format(base_url,  path)
    if not url.endswith('/'):
        url += '/'
    url_params_str = urlencode(url_params)
    if url_params_str:
        url += '?' + url_params_str
    return url


def prepare_base_url(sandbox=False, version=DEFAULT_API_VERSION):
    """Prepare url from path and params"""
    base_url = BASE_URL.format(version) if not sandbox \
        else BASE_SANDBOX_URL.format(version)
    return base_url


def check_kwargs(*all_args):

    def dec(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for kw in kwargs:
                if kw not in all_args:
                    raise ValueError(
                        'Keyword argument {0} is not allowed'.format(kw))
            return func(*args, **kwargs)
        return wrapper
    return dec


check_kwargs = check_kwargs('data', 'account_id')
