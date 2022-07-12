Text
====

`Available as an interactive Colab notebook here <https://colab.research.google.com/drive/1E-q_UdRFkxQRI7Lx6OxDfTw_WBD4cyuI?usp=sharing>`_

To run any of these examples, you'll want to save a bit of code in a python file, with any name, e.g. ``text.py``, and then run that file by navigating to it on the command line and constructing a call like, ``coldtype text.py``

Before we begin, let’s run some code needed to setup all the examples below. (If you’re copying just the code from one of the blocks below, you'll need to also copy this code and put it at the top of your source file.)

.. code:: python

    from coldtype import *

    co = Font.ColdtypeObviously()

Basic Text
----------

Let’s start with a simple Hello World, except in this case, let’s just say COLDTYPE, because the coldtype repository has a special version of Obviously in it that just has those letters.

.. code:: python

    @renderable((1000, 200))
    def basic(r):
        return (StSt("COLDTYPE", co, 150).align(r))

Which should get you this:

.. image:: /_static/renders/text_basic.png
    :width: 500
    :class: add-border

You might be wondering why the text is blue — that’s the default fill color for any text in coldtype. Let’s mess with the color and set some variable font axis values:

.. code:: python

    @renderable((1000, 200))
    def lessbasic(r):
        return (StSt("COLDTYPE", co, 150,
            wdth=0.5, rotate=10, tu=150)
            .align(r)
            .f(hsl(0.8, s=0.75)))

.. image:: /_static/renders/text_lessbasic.png
    :width: 500
    :class: add-border

What’s interesting (and different) about setting text with Coldtype is that you aren’t telling the computer to draw text, you're asking for information about the individual glyphs and where they sit, given the parameters you’re passing into ``StSt`` function.

Put another way, what you get back from calling ``(StSt...)`` is a rich set of data that can be inspected and manipulated.

.. code:: python

    @renderable((1000, 200))
    def print_tree(r):
        pens = (StSt("COLDTYPE", co, 150,
            wdth=0.5, rotate=10, tu=150)
            .align(r)
            .f(Gradient.Vertical(r,
                hsl(0.5, s=0.8),
                hsl(0.8, s=0.75))))
        
        print(pens.tree())
        
        pens[0].rotate(180)
        pens[-1].rotate(180)
        pens[-2].rotate(10)

        return pens

Because of the line ``print(pens.tree())``, you should see something like this in your terminal when you run that example:

.. code:: text

    <®:P:/8...>
        - <®:P:RecordingPen(12mvs) {frame=Rect(175.51,43.75,57.30,112.50),glyphName=C}>
        - <®:P:RecordingPen(12mvs) {frame=Rect(255.31,43.75,70.50,112.50),glyphName=O}>
        - <®:P:RecordingPen(12mvs) {frame=Rect(348.31,43.75,45.30,112.50),glyphName=L}>
        - <®:P:RecordingPen(18mvs) {frame=Rect(416.11,43.75,70.80,112.50),glyphName=D}>
        - <®:P:RecordingPen(16mvs) {frame=Rect(509.41,43.75,51.90,112.50),glyphName=T}>
        - <®:P:RecordingPen(22mvs) {frame=Rect(583.81,43.75,63.75,112.50),glyphName=Y}>
        - <®:P:RecordingPen(16mvs) {frame=Rect(670.06,43.75,67.05,112.50),glyphName=P}>
        - <®:P:RecordingPen(22mvs) {frame=Rect(759.61,43.75,56.70,112.50),glyphName=E}>

And because of the lines with calls to `rotate`, you should see this on your screen:

.. image:: /_static/renders/text_print_tree.png
    :width: 500
    :class: add-border

Less Basic Text
---------------

Usually, glyph-wise structured representation of text is not a feature of software or software libraries, because when programmers sit down to implement support for text, they do it with the understanding that if you want text, you usually want a `lot` of text, set in large blocks, like this paragraph that you’re reading now.

But for lots of graphic design (particularly animation), what you actually want is very precise control over only a few glyphs, maybe a line or two. That was the magic of technologies like moveable type, or especially Letraset; those technologies gave designers direct control over letterforms. A lot like when you hit "Convert to Outlines" in Illustrator today.

Of course, there’s a big downside to having direct control: it is excruciatingly slow. And more than that, even when you’re working with just a few letters, you might need to change those letters at the last minute, right before a project is due.

Which is where code really shines. All the manipulations I’ve done so far are not "destructive," like Convert to Outlines. As far as we’re concerned, the "textbox" (so to speak) is still intact, ``StSt("COLDTYPE"...``

To illustrate that point, let’s change the text:

.. code:: python

    @renderable((1000, 200))
    def typecold(r):
        pens = (StSt("TYPECOLD", co, 150,
            wdth=0.5, rotate=10, tu=150)
            .align(r)
            .f(Gradient.Vertical(r, hsl(0.5, s=0.8), hsl(0.8, s=0.75))))
        
        pens[0].rotate(180)
        pens[-1].rotate(180)
        pens[-2].rotate(10)
        return pens

.. image:: /_static/renders/text_typecold.png
    :width: 500
    :class: add-border

The last two examples also illustrate something important about Coldtype — (almost) everything is self-mutating by default. So a line like ``pens[0].rotate(180)`` changes ``pens[0]`` directly, meaning you don’t need to assign it to a new variable. This makes it very easy to directly manipulate nested structures without needing to reassign variables.

This also means that sometimes it is very necessary to ``copy`` pens in order to double them, so you can make changes to a copy without modifying the original. For instance:

.. code:: python

    @renderable((1000, 200))
    def simpledrop(r):
        pens = (StSt("TYPECOLD", co, 150,
            wdth=0.5, rotate=10, tu=250)
            .align(r)
            .f(1))
        
        return P(
            pens.copy().translate(10, -10).f(0),
            pens.s(hsl(0.9)).sw(3))

.. image:: /_static/renders/text_simpledrop.png
    :width: 500
    :class: add-border

I’ll admit the impact of the interesting dropshadow here is lessened somewhat by the appearance of the strange pink lines in the top layer of text. When I added the code stroking the pens (``.s(hsl(0.9)).sw(3)``), I thought it would look like a standard stroked shape. But if you’re familiar with how variable fonts are constructed, those lines might not seem all that strange to you — they indicate that the letters are constructed in order to interpolate cleanly. That said, we probably don’t want to see them! So there’s a special ``ro=1`` flag that you can pass to any ``StSt`` function, and that’ll ``(r)emove (o)verlaps`` on all the glyphs before they come back to you in their correct positions. (Or you could chain a call to ``removeOverlaps`` on the pens.)

.. code:: python

    @renderable((1000, 200))
    def ro(r):
        return (StSt("TYPECOLD", co, 150,
            wdth=0.5, rotate=10, tu=100, ro=1)
            .align(r)
            .f(1)
            .pen()
            .layer(
                lambda p: p.castshadow(-45, 50).f(0),
                lambda p: p.s(hsl(0.9)).sw(3))
            .align(r, th=1, tv=1))

.. image:: /_static/renders/text_ro.png
    :width: 500
    :class: add-border

Fixed! Also I did some completely unrelated things there.

* Instead of simply offsetting the main text to get a shadow, this example collapses the set of pens to a single pen (via ``.pen()``), and then uses a built-in method called ``castshadow(<angle>, <distance>)`` to cast a shadow.

* When you cast a shadow like that, your text might look a little un-centered, so to fix that we’ve added an additional ``align`` call at the end, passing ``th=1`` and ``tv=1`` to indicate that we want the whole thing centered perfectly (true-horizontal and true-vertical) within the bounding rectangle ``r``. (Those flags are useful for a type-centric graphics engine, because up until now we’ve relied on the pre-set cap-height of the letters to vertically align glyphs, rather than their "true height" which varies from letter to letter.)

* Instead of ``copy``\ing anything, the example now uses the ``.layer`` method, which does the copying for you, and also removes the "original" in favor of the two lambda functions provided. Basically, this is a copy-and-replace operation, where we've provided two "replace" operations. So to recap: via ``StSt``, we created a set of pens (aka vectors aka shapes), then we reduced that to a single pen, then we layered that pen, resulting in two new pens (one for the shadow, one for the filled and stroked shape on top). The layer function also allows us to directly return the "chain," without having to declare intermediate variables.

One additional refinement you may want to make in an example like this is that you'd want to individually cast shadows based on a glyph + a little bit of stroke set around it, in the style of the 19th-century type designers. So let’s do that:

.. code:: python

    @renderable((1000, 200))
    def stroke_shadow(r):
        return (StSt("COLDTYPE", co, 150,
            wdth=1, rotate=10, tu=100, ro=1)
            .align(r)
            .f(1)
            .layer(
                lambda ps: ps.pmap(lambda p: p
                    .outline(10)
                    .removeOverlap()
                    .castshadow(-45, 50)
                    .f(None)
                    .s(hsl(0.6, s=1, l=0.4))
                    .sw(4)),
                lambda ps: ps.s(hsl(0.9)).sw(4))
            .align(r, th=1, tv=1))

.. image:: /_static/renders/text_stroke_shadow.png
    :width: 500
    :class: add-border

Dang, you know I thought that example would just work, but it looks like there are some tiny little dots present, which I think are artifacts of the ``castshadow`` call. I didn’t write the guts of that (Loïc Sander wrote something called a ``TranslationPen`` which is used by coldtype internally), so I don’t understand it completely, but it shouldn’t be difficult to devise a way to clean up those tiny specks by testing the ``bounds`` of each of the contours created by the ``TranslationPen``. We can do that by iterating over the individual contours by exploding the path into its constituent contours, then filtering those contours, then imploding those contours back into a single path again. We can also use the opportunity to demonstrate some debugging techniques, like isolating a single letter and blowing it up.

.. code:: python

    @renderable((1000, 500))
    def stroke_shadow_cleanup(r):
        def shadow_and_clean(p):
            return (p
                .outline(10)
                .reverse()
                .removeOverlap()
                .castshadow(-5, 500)
                .explode()
                .filter(lambda c: c.bounds().w > 50)
                .implode()
                .f(None)
                .s(hsl(0.6, s=1, l=0.4))
                .sw(4))

        return (StSt("O", co, 500,
            wdth=0.5, rotate=10, tu=100, ro=1)
            .align(r)
            .f(1)
            .layer(
                lambda ps: ps.pmap(shadow_and_clean),
                lambda ps: ps.s(hsl(0.9)).sw(4))
            .align(r, th=1, tv=1))

.. image:: /_static/renders/text_stroke_shadow_cleanup.png
    :width: 500
    :class: add-border

Got it! If you comment out the ``.filter`` line, you should see the little speck show up again.

N.B. We pulled the lambda being passed to ``pmap`` (pens-map) out into its own function, ``shadow_and_clean``. It’s not really a "reusable" function, but it is a little clearer in this instance to have that logic separated from the main chained expression.

Two suggestions to help you better understand code or find weird looks: try commenting out various stuff and using random colors.

.. code:: python

    @renderable((1000, 250))
    def stroke_shadow_random(r):
        return (StSt("COLDTYPE", co, 150,
            wdth=0.5, rotate=10, tu=100, ro=1)
            .align(r)
            .f(1)
            .layer(
                lambda ps: ps.pmap(lambda p: p
                    .outline(10)
                    #.remove_overlap()
                    .castshadow(-45, 50)
                    .f(hsl(random(), s=1, a=0.1))
                    .s(hsl(random(), s=1, l=0.4))
                    .sw(4)),
                lambda ps: ps.pmap(lambda p: p
                    .s(hsl(random())).sw(4)))
            .align(r, th=1, tv=1))

.. image:: /_static/renders/text_stroke_shadow_random.png
    :width: 500
    :class: add-border

Multi-line Text
---------------

.. code:: python

    @renderable ((1000, 550))
    def multiline(r):
        return (StSt("COLDTYPE\nTYPECOLD", co, 300, 
            wdth=1, fit=500)
            .align(r)
            .f(0))

.. image:: /_static/renders/text_multiline.png
    :width: 500
    :class: add-border

Text-on-a-path
--------------

If you like to align glyphs along an arbitrary path, you can use the ``P::distribute_on_path`` method to set the glyphs returned from a ``StSt``.

.. code:: python

    @renderable((1000, 1000))
    def on_a_path(r):
        circle = P().oval(r.inset(250)).reverse()
        return (StSt("COLDTYPE", co, 200, wdth=1)
            .distribute_on_path(circle, offset=275)
            .f(0))

.. image:: /_static/renders/text_on_a_path.png
    :width: 500
    :class: add-border

What if we want more text on the circle and we want it to fit automatically to the length of the curve on which it’s set — without overlapping? Simple append a ``fit=`` keyword argument to fit the text to the length of the curve that we'll end up setting the pens on.

.. code:: python

    @renderable((1000, 1000))
    def text_on_a_path_fit(r):
        circle = P().oval(r.inset(250)).reverse()
        return (StSt("COLDTYPE COLDTYPE COLDTYPE ",
            co, 200,
            wdth=1, tu=100, space=500, fit=circle.length())
            .distribute_on_path(circle)
            .f(Gradient.H(circle.bounds(),
                hsl(0.5, s=0.6),
                hsl(0.85, s=0.6))))

.. image:: /_static/renders/text_text_on_a_path_fit.png
    :width: 500
    :class: add-border

One thing that’s weird about setting text on a curve is that, depending on the curve, it can exaggerate — or eliminate — spacing between letters. Sometimes that doesn’t really matter — in the case of this circle, because the curve only bends in one manner, the text is always extra spacey, which usually isn't a problem. But if we set the text on a sine-wave, the issue becomes more apparent, since the spacing is both expanded and compressed on the same curve, and when letters overlap excessively, they can get illegible quickly.

Is there a solution? Probably many but the one I like a lot is the ``understroke`` method on the ``DATPens`` class, which interleaves a stroked version of each letter in a set (a technique popular in pulp/comic titling & the subsequent graffiti styles they inspired).

Let’s see what that looks like.

.. code:: python
    
    import coldtype.fx.shapes as shapes

    @renderable((1000, 500))
    def text_on_a_path_understroke(r):
        sine = P().ch(shapes.sine(r.inset(0, 180), 3))
        return (StSt("COLDTYPE COLDTYPE COLDTYPE",
            co, 100,
            wdth=1, tu=-50, space=500,
            fit=sine.length())
            .distribute_on_path(sine)
            .understroke(sw=10)
            .f(Gradient.H(sine.bounds(),
                hsl(0.7, l=0.6, s=0.65),
                hsl(0.05, l=0.6, s=0.65)))
            .translate(0, -20))

.. image:: /_static/renders/text_text_on_a_path_understroke.png
    :width: 500
    :class: add-border

Interesting! But there’s one thing to correct if we want better legibility. You'll notice in that first purple COLDTYPE, the C is unrecognizable, because the O that comes after it is on top of it. This is how text layout engines usually work for LTR languages — the topmost glyph is the right-most glyph. But that’s not what we want — we want to reverse the order of the glyphs. Luckily, that’s easy, just pass a ``r=1`` (or ``reverse=1``), to the ``Style`` constructor.

.. code:: python

    @renderable((1000, 500))
    def text_on_a_path_understroke_reversed(r):
        sine = P().ch(shapes.sine(r.inset(0, 180), 3))
        return (StSt("COLDTYPE COLDTYPE COLDTYPE",
            co, 100,
            wdth=1,
            tu=-50,
            space=500,
            r=1,
            fit=sine.length())
            .distribute_on_path(sine)
            .understroke(sw=10)
            .f(Gradient.H(sine.bounds(),
                hsl(0.7, l=0.7, s=0.65),
                hsl(0.05, l=0.6, s=0.65)))
            .translate(0, -20))

.. image:: /_static/renders/text_text_on_a_path_understroke_reversed.png
    :width: 500
    :class: add-border

It’s a subtle change, but one that (to me) makes a huge difference. I also lightened the purple in the gradient, I think it looks a little better that way, right?
