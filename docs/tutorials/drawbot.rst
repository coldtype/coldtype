DrawBot-in-Coldtype
===================

Though `DrawBot <https://drawbot.com>`_ and Coldtype encourage different programming styles, DrawBot can be used inside Coldtype, by using a special type of renderable — the ``@drawbot_script`` renderable.

Installing
----------

You’ll also need to install DrawBot in your virtualenv, like so:

.. code:: bash

    pip install pip install git+https://github.com/typemytype/drawbot

@drawbot_script
---------------

Now that you’ve got the module version of DrawBot installed, with just a little be of preamble, you can now use Coldtype to do anything you'd normally do in a DrawBot script.

.. code:: python

    from coldtype import *
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
    
    long_txt2 = "Here is another long string, this time set into an oval, made possible by sending textBox a BezierPath generated from a DATPen via the .bp method available on Coldtype’s DATPen class."

    @drawbot_script((500, 500))
    def combined_idioms(r):
        fontSize(24)
        textBox(long_txt1, r.inset(10))
        # Coldtype Rect's can be passed anywhere a rectangle-like list would be passed in DrawBot

        oval = DATPen().oval(r.take(0.75, "mny").inset(20).square())
        oval.copy().outline(20).f(hsl(0.95, 1, 0.8, a=0.25)).db_drawPath()
        textBox(long_txt2, oval.bp(), align="right")
    
.. image:: /_static/renders/drawbot_combined_idioms.png
    :width: 250
    :class: add-border

Multi-page documents
--------------------

In general, Coldtype does not support the idea of a multi-page document; the closest thing supported natively by Coldypte is an ``@animation`` renderable — and if you think about it, what’s the real difference between a multi-frame animation and a multi-page document? Luckily there’s a ``@drawbot_animation`` renderable that makes multi-frame drawBot animations very easy.

All that said, it is still quite possible to do normal DrawBot things in a Coldtype script. So here’s an example of generating a multi-page PDF, using a combination of Coldtype and DrawBot constructs.

.. code:: python

    tl = Timeline(10) # a 10-page document

    @drawbot_animation((500, 200))
    def multipage_doc(f):
        c = hsl(f.a.progress(f.i).e, s=0.5, l=0.5)
        DATPen().rect(f.a.r).f(c).db_drawPath()
        fontSize(50)
        fill(1)
        textBox("Page " + str(f.i), f.a.r.inset(50))
    
    multipage_doc_contactsheet = multipage_doc.contactsheet(2)
    
    def release(passes):
        newDrawing()
        r = multipage_doc.rect
        w, h = r.wh()
        for idx in range(0, multipage_doc.duration):
            print(f"Saving page {idx}...")
            newPage(w, h)
            multipage_doc.func(Frame(idx, multipage_doc, []))
        saveImage("docs/tutorials/drawbot_multipage.pdf")
        endDrawing()

.. image:: /_static/renders/drawbot_multipage_doc_contactsheet.png
    :width: 500
    :class: add-border


Scaling
-------

Because the default behavior of DrawBot is to display a PDF of the result of your code and to zoom in on a composition automatically, you might be surprised that graphics appear pretty small in the Coldtype viewer window by default. To remedy that, there are a few options:

* You can zoom in with +/- on your keyboard
* You can specify a `preview-scale` argument to the renderer itself when you start it on the command-line, ala ``coldtype drawbot_script.py -ps 2``
* You can type `ps 2` into a running renderer CLI prompt, to set the scale programmatically

