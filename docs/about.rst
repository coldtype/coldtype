About
=====

What is Coldtype?
-----------------

**A cross-platform library to help you precisely & programmatically do display typography with Python.**

An example:

.. code:: python

    from coldtype import *

    @renderable((1200, 350))
    def render(r):
        c1 = hsl(0.65, 0.7)
        c2 = hsl(0.53, 0.6)

        return DATPens([
            (DATPen()
                .rect(r.inset(10))
                .outline(10)
                .f(Gradient.Horizontal(r,
                    c2.lighter(0.3),
                    c1.lighter(0.3)))),
            (StyledString("COLDTYPE",
                Style("assets/ColdtypeObviously-VF.ttf", 250,
                    wdth=1, tu=-170, r=1, rotate=15,
                    kp={"P/E":-150, "T/Y":-50}))
                .pens()
                .align(r)
                .f(Gradient.Horizontal(r, c1, c2))
                .understroke(s=1, sw=5))
                .translate(0, 5)])

.. image:: /_static/renders/about_render.png
    :width: 600
    :class: add-border

Some oddities to note if you’re familiar with other graphics programming environments:

* There is no "canvas"; all graphics are **structured data** ``return``-ed from a function to the renderer, which does all the actual drawing-to-a-virtual-canvas.

* There is an idiomatic emphasis on **method-chaining**, which (I feel) is an underappreciated way to do graphics programming, since the resulting code is easily editable and experimentable. Of course, some (like the creator of Python) have called this style of programming "un-Pythonic." Take from that what you will!

* As might already be clear from the first two points, coldtype is not meant to be a good introduction to programming. The point here is to be a toolkit that can help you create professional graphics, particularly **complex animations** that blend multiple data sources, like text defined in Premiere, MIDI files, or even Ableton Live project files. (TODO: add links to tutorials on each of those)

Here’s the code for a somewhat complex animation:

.. code:: python

    states = [
        dict(wdth=0, rotate=0, tu=300),
        dict(wdth=1, rotate=15, tu=-150),
        dict(wdth=0.25, rotate=-15, tu=250),
        dict(wdth=0.75, rotate=0, tu=-175),
        dict(wdth=0.5, rotate=25, tu=100)
    ]

    obvs = Font("assets/ColdtypeObviously.designspace")
    loop = Loop(200, len(states), 10)

    @animation(timeline=loop, storyboard=[130], bg=1, rect=(700, 300))
    def banner(f):
        phase = f.a.t.current_phase(f.i)
        state = phase.calc_state(states)
        return (StyledString("COLDTYPE",
            Style(obvs, 150, fill=0, **state, r=1, ro=1))
            .pens()
            .align(f.a.r)
            .f(0)
            .understroke(s=1, sw=10))

.. code:: ruby
    
    banner_contact = banner.contactsheet(2, [0, 33, 66, 99, 133, 166])

And here’re a few frames from what that code creates:

.. image:: /_static/renders/about_banner_contactsheet.png
    :width: 700
    :class: add-border

And here it is as a gif:

.. image:: https://raw.githubusercontent.com/goodhertz/coldtype/main/assets/banner_3.gif
    :width: 700


Why is Coldtype?
----------------

There are lots of ways to set type with code. Most ways — HTML/CSS/JS, Processing, etc. — are great for 90% of what most people want to do with Latin-based writing systems. Then the road runs out and you can’t do anything else.

Coldtype is an offroad vehicle that lets you keep driving where there are no roads. Like many vehicles built for specialized use, it is not particularly user-friendly. It has no doors (please climb in through the window), and the steering wheel is not very intuitive, also it’s a stick-shift, and you should probably know how to code (or be willing to learn) if you’re going to drive it alone out into the desert. (I apologize for how automotive this metaphor is getting. Probably should’ve gone with some metaphor about people making custom synthesizers in the 70s.)

What about DrawBot?
-------------------

If you’ve heard of `DrawBot <https://drawbot.com/>`_ — another offroad vehicle — you may be wondering how Coldtype is different. The answer is that Coldtype provides a very different programming idiom, one based around creating and modifying structured data, rather than — as is common in most creative coding platforms (including DrawBot and Processing) — an idiom based around a metaphorical canvas that you render to directly.

I should point out that DrawBot is fantastic and that Coldtype would not exist without DrawBot, mostly because using DrawBot was my first time driving in the typographical offroad. That said, Coldtype mostly exists as a response to things I found awkward when programming long-form animations with DrawBot. (Also, you can use `DrawBot as a library from within Coldtype </tutorials/drawbot.html>`_).

Why not HTML/CSS/JavaScript?
----------------------------

