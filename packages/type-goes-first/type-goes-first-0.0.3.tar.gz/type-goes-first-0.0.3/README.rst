type-goes-first
===============

.. image:: https://img.shields.io/pypi/v/type-goes-first.svg?style=flat-square   :target: 

Ensures that FeatureCollection is defined at the top of a geojson.
Intended for use with supermercado.

.. code-block:: console
    
    pip install type-goes-first

    echo "[0,0,0]" | mercantile children --depth 2 | supermercado edges | supermercado union | tgf | geojsonio

