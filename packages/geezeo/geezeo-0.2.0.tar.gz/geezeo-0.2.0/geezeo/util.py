# -*- coding: utf-8 -*-

"""
Basic DTOs and exceptions used throughout the SDK.
"""

import sys

# urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning
v = sys.version_info
if (v.major, v.minor, v.micro) < (2, 7, 9):
    raise DeprecationWarning('For security reasons, the Geezeo Python SDK '
                             'requires Python 2.7.9 or higher.')


class GeezeoError(Exception):

    """
    Parent of all Geezeo errors.
    """


class APIError(GeezeoError):

    """
    Exception indicating that the server rejected a request.

    .. attribute:: response

        :class:`requests.Response` object with a non-200 status
    """

    def __init__(self, response, *args, **kwargs):
        self.response = response
        super(APIError, self).__init__(*args, **kwargs)


class UnauthorizedError(APIError):

    """
    The API has indicated that the consumer credentials are invalid.
    """


class DoesNotExistError(APIError):

    """
    The entity being requested doesn't exist.
    """


class ServerError(APIError):

    """
    Something went wrong on the server.
    """


class NetworkError(GeezeoError):

    """
    Something went wrong while trying to communicate with the server.

    This exception is not caused by the server telling us something is wrong,
    but by the server not being able to tell us anything at all. Usually, this
    means that something is wrong with the network, or that the server is
    unavailable.

    This exception can be thrown by most methods of an :class:`SDK` object, or
    of objects retrieved from the API.

    .. attribute:: cause

        Exception that was thrown by Requests and wrapped in this one.
    """

    def __init__(self, cause, *args, **kwargs):
        self.cause = cause
        super(NetworkError, self).__init__(*args, **kwargs)


class PagedResults(object):

    """
    Set of results from a paginated API endpoint.

    This class generally acts like a list: you can iterate over it to get the
    individual elements, or use indices to get individual ones.

    .. attribute:: data

        List of result objects from this page.

    .. attribute:: current_page

        Integer indicating which page this is.

    .. attribute:: last_page

        Integer indicating the last page of available results.

    .. attribute:: has_more

        Boolean indicating whether there is a next page.
    """

    def __init__(self, data, current_page, last_page):
        self.data = data
        self.current_page = current_page
        self.last_page = last_page
        self.has_more = self.current_page < self.last_page

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, index):
        return self.data[index]

    def __contains__(self, item):
        return item in self.data

    def __len__(self):
        return len(self.data)

    def __reversed__(self):
        return reversed(self.data)


class User(object):

    """
    Represent a user, in order to update and retrieve their data.

    .. attribute:: id

        Unique string identifier for the user.

    .. attribute:: first_name

        User's first name, e.g. ``'John'``

    .. attribute:: last_name

        User's last name, e.g. ``'Doe'``

    .. attribute:: email

        User's email address, e.g. ``'j.doe@doma.in'``
    """

    def __init__(self, data):
        # {
        #   "id": "42",
        #   "login": "jsmith42",
        #   "first_name": "Alice",
        #   "last_name": "Smith",
        #   "email": "user@example.com",
        #   "login_count": 1,
        #   "last_login_at": "2013-09-29T15:16:36Z",
        #   "postal_code": "06252",
        #   "birth_year": 1980,
        #   "sex": "Male",
        #   "custom_tags": []
        # }

        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']

    def to_json(self):
        """
        Render as JSON.

        .. code-block:: javascript

            {
                "id": "1",
                "firstName": "John",
                "lastName": "Doe",
                "email": "j.doe@doma.in"
            }
        """
        return {
            'id': self.id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'email': self.email,
        }


class Institution(object):

    """
    Financial institution info.

    .. attribute:: id

        Unique string identifier for the institution.

    .. attribute:: name

        Name of the institution.
    """

    def to_json(self):
        """
        Render as JSON.

        .. code-block:: javascript

            {
                "id": "4321",
                "name": "Horse Financial"
            }
        """

        return {
            'id': self.id,
            'name': self.name,
        }


class Account(object):

    """
    Represent an account held by a user at a financial institution.

    .. attribute:: id

        Unique string identifier for the account.

    .. attribute:: name

        Account name, e.g. ``'Freelancing Income'``.

    .. attribute:: account_type

        String describing the kind of account. One of:

        * ``'checking'``
        * ``'savings'``
        * ``'money_market'``
        * ``'autos'``
        * ``'creditline'``
        * ``'home'``
        * ``'loan'``
        * ``'student_loans'``
        * ``'investment'``
        * ``'asset'``
        * ``'cd'``
        * ``'card'``
        * ``'cards'``
        * ``'bill'``
    """

    def __init__(self, data):
        # {
        #   "id": 657,
        #   "name": "My Checking",
        #   "balance": "3897.52",
        #   "reference_id": null,
        #   "aggregation_type": "cashedge",
        #   "state": "active",
        #   "account_type": "checking",
        #   "include_in_expenses": true,
        #   "include_in_budget": true,
        #   "include_in_cashflow": true,
        #   "include_in_dashboard": true,
        #   "include_in_goals": true,
        #   "include_in_networth": true,
        #   "cashedge_account_type": {
        #     "name": "Savings",
        #     "acct_type": "SDA",
        #     "ext_type": "SDA",
        #     "group": "Cash"
        #   }
        # }

        self.id = data['id']
        self.name = data['name']
        self.account_type = data['account_type']

    def to_json(self):
        """
        Render as JSON.

        .. code-block:: javascript

            {
                "id": "123",
                "name": "Main Checking",
                "accountType": "checking"
            }
        """

        return {
            'id': self.id,
            'name': self.name,
            'accountType': self.account_type,
        }
