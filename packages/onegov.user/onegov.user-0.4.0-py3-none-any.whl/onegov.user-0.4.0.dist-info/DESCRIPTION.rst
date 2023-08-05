

Run the Tests
-------------

Install tox and run it::

    pip install tox
    tox

Limit the tests to a specific python version::

    tox -e py27

Conventions
-----------

Onegov User follows PEP8 as close as possible. To test for it run::

    tox -e pep8

Onegov User uses `Semantic Versioning <http://semver.org/>`_

Build Status
------------

.. image:: https://travis-ci.org/OneGov/onegov.user.png
  :target: https://travis-ci.org/OneGov/onegov.user
  :alt: Build Status

Coverage
--------

.. image:: https://coveralls.io/repos/OneGov/onegov.user/badge.png?branch=master
  :target: https://coveralls.io/r/OneGov/onegov.user?branch=master
  :alt: Project Coverage

Latest PyPI Release
-------------------

.. image:: https://badge.fury.io/py/onegov.user.svg
    :target: https://badge.fury.io/py/onegov.user
    :alt: Latest PyPI Release

License
-------
onegov.user is released under GPLv2

Changelog
---------

Unreleased
~~~~~~~~~~

0.4.0 (2016-01-13)
~~~~~~~~~~~~~~~~~~~

- Adds an initials property to the user.
  [href]

- Adds a title property to the user.
  [href]

0.3.1 (2015-12-16)
~~~~~~~~~~~~~~~~~~~

- Turns the Yubikey field into an ordinary string field.
  [href]

- Replayed Yubikeys no longer lead to an exception.
  [href]

0.3.0 (2015-11-20)
~~~~~~~~~~~~~~~~~~~

- Adds 2FA support with Yubikey as the first possible option.
  [href]

0.2.1 (2015-10-15)
~~~~~~~~~~~~~~~~~~~

- Use 'de_CH' translation instead of 'de'.
  [href]

0.2.0 (2015-10-12)
~~~~~~~~~~~~~~~~~~~

- Removes Python 2.x support.
  [href]

0.1.1 (2015-10-06)
~~~~~~~~~~~~~~~~~~~

- Fixes 'to' parameter not being passed on by Auth.from_request.
  [href]

0.1.0 (2015-10-05)
~~~~~~~~~~~~~~~~~~~

- Adds a generic authentication model for login/logout views.
  [href]

0.0.3 (2015-10-02)
~~~~~~~~~~~~~~~~~~~

- Adds a generic login form
  [href]

0.0.2 (2015-06-26)
~~~~~~~~~~~~~~~~~~~

- Adds support for onegov.core.upgrade
  [href]

- Remove support for Python 3.3
  [href]

0.0.1 (2015-04-29)
~~~~~~~~~~~~~~~~~~~

- Initial Release [href]


