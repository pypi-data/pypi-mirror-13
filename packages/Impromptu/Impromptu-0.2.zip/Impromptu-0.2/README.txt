Impromptu
=========

This is a little Python script, which displays a pseudo-HTML file in a window
and scrolls the text in upwards or downwards direction.

You can use it, for example, as a teleprompter while recording a podcast or
an audiobook or for a presentation. You can use differents fonts, colors and
sizes via a subset of the HTML4 standard [1]_ and control the scrolling speed
and direction via command line options and keyboard commands while the
application is running.

The program can also display ReStructuredText_ documents converted to HTML with
``rst2html``.

.. [1] http://www.pyglet.org/doc/programming_guide/formatted_text.html#html


Usage
-----

Linux::

    ./impromptu.py <file>

Mac OS X or Microsoft Windows::

    pythonw impromptu.py <file>

Use option ``-h`` to show a list of command line options.

While in the main window, press ``F1`` to show a list of supported keyboard
commands.

For a demo (and a laugh) run impromptu with the HTML file included in the
source distribution::

    python impromptu.py hungarian.html


Installation
------------

Though installation of the script is not necessary to run it, you may install
it with the usual distutils command::

    python setup.py install

This will take care of downloading and installing any required packages (see
below) as well.


Requirements
------------

Impromptu relies on the Pyglet_ python package. You need to install pyglet
before you can use this script::

    pip install pyglet

or download an installer for Windows or OS X from

    http://www.pyglet.org/

.. _pyglet: http://www.pyglet.org/


Share & Enjoy

Chris Arndt <chris@chrisarndt.de>
