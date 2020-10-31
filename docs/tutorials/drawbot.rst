DrawBot-in-Coldtype
===================

Though `DrawBot <https://drawbot.com>`_ and Coldtype encourage different programming styles, DrawBot can be used inside Coldtype, by using a special type of renderable — the ``@drawbot_script`` renderable.

So with just a little be of preamble, you can now do anything you'd normally do in a DrawBot script.

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

Unlike other renderables, the @drawbot_script renderable is "self-rasterizing", meaning what it communicates to the renderer is not data about what to draw, but the path to an image itself. The details aren't that important, but the takeaway is that this is pretty close to a normal DrawBot programming session, with the caveat that when you zoom in and out in the viewer, the script must re-render completely, because what you’re seeing is an image (and not a PDF like you see the DrawBot app).

Another caveat is that drawBot's ``newPage`` and ``size`` functions won’t work, as those instructions must be passed to the @drawbot_script

Combining Idioms
----------------

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

    @drawbot_animation((500, 500))
    def multipage_doc(f):
        fontSize(120)
        fill(*hsl(0.65, s=1))
        textBox(str(f.i), f.a.r.inset(100))
    
    def release(_):
        newDrawing()
        r = multipage_doc.rect
        w, h = r.wh()
        for idx in range(0, multipage_doc.duration):
            print(idx)
            db.newPage(w, h)
            multipage_doc.func(Frame(idx, multipage_doc, []))
        db.saveImage("test.pdf")
        db.endDrawing()

.. image:: /_static/renders/drawbot_multipage_doc.png
    :width: 250
    :class: add-border

