Draw compose
============

Render compose files with one command line!

This project needs graphviz installed.

Simple example
--------------

.. figure:: https://raw.githubusercontent.com/Alexis-benoist/draw-compose/master/fixtures/simple.png?raw=true
   :alt: Simple Example

   Simple example

Classic python example
----------------------

.. figure:: https://raw.githubusercontent.com/Alexis-benoist/draw-compose/master/fixtures/real.png?raw=true
   :alt: Python web app

   Python classic

Install
=======

On OSX:
-------

Install graphviz ``brew install graphviz`` and draw-compose:

::

    $ pip install draw-compose

Use
===

Renders by default ``docker-compose.yml`` in the current folder.

::

    $ draw-compose -o docker.png

Or a specific docker file can be rendered:

::

    $ draw-compose -i fixtures/real.yml -o docker-specific.png
