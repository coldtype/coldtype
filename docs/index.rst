coldtype
====================================

`Coldtype` is a cross-platform library for programming high-quality display typography with Python.

Do you want to make graphics and animations with code? This is a good & strange way to do that.

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

And here’s a video made with a combination of  coldtype and After Effects:

.. raw:: html

   <div id="video" style="max-width:500px;margin-bottom:20px"><div style="padding:100% 0 0 0;position:relative;"><iframe src="https://player.vimeo.com/video/408581790?loop=1&title=0&byline=0&portrait=0" style="position:absolute;top:0;left:0;width:100%;height:100%;" frameborder="0" allow="autoplay; fullscreen" allowfullscreen></iframe></div><script src="https://player.vimeo.com/api/player.js"></script></div>


The code for that video is available here: https://github.com/goodhertz/coldtype-examples/blob/master/animations/808.py


Reference
-------------

.. toctree::
   :maxdepth: 10

   install
   tutorials/index
   api/index

.. toctree::
   :maxdepth: 2
   :caption: Links

   github <https://github.com/goodhertz/coldtype>
   goodhertz.com <https://goodhertz.com>

.. toctree::
   :maxdepth: 2
   :caption: Examples

   coldtype-examples <https://github.com/goodhertz/coldtype-examples>
   808.py <https://github.com/goodhertz/coldtype-examples/blob/master/animations/808.py>
   banner.py <https://github.com/goodhertz/coldtype-examples/blob/master/animations/banner.py>
   digestive_wind.py <https://github.com/goodhertz/coldtype-examples/blob/master/animations/digestive_wind.py>
   stacked_and_justified.py <https://github.com/goodhertz/coldtype-examples/blob/master/animations/stacked_and_justified.py>
   vulfbach.py <https://github.com/goodhertz/coldtype-examples/blob/master/animations/vulfbach.py>



Indices and tables
==================

* :ref:`search`
