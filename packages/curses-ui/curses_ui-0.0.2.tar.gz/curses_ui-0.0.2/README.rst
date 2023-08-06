Python Curses UI
================
WIP - docs to come.

Installing
----------
.. code-block::

    pip install curses_ui

Tests
-----
To run unit tests::

    ./test 

NB:
    The UI isn't well tested due to the complexity of testing a curses environment (hints welcome!) - use the demo
    instead.

Demo
----
De facto tests, to run::

    ./demo

Notes
-----
* `Curses UI characters <http://melvilletheatre.com/articles/ncurses-extended-characters/index.html>`_

General Todo List
-----------------
* Text overflow protection, consider the widget ``write()`` function
* Word wrap support, used by labels and text components

Widget Todo List
----------------
* Scrolling panel
* Proper tab support

Building
--------
.. code-block::

    python setup.py sdist
    twine upload dist/*

