Type Design
===========

Live Reload UFOs
----------------

One fun thing that coldtype can do out of the box is load ``.ufo`` and ``.designspace`` files, as well as monitor those files for changes.

Here’s an example of creating a complex lockup of text using the ``assets/ColdtypeObviously_BlackItalic.ufo`` UFO source, then automatically monitoring the UFO source and refreshing the rendered composition based on any changes made there.

.. code:: python

    from coldtype import *

    ufo_ttf = Font("assets/ColdtypeObviously_BlackItalic.ufo")

    @renderable((1200, 300))
    def ufo_monitor(r):
        return [
            DATPen().rect(r).f(0),
            (StyledString("CDELOPTY",
                Style(ufo_ttf, 250, tu=-150, r=1))
                .pens()
                .f(Gradient.H(r, hsl(0.05, s=0.75), hsl(0.8, s=0.75)))
                .understroke(s=0, sw=15)
                .align(r))
        ]

.. image:: /_static/renders/type_design_ufo_monitor.png
    :width: 600

Now if you run the code above (via ``coldtype <your-filename-here>.py``) and then open up the source UFO in RoboFont or another UFO-capable font editor, any changes you save to the source will update automatically in the preview window, if you leave the process hanging.

And because the font is loaded by compiling it to a ttf (via ``FontGoggles``), you can also use a coldtype program as a way to test OT feature code in realtime, without any additional code — simply edit the feature code, hit save, & the coldtype program above with automatically update.