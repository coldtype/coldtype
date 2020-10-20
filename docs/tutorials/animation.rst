Animation
=========

Lots of example animations in the `coldtype-examples <https://github.com/goodhertz/coldtype-examples>`_ repo.

That said, here’s a little example:

.. code:: python

    from coldtype import *

    tl = Timeline(30)

    @animation(timeline=tl)
    def render(f):
        e = f.a.progress(f.i, loops=1, easefn="qeio").e
        return (DATPen()
            .oval(f.a.r.inset(100*e))
            .f(hsl(e)))

Save that in a file called ``animation.py``, then run it ala ``coldtype animation.py`` — when the render preview runs and a window pops up, try hitting the left and right arrow keys on your keyboard to go backward and forward in time.

If you want to see the full animation, hit the key "a" on your keyboard, and you should see some text appear in your terminal, noting that the frames of the animation are being saved to disk. When it finishes (it’ll say something like ``rendered``), you can hit the space bar on the viewer and it should playback the animation. Hit the spacebar again to stop the looped playback.