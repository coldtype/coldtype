---
title: "One-Letters Cheatsheet"
---

Here are some common one-letter abbreviations you'll find throughout idiomatic Coldtype code.

* ``e`` usually refers to "easing", as in the ``f.e`` function (frame.easing)
* ``f`` usually refers, when used as a variable, to the ``Frame`` object that is passed to an ``@animation`` renderable.
* ``.f`` refers, when used as a function, to *fill*, as in the fill color of a path
* ``.s`` refers, when used as a function, to *stroke*, and ``.sw`` refers to *stroke width*
* ``.fssw`` refers to fill-stroke-strokewidth as a single concept. This is something I use all the time in my own work, as I almost never set a stroke without also setting the fill (usually to -1 to be transparent).
* ``r`` usually refers, when used as a variable, to the ``Rect`` object that is passed to a ``@renderable`` renderable.
* ``f.a.r`` is a common shorthand for frame.animation.rect, i.e. the rectangle frame of an ``@animation`` renderable.