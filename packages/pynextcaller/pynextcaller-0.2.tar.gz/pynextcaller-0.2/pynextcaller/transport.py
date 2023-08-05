from __future__ import unicode_literals
import json
import requests

from .constants import *
from .exceptions import *


__all__ = (
    'api_request',
    'make_http_request',
)


def _to_json(content):
    try:
        return json.loads(content)
    except (TypeError, ValueError):
        return content


def _prepare_request_data(
        data=None, headers=None, method='GET',
        timeout=None, ssl_verify=True):
    if headers is None:
        headers = {}
    kwargs = {}
    if timeout is None:
        timeout = DEFAULT_REQUEST_TIMEOUT
    kwargs['timeout'] = timeout
    if method == 'GET':
        kwargs['params'] = data
    else:
        kwargs['data'] = data
    kwargs['headers'] = headers
    kwargs['allow_redirects'] = True
    kwargs['verify'] = ssl_verify
    return kwargs


def _raise_http_error(response):
    """
    Raises `HttpException` subclass, if an error occurred while handling request.
    """
    status_code = response.status_code
    try:
        content = response.json()
    except ValueError:
        content = {}

    if status_code == 429:
        handle_too_many_requests_error(response, content)
    elif 400 <= status_code < 500:
        raise ClientHttpException(response, content)
    elif 500 <= status_code < 600:
        raise ServerHttpException(response, content)


def api_request(url, data=None, headers=None, method='GET', timeout=None, ssl_verify=True):
    kwargs = _prepare_request_data(
        data=data, headers=headers, method=method,
        timeout=timeout, ssl_verify=ssl_verify
    )
    response = requests.request(method, url, **kwargs)
    if response.status_code >= 400:
        _raise_http_error(response)
    return response.text


def _build_headers(auth, user_agent=None, content_type=None):
    headers = auth.get_headers()
    headers['Connection'] = 'Keep-Alive'
    if content_type is not None:
        headers['Content-Type'] = content_type
    if user_agent is not None:
        headers['User-Agent'] = user_agent
    return headers


def make_http_request(auth, url, data=None, method='GET', user_agent=None, content_type=None):
    if data is None:
        data = {}
    if user_agent is None:
        user_agent = DEFAULT_USER_AGENT
    headers = _build_headers(
        auth, user_agent=user_agent, content_type=content_type)
    requests_kwargs = {
        'method': method,
        'headers': headers,
        'data': data
    }
    response = api_request(url, **requests_kwargs)
    return response
