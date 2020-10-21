coldtype
====================================

`Coldtype` is a cross-platform library for programming and animating high-quality display typography with Python.

Put another way: do you want to make graphics and animations with code? This is a good & strange way to do that.

Here’s an example:

.. code:: python

   from coldtype import *

   @renderable((700, 350))
   def coldtype(r):
      return (StyledString("COLDTYPE",
         Style("assets/ColdtypeObviously-VF.ttf",
            350, wdth=0, tu=20, r=1, rotate=10, ro=1))
         .pens()
         .align(r)
         .f(Gradient.Horizontal(r, hsl(0.69, s=1, l=0.55), hsl(0.55, s=1, l=0.6)))
         .translate(0, 5))

.. image:: /_static/renders/index_coldtype.png
   :width: 350

Some oddities to note if you’re familiar with other graphics programming environments:

* There is no "canvas" — all graphics are **hierarchical data** ``return``-ed from a function to the renderer, which does all the actual drawing-to-a-virtual-canvas.

* There is a lot of emphasis on **method-chaining**, which (I feel) is an underappreciated way to do graphics programming, since the resulting code is easily editable and experimentable. Of course, some (like the creator of Python) have called this style of programming "un-Pythonic."

* As might already be clear from the first two points, coldtype is not meant to be a good introduction to programming (though it might still be, I'm not sure). The emphasis here is on programming patterns that ease the creation of professional graphics, particularly **complex animations**.

With all that in mind, here’s a somewhat complex animation made with a combination of  coldtype and After Effects, to demonstrate what’s possible with not-so-much code:

.. raw:: html

   <div id="video" style="max-width:500px;margin-bottom:20px"><div style="padding:100% 0 0 0;position:relative;"><iframe src="https://player.vimeo.com/video/408581790?loop=1&title=0&byline=0&portrait=0" style="position:absolute;top:0;left:0;width:100%;height:100%;" frameborder="0" allow="autoplay; fullscreen" allowfullscreen></iframe></div><script src="https://player.vimeo.com/api/player.js"></script></div>


The code for that video is available here: https://github.com/goodhertz/coldtype-examples/blob/main/animations/808.py

For more of examples of what coldtype can do:

- `Vulfpeck, “LAX” <https://www.youtube.com/watch?v=NzxW8nxgENA>`_
- `"Buggin’ Out (Phife Dawg’s Verse)" <https://vimeo.com/377148622>`_
- A `3D type specimen <https://vimeo.com/354292807>`_
- `Goodhertz plugins <https://goodhertz.com/>`_
- Anything recent on `my website <https://robstenson.com/>`_

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
   808.py <https://github.com/goodhertz/coldtype-examples/blob/main/animations/808.py>
   banner.py <https://github.com/goodhertz/coldtype-examples/blob/main/animations/banner.py>
   digestive_wind.py <https://github.com/goodhertz/coldtype-examples/blob/main/animations/digestive_wind.py>
   stacked_and_justified.py <https://github.com/goodhertz/coldtype-examples/blob/main/animations/stacked_and_justified.py>
   vulfbach.py <https://github.com/goodhertz/coldtype-examples/blob/main/sanimations/vulfbach.py>



Indices and tables
==================

* :ref:`search`
