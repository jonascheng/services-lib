Quick Start
===========
Installation
------------
Just use pip to install. This package already deploy to
`pypi <https://pypi.python.org/pypi/soocii-services-lib>`_. ::

   pip install soocii-services-lib

The lib contains several components for different scenarios. By default, the package only contains the essential dependencies for encrypting/decrypting tokens. If command line tool is required, the extra **cli** can install the necessary dependencies. ::

    pip install soocii-services-lib[cli]

There are a few extras packaging dependency for different purposes as below:

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Extra
     - Description
   * - cli
     - it is required by command line tools :py:mod:`soocii_services_lib.click`
   * - flask
     - it contains flask which is dependency of :py:class:`flask_soocii_auth.SoociiAuthenticator`

click.py
--------
Basic Usage
^^^^^^^^^^^
Add following code to your soocii.py. Then you can use soocii.py with some basic commands. ::

    import click
    from soocii_services_lib.click import CiTools, build_soocii_cli

    tools = CiTools('vision')
    soocii_cli = build_soocii_cli(tools)
    click.CommandCollection(sources=[soocii_cli])

Customized Specific Command
^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you need some different implementation of some commands, you can customized the commands which you need as following
example. ::

   import os
   import click
   from soocii_services_lib.click import CiTools, build_soocii_cli


   def setup_env():
       os.environ['SECRET'] = "thisisasecret"

   class MyCiTools(CiTools):
       def build(self):
           setup_env()
           super().build()

   tools = MyCiTools('pepper')
   soocii_cli = build_soocii_cli(tools)
   cli = click.CommandCollection(sources=[soocii_cli])

util.py
-------
:py:func:`soocii_services_lib.util.wait_for_internet_connection`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
You can use this function to wait for specific server ready (Ex. wait for elasticsearch server ready)

auth.py
-------
(Deprecated) This package provide two APIs to generate and decode access token used by Soocii.

#. :py:func:`soocii_services_lib.auth.generate_access_token`
#. :py:func:`soocii_services_lib.auth.decode_access_token`

You need to setup secrets in environment variables, :envvar:`ACCESS_TOKEN_SECRET` and :envvar:`REFRESH_TOKEN_SECRET`
before starting using these two APIs

tokens.py
---------

There are two token cryper provided in the module to replace legacy functions **generate_access_token** and **decode_access_token**. You can create the instance of :py:class:`soocii_services_lib.tokens.AccessTokenCryper` as the following example. ::

    from soocii_services_lib.tokens import AccessTokenCryper

    cryper = AccessTokenCryper(secret_key)

    # get user access_token with basic information, the default lang will be 'EN-US'
    access_token = cryper.get_user_token(pid='PID',
                                  id=1,
                                  uid='8f326d0df0d9472397dc470b7ea6e581',
                                  soocii_id='soocii_id')

    # put more custom fields into the token
    access_token = cryper.get_user_token(pid='PID',
                                  id=1,
                                  uid='8f326d0df0d9472397dc470b7ea6e581',
                                  soocii_id='soocii_id',
                                  lang='ZH-TW',
                                  device_type='IOS'

    # decrypt token
    token = cryper.loads(access_token)

The new token will automatically add the field **role** to indicate the token type. It can generate the token used by backstage and service as below: ::

    cryper.get_backstage_token(id=1)  # backstage user id
    cryper.get_service_token(name='streamer')  # name indicates service name

After decrypting token, the helper function :py:meth:`soocii_services_lib.tokens.AccessToken.is_role` can use to verify role ::

    from soocii_services_lib.tokens import AccessToken

    if token.is_role(AccessToken.ROLE_USER):
        # this is a user token
    elif token.is_role(AccessToken.ROLE_BACKSTAGE):
        # this is a backstage token
    elif token.is_role(AccessToken.ROLE_SERVICE):
        # this is a service token

Similarly, refresh token can be served by :py:class:`soocii_services_lib.tokens.RefreshTokenCryper` as following example: ::

    from soocii_services_lib.tokens import RefreshTokenCryper

    cryper = RefreshTokenCryper(secret_key)

    # get the particular access_token of the user
    refresh_token = cryper.get_token(access_token);

    data = cryper.loads(refresh_token)

The cryper will raise exceptions during invoking get_* function

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Exception
     - Description
   * - :py:exc:`~soocii_services_lib.exceptions.TokenSchemaError`
     - the token is not fulfil schema


The cryper will raise exceptions during invoking loads() function

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Exception
     - Description
   * - :py:exc:`~soocii_services_lib.exceptions.TokenExpiredError`
     - the token is expired
   * - :py:exc:`~soocii_services_lib.exceptions.TokenSchemaError`
     - the token is not fulfil schema
   * - :py:exc:`~soocii_services_lib.exceptions.AccessTokenValidationError`
     - the access token is invalid or data malformed
   * - :py:exc:`~soocii_services_lib.exceptions.RefreshTokenValidationError`
     - the refresh token is invalid or data malformed


Flask Extension - SoociiAuthenticator
-------------------------------------
Basic Usage
^^^^^^^^^^^
::

    import os

    from flask.ext.soocii_auth import SoociiAuthenticator

    os.environ['ACCESS_TOKEN_SECRET'] = '6ca21c5ab8a6c181f5cfb91479588e37'
    os.environ['REFRESH_TOKEN_SECRET'] = 'ea57844efdcd163c4d84b8f7bf087baf'

    app = Flask(__name__)
    SoociiAuthenticator(app)

:py:class:`flask_soocii_auth.SoociiAuthenticator` will decode and validate access token.
Decoded token will be stored in `g.access_token` and encoded access token will be stored in `g.raw_access_token`.

:py:class:`flask_soocii_auth.SoociiAuthenticator` will also store user info in `g.user`.
You can refer to :py:mod:`flask_soocii_auth.users` for more information.

Requests which are allowed without token
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you have some endpoints/request which are allowed to access server's resource with access token, you can implement a
function which `args[0]` is `flask.request` and return boolean to indicate whether the request is valid without token.
Then pass this function to :py:class:`flask_soocii_auth.SoociiAuthenticator` constructor.
::

    import os

    from flask.ext.soocii_auth import SoociiAuthenticator

    os.environ['ACCESS_TOKEN_SECRET'] = '6ca21c5ab8a6c181f5cfb91479588e37'
    os.environ['REFRESH_TOKEN_SECRET'] = 'ea57844efdcd163c4d84b8f7bf087baf'

    def is_safe_request(req):
        if 'healthcheck' in req.path:
            return True
        return False

    app = Flask(__name__)
    SoociiAuthenticator(app, is_safe_request)
