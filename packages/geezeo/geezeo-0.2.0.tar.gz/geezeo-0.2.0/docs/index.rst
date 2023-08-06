.. geezeo documentation master file, created by
   sphinx-quickstart on Tue Jul  9 22:26:36 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Geezeo SDK's documentation!
======================================

.. _Flask: http://flask.pocoo.org/
.. _Redis: http://redis.io

For full details, see the :ref:`API docs <api-docs>`.

Example
-------

Here is a `Flask`_ app that makes very simple use of the Geezeo SDK.

.. code-block:: python
    :linenos:

    import geezeo
    import flask

    api_key = 'VERYVERYSECRET'
    user_id = 'userone'
    url = 'https://bank.horse/'
    sdk = geezeo.SDK(api_key, user_id, url)

    app = flask.Flask(__name__)


    @app.route('/our-api/aggregation/search')
    def search():
        search_string = request.args.get('q', '')

        # Get a sequence of AuthPrompt objects, and just return the first,
        # because we feel lucky.
        auth_prompts = sdk.search_institutions(search_string)
        auth_prompt = next(auth_prompts)
        return auth_prompt.to_json()


    @app.route('/our-api/aggregation/login')
    def submit_prompt():

        # We need to restore the prompt that we passed down to the client
        # earlier; it has state that the upstream server will need.
        submit_key = cache.get(request.form['submit_key'])

        # Send the authentication information to the
        try:
            auth_information = json.loads(request.form['auth'])
            institution = sdk.authenticate(submit_key, auth_information)

        # If the institution requires multi-factor auth, an exception will be
        # raised with a follow-up prompt.
        except MFARequiredError as e:
            return {
                'finished': False,
                'auth_prompt': e.auth_prompt.to_json()
            }

        # If authentication succeeds, we receive an AggregatedInstitution.
        else:
            return {
                'finished': True,
                'institution': institution.to_json()
            }

    app.run(host='api.bank.horse', port=8765)
