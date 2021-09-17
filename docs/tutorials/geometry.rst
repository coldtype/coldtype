Geometry
========

`Available as an interactive Colab notebook here <https://colab.research.google.com/drive/1ldEBGu6z5kJBamnpCA1D71fecpZyFbPs?usp=sharing>`_

To run any of these examples, you'll want to save a bit of code in a python file, with any name, e.g. ``geometry.py``, and then run that file by navigating to it on the command line and constructing a call like, ``coldtype geometry.py``

Dividing Rect(angles)
---------------------

One of the core concepts of Coldtype is the use of the ``coldtype.geometry.Rect`` class to encapsulate rectangles and methods for slicing & dicing them.

The most basic rectangle is the one passed to a renderable, i.e. the ``r`` variable you get when you define a renderable function, like ``def rect(r)`` below. So to fill the entire canvas with a single random color, you can do something like this:

.. code:: python

    from coldtype import *

    @renderable((700, 300))
    def rect(r):
        return P(r).f(hsl(random()))

.. image:: /_static/renders/geometry_rect.png
    :width: 350
    :class: add-border

All ``@renderables`` have a rectangle associated with them (the full rectangle of the artifact canvas), and all rendering functions are passed rectangles, either via the first and only argument, or as a property of the first argument, as is the case with ``@animation`` renderables, which pass a ``Frame`` argument that makes the rectangle accessible via ``f.a.r`` (where ``f`` is the ``Frame``).

But we’re getting ahead of ourselves.

A ``Rect`` has lots of methods, though the most useful ones are ``inset``, ``offset``, ``take``, ``divide``, and ``subdivide``.

Here’s a simple example that insets, offsets, subtracts, and then subtracts again. (Probably not something I’d write in reality, but good for demonstration purposes.)

.. code:: python

    @renderable((700, 300))
    def iot(r):
        return (P()
            .rect(r
                .take(0.5, "W") # "W" for "West"
                .inset(20, 20)
                .offset(0, 10)
                .subtract(20, "E")
                .subtract(10, "N"))
            .f(hsl(0.5)))

.. image:: /_static/renders/geometry_iot.png
    :width: 350
    :class: add-border

More complex slicing & dicing
-----------------------------

**N.B.** You may have noticed that the rect functions that a mix of float and int arguments. That’s because a value less than 1.0 will be treated, by the dividing-series of rect functions, as percentages of the dimension implied by the edge argument. So in that ``take(0.5, "W")`` above, the ``0.5`` specifies 50% of the width of the rectangle (width because of the ``W`` edge argument).

Here’s an example that divides a rectangle into left and right rectangles, and shows another useful method, ``square`` (which takes the largest square possible from the center of the given rectangle).

.. code:: python

    @renderable((700, 300))
    def lr(r):
        ri = r.inset(50, 50)
        left, right = ri.divide(0.5, "W")
        return PS([
            (P().rect(ri)
                .f(None)
                .s(0.75)
                .sw(2)),
            (P().oval(left
                    .square()
                    .offset(100, 0))
                .f(hsl(0.6, a=0.5))),
            (P().oval(right
                    .square()
                    .inset(-50))
                .f(hsl(0, a=0.5)))])

.. image:: /_static/renders/geometry_lr.png
    :width: 350
    :class: add-border

Here’s an example using ``subdivide`` to subdivide a larger rectangle into smaller pieces, essentially columns.

.. code:: python

    @renderable((700, 300))
    def columns(r):
        cs = r.inset(10).subdivide(5, "W")
        return PS.Enumerate(cs, lambda x:
            P(x.el.inset(10)).f(hsl(random())))

.. image:: /_static/renders/geometry_columns.png
    :width: 350
    :class: add-border

Of course, columns like that aren’t very typographic. Here’s an example using ``subdivide_with_leading``, a useful method for quickly getting standard rows or columns with classic spacing.

.. code:: python

    @renderable((700, 500))
    def columns_leading(r):
        cs = r.subdivide_with_leading(5, 20, "N")
        return PS.Enumerate(cs, lambda x:
            P(x.el).f(hsl(random())))

.. image:: /_static/renders/geometry_columns_leading.png
    :width: 350
    :class: add-border