=============
config-sempai
=============

Have you ever been kept awake at night, desperately feeling a burning desire to
do nothing else but directly import JSON/YAML/XML files as if they were python
modules? Now you can!

This abomination allows you to write

.. code:: python

     import some_json_file

and if ``some_json_file.json`` can be found, it will be available as if it is a
python module. The same goes for yaml and xml files.

Usage
-----

Slap a json file somewhere on your python path. ``tester.json``:

.. code:: json

    {
        "hello": "world",
        "this": {
            "can": {
                "be": "nested"
            }
        }
    }

Now import configsempai and your json file!

.. code:: python

    >>> from configsempai import magic
    >>> import tester
    >>> tester
    <module 'tester' from 'tester.json'>
    >>> tester.hello
    u'world'
    >>> tester.this.can.be
    u'nested'
    >>>

Alternatively, a context manager may be used (100% less magic):

.. code:: python

    >>> import configsempai
    >>> with configsempai.imports():
    ...     import tester
    >>> tester
    <module 'tester' from 'tester.json'>


Python packages are also supported:

.. code:: bash

    $ tree
    .
    └── python_package
        ├── file.json
        ├── __init__.py
        └── nested_package
            ├── __init__.py
            └── second.json

.. code:: python

    >>> from configsempai import magic
    >>> from python_package import file
    >>> file
    <module 'python_package.file' from 'python_package/file.json'>
    >>> import python_package.nested_package.second
    >>> python_package.nested_package.second
    <module 'python_package.nested_package.second' from 'python_package/nested_package/second.json'>
