coldtype
====================================

`coldtype` is a library for programmatic display typography

Here’s an example:

.. code:: python

   from coldtype import *

   @renderable((700, 350))
   def render(r):
      return (StyledString("COLDTYPE",
         Style("assets/ColdtypeObviously-VF.ttf",
            350, wdth=0, tu=20, r=1, rotate=10, ro=1))
         .pens()
         .align(r)
         .f(Gradient.Horizontal(r, hsl(0.95, s=1, l=0.65), hsl(0.7, s=1, l=0.7)))
         .translate(0, 5))

.. image:: /_static/renders/index_render.png
   :width: 350

Examples
--------

.. toctree::
   :maxdepth: 3

   examples/index

Documentation
-------------

.. toctree::
   :maxdepth: 2

   text
   pens



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
