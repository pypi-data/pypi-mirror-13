radioglobo
==========

``radioglobo`` is a simple script to play http://radioglobo.globo.com/ radio
streaming in the shell.


Installation
------------

.. _`PyPI Package Index`: http://pypi.python.org/pypi

``radioglobo`` is available on the `PyPI Package Index`_, and you can install it
using ``pip``::

    # pip install radioglobo

The script relies on the ``mpv`` media player to play the streaming. Please
make sure to have it installed before trying it.


Usage
-----

After having ``radioglobo`` installed, you can list the radio stations available::

    $ radioglobo stations

To play one of the listed stations, just run::

    $ radioglobo play <STATION>

Where ``<STATION>`` is one of the stations listed on previous command, e.g.
``SP``::

    $ radioglobo play SP

That's it, ``mpv`` should start playing the radio streaming for you!
