# -*- coding: utf-8 -*-

"""
DTOs and some logic for managing aggregated accounts.
"""

import base64
import json
from . import util


def encode_submit_key(data):
    """
    Turn a JSON-serializable object into a string of echo data.

    :param dict data: arbitrary JSON-serializable object
    :return: string of base 64
    """

    json_data = json.dumps(data)
    json_bytes = json_data.encode('ascii')
    base64_bytes = base64.b64encode(json_bytes)
    submit_key = base64_bytes.decode('ascii')
    return submit_key


def decode_submit_key(submit_key):
    """
    Turn a submit key back into data.

    :param str submit_key: echo data saved from an AuthPrompt object
    :return: dictionary of submit key data
    """

    base64_bytes = submit_key.encode('ascii')
    json_bytes = base64.b64decode(base64_bytes)
    json_data = json_bytes.decode('ascii')
    data = json.loads(json_data)
    return data


class AuthPrompt(object):

    """
    Login form for a user to authenticate with a financial institution.

    Geezeo uses a third-party financial aggregator to provide information on
    accounts and transations for multiple financial institutions. This class
    is essentially a login form for such an institution.

    .. attribute:: name

        The name of the institution with whom this prompt will let the user
        authenticate.

    .. attribute:: id

        Unique string identifier for the institution involved.

    .. attribute:: submit_key

        String that uniquely identifies this prompt. This will need to be
        passed to :meth:`SDK.authenticate` in order to submit the prompt.

    .. attribute:: parameters

        List of :class:`AuthParameter` objects. The set of :attr:`key
        <AuthParameter.key>` attributes indicate what keys need to be present
        in the ``responses`` argument of :meth:`submit`.
    """

    def __init__(self, data):
        # {
        #   "id": 2,
        #   "fi_id": 20349,
        #   "name": "CashEdge Test Bank (Agg) - Retail Non 2FA",
        #   "url": "https://cashbank.cashedge.com/.../LoginPage.jsp",
        #   "ce_login_parameters": [
        #     {
        #       "id": 3,
        #       "parameter_id": "42971",
        #       "parameter_caption": "UserName",
        #       "parameter_type": "login",
        #       "parameter_max_length": 20
        #     },
        #     {
        #       "id": 4,
        #       "parameter_id": "42972",
        #       "parameter_caption": "Password",
        #       "parameter_type": "password",
        #       "parameter_max_length": 20
        #     }
        #   ]
        # }

        self.name = data['name']
        self.id = str(data['id'])
        self.parameters = [AuthParameter(param)
                           for param in data['ce_login_parameters']]

        self.submit_key = encode_submit_key({
            'type': 'auth',
            'id': self.id,
            'name': self.name,
            'parameters': [param.to_json() for param in self.parameters],
        })

    def to_json(self):
        """
        Render as JSON.

        .. code-block:: javascript

            {
                "name": "Horse Financial",
                "id": "4321",
                "submitKey": "eyJvdGhlcl90aGluZyI6ICIyZXJkc2Fwc2EiLCAidGh=",
                "parameters": [
                    {
                        "key": "8765",
                        "caption": "User name",
                        "type": "username",
                        "maxLength": 20
                    },
                    {
                        "key": "8766",
                        "caption": "Password",
                        "type": "password",
                        "maxLength": null
                    }
                ]
            }
        """

        return {
            'name': self.name,
            'id': self.id,
            'parameters': [param.to_json() for param in self.parameters],
            'submitKey': self.submit_key,
        }


class AggregatedInstitution(util.Institution):

    """
    Institution with aggregated accounts.

    .. attribute:: id

        See :attr:`Institution.id`.

    .. attribute:: name

        See :attr:`Institution.name`.

    .. attribute:: submit_key

        Key used to update authentication information for the institution.

    .. attribute:: parameters

        List of :class:`AuthParameter` objects carried over from the
        :class:`AuthPrompt` that was submitted to authenticate with this
        institution.

    .. attribute:: accounts

        List of :class:`Account` objects, one for each account that the user
        holds at the newly authenticated institution.
    """

    def __init__(self, submit_data, accounts):
        self.id = submit_data['id']
        self.name = submit_data['name']

        self.parameters = [AuthParameter.from_json(item)
                           for item in submit_data['parameters']]

        self.submit_key = encode_submit_key({
            'type': 'institution',
            'id': self.id,
            'name': self.name,
            'parameters': submit_data['parameters'],
        })

        self.accounts = accounts

    def to_json(self):
        """
        Render as JSON.

        .. code-block:: javascript

            {
                "id": "4321",
                "name": "Horse Financial",
                "submitKey": "eyJvdGhlcl90aGluZyI6ICIyZXJkc2Fwc2EiLCAidGh=",
                "parameters": [
                    {
                        "key": "8765",
                        "caption": "User name",
                        "type": "username",
                        "maxLength": 20
                    },
                    {
                        "key": "8766",
                        "caption": "Password",
                        "type": "password",
                        "maxLength": null
                    }
                ],
                "accounts": [
                    {
                        "id": "123",
                        "name": "Main Checking",
                        "accountType": "checking"
                    }
                ]
            }
        """

        return {
            'id': self.id,
            'name': self.name,
            'submitKey': self.submit_key,
            'parameters': [p.to_json() for p in self.parameters],
            'accounts': [a.to_json() for a in self.accounts],
        }


class MFAPrompt(AuthPrompt):

    def __init__(self, data, submit_data):
        # {
        #   "mfa_parameters": [
        #     {
        #       "ce_fi_id": null,
        #       "parameter_caption": "What is your favorite color?",
        #       "parameter_id": "answer",
        #       "parameter_max_length": null,
        #       "parameter_type": "password"
        #     }
        #   ],
        #   "session_key": "464a674e7367646...627879413d3d",
        #   "harvest_id": "123770714",
        #   "login_id": "19349692"
        # }

        self.id = submit_data['id']
        self.name = submit_data['name']

        self.parameters = []
        for parameter_data in data['mfa_parameters']:
            self.parameters.append(AuthParameter(parameter_data))

        self.submit_key = encode_submit_key({
            'type': 'mfa',
            'id': self.id,
            'name': self.name,
            'parameters': submit_data['parameters'],

            'session_key': data['session_key'],
            'harvest_id': data['harvest_id'],
            'login_id': data['login_id'],
        })


class MFARequiredError(Exception):

    """
    A financial institution requires multi-factor authentication.

    This class is an :class:`Exception` that can be raised during attempts to
    communicate with an aggregated financial institution, such as when calling
    :meth:`SDK.authenticate`. If an :class:`MFArequiredError` exception is
    raised, the institution has issued a multi-factor auth challenge, and a
    follow-up request is needed before the desired data will be returned.

    To continue the transaction, use the new :attr:`auth_prompt`.

    .. attribute:: message

        String describing the prompt as a whole.

    .. attribute:: auth_prompt

        An :attr:`AuthPrompt` that can be submitted to continue the
        authentication process.
    """

    def __init__(self, message, data, submit_data):
        # {
        #   "response": {
        #     "message": "The account requires further authentication",
        #     "data": {
        #       "mfa_parameters": [
        #         {
        #           "ce_fi_id": null,
        #           "parameter_caption": "What is your favorite color?",
        #           "parameter_id": "answer",
        #           "parameter_max_length": null,
        #           "parameter_type": "password"
        #         }
        #       ],
        #       "session_key": "464a674e7367646...627879413d3d",
        #       "harvest_id": "123770714",
        #       "login_id": "19349692"
        #     }
        #   }
        # }

        self.message = message
        self.auth_prompt = MFAPrompt(data, submit_data)

    def to_json(self):
        data = self.auth_prompt.to_json
        data['message'] = self.message
        return data


class AuthParameter(object):
    """
    One part of a multi-factor authentication prompt.

    .. attribute:: key

        String that identifies this parameter uniquely among the parameters
        for the parent prompt.

    .. attribute:: caption

        String challenge for the user, e.g. ``"What is your favorite
        color?"``.

    .. attribute:: type

        String description of the information to be provided, e.g.
        ``"password"``.

    .. attribute:: max_length

        Maximum length that the answer for the parameter can have (int).
        This may be ``None``, indicating that there is no max length.
    """

    def __init__(self, data):
        # {
        #   "id": 3,
        #   "parameter_id": "42971",
        #   "parameter_caption": "UserName",
        #   "parameter_type": "login",
        #   "parameter_max_length": 20
        # }

        self.key = data['parameter_id']
        self.caption = data['parameter_caption']
        self.type = data['parameter_type']
        self.max_length = data['parameter_max_length']

    @classmethod
    def from_json(cls, data):
        return cls({
            'parameter_id': data['key'],
            'parameter_caption': data['caption'],
            'parameter_type': data['type'],
            'parameter_max_length': data['maxLength'],
        })

    def to_json(self):
        """
        Render as JSON.

        .. code-block:: javascript

            {
                "key": "8765",
                "caption": "User name",
                "type": "username",
                "maxLength": 20
            }
        """

        return {
            'key': self.key,
            'caption': self.caption,
            'type': self.type,
            'maxLength': self.max_length,
        }
