securityheaders
===============

*securityheaders* is a CLI application to analyze the Security Headers
of a given URL using securityheaders.io

.. figure:: https://raw.githubusercontent.com/timofurrer/securityheaders/master/screenshots/cli.jpg
   :alt: Screenshot CLI

   Screenshot CLI

Installation
------------

Install in python 3 environment:

.. code:: bash

    pip3 install securityheaders

*Note: you might need root privileges or use ``--user`` switch*

Usage
-----

::

    Usage: securityheaders [OPTIONS] URL

      Get Security Headers from a given URL. The data is fetched from
        SecurityHeaders.io.

    Options:
      --version  Show the version and exit.
      --json     Print the Security Headers analysis as JSON
      --help     Show this message and exit.

Thanks
------

Thanks to **`SecurityHeaders.io <https://securityheaders.io>`__** for
their awesome service!
