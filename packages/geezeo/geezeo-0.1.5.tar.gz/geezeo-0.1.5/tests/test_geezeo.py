#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_geezeo
----------------------------------

Tests for `geezeo` module.
"""

import unittest
import geezeo
import six
from pytest import raises


class TestSDK(unittest.TestCase):

    url = 'https://geez3o.geezeo.com'
    user_id = 'david-donna-amston'
    api_key = ('b695f27def0277d34c726576772c5223b84bbd43e23391c5da2f344f5'
               '3c3e1a41cbcfe93104d010790d84c376ca25863a502039c6fe9c034da'
               '73f6edb7cd02e9')

    def test_successful_sdk_creation(self):
        geezeo.SDK(self.api_key, self.user_id, self.url)

    def test_url_is_set_correctly(self):
        sdk = geezeo.SDK(self.api_key, self.user_id, self.url)
        assert sdk.url == self.url

    def test_user_is_set_correctly(self):
        "Make sure we get a User with the correct user_id."
        sdk = geezeo.SDK(self.api_key, self.user_id, self.url)
        assert isinstance(sdk.user, geezeo.User)
        assert sdk.user.id, self.user_id

    def test_unsuccessful_sdk_creation_with_bad_api_key(self):
        "Use a mangled key, and expect failure."
        with raises(geezeo.UnauthorizedError):
            geezeo.SDK(self.api_key[10:], self.user_id, self.url)

    def test_unsuccessful_sdk_creation_with_bad_user_id(self):
        "Use a mangled key, and expect failure."
        with raises(geezeo.DoesNotExistError):
            geezeo.SDK(self.api_key, self.user_id[3:], self.url)

    def test_unsuccessful_sdk_creation_with_bad_url(self):
        "Use a mangled key, and expect failure."
        with raises(geezeo.NetworkError):
            geezeo.SDK(self.api_key, self.user_id, self.url + '.horse')

    def test_unsuccessful_sdk_creation_with_bad_existing_url(self):
        "Use a mangled key, and expect failure."
        with raises(geezeo.DoesNotExistError):
            geezeo.SDK(self.api_key, self.user_id, 'https://www.google.com')


class TestAggregation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.sdk = geezeo.SDK(TestSDK.api_key, TestSDK.user_id, TestSDK.url)

    def test_get_all_fails_with_non_integer_page(self):
        with raises(Exception):
            self.sdk.get_all_institutions(page='1')

    def test_get_all_fails_with_zero_page(self):
        with raises(Exception):
            self.sdk.get_all_institutions(page=0)

    def test_get_all_fails_with_negative_one_page(self):
        with raises(Exception):
            self.sdk.get_all_institutions(page=-1)

    def test_get_all_is_empty_with_absurd_page(self):
        results = self.sdk.get_all_institutions(page=1000000)
        assert isinstance(results, geezeo.PagedResults)
        assert results.data == []

    def test_get_all_returns_paged_results(self):
        results = self.sdk.get_all_institutions()
        assert isinstance(results, geezeo.PagedResults)
        assert len(results) > 0
        assert all(isinstance(p, geezeo.AuthPrompt) for p in results)

    def test_get_all_returns_different_results_for_different_pages(self):
        r1 = self.sdk.get_all_institutions(page=1)
        r2 = self.sdk.get_all_institutions(page=2)
        assert r1.data != r2.data
        assert r1.current_page == 1
        assert r2.current_page == 2

    def test_get_featured_institutions_returns_prompt_list(self):
        prompts = self.sdk.get_featured_institutions()
        assert isinstance(prompts, list)
        assert len(prompts) > 1
        assert all(isinstance(p, geezeo.AuthPrompt) for p in prompts)

    def test_gibberish_search_string_yields_no_results(self):
        result = self.sdk.search_institutions('alkdfoqweifyow764ryoaiu')
        assert isinstance(result, geezeo.PagedResults)
        assert len(result) == 0

    def test_bad_search_scope_raises_exception(self):
        for bad_scope in [1, 'foo', ' url ']:
            with raises(Exception):
                self.sdk.search_institutions('bank', scope=bad_scope)

    def test_bad_search_page_raises_exception(self):
        for bad_page in [-1, 0, 1.2, None]:
            with raises(Exception):
                self.sdk.search_institutions('bank', page=bad_page)

    def test_high_search_page_yields_no_results(self):
        results = self.sdk.search_institutions('bank', page=1000000)
        assert isinstance(results, geezeo.PagedResults)
        assert results.data == []

    def test_search_scope_can_be_absent(self):
        self.sdk.search_institutions('bank')

    def test_search_scope_can_be_url(self):
        self.sdk.search_institutions('bank', scope='url')

    def test_search_scope_can_be_name(self):
        self.sdk.search_institutions('bank', scope='name')

    def test_search_defaults_to_first_page(self):
        result = self.sdk.search_institutions('bank')
        assert result.current_page == 1

    def test_search_page_can_be_changed(self):
        page_one = self.sdk.search_institutions('bank')
        result = self.sdk.search_institutions('bank', page=2)
        assert result.current_page == 2
        assert result.data != page_one.data

    def test_submit_key_serialization(self):
        prompt = geezeo.AuthPrompt({
            "id": 2,
            "fi_id": 20349,
            "name": "CashEdge Test Bank (Agg) - Retail Non 2FA",
            "url": "https://cashbank.cashedge.com/.../LoginPage.jsp",
            "ce_login_parameters": [
                {
                    "id": 3,
                    "parameter_id": "42971",
                    "parameter_caption": "UserName",
                    "parameter_type": "login",
                    "parameter_max_length": 20
                },
                {
                    "id": 4,
                    "parameter_id": "42972",
                    "parameter_caption": "Password",
                    "parameter_type": "password",
                    "parameter_max_length": 20
                }
            ]
        })
        assert type(prompt.submit_key) is six.text_type

    def test_submit_key_deserialization(self):
        prompt = geezeo.AuthPrompt({
            "id": 2,
            "fi_id": 20349,
            "name": "CashEdge Test Bank (Agg) - Retail Non 2FA",
            "url": "https://cashbank.cashedge.com/.../LoginPage.jsp",
            "ce_login_parameters": [
                {
                    "id": 3,
                    "parameter_id": "42971",
                    "parameter_caption": "UserName",
                    "parameter_type": "login",
                    "parameter_max_length": 20
                },
                {
                    "id": 4,
                    "parameter_id": "42972",
                    "parameter_caption": "Password",
                    "parameter_type": "password",
                    "parameter_max_length": 20
                }
            ]
        })
        key_data = geezeo.decode_submit_key(prompt.submit_key)
        assert key_data == {
            'type': 'auth',
            'id': '2',
            'name': 'CashEdge Test Bank (Agg) - Retail Non 2FA',
            'parameters': [
                {
                    'key': '42971',
                    'caption': 'UserName',
                    'type': 'login',
                    'max_length': 20,
                },
                {
                    'key': '42972',
                    'caption': 'Password',
                    'type': 'password',
                    'max_length': 20,
                },
            ]
        }

    def test_non_mfa_login(self):
        prompts = self.sdk.search_institutions('CashEdge Test Bank Agg')
        for p in prompts:
            if p.name == "CashEdge Test Bank (Agg) - Retail Non 2FA":
                prompt = p
                break
        auth_info = {}
        for param in prompt.parameters:
            if param.caption == 'UserName':
                auth_info[param.key] = 'script1'
            elif param.caption == 'Password':
                auth_info[param.key] = 'cashedge1'
        result = self.sdk.authenticate(prompt.submit_key, auth_info)
        assert isinstance(result, geezeo.AggregatedInstitution)

    def test_mfa_login(self):
        prompts = self.sdk.search_institutions('CashEdge Test Bank Agg')
        for p in prompts:
            if p.name == "CashEdge Test Bank (Agg) - Retail 2FA":
                prompt = p
                break
        auth_info = {}
        for param in prompt.parameters:
            if param.caption == 'User ID':
                auth_info[param.key] = 'test'
            elif param.caption == 'Password':
                auth_info[param.key] = 'test'
        try:
            self.sdk.authenticate(prompt.submit_key, auth_info)
        except geezeo.MFARequiredError as e:
            assert len(e.auth_prompt.parameters) == 1
            parameters = {e.auth_prompt.parameters[0].key: 'red'}
            self.sdk.authenticate(e.auth_prompt.submit_key, parameters)
        else:
            assert False, "Didn't get MFA prompt."


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
