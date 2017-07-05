Development
===========

Setup Environment
-----------------
You can use pip `editable <https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs>`_ mode to develop
this package. ::

    pip install -e .[test]

Run Test
--------
You can use pyenv to install python 3.3.6 and 3.5.3. Then run following command to test with different python
versions. ::

    tox

Deploy to PYPI
--------------
#. Update version number in setup.py. Follow Semantic Version
#. Send a PR on develop branch
#. Create a PR to merge develop branch into master branch
#. Tag master branch with version