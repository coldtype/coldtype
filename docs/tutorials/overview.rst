Overview
========

Anatomy of a Coldtype Program
-----------------------------

A coldtype program is a source file, usually a *.py python file. Inside that file, you can write anything you want, but at the very least you'll need do two things, **import coldtype** and **define a renderable function**.

So to get going from scratch, create a new Python source file, something like ``anatomy.py`` or whatever you want to call it.

Then for the first line:

.. code:: python

    from coldtype import *

(You could also do ``import coldtype``, but for the examples in this documentation, ``from coldtype import *`` is the idiomatic import.)

For the second – that **defining a renderable function**, all you need is a function that accepts a single argument, a ``Rect``, like so:

.. code:: python

    def show_something(r:Rect):
        return DATPen().rect(r)

If you followed the install instructions and have activated your virtual environment, you can now run this file from the command-line, like so:

.. code

    coldtype anatomy.py

Unfortunately, you won't see anything other than a window that pops up and says: "Nothing found."

That's because we didn't tell the renderer that anything in our source file is ``renderable``. We can remedy that situation by adding the ``@renderable`` decorator right above where we define our rendering function.

So let’s create a new function and mark it as renderable.

.. code:: python

    @renderable()
    def really_show_something(r:Rect):
        return DATPen().rect(r)

Now when you save the source file (no need to stop it and restart it on the command line), you should see a large pink rectangle.

Workflow of a Coldtype Program
------------------------------

At this point you might be wondering, `how do I save what's on screen to a file on my computer?`

If you familiar with DrawBot, you might think you need to write some code to do that, but one of the core tenets of coldtype is that rendering and rasterizing are handled by the renderer, not by the source code. This makes some things that are easy in DrawBot difficult in Coldtype, but it also makes many things that are difficult in DrawBot extremely easy in Coldtype.

If you have you’re program running, to render what you have so far to disk, just focus on the Coldtype viewer window and hit the ``a`` key on your keyboard. That should print some things out on the command-line, including the path a png file.

Why ``a``? That stands for "all," as in ``render-all``. In Coldtype there is a distinction between rendering all of what a file represents, versus just a segment (workarea) of what a file represents. If you're coding a small number of static graphics like the pink rectangle in our source file, the distinction between render-all and render-workarea is basically meaningless. But when you’re working on an animatioon, the distinction becomes crucial.

