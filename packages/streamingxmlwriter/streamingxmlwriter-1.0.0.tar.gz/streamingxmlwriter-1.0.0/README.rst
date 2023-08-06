streamingxmlwriter
==================

.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3
.. image:: https://badge.fury.io/py/streamingxmlwriter.svg
    :target: http://badge.fury.io/py/streamingxmlwriter
.. image:: https://travis-ci.org/acsone/streamingxmlwriter.svg?branch=master
   :target: https://travis-ci.org/acsone/streamingxmlwriter
.. image:: https://coveralls.io/repos/acsone/streamingxmlwriter/badge.svg?branch=master&service=github
   :target: https://coveralls.io/repos/github/acsone/streamingxmlwriter/badge.svg?branch=master

A lightweight pythonic standard compliant streaming xml writer.

  .. code:: python

    from io import BytesIO

    import streamingxmlwriter

    stream = BytesIO()
    with streamingxmlwriter.from_stream(stream) as writer:
        writer.start_namespace('myns', 'http://mynamespace.org/')
        with writer.element('myns:root', {'att1': '1'}):
            with writer.element('myns:child1'):
                writer.characters('text content')
            writer.comment(' a comment ')
            with writer.element('myns:child2'):
                writer.characters('text content')
            # shortcut for elements containing a single text node
            writer.text_element('myns:child3', 'text content', {'att2': '2'})

For more API examples, look at the documentation of the
``StreamingXMLWriter`` class in ``core.py``.

Under the hood it generates SAX events to the standard xml.sax.saxutils.XMLGenerator.
It also provides a `from_sax_handler` constructor so it can also be used to emit
sax events for other purposes than outputing to an io stream.

Python 2 (2.7+) and python 3 (3.3+) are supported.

Supported XML features are:

  * elements
  * attributes
  * text
  * processing instructions
  * comments
  * selectable encoding
  * namespaces for elements and attributes, with or without prefix

Unsupported XML features (yet):

  * DOCTYPE declaration
  * entities
  * CDATA sections

Credits
=======

Author
------

  * Stéphane Bidoul (ACSONE)

Maintainer
----------

.. image:: https://www.acsone.eu/logo.png
   :alt: ACSONE SA/NV
   :target: http://www.acsone.eu

This module is maintained by ACSONE SA/NV.
