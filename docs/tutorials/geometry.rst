Geometry
======

To run any of these examples, you'll want to save a bit of code in a python file, with any name, e.g. ``geometry.py``, and then run that file by navigating to it on the command line and constructing a call like, ``coldtype geometry.py``

Rect(angles)
------------

One of the core concepts of Coldtype is the use of the ``coldtype.geometry.Rect`` class to encapsulate rectangles and methods for slicing & dicing them.

.. code:: python

    from coldtype import *

    @renderable((300, 300))
    def columns(r):
        dps = DATPenSet()
        for c in r.inset(10).subdivide(3, "mnx"):
            dps += DATPen().rect(c.inset(10)).f(hsl(random()))

.. image:: /_static/renders/shapes_rectangle.png
    :width: 150