Animation
=========

There are lots of examples of somewhat complex animation in the `examples/animations <https://github.com/goodhertz/coldtype/tree/main/examples/animations>`_ directory, but here are some simpler (and shorter) ones, that demonstrate the fundamentals of how animations are built in coldtype.

A circle moving
---------------

.. code:: python

    from coldtype import *

    tl = Timeline(30)

    @animation((250, 250), timeline=tl, bg=1)
    def circle(f):
        e = f.a.progress(f.i, easefn="qeio").e
        return [
            DATPen().rect(f.a.r).f(1),
            (DATPen()
                .oval(f.a.r.offset(-f.a.r.w+f.a.r.w*2*e, 0))
                .f(hsl(e, s=0.75)))]
    
.. code:: ruby

    #circle_contactsheet = circle.contactsheet(6)

Save that code in a file called ``animation.py``, then run it ala ``coldtype animation.py`` — when the render preview runs and a window pops up, try hitting the left and right arrow keys on your keyboard to go backward and forward in time.

If you **hold down the arrow keys**, you can preview the animation; depending on how complex your animation is, "previewing" might be exactly the same as viewing the final animation, if the frames render as fast as real-time. (Even if they don’t, holding down the right arrow key should still give you a good sense of the mechanics of the animation in time.)

To see the animation come to life, hit the space bar. If your animation renders faster than real-time (i.e. faster than the frame-rate defined in the Timeline associated with the ``@animation`` decorator), when you hit the spacebar, the animation will play back at the defined frame rate (which defaults to 30fps). If not, not a big deal, it'll just be a little slower than the intended frame rate.

One cool thing to note — once you hit the space bar, if you make changes to the source file and hit save, the animation will update and keeping playing back.

If you want to see the full animation played back at it's true frame rate regardless of how intensive the rendering is, hit the key "a" on your keyboard, and you should see some text appear in your terminal, noting that the frames of the animation are being saved to disk. When it finishes (it’ll say something like ``rendered``), the animation will automatically start playing back. You can hit ``shift+space`` in the viewer to stop that playback.

Here’re all the frames of that animation (a circle moving across the frame, and changing colors):

.. image:: /_static/renders/animation_circle_contactsheet.png
    :width: 500
    :class: add-border

A letter flying
---------------

.. code:: python

    from coldtype import *

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

.. code:: ruby

    #flyinga_contact = flyinga.contactsheet(4, slice(0, None, 1))

.. image:: /_static/renders/animation_flyinga_contactsheet.png
    :width: 500
    :class: add-border

And here’s a little bit of code to generate gifs, using ffmpeg, which will need to be installed on your computer independently of coldtype (via something like `brew install ffmpeg`) (or you can, as described below, import the pngs as an image sequence into something like Premiere).

To get this code to run, you want to trigger the ``Release`` KeyboardShortcut, by hitting `cmd+L` in the viewing app.

.. code:: python

    def release(passes):
        FFMPEGExport(circle, passes).gif().write()
        FFMPEGExport(flyinga, passes).gif().write()

.. image:: /_static/renders/circle.gif
    :width: 125
    :class: add-border

.. image:: /_static/renders/flyinga.gif
    :width: 125
    :class: add-border

Jumping to Adobe
----------------

While it is possible to complete an animation using nothing but code (and in the near future this process will get easier), I usually employ a program like Premiere or After Effects to both view and finish animations that I start in code, either to apply effects in After Effects, or to match the animation with music in Premiere. Because animations done in Coldtype are rendered to PNGs, you can import those easily in any video editing program. (In Premiere, just make sure to select the 0000 image, then select Options > Image Sequence when importing.)

To generate a full set of frames for a coldtype animation, hit the ``a`` key in the viewer app — once you do, you should see the command line prompt printing out a bunch of information about frames being rendered. (Also, once you do that, you can hit ``shift+space`` to preview the animation in real time at the correct frame rate, using the cached frames.)