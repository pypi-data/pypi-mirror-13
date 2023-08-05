from __future__ import unicode_literals
from .auth import *
from .constants import *
from .utils import *
from .transport import make_http_request


class NextCallerClient(object):
    """The NextCaller API client"""

    def __init__(self, username, password, sandbox=False):
        """
        Initialize NextCaller client with API username
        and password for Basic Authorization

        :param username:str     API username
        :param password:str     API password
        :param sandbox:bool     If True - sandbox mode is turned on
        """
        self.auth = BasicAuth(username, password)
        self.sandbox = bool(sandbox)
        self.base_url = prepare_base_url(sandbox)

    @check_kwargs
    def get_by_phone(self, phone, **kwargs):
        """
        Get profile by a phone number

        :param phone:str    10 digit phone number
        :param kwargs:dict  Additional params for request

        :return:list        Serialised response as list
        """
        url_params = dict({
            'phone': phone,
            'format': JSON_RESPONSE_FORMAT,
        }, **kwargs)
        url = prepare_url(self.base_url, 'records/', url_params=url_params)
        response = make_http_request(self.auth, url, method='GET')
        return default_handle_response(response)

    @check_kwargs
    def get_by_profile_id(self, profile_id, **kwargs):
        """
        Get profile by a profile id

        :param profile_id:str   Profile identifier from get_by_phone
                                response with length in 30 symbols
        :param kwargs:dict      Additional params for request

        :return:dict            Serialised response as dictionary
        """
        url_params = dict({
            'format': JSON_RESPONSE_FORMAT
        }, **kwargs)
        url = prepare_url(self.base_url, 'users/{0}/'.format(profile_id),
                          url_params=url_params)
        response = make_http_request(self.auth, url, method='GET')
        return default_handle_response(response)

    @check_kwargs
    def get_by_name_address(self, name_address_data, **kwargs):
        """
        Get profile by name and address

        :param name_address_data:dict       Dictionary with name and address data for search
        :param kwargs:dict                  Additional params for request

        :return:dict                        Serialised response as dictionary
        """
        name_address_data.update(kwargs)
        url_params = dict({
            'format': JSON_RESPONSE_FORMAT
        }, **name_address_data)
        url = prepare_url(self.base_url, 'records/', url_params=url_params)
        response = make_http_request(self.auth, url, method='GET')
        return default_handle_response(response)

    @check_kwargs
    def get_by_email(self, email, **kwargs):
        """
        Get profile by an email

        :param email:str        The complete email address you want to look up a profile for
        :param kwargs:dict      Additional params for request

        :return:dict            Serialised response as dictionary
        """
        url_params = dict({
            'email': email,
            'format': JSON_RESPONSE_FORMAT
        }, **kwargs)
        url = prepare_url(self.base_url, 'records/', url_params=url_params)
        response = make_http_request(self.auth, url, method='GET')
        return default_handle_response(response)

    @check_kwargs
    def update_by_profile_id(self, profile_id, profile_data, **kwargs):
        """
        Update profile by a profile id

        :param profile_id:str   Profile identifier from get_by_phone
                                response with length in 30 symbols
        :param profile_data:dict        Data to update as dictionary
        :param kwargs:dict              Additional params for request

        :return:str                     HTTP Body of response as text
        """
        url_params = dict({
            'format': JSON_RESPONSE_FORMAT
        }, **kwargs)
        url = prepare_url(self.base_url, 'users/{0}/'.format(profile_id),
                          url_params=url_params)
        profile_data = prepare_json_data(profile_data)
        return make_http_request(
            self.auth, url, data=profile_data, method='POST', content_type=JSON_CONTENT_TYPE
        )

    @check_kwargs
    def get_fraud_level(self, phone, **kwargs):
        """
        Get fraud level for a phone number

        :param phone:str    10 digit phone number
        :param kwargs:dict  Additional params for request

        :return:dict        Serialised response as dictionary
        """
        url_params = dict({
            'phone': phone,
            'format': JSON_RESPONSE_FORMAT,
        }, **kwargs)
        url = prepare_url(self.base_url, 'fraud/', url_params=url_params)
        response = make_http_request(self.auth, url, method='GET')
        return default_handle_response(response)


