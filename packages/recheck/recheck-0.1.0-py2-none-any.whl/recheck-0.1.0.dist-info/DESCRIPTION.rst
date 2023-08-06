recheck
=======

.. image:: https://pypip.in/v/recheck/badge.png
    :target: https://pypi.python.org/pypi/recheck
    :alt: Latest PyPI version

.. image:: https://travis-ci.org/borntyping/cookiecutter-pypackage-minimal.png
   :target: https://travis-ci.org/borntyping/cookiecutter-pypackage-minimal
   :alt: Latest Travis CI build status

Re(quirements)Check


Usage
-----

Usage::

    recheck -r /path/to/requirements/file

You may also provide an ignore file.  The default is ``$CWD/.recheckignore``.  You can pass a different file by providing a ``-i`` flag::

    recheck -r /path/to/requirements/file -i /path/to/ignore/file

The ignore file should list dependencies (one per line) you wish to ignore from the check.

Installation
------------

Run::

    pip install recheck


Licence
-------

MIT

Authors
-------

`recheck` was written by `Kevin J. Qiu <kevin@idempotent.ca>`_.


