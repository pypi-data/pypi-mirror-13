let
===
*Assign variables wherever, whenever you want.*

Installation
------------
Install via pip:

.. code-block:: bash

    $ pip install let

Done.

If you insist on the (slightly) harder way of installing, from source,
you know how to do it already and don't need my help.

I might later upload the source to:
https://github.com/TaylorSMarks/let

Quick Start
-----------
Once you've installed, you can really quickly verified that it works with just this:

.. code-block:: python

    >>> from let import let
    >>> if let(count = len('Hello World!')):
    ...     print(count)
    12

Documentation
-------------
In C, Java, and many other languages, it's possible to assign variables inside
of if or while condition statements. This is useful in allowing you to concisely
both assign the value, and check whether a condition is met.

This ability doesn't exist in Python, because of the thought that when people
write something like:

.. code-block:: python

    if row = db.fetch_results():
        ...

They may have actually meant:

.. code-block:: python

    if row == db.fetch_results():
        ...

Personally, I have never made this mistake. It seems far more like a theoretical
mistake that could plausibly happen than one that actually happens and warrants
removing features, as was chosen in Python.

Anyways, the let function in this module gives you something very close to that
ability in other languages. A few examples:

.. code-block:: python

    if let(name = longInstanceName.longAttributeName):
        ...

    # Yes, db.fetch_results() should just return a generator. No, it doesn't.
    while let(results = db.fetch_results()):
        ...

    if let(count = len(nameValuePair)) != 1:
        raise Exception('Bad amount: {}'.format(count))

Copyright
---------
This software is Copyright (c) 2016 Taylor Marks <taylor@marksfam.com>.

See the bundled LICENSE file for more information.
