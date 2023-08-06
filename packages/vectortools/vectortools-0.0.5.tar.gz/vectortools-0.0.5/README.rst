===========
vectortools
===========


.. image:: https://img.shields.io/pypi/v/vectortools.svg
    :alt: The PyPI package
    :target: https://pypi.python.org/pypi/vectortools

.. image:: https://img.shields.io/pypi/dw/vectortools.svg
    :alt: PyPI download statistics
    :target: https://pypi.python.org/pypi/vectortools


Installation
============

::

  pip install vectortools


Usage
=====

Converting shapefile to geojson ::

  from vectortools.geojson import convert_to_geojson

  convert_to_geojson('world_borders.shp')