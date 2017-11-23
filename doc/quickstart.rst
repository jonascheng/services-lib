Quick Start
===========
Installation
------------
Just use pip to install. This package already deploy to
`pypi <https://pypi.python.org/pypi/soocii-services-lib>`_. ::

   pip install soocii-services-lib

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
This package provide two APIs to generate and decode access token used by Soocii.

#. :py:func:`soocii_services_lib.auth.generate_access_token`
#. :py:func:`soocii_services_lib.auth.decode_access_token`

You need to setup secrets in environment variables, :envvar:`ACCESS_TOKEN_SECRET` and :envvar:`REFRESH_TOKEN_SECRET`
before starting using these two APIs