I think since I started doing animations with Python a couple years ago (using DrawBot), typographic tools in JS have gotten a lot better, but I always found it awkward to program animations in JS, since I never found a good way to run a headless browser when I needed to rasterize frames for an animation. That said, the programming style of Coldtype is very influenced by JS programming patterns (like method-chaining and liberal use of anonymous functions), so if you're familiar with JS, you might feel at home writing a Coldtype program.

What about Adobe products?
--------------------------

I’ve learned over the last few years to distrust any `Type Tool` in an Adobe product (or anywhere else). Yes, those can be very good — like HTML+CSS — for doing simple Latin-based typography for static designs. But then, all of a sudden, they are very bad. You can think of Adobe products as a train that you get on and you can fall asleep in a nice seat and the train will get you where you want to go, except when you wake up and realize you wanted to go somewhere the train doesn't go and you think `i guess i’ll walk there` (Walking in this metaphor is when you right click and hit `Convert to Outlines`.)

Walking can be a lot of fun, and you get to see a lot. Drawing is a lot like walking. Fabulous exercise; great learning experience. But sometimes you want to get there faster or you want to go farther.

What can coldtype do?
---------------------

* `Vulfpeck, “LAX” <https://www.youtube.com/watch?v=NzxW8nxgENA>`_

* `"Buggin’ Out (Phife Dawg’s Verse)" <https://vimeo.com/377148622>`_

* A `3D type specimen <https://vimeo.com/354292807>`_

* `Goodhertz plugins <https://goodhertz.com/>`_

* Anything recent on `robstenson.com <https://robstenson.com/>`_

How does coldtype rasterize graphics?
-------------------------------------

Coldtype is written in a modular fashion, to allow rasterization/vectorization using a number of different backends. For most of its life before October 2020, I used Coldtype as a frontend to the DrawBot rasterizer (itself a frontend to the CoreGraphics rasterization engine), as well as a frontend for a custom JSON-serializer (used for Goodhertz plugins). You can still use Coldtype with DrawBot as the rasterizer (or with `DrawBot as a direct canvas <tutorials/drawbot.html>`_), but as of now, Coldtype by default rasterizes using the `skia-python <https://kyamagu.github.io/skia-python/>`_ package, which is cross-platform, quite fast, and has great support for image manipulation, via GL shaders.

You can also use Coldtype to draw graphics directly with the skia-python package, as demonstrated in the ``test/test_skia_direct.py`` file in this repository.

There is also support for (in varying degrees of quality): SVG, Cairo, Blender, and AxiDraw (a robotic drawing machine). (TODO add tutorial links for all of these, well except for Cairo, skia-python is just better than Cairo.)

Why “coldtype”?
---------------

Coldtype refers to the short-lived era of early `semi-digital typesetting <https://en.wikipedia.org/wiki/Phototypesetting>`_ (extending roughly from the late 1940s to the widespread adoption of personal computing in the early 1990s), during which time computers were used to control various analog photographic processes for setting type, technologies now known, usually, as “phototype,” but sometimes also known as “coldtype,” to distinguish it from hot-metal type, which was the previous standard.

Phototype/coldtype was a hybrid moment in typographic history, and a fascinating one — 500 years of metal-type-based assumptions were upended all at once, as letters now did not need to live on a rectangular metal body, meaning they could get really close together, and designers could begin to think of type as a 2D material that could be layered and manipulated in new and exciting ways. To me, some of the spirit of that time has been lost with mainstream digital typesetting tools, which in many ways preserve more of the spirit of metal type than the spirit of phototype. That is, today's tools make it very easy to do many things, like set a great big column of text, but those same tools make it very difficult to do many other cool things, like pop a stylistic set on and off while varying a WDTH axis and re-ordering glyphs from left-to-right, so they overlap properly. This library is a way to make some of those difficult things easy; consequently, many of the easy things become difficult.

Is Coldtype capitalized?
------------------------

I can’t decide, as you may be able to tell from this documentation’s inconsistent capitalization scheme.

Who works on this?
------------------

This library is mostly the work of me, `Rob Stenson <https://robstenson.com>`_, but I want to acknowledge the work of some people and projects who’ve helped bring this project to life:

* `Goodhertz <https://goodhertz.com>`_ has supported the open-sourcing of this library, which was originally written to set text in audio plugin interfaces.

* Coldtype Obviously is a open-source subset of the commercially-available font `Obviously <https://ohnotype.co/fonts/obviously>`_ by OHno Type Co; s/o to James Edmondson for donating those 8 characters to this project.

* Mutator Sans included for testing was written by Erik van Blokland, Copyright (c) 2017

* Recursive Mono Casual Italic is an `open-source typeface <https://github.com/arrowtype/recursive>`_ by `Arrow Type <https://www.arrowtype.com/>`_

* Coldtype also relies heavily on the incredible library `fontTools <https://github.com/fonttools/fonttools>`_
