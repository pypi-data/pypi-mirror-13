.. image:: https://drone.io/bitbucket.org/prometheus/rios.core/status.png
   :target: https://drone.io/bitbucket.org/prometheus/rios.core/latest
   :alt: Build Status
.. image:: https://readthedocs.org/projects/rioscore/badge/?version=stable
   :target: https://rioscore.readthedocs.org
   :alt: API Documentation
.. image:: https://img.shields.io/pypi/v/rios.core.svg
   :target: https://pypi.python.org/pypi/rios.core
.. image:: https://img.shields.io/pypi/l/rios.core.svg
   :target: https://pypi.python.org/pypi/rios.core

******************
RIOS.CORE Overview
******************

RIOS.CORE is a `Python`_ package that provides basic validation and
formatting functionality for data structures that adhere to the `RIOS`_
specifications (formally known as PRISMH).

.. _`Python`: https://www.python.org
.. _`RIOS`: https://rios.readthedocs.org


Example Usage
=============

This package exposes a handful of simple functions for validating and
formatting the standard RIOS data structures::

    >>> from rios.core import validate_instrument, get_instrument_json

    >>> instrument = {"foo": "bar", "id": "urn:my-instrument", "title": "An Instrument Title", "record": [{"id": "field1","type": "text"}], "version": "1.0"}
    >>> validate_instrument(instrument)
    Traceback (most recent call last):
        ...
    colander.Invalid: {'': u'Unrecognized keys in mapping: "{\'foo\': \'bar\'}"'}

    >>> del instrument['foo']
    >>> validate_instrument(instrument)

    >>> print get_instrument_json(instrument)
    {
      "id": "urn:my-instrument",
      "version": "1.0",
      "title": "An Instrument Title",
      "record": [
        {
          "id": "field1",
          "type": "text"
        }
      ]
    }


For more information on the available functionality, please read the API
documentation.


Contributing
============

Contributions and/or fixes to this package are more than welcome. Please submit
them by forking this repository and creating a Pull Request that includes your
changes. We ask that you please include unit tests and any appropriate
documentation updates along with your code changes.

This project will adhere to the `Semantic Versioning`_ methodology as much as
possible, so when building dependent projects, please use appropriate version
restrictions.

.. _`Semantic Versioning`: http://semver.org

A development environment can be set up to work on this package by doing the
following::

    $ virtualenv rios
    $ cd rios
    $ . bin/activate
    $ hg clone ssh://hg@bitbucket.org/prometheus/rios.core
    $ pip install -e ./rios.core[dev]


License/Copyright
=================

This project is licensed under the GNU Affero General Public License, version
3. See the accompanying ``LICENSE.rst`` file for details.

Copyright (c) 2015, Prometheus Research, LLC

