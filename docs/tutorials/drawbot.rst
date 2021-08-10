DrawBot-in-Coldtype
===================

Though `DrawBot <https://drawbot.com>`_ and Coldtype encourage different programming styles, DrawBot can be used inside Coldtype, by using a special type of renderable — the ``@drawbot_script`` renderable.

Installing
----------

DrawBot is not installed by default with Coldtype, so you’ll need to install DrawBot in your virtualenv, like so:

.. code:: bash

    pip install pip install git+https://github.com/typemytype/drawbot

@drawbot_script
---------------

Now that you’ve got the module version of DrawBot installed, with just a little bit of preamble, you can now use Coldtype to do anything you'd normally do in a DrawBot script.

.. code:: python

    from coldtype import *
    from coldtype.drawbot import *
    from drawBot import *

    @drawbot_script((500, 300))
    def db_text(r):
        fontSize(100)
        text("Hello!", (50, 50))

.. image:: /_static/renders/drawbot_db_text.png
    :width: 250
    :class: add-border

Unlike other renderables, the ``@drawbot_script`` renderable is "self-rasterizing", meaning what it communicates to the renderer is not data about what to draw, but the path to a pre-baked image. The details of that process aren't that important, but the takeaway is that this is pretty close to a normal DrawBot programming session, with the caveat that when you zoom in and out in the viewer, the script must re-render completely, because what you’re seeing is an image (and not a PDF like you see the DrawBot app). (More about zooming down below in "Scaling.")

Another caveat is that drawBot's ``newPage`` and ``size`` functions won’t work, as the dimensions of a graphic must be passed to the ``@drawbot_script`` decorator, ala ``@drawbot_script((500, 500))`` if you wanted a 500px x 500px graphic. (More down below on why ``newPage`` doesn’t make sense in Coldtype.)

Combining Idioms
----------------

You might be wondering why you’d want to use DrawBot in Coldtype. To me, one big upside is being able to use any text editor you want, rather than the DrawBot app itself.

.. code:: python

    long_txt1 = "Here is a long string which needs line-breaks to be typeset correctly — something Coldtype can’t do but DrawBot (by leveraging the CoreText APIs on macOS) can handle with aplomb."
    
    long_txt2 = "Here is another long string, this time set into an oval, made possible by sending textBox a BezierPath generated from a DATPen via the tobp method available in the coldtype.drawbot helpers module."

    import coldtype.drawbot as ctdb

    @drawbot_script((500, 500))
    def combined_idioms(r):
        fontSize(24)
        textBox(long_txt1, r.inset(10))
        # Coldtype Rect's can be passed anywhere a rectangle-like list would be passed in DrawBot

        oval = (DATPen()
            .oval(r.take(0.75, "mny")
                .inset(20).square()))

        (oval.copy()
            .outline(20)
            .f(hsl(0.95, 1, 0.8, a=0.25))
            .chain(ctdb.dbdraw))
        
        textBox(long_txt2,
            ctdb.tobp(oval), align="right")
    
.. image:: /_static/renders/drawbot_combined_idioms.png
    :width: 250
    :class: add-border

Multi-page documents
--------------------

In general, Coldtype does not support the idea of a multi-page document; the closest thing supported natively by Coldtype is an ``@animation`` renderable — and if you think about it, what’s the real difference between a multi-frame animation and a multi-page document? Luckily there’s a ``@drawbot_animation`` renderable that makes multi-frame drawBot animations very easy.

All that said, it is still quite possible to do normal DrawBot things in a Coldtype script. So here’s an example of generating a multi-page PDF, using a combination of Coldtype and DrawBot constructs.

.. code:: python

    @drawbot_animation((500, 200))
    def multipage_doc(f):
        c = hsl(f.a.progress(f.i).e, s=0.5, l=0.5)
        (DATPen(f.a.r)
            .f(c)
            .chain(ctdb.dbdraw))
        fontSize(50)
        fill(1)
        textBox("Page " + str(f.i), f.a.r.inset(50))


    def release(passes):
        ctdb.pdfdoc(multipage_doc,
            "examples/drawbot/drawbot_multipage.pdf")

.. code:: ruby

    multipage_doc_contactsheet = multipage_doc.contactsheet(2)

.. image:: /_static/renders/drawbot_multipage_doc_contactsheet.png
    :width: 500
    :class: add-border

The key to making this work is the magic function ``release``, which can be defined once in any Coldtype source file, and provides a "second chance" to create artifacts based on what's been rendered by the coldtype renderer. The salient point here is that you can write your own special code to run whenever the ``release`` action is called, which can be outside the standard save/reload/render workflow of Coldtype. This can be useful for all kinds of things (it’s how this documentation is generated, for example), but here it's useful because we're saying, `OK`, the graphics look good, let's now use DrawBot to bake a PDF, using the same code that we've been editing and previewing via the Coldtype viewer.

How to trigger the release code? I trigger it via a MIDI trigger + a .coldtype.py configuration file, but it’s as easy as typing "release" into the running command line prompt, or hitting the R key with the viewer app focused.


Scaling
-------

Because the default behavior of DrawBot is to display a PDF of the result of your code and to zoom in on a composition automatically, you might be surprised that graphics appear pretty small in the Coldtype viewer window by default, because Coldtype defaults to showing the graphics at actual size. If you'd like to default to showing your graphics at a higher resolution (i.e. if you’re making a PDF), there are a few options:

* You can zoom in with +/- on your keyboard in the viewer app
* You can specify a `preview-scale` argument to the renderer itself when you start it on the command-line, ala ``coldtype drawbot_script.py -ps 2``

Coldtype-in-DrawBot
-------------------

If you’re used to Coldtype idioms but want to use DrawBot, you can install the core functionality of Coldtype in DrawBot and use it like a normal Python package.

To install Coldtype in DrawBot, open up DrawBot and then navigate via the top bar to Python > Install Python Packages. There you can switch the input selector to "Install" and then type in "coldtype".

Now you should be able to access Coldtype-in-DrawBot.

.. code:: python

    from coldtype.drawbot import *

    r = page_rect()
    fp = "/System/Library/Fonts/SFCompactRounded.ttf"
    f = Font.Cacheable(fp)

    (StSt("Coldtype", f, 200, r, wght=1)
        .f(hsl(0.8))
        .align(r)
        .chain(dbdraw))
