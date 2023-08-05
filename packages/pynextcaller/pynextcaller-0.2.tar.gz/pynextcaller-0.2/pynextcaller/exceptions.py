from requests import RequestException
from .constants import (
    DEFAULT_RATE_LIMIT_EXCEEDED_CODE, DEFAULT_RATE_LIMIT_LIMIT_HEADER, DEFAULT_RATE_LIMIT_RESET_HEADER
)


class HttpException(RequestException):
    """
    An error occurred while handling request.
    """
    MESSAGE_ERROR_TYPE = 'Error'

    def __init__(self, response, content=None, *args, **kwargs):
        super(HttpException, self).__init__(response=response, *args, **kwargs)
        self.content = content if content is not None else self._prepare_content()
        self.message = self._prepare_message()

    def _prepare_content(self):
        try:
            return self.response.json()
        except ValueError:
            return {}

    def _prepare_message(self):
        return '{} {}: {}'.format(self.response.status_code, self.MESSAGE_ERROR_TYPE, self.response.reason)


class ClientHttpException(HttpException):
    """
    Client side error occurred.
    """
    MESSAGE_ERROR_TYPE = 'Client Error'


class ServerHttpException(HttpException):
    """
    Server side error occurred.
    """
    MESSAGE_ERROR_TYPE = 'Server Error'


class TooManyRequestsException(ClientHttpException):
    """
    '429 Too Many Requests' error occurred.
    """

    def __init__(self, response, *args, **kwargs):
        super(TooManyRequestsException, self).__init__(response, *args, **kwargs)
        self.rate_limit = self.response.headers[DEFAULT_RATE_LIMIT_LIMIT_HEADER]
        self.reset_time = self.response.headers[DEFAULT_RATE_LIMIT_RESET_HEADER]


def handle_too_many_requests_error(response, content, *args, **kwargs):
    try:
        if content['error']['code'] == DEFAULT_RATE_LIMIT_EXCEEDED_CODE:
            raise TooManyRequestsException(response, content, *args, **kwargs)
        else:
            raise ClientHttpException(response, content, *args, **kwargs)
    except KeyError:
        raise HttpException(response, content, *args, **kwargs)
