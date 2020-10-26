About
=====

What is Coldtype?
-----------------

**A cross-platform library to help you precisely & programmatically do high-quality display typography with Python.**

An example:

.. code:: python

    from coldtype import *

    @renderable((1200, 350))
    def render(r):
        c1 = hsl(0.65, 0.7)
        c2 = hsl(0.53, 0.6)

        return DATPenSet([
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

* There is no "canvas" — all graphics are **hierarchical data** ``return``-ed from a function to the renderer, which does all the actual drawing-to-a-virtual-canvas.

* There is a lot of emphasis on **method-chaining**, which (I feel) is an underappreciated way to do graphics programming, since the resulting code is easily editable and experimentable. Of course, some (like the creator of Python) have called this style of programming "un-Pythonic." Take from that what you will!

* As might already be clear from the first two points, coldtype is not meant to be a good introduction to programming (though it might still be, I'm not sure). The emphasis here is on programming patterns that ease the creation of professional graphics, particularly **complex animations** that blend multiple data sources, like text defined in Premiere, MIDI files, or even Ableton Live project files. (TODO: add links to tutorials on each of those)

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
    
    banner_contact = banner.contactsheet(2, [0, 33, 66, 99, 133, 166])

And here’s the result, rendered as a contact sheet with frames ``[0, 33, 66, 99, 133, 166]`` (that last line of code creates a contact sheet from an animation):

.. image:: /_static/renders/about_banner_contact.png
    :width: 700
    :class: add-border


And why?
--------

Yes, there are lots of ways to set type with code. Most ways — HTML/CSS/JS, Processing, etc. — are great for 90% of what most people want to do with Latin-based writing systems. Then the road runs out and you can’t do anything else.

Coldtype is an offroad vehicle that lets you keep driving where there are no roads. Like many vehicles built for specialized use, it is not user-friendly. It has no doors (please climb in through the window), and the steering wheel is not very intuitive, also it’s a stick-shift, and you should probably know how to code (or be willing to learn) if you’re going to drive it alone out into the desert. (I apologize for how automotive this metaphor is getting. Probably should’ve gone with some metaphor about people making custom synthesizers in the 70s.)

What about DrawBot?
-------------------

If you’ve heard of `DrawBot <https://drawbot.com/>`_ — another offroad vehicle — you may be wondering how Coldtype is different. The answer is that Coldtype provides a very different programming idiom, one based around creating and modifying structured data, rather than — as is common in most creative coding platforms (including DrawBot and Processing) — an idiom based around a metaphorical canvas that you render to directly.

I should point out that DrawBot is fantastic and that Coldtype would not exist without DrawBot, mostly because using DrawBot was my first time driving in the typographical offroad. That said, Coldtype mostly exists as a response to things I found awkward when programming animations with DrawBot.

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

Why “coldtype”?
---------------

Coldtype refers to the short-lived era of early semi-digital typesetting (extending roughly from the late 1940s to the widespread adoption of personal computing in the early 1990s), during which time computers were used to control various analog photographic processes for setting type, technologies now known, usually, as “phototype,” but sometimes also known as “coldtype,” to distinguish it from hot-metal type, which was the previous standard. (And it was hot — Linotype machines were known to squirt molten lead out at the operator.)

Phototype/coldtype was a hybrid moment in typographic history, and a fascinating one — 500 years of metal-type-based assumptions were upended all at once, as letters now did not need to live on a rectangular metal body, meaning they could get really close together. (Which, for me, really helps explain, like, all of graphic design between 1960 and 1980.)

Also originally I thought it was a funny name because I wanted to make a very fast typesetting library using HarfBuzz, and when computers run quickly and efficiently, they remain cold. Of course, I now regularly use all 8 cores of my computer when I use render 1000s of frames at once using coldtype, which gets the fans going. An aspiration, then, more than a reality.

Is Coldtype capitalized?
------------------------

I can’t decide, as you may be able to tell from this documentation’s inconsistent capitalization scheme.

Who works on this?
------------------

This library is mostly the work of me, `Rob Stenson <https://robstenson.com>`_, but I want to acknowledge the work of some people and projects who’ve helped bring this project to life:

* `Goodhertz <https://goodhertz.com>`, who has supported the open-sourcing of this library, which was originally written to set text in audio plugin interfaces.

* Coldtype Obviously is a open-source subset of the commercially-available font `Obviously <https://ohnotype.co/fonts/obviously>`_ by OHno Type Co; s/o to James Edmondson for donating those 8 characters to this project.

* ``coldtype.pens.outlinepen`` contains code written by Frederik Berlaen, Copyright (c) 2016

* ``coldtype.pens.translationpen`` contains code written by Loïc Sander, Copyright (c) 2014

* ``coldtype.fontgoggles`` contains parts of the `FontGoggles <https://github.com/justvanrossum/fontgoggles>`_ codebase, written by Just van Rossum, Copyright (c) 2019 Google, LLC. Just is also responsible for DrawBot which the main inspiration behind this project.

* Mutator Sans included for testing was written by Erik van Blokland, Copyright (c) 2017

* Recursive Mono Casual Italic is an `open-source typeface <https://github.com/arrowtype/recursive>`_ by @arrowtype

* Coldtype relies heavily (via FontGoggles) on the incredible `HarfBuzz <https://github.com/harfbuzz/harfbuzz>`_ text shaping library.

* Coldtype also relies heavily on the also incredible `fontTools <https://github.com/fonttools/fonttools>`_
