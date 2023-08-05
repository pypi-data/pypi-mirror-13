.. _api-docs:

========
API Docs
========

.. automodule:: geezeo
    :members:


Exceptions
----------

    .. autoexception:: UnauthorizedError
        :members:

    .. autoexception:: DoesNotExistError
        :members:

    .. autoexception:: NetworkError
        :members:


The SDK Object
--------------

    .. autoclass:: SDK

        .. autoattribute:: api_key

        .. autoattribute:: user

        .. autoattribute:: url

        .. automethod:: search_institutions

        .. automethod:: get_featured_institutions

        .. automethod:: get_all_institutions

        .. automethod:: authenticate

        .. automethod:: update_authentication


Utility and Data Classes
------------------------

    .. autoclass:: PagedResults
        :members:

    .. autoclass:: Institution

        .. autoattribute:: id

        .. autoattribute:: name

        .. automethod:: to_json

    .. autoclass:: User

        .. autoattribute:: id

        .. autoattribute:: first_name

        .. autoattribute:: last_name

        .. autoattribute:: email

        .. automethod:: to_json

    .. autoclass:: Account

        .. autoattribute:: id

        .. autoattribute:: name

        .. autoattribute:: account_type

        .. automethod:: to_json


Aggregation
-----------

    .. autoclass:: AuthPrompt

        .. autoattribute:: id

        .. autoattribute:: name

        .. autoattribute:: submit_key

        .. autoattribute:: parameters

        .. automethod:: to_json

    .. autoclass:: AggregatedInstitution(Institution)

        .. autoattribute:: id

        .. autoattribute:: name

        .. autoattribute:: submit_key

        .. autoattribute:: parameters

        .. autoattribute:: accounts

        .. automethod:: to_json

    .. autoexception:: MFARequiredError(Exception)
        :members:

    .. autoclass:: AuthParameter

        .. autoattribute:: key

        .. autoattribute:: caption

        .. autoattribute:: type

        .. autoattribute:: max_length

        .. automethod:: to_json