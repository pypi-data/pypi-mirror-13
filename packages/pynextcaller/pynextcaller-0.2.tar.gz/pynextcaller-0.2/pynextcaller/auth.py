from __future__ import unicode_literals
from base64 import b64encode
from .constants import DEFAULT_PLATFORM_ACCOUNT_HEADER , DEFAULT_PLATFORM_ACCOUNT_ID


__all__ = (
    'BasicAuth',
    'PlatformBasicAuth',
    'PlatformAuthContextManager'
)


class BasicAuth(object):
    """Basic auth class"""

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_headers(self):
        """Prepare auth_headers"""
        value = b64encode(
            ("{0}:{1}".format(self.username, self.password)).encode('utf-8')
        ).decode('utf-8')
        return {'Authorization': 'Basic {0}'.format(value)}

    def __call__(self):
        return self.get_headers()


class PlatformBasicAuth(BasicAuth):
    """Platform API auth class"""

    def __init__(self, username, password):
        super(PlatformBasicAuth, self).__init__(username, password)
        self.account_id = DEFAULT_PLATFORM_ACCOUNT_ID

    def get_headers(self):
        base_headers = super(PlatformBasicAuth, self).get_headers()
        base_headers.update({DEFAULT_PLATFORM_ACCOUNT_HEADER: self.account_id})
        return base_headers

    def switch_account_id(self, account_id):
        self.account_id = account_id


class PlatformAuthContextManager(object):
    """
    ContextManager used for switching PlatformBasicAuth.account_id value
    to the account_id value passed to the NextCallerPlatformClient method.
    """

    def __init__(self, auth, account_id):
        self.auth = auth
        self.account_id = account_id

    def __enter__(self):
        self.auth.switch_account_id(self.account_id)

    def __exit__(self, exp_type, exp_value, traceback):
        self.auth.switch_account_id(DEFAULT_PLATFORM_ACCOUNT_ID)
