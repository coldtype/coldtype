Animation
=========

Lots of example animations in the `coldtype-examples <https://github.com/goodhertz/coldtype-examples>`_ repo.

That said, here’s a little example to understand the fundamentals of how animations are built in coldtype.

.. code:: python

    from coldtype import *

    tl = Timeline(30)

    @animation((250, 250), timeline=tl, bg=1)
    def circle(f):
        e = f.a.progress(f.i, easefn="qeio").e
        return (DATPen()
            .oval(f.a.r.offset(-f.a.r.w+f.a.r.w*2*e, 0))
            .f(hsl(e, s=0.75)))
    
    circle_contactsheet = circle.contactsheet(6) # to render the full animation as a contact-sheet

Here’s all the frames of that animation (a circle moving across the frame, and changing colors), rendered as a contact sheet (ala the last right of the code right above here[#contactsheet]_):



.. image:: /_static/renders/animation_circle_contact.png
    :width: 500
    :class: add-border

Save that in a file called ``animation.py``, then run it ala ``coldtype animation.py`` — when the render preview runs and a window pops up, try hitting the left and right arrow keys on your keyboard to go backward and forward in time.

If you want to see the full animation, hit the key "a" on your keyboard, and you should see some text appear in your terminal, noting that the frames of the animation are being saved to disk. When it finishes (it’ll say something like ``rendered``), you can hit the space bar on the viewer and it should playback the animation. Hit the spacebar again to stop the looped playback.

.. code:: python

    from random import Random
    rnd = Random()
    rnd.seed(0)

    tl2 = Timeline(24)

    @animation((250, 250), storyboard=[0], bg=0, timeline=tl2)
    def flyinga(f):
        qeio = f.a.progress(f.i, easefn="qeio").e
        eei = f.a.progress(f.i, easefn="eei").e
        return [
            (DATPen()
                .rect(f.a.r)
                .f(hsl(qeio))),
            (StyledString("A",
                Style("assets/MutatorSans.ttf", 50, wght=0.2))
                .pen()
                .align(f.a.r)
                .scale(1+50*eei)
                .rotate(360*qeio)
                .f(1))]

    flyinga_contact = flyinga.contactsheet(4, slice(0, None, 1))

.. image:: /_static/renders/animation_flyinga_contact.png
    :width: 500
    :class: add-border

.. rubric:: Footnotes

.. [#contactsheet] The concept of a ``contactsheet`` is probably not something you’ll need to use in your own animations — it’s mostly used here as a way to illustrate the animations without requiring that the animation be embedded as a video file.