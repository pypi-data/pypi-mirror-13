type-goes-first
===============

.. image:: https://travis-ci.org/jacquestardie/tgf.svg
   :target: https://travis-ci.org/jacquestardie/tgf

Ensures that FeatureCollection is defined at the top of a geojson.
Intended for use with supermercado.

.. code-block:: console
    
    pip install tgf

    echo "[0,0,0]" | mercantile children --depth 2 | supermercado edges | supermercado union | tgf | geojsonio

