Shapes
======

To run any of these examples, you'll want to save a bit of code in a python file, with any name, e.g. ``shape.py``, and then run that file by navigating to it on the command line and constructing a call like, ``coldtype shape.py``

Basic Shapes
------------

Let’s start with a classic rectangle.

.. code:: python

    from coldtype import *

    @renderable((300, 300))
    def rectangle(r):
        return DATPen().rect(r.inset(50)).f(hsl(0.9))

.. image:: /_static/renders/shapes_rectangle.png
    :width: 150

That’s how to draw a rectangle with a 50px padding around the edges (the padding comes from the ``r.inset(50)`` call). (I’m re-reading this now and if you’re thinking to yourself: that’s a square — well that makes sense, but a square’s just a rectangle with the same width & height.)

How about an oval?

.. code:: python

    @renderable((300, 300))
    def oval(r):
        return DATPen().oval(r.inset(45)).f(hsl(0.6))

.. image:: /_static/renders/shapes_oval.png
    :width: 150

That’s an oval. Sweeet.

What if you want to combine an oval and a rect?

.. code:: python

    @renderable((300, 300))
    def ovalrect(r):
        return (DATPen()
            .oval(r.inset(60))
            .translate(30, 30)
            .union(DATPen()
                .rect(r.inset(65))
                .translate(-30, -30))
            .f(hsl(0.05, l=0.6, s=0.75)))

.. image:: /_static/renders/shapes_ovalrect.png
    :width: 150

Or maybe you want just the parts of those two shapes that don’t overlap? And maybe you want to fill the shape with a gradient and rotate the rect a little bit and then eyeball how it should be centered in its frame?

.. code:: python

    @renderable((300, 300))
    def ovalrect_diff(r):
        return (DATPen()
            .oval(r.inset(60))
            .translate(30, 30)
            .xor(DATPen()
                .rect(r.inset(65))
                .translate(-30, -30)
                .rotate(-5))
            .f(Gradient.Horizontal(r,
                hsl(0.05, l=0.6, s=0.75),
                hsl(0.8, l=0.6, s=0.5)))
            .translate(7)) # & eyeball it

.. image:: /_static/renders/shapes_ovalrect_diff.png
    :width: 150

Modifying Shapes
----------------

Here’s an example of building up a chain of effects to modify a simple vector shape.

.. code:: python

    @renderable((300, 300))
    def ovalmod(r):
        return (DATPen()
            .oval(r.inset(60))
            .flatten(5) # <- breaks the oval down into non-curves, 5 is the length of the segment
            .roughen(15) # <- randomizes the vertices of the shape
            .smooth() # <- attempts to "smooth" the lines
            .f(hsl(0.05, l=0.6, s=0.75)))

.. image:: /_static/renders/shapes_ovalmod.png
    :width: 150