======
Pantry
======

.. image:: https://travis-ci.org/kryptn/Pantry.svg?branch=master
    :target: https://travis-ci.org/kryptn/Pantry

A simple context manager based file store that uses the pickle module

Use:

::

    from pantry import pantry

    shelves = {'first': ['cereal', 'rice', 'beans'],
               'second': ['spam', 'spam', 'baked beans', 'spam']}

    with pantry('pantry.txt') as db:
        db['shelves'] = shelves

