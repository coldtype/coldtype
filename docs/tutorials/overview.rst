Overview
========

Anatomy of a Coldtype Program
-----------------------------

A coldtype program is a source file, usually a Python file with a ``*.py`` file extension. Inside that file, you can write anything you want, but at the very least you'll need do two things

1. Import the coldtype library
2. Define a renderable function

So to get going from scratch, create a new Python source file, something like ``anatomy.py`` or whatever you want to call it.

Then for the first line:

.. code:: python

    from coldtype import *

(You could also do ``import coldtype``, but for the examples in this documentation, ``from coldtype import *`` is the idiomatic import.)

For the second requirement – **defining a renderable function** — all you need is a function that accepts a single argument, a ``Rect``, like so:

.. code:: python

    def show_something(r:Rect):
        return P().rect(r)

If you followed the install instructions and have activated your virtual environment, you can now run this file from the command-line, like so:

.. code:: bash

    coldtype anatomy.py

Unfortunately, you won't see anything other than a window that pops up and says: "Nothing found."

That's because we didn't tell the renderer that anything in our source file is ``renderable``. We can remedy that situation by adding the ``@renderable`` decorator right above where we define our rendering function.

So let’s create a new function and mark it as renderable.

.. code:: python

    @renderable()
    def really_show_something(r:Rect):
        return P().rect(r)

.. image:: /_static/renders/overview_really_show_something.png
    :width: 540
    :class: add-border

Now when you save the source file (no need to stop it and restart it on the command line), you should see a gigantic pink rectangle. If you try changing something about that rectangle, like adding ``.f(hsl(random()))`` to the end of the return statement, or change the ``.rect`` to a ``.oval`` , as soon as you save the source file, you should see changes in the viewer.

Multiple renderables
--------------------

You can specify as many renderables in a source file as you’d like. So if you want to make something different — maybe some text in an oval in a 1440x1080 rectangle — you can just add another decorated function, like so:

.. code:: python

    @renderable((1440, 1080))
    def sample_text(r):
        return PS([
            P().oval(r.inset(20)).f(hsl(random())),
            (StSt("COLDTYPE",
                Font.ColdtypeObviously(), 500,
                wdth=0, tu=100, rotate=10)
                .align(r)
                .f(1))])

.. image:: /_static/renders/overview_sample_text.png
    :width: 720
    :class: add-border

Some of that text-setting code might seem a little bewildering, but all of it’s covered in the Text tutorial in this documentation.

(Kind of an aside, but if you have a file with lots of renderable functions, you can filter which functions are rendered by typing something like ``ff .*text`` into the running command line process. ``ff`` stands for filter-functions, and the ``.*text`` is a regular expression that matches the names of the functions. To undo that change, you can either stop and restart the process, or type in ``ff .*``, which is a regex that matches any function name.)


Workflow of a Coldtype Program
------------------------------

At this point you might be wondering, `how do I save what's on screen to a file on my computer?`

If you’re familiar with DrawBot, you might think you need to write some code to do that, but one of the core tenets of coldtype is that rendering and rasterizing are handled by the renderer, not by the source code. This makes some things that are easy in DrawBot difficult in Coldtype, but it also makes many things that are difficult in DrawBot extremely easy in Coldtype.

If you have you’re program running, to render what you have so far to disk, you can focus on the Coldtype viewer window and hit the ``a`` key on your keyboard. That should print some things out on the command-line, including the path of a brand-new png file.

A few notes:

* The name of the file created is the name of the source file combined with the name of the function. So in this case, the ``sample_text`` function rendered to a png called ``renders/overview_sample_text.png``. The ``renders`` folder is automatically created by the renderer. (All of this can be customized, but this is the default behavior for all non-animation graphics.)

* ``a`` stands for "all," as in ``render-all``. In Coldtype there is a distinction between rendering all of what a file represents, versus just a segment (workarea) of what a file represents. If you're coding a small number of static graphics like the pink rectangle in our source file, the distinction between render-all and render-workarea is basically meaningless, because it takes such a short amount of time to render everything. But when you’re working on an animation — when you’re rendering 3000 frames and each frame takes a few milliseconds to render — the distinction becomes crucial.

Another core tenet of Coldtype is that it should be easy to trigger things like `render-all` in a variety of ways.

For instance, you can also type ``render_all`` into the command line prompt and hit enter. Or you can abbreviate that and just type in ``a`` and hit enter.

You can also hook that action up to a MIDI controller, by writing ``~/.coldtype.py`` configuration file. (More on that in the MIDI tutorial.)

You can even write another program in any language you want that sends messages via websocket to a running coldtype program, which is how the Coldtype Adobe panel extension works. (More on that in the Premiere and After Effects tutorials.)
