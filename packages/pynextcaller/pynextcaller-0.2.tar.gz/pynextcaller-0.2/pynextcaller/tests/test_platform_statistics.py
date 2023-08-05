from __future__ import unicode_literals
import json
import unittest
try:
    from unittest import mock
except ImportError:
    import mock
try:
    from .base import BasePlatformTestCase
    from .test_by_phone import PHONE_JSON_RESULT_EXAMPLE
except (ValueError, ImportError):
    from pynextcaller.tests.base import BasePlatformTestCase
    from pynextcaller.tests.test_by_phone import PHONE_JSON_RESULT_EXAMPLE


PLATFORM_STATISTICS_JSON_RESULT_EXAMPLE = '''
{
    "object_list": [
        {
            "id": "test",
            "first_name": "",
            "last_name": "",
            "company_name": "",
            "email": "",
            "number_of_operations": 3,
            "billed_operations": {
                "2014-11": 3
            },
            "total_operations": {
                "2014-11": 3
            },
            "object": "account",
            "resource_uri": "/v2/accounts/test/"
        }
    ],
    "page": 1,
    "has_next": false,
    "total_pages": 1,
    "object": "page",
    "total_platform_operations": {
        "2014-11": 3
    },
    "billed_platform_operations": {
        "2014-11": 3
    }
}
'''


PLATFORM_STATISTICS_ACCOUNT_JSON_RESULT_EXAMPLE = '''
{
    "id": "test",
    "first_name": "",
    "last_name": "",
    "company_name": "",
    "email": "",
    "number_of_operations": 3,
    "billed_operations": {
        "2014-11": 3
    },
    "total_operations": {
        "2014-11": 3
    },
    "object": "account",
    "resource_uri": "/v2/accounts/test/"
}
'''


PLATFORM_ACCOUNT_CREATE_JSON_REQUEST_EXAMPLE = {
    "id": "test_username",
    "first_name": "Clark",
    "last_name": "Kent",
    "email": "test@test.com"
}


PLATFORM_ACCOUNT_CREATE_WRONG_JSON_REQUEST_EXAMPLE = {
    "first_name": "Clark",
    "last_name": "Kent",
    "email": "test@test.com"
}


PLATFORM_ACCOUNT_CREATE_WRONG_RESULT = '''
{
    "error": {
        "message": "Validation Error",
        "code": "422",
        "type": "Unprocessable Entity",
        "description": {
            "id": [
                "This field cannot be blank."
            ]
        }
    }
}
'''


PLATFORM_ACCOUNT_UPDATE_JSON_REQUEST_EXAMPLE = {
    "first_name": "Clark",
    "last_name": "Kent",
    "email": "test@test.com"
}


PLATFORM_ACCOUNT_UPDATE_WRONG_JSON_REQUEST_EXAMPLE = {
    "first_name": "Clark",
    "last_name": "Kent",
    "email": "XXXX"
}


PLATFORM_ACCOUNT_UPDATE_WRONG_RESULT = '''
{
    "error": {
        "message": "Validation Error",
        "code": "422",
        "type": "Unprocessable Entity",
        "description": {
            "email": [
                "Enter a valid email address."
            ]
        }
    }
}
'''


class PlatformTestCase(BasePlatformTestCase):

    def test_get_by_phone_without_account_id(self):
        phone = 1231231231
        self.assertRaises(TypeError, self.client.get_by_phone, phone)

    def test_get_by_phone_with_account_id(self):
        phone = 1231231231
        account_id = 'test_username'
        self.patch_http_request(PHONE_JSON_RESULT_EXAMPLE)
        res = self.client.get_by_phone(phone, account_id=account_id)
        self.assertTrue(res['records'])
        self.assertEqual(res['records'][0]['email'], 'demo@nextcaller.com')
        self.assertEqual(res['records'][0]['first_name'], 'Jerry')
        self.assertEqual(res['records'][0]['last_name'], 'Seinfeld')

    def test_get_all_statistics(self):
        self.patch_http_request(PLATFORM_STATISTICS_JSON_RESULT_EXAMPLE)
        res = self.client.get_platform_statistics()
        self.assertTrue(res['billed_platform_operations'])
        self.assertTrue(res['total_platform_operations'])
        self.assertEqual(res['object_list'][0]['id'], 'test')
        self.assertEqual(res['object_list'][0]['number_of_operations'], 3)

    def test_get_users_statistics(self):
        self.patch_http_request(PLATFORM_STATISTICS_ACCOUNT_JSON_RESULT_EXAMPLE)
        res = self.client.get_platform_account('test')
        self.assertEqual(res['id'], 'test')
        self.assertEqual(res['number_of_operations'], 3)

    def test_create_platform_account(self):
        fake_response = self.FakeResponse()
        fake_response.status_code = 201
        self.patch_http_request(fake_response)
        res = self.client.create_platform_account(PLATFORM_ACCOUNT_CREATE_JSON_REQUEST_EXAMPLE)
        self.assertEqual(res.status_code, 201)

    def test_create_wrong_platform_account(self):
        fake_response = self.FakeResponse()
        fake_response.status_code = 400
        fake_response.content = PLATFORM_ACCOUNT_CREATE_WRONG_RESULT
        self.patch_http_request(fake_response)
        res = self.client.create_platform_account(PLATFORM_ACCOUNT_CREATE_WRONG_JSON_REQUEST_EXAMPLE)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            json.loads(res.content)['error']['description']['id'][0], 'This field cannot be blank.'
        )

    def test_update_platform_account(self):
        account_id = 'test_username'
        self.patch_http_request(self.fake_response)
        res = self.client.update_platform_account(PLATFORM_ACCOUNT_UPDATE_JSON_REQUEST_EXAMPLE, account_id)
        self.assertEqual(res.status_code, 204)

    def test_update_wrong_platform_account(self):
        account_id = 'test_username'
        fake_response = self.FakeResponse()
        fake_response.status_code = 400
        fake_response.content = PLATFORM_ACCOUNT_UPDATE_WRONG_RESULT
        self.patch_http_request(fake_response)
        res = self.client.update_platform_account(PLATFORM_ACCOUNT_UPDATE_WRONG_JSON_REQUEST_EXAMPLE, account_id)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            json.loads(res.content)['error']['description']['email'][0], 'Enter a valid email address.'
        )


if __name__ == '__main__':
    unittest.main()
