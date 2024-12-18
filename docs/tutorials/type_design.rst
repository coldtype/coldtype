Type Design
===========

Live Reload UFOs
----------------

One fun thing that coldtype can do out of the box is load ``.ufo`` and ``.designspace`` files, as well as monitor those files for changes.

Here’s an example of creating a somewhat complex text setting using the ``assets/ColdtypeObviously_BlackItalic.ufo`` UFO source, then automatically monitoring the UFO source and refreshing the rendered composition based on any changes saved to the UFO.

.. code:: python

    from coldtype import *

    ufo_ttf = Font("assets/ColdtypeObviously_BlackItalic.ufo")

    @renderable((1200, 300), watch=[ufo_ttf], bg=0)
    def ufo_monitor(r):
        return (StSt("CDELOPTY", ufo_ttf, 250, tu=-150, r=1)
            .fssw(Gradient.H(r, hsl(0.05, s=0.75), hsl(0.8, s=0.75))
                , 0, 15, 1)
            .align(r))

.. image:: /_static/renders/type_design_ufo_monitor.png
    :width: 600

Now if you run the code above (via ``coldtype <your-filename-here>.py``) and then open up the source UFO in RoboFont or another UFO-capable font editor, any changes you save to the source will update automatically in the preview window, if you leave the process hanging.

This works because the font is passed to ``watch=`` keyword argument of the ``@renderable`` decorator. This instructs the renderer to monitor that font’s source UFO for changes. (This also works for standard fonts, i.e. ``.ttf`` and ``.otf`` files.)

Also worth noting: because the UFO font is loaded above by compiling it to a ttf (coldtype does this automatically via ``FontGoggles`` when you pass a ``.ufo`` to ``Font``), you can also use a coldtype program as a way to test OT feature code in realtime — simply edit the feature code, hit save, & the coldtype program above with automatically update.

If you want to address glyphs in a UFO directly by their glyph names, you can also load a ``defcon.Font`` directly, as an alternate representation of the UFO source. (``DefconFont`` is provided by coldtype as an alternate name for ``defcon.Font``) This method skips any typesetting code and uses the glyphs in the UFO as pens, via the helper method ``glyph`` provided by ``P`` (which records a ``defcon.Glyph`` to the given pen).

.. code:: python

    ufo = DefconFont("assets/ColdtypeObviously_BlackItalic.ufo")

    @renderable((500, 500), watch=[ufo.path])
    def defcon_monitor(r):
        return (P()
            .glyph(ufo["C"])
            .scale(0.5)
            .align(r)
            .f(0))

.. image:: /_static/renders/type_design_defcon_monitor.png
    :width: 250
    :class: add-border

`N.B.` Rather than passing the ``ufo`` object directly to the ``watch=`` argument, we’ve passed it’s ``.path`` property — in the first example we passed the ``Font`` object directly, but coldtype knows how to handle that natively. For anything other than a ``Font``, you can pass its filesystem representation, meaning you can monitor any file on your computer.

.. code:: python

    generic_txt = Path("docs/tutorials/scratch.txt")

    @renderable((800, 200), watch=[generic_txt])
    def txt(r):
        return P(
            StSt(
                "> " + generic_txt.read_text() + " <",
                "assets/RecMono-CasualItalic.ttf", 50)
                .f(0.25)
                .align(r))

.. image:: /_static/renders/type_design_txt.png
    :width: 400
    :class: add-border