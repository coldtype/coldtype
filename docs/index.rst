coldtype
====================================

`Coldtype` is a cross-platform library for programming and animating display typography with Python.

Put another way: do you want to make typographic graphics and animations with code? This is a good & idiosyncratic way to do that.

🌋 **Disclaimer**: coldtype is alpha-quality software 🌋

TLDR (if you're using a python >= 3.7)

.. code:: bash
   
   pip install "coldtype[viewer]"
   coldtype demo

Here’s an example:

.. code:: python

   from coldtype import *

   fnt = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")

   @renderable((700, 350))
   def coldtype_simple(r):
      return (StSt("COLDTYPE", fnt, 350,
            wdth=0, tu=20, r=1, rotate=10)
         .align(r)
         .f(hsl(0.65, 0.6)))

.. image:: /_static/renders/index_coldtype_simple.png
   :width: 350

If you’re familiar with other graphics programming libraries, that code snippet might seem a little odd, given that it’s **canvas-less** & highly **abbreviated**, with a idiomatic emphasis on **method-chaining** & **structured data** (which can make programming **animations** a lot easier and faster). `More on those bold words on the about page.`

A more complex example
----------------------

Here’s a somewhat complex animation — made entirely with coldtype — demonstrating what’s possible with not-so-much code:

.. raw:: html

   <div id="video" style="max-width:500px;margin-bottom:20px"><div style="padding:100% 0 0 0;position:relative;"><iframe src="https://player.vimeo.com/video/479376752?loop=1&title=0&byline=0&portrait=0" style="position:absolute;top:0;left:0;width:100%;height:100%;" frameborder="0" allow="autoplay; fullscreen" allowfullscreen></iframe></div><script src="https://player.vimeo.com/api/player.js"></script></div>


The code for that video is available here: https://github.com/goodhertz/coldtype/tree/main/examples/animations/808.py


Table of Contents
-----------------

.. toctree::
   :maxdepth: 10

   about
   install
   cheatsheets/index
   tutorials/index
   api/index

.. toctree::
   :maxdepth: 2
   :caption: Links

   the coldtype blog <https://blog.coldtype.xyz>
   the coldtype discord <https://discord.gg/rWaJDqb8jE>
   github <https://github.com/goodhertz/coldtype>
   goodhertz.com <https://goodhertz.com>

.. toctree::
   :maxdepth: 2
   :caption: Examples

   808.py <https://github.com/goodhertz/coldtype/tree/main/examples/animations/808.py>
   banner.py <https://github.com/goodhertz/coldtype/tree/main/examples/animations/banner.py>
   digestive_wind.py <https://github.com/goodhertz/coldtype/tree/main/examples/animations/digestive_wind.py>
   metaprogramming.py <https://github.com/goodhertz/coldtype/tree/main/examples/animations/metaprogramming.py>
   stacked_and_justified.py <https://github.com/goodhertz/coldtype/tree/main/examples/animations/stacked_and_justified.py>
   vulfbach.py <https://github.com/goodhertz/coldtype/tree/main/examples/animations/vulfbach.py>


Indices and tables
==================

* :ref:`search`
