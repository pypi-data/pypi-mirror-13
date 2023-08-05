==========
sqlitelist
==========
sqlitelist is a SQLite3 wrapper with a python list-like interface. It comes with one purpose - to keep your data if it bigger than your RAM size.

.. code-block:: python
>>> from sqlitelist import open
>>> with open('db') as lst:
...     lst.append('hello')
...     lst.extend(['world', {}])
>>> print(len(lst))
>>> for item in lst:
>>>     print(item)


===================================
There is some performance features
===================================

.. code-block:: python
>>> from sqlitelist import open
>>> with open('db', journal_mode='MEMORY', autocommit=False) as lst:
...     for _ in range(1000):
...         lst.extend(['some', 'data', {'key': 'value', 'another key': 1}])
...     lst.commit()
>>> # Do not forget to commit your changes if autocommit is off.
>>> lst.flush()  # For flush all your data without removing a database file.


========
Features
========
Values can be any pickable objects.
Support for slices (step and negative indices aren't supported [yet])

.. code-block:: python
>>> with open('db') as lst:
...     print(lst[1:200])
...     print(lst[:50])
...     print(lst[50:])

Support for getting items by it's index

.. code-block:: python
>>> with open('db') as lst:
...     lst[5]
...     lst[-3]

Support for pop, append and extend methods

.. code-block:: python
>>> with open('db') as lst:
...     lst.pop()
...     lst.pop(50)  # Pop the element in the 51th place

Support for delete (indices and slices with no negative values)

.. code-block:: python
>>> with open('db') as lst:
...     del lst[0]
...     del lst[-50]
...     del lst[:50]
...     del lst[50:]


Support for iteration (no multithreading support!)

.. code-block:: python
>>> with open('db') as lst:
...     for item in lst:
...         print(item)