class NextCallerPlatformClient(NextCallerClient):
    """The NextCaller platform API client"""

    def __init__(self, username, password, sandbox=False):
        """
        Initialize NextCaller client with API username
        and password for Basic Authorization

        :param username:str     API username
        :param password:str     API password
        :param sandbox:bool     If True - sandbox mode is turned on
        """
        super(NextCallerPlatformClient, self).__init__(username, password, sandbox)
        self.auth = PlatformBasicAuth(username, password)

    @check_kwargs
    def get_by_phone(self, phone, account_id=DEFAULT_PLATFORM_ACCOUNT_ID, **kwargs):
        """
        Get profile by a phone number

        :param phone:str                10 digit phone number
        :param account_id:str           Name of platform account
        :param kwargs:dict              Additional params for request

        :return:list                    Serialised response as list
        """
        with PlatformAuthContextManager(self.auth, account_id):
            return super(NextCallerPlatformClient, self).get_by_phone(phone, **kwargs)

    @check_kwargs
    def get_by_profile_id(self, profile_id, account_id=DEFAULT_PLATFORM_ACCOUNT_ID, **kwargs):
        """
        Get profile by a profile id

        :param profile_id:str           Profile identifier from get_by_phone
                                        response with length in 30 symbols
        :param account_id:str           Name of platform account
        :param kwargs:dict              Additional params for request

        :return:dict                    Serialised response as dictionary
        """
        with PlatformAuthContextManager(self.auth, account_id):
            return super(NextCallerPlatformClient, self).get_by_profile_id(profile_id, **kwargs)

    @check_kwargs
    def get_by_name_address(self, name_address_data, account_id=DEFAULT_PLATFORM_ACCOUNT_ID, **kwargs):
        """
        Get profile by name and address

        :param name_address_data:dict       Dictionary with name and address data for search
        :param account_id:str               Name of platform account
        :param kwargs:dict                  Additional params for request

        :return:dict                        Serialised response as dictionary
        """
        with PlatformAuthContextManager(self.auth, account_id):
            return super(NextCallerPlatformClient, self).get_by_name_address(name_address_data, **kwargs)

    @check_kwargs
    def get_by_email(self, email, account_id=DEFAULT_PLATFORM_ACCOUNT_ID, **kwargs):
        """
        Get profile by a email

        :param email:str        The complete email address you want to look up a profile for
        :param account_id:str   Name of platform account
        :param kwargs:dict      Additional params for request

        :return:dict            Serialised response as dictionary
        """
        with PlatformAuthContextManager(self.auth, account_id):
            return super(NextCallerPlatformClient, self).get_by_email(email, **kwargs)

    @check_kwargs
    def update_by_profile_id(self, profile_id, profile_data, account_id=DEFAULT_PLATFORM_ACCOUNT_ID, **kwargs):
        """
        Update profile by a profile id

        :param profile_id:str           Profile identifier from get_by_phone
                                        response with length in 30 symbols
        :param profile_data:dict        Data to update as dictionary
        :param account_id:str           Name of platform account
        :param kwargs:dict              Additional params for request

        :return:str                     HTTP Body of response as text
        """
        with PlatformAuthContextManager(self.auth, account_id):
            return super(NextCallerPlatformClient, self).update_by_profile_id(profile_id, profile_data, **kwargs)

    def get_platform_statistics(self, page=1, **kwargs):
        """
        Get platform statistics as dictionary
        with list of platform accounts

        :param page:int     Number of page with users
        :param kwargs:dict  Additional params for request

        :return:dict        Dictionary with platform statistic
        """
        url_params = dict({
            'page': page,
            'format': JSON_RESPONSE_FORMAT,
        }, **kwargs)
        url = prepare_url(
            self.base_url, 'accounts/', url_params=url_params)
        response = make_http_request(self.auth, url, method='GET')
        return default_handle_response(response)

    def get_platform_account(self, account_id, **kwargs):
        """
        Get platform account detail data by account ID

        :param account_id:str          Name of platform account

        :return:dict                   platform account detail data
        """
        url_params = dict({
            'format': JSON_RESPONSE_FORMAT
        }, **kwargs)
        url_path = 'accounts/{0}/'.format(account_id)
        url = prepare_url(self.base_url, url_path, url_params=url_params)
        response = make_http_request(self.auth, url, method='GET')
        return default_handle_response(response)

    def create_platform_account(self, account_data):
        """
        Create platform account

        :param account_data:dict        Initial data to create new platform account as dictionary

        :return:str                     HTTP Body of response as text
        """
        url_params = {
            'format': JSON_RESPONSE_FORMAT
        }
        url = prepare_url(
            self.base_url, 'accounts/',
            url_params=url_params)
        account_data = prepare_json_data(account_data)
        return make_http_request(
            self.auth, url, data=account_data, method='POST', content_type=JSON_CONTENT_TYPE
        )

    def update_platform_account(self, account_data, account_id):
        """
        Update platform account data

        :param account_data:dict        Data to update as dictionary
        :param account_id:str           Name of platform account

        :return:str                     HTTP Body of response as text
        """
        url_params = {
            'format': JSON_RESPONSE_FORMAT
        }
        url = prepare_url(
            self.base_url, 'accounts/{0}/'.format(account_id),
            url_params=url_params)
        account_data = prepare_json_data(account_data)
        return make_http_request(
            self.auth, url, data=account_data, method='PUT', content_type=JSON_CONTENT_TYPE
        )

    def get_fraud_level(self, phone, account_id=DEFAULT_PLATFORM_ACCOUNT_ID, **kwargs):
        """
        Get fraud level for a phone

        :param phone:str                10 digit phone number
        :param account_id:str           Name of platform account
        :param kwargs:dict              Additional params for request

        :return:dict                    Serialised response as dictionary
        """
        with PlatformAuthContextManager(self.auth, account_id):
            return super(NextCallerPlatformClient, self).get_fraud_level(phone, **kwargs)
