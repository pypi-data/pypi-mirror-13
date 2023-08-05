playsound
=========
*Pure Python, cross platform, single function module with no dependencies for playing sounds.*

Installation
------------
Install via pip:

.. code-block:: bash

    $ pip install playsound

Done.

If you insist on the (slightly) harder way of installing, from source,
you know how to do it already and don't need my help.

This library might be uploaded to github at some point at
https://github.com/TaylorSMarks

Quick Start
-----------
Once you've installed, you can really quickly verified that it works with just this:

.. code-block:: python

    >>> from playsound import playsound
    >>> playsound('/path/to/a/sound/file/you/want/to/play.wav')

Documentation
-------------
The playsound module contains only one thing - the function (also named) playsound.

It requires one argument - the path to the file with the sound you'd like to play.

WAVE files should definitely work on all platforms. MP3 is known to work on OS X. Other format/platform combos may also work.

Relies on winsound.PlaySound on Windows, AppKit.NSSound on OS X, and ossaudiodev on Linux.

There's an optional second argument, block, which is set to True by default. Setting it to False does what you'd expect on OS X and Windows. It does nothing on Linux.

Requirements
------------
playsound should work on any version of OS X, Windows, or Linux, and any version
of Python since 2.3. So basically there are no requirements.

Admittedly, I haven't tested it on particularly old versions of Python or OS X,
and I haven't tested it on Linux at all, but it should just work everywhere.

Copyright
---------
This software is Copyright (c) 2016 Taylor Marks <taylor@marksfam.com>.

See the bundled LICENSE file for more information.
