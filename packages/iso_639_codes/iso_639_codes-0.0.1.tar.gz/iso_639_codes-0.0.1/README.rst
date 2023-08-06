ISO 639-1 ↔ ISO 639-2 translator
================================

.. image:: https://badge.fury.io/py/iso_639_codes.png
    :target: https://pypi.python.org/pypi/iso_639_codes

.. image:: https://img.shields.io/pypi/dm/iso_639_codes.svg
    :target: https://pypi.python.org/pypi/iso_639_codes

.. image:: https://img.shields.io/github/issues/Bystroushaak/iso_639_codes.svg
    :target: https://github.com/Bystroushaak/iso_639_codes/issues

This package may be used for translation between ISO 639-1 and ISO 639-2.

.. code-block:: python

    >>> from iso_639_codes import translate
    >>> translate("cs")
    'cze'
    >>> translate("cze")
    'cs'

Or alternative value in case that the code was not found:

.. code-block:: python

    >>> translate("xe", alt="alt")
    'alt'

There are two dicts which you may use for translation yourself:

 - iso_639_codes.iso_639_2_to_1
 - iso_639_codes.iso_639_1_to_2

Installation
------------
Module is hosted at `PYPI <https://pypi.python.org/pypi/iso_639_codes/>`_, and
can be installed using `PIP <http://en.wikipedia.org/wiki/Pip_%28package_manager%29>`_:

::

    pip install iso_639_codes