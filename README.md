__⚠️🌋 Warning: the code is alpha-quality; the API is subject to change; the documentation is sparse 🌋⚠️__

---

# Coldtype

_Hello and welcome to `coldtype`, an odd little library for programmatic typography, written for use on [Goodhertz](https://goodhertz.com) projects and [text animations](https://vimeo.com/robstenson)._

For __installation and tutorials__, check out [coldtype.goodhertz.com](https://coldtype.goodhertz.com)

For motivation and few examples, read on below.

---

![An example](https://raw.githubusercontent.com/goodhertz/coldtype/master/examples/renders/simple_render.png)


```python
from coldtype import *

@renderable((1580, 350))
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
```

# Documentation

Check out [coldtype.goodhertz.com](https://coldtype.goodhertz.com) for instructions on installing and getting started with coldtype.

## More Examples

The best way to get familiar with Coldtype is to look at and try modifying some example code, like the animating gif below. To try out this example and many more, check out the [coldtype-examples](https://github.com/goodhertz/coldtype-examples) repository.

![An example](https://coldtype.goodhertz.co/media/banner_3.gif)
---
```python
from coldtype import *

states = [
    dict(wdth=0, rotate=0, tu=300),
    dict(wdth=1, rotate=15, tu=-150),
    dict(wdth=0.25, rotate=-15, tu=350),
    dict(wdth=0.75, rotate=0, tu=-175),
    dict(wdth=0.5, rotate=25, tu=100)
]

obvs = Font("fonts/ColdtypeObviously.designspace")
loop = Loop(200, len(states), 10)

@animation(timeline=loop, storyboard=[130], bg=1, rect=(1500, 300))
def render(f):
    phase = f.a.t.current_phase(f.i)
    state = phase.calc_state(states)
    return (StyledString("COLDTYPE",
        Style(obvs, 250, fill=0, **state, r=1, ro=1))
        .pens()
        .align(f.a.r)
        .f(0)
        .understroke(s=1, sw=15))
```
_source code and instructions for running available here:_ [banner.py](https://github.com/goodhertz/coldtype-examples/blob/master/animations/banner.py)

___

## What is Coldtype?

__A cross-platform library to help you precisely & programmatically do high-quality display typography with Python.__

_Problem_: you want to create images and animations with code, but you don’t want to sacrifice high-quality display typography.

_Solution_: Coldtype (or DrawBot!)

Yes, there are lots of ways to set type with code. Most ways — HTML/CSS/JS, Processing, etc. — are great for 90% of what most people want to do with Latin-based writing systems. Then the road runs out and you can’t do anything else.

Coldtype is an offroad vehicle that lets you keep driving where there are no roads. Like many vehicles built for specialized use, it is not user-friendly. It has no doors (please climb in through the window), and the steering wheel is not very intuitive, also it’s a stick-shift, and you should probably know how to code (or be willing to learn) if you’re going to drive it alone out into the desert. (I apologize for how automotive this metaphor is getting. Probably should’ve gone with some metaphor about people making custom synthesizers in the 70s.)

### What about DrawBot?

If you’ve heard of [DrawBot](http://www.drawbot.com/) — another offroad vehicle that lets you drive where you want — you may be wondering how Coldtype is different. The answer is that Coldtype provides a very different programming idiom, one based around creating and modifying structured data that can be rendered, rather than — as is common in most “creative coding” platforms (including DrawBot and Processing) — providing a metaphorical canvas that you render to directly.

(I should point out that DrawBot is fantastic and that Coldtype would not exist without DrawBot, mostly because using DrawBot was my first time driving in the typographical offroad. That said, Coldtype mostly exists as a response to things I found awkward when programming animations with DrawBot.)

### What about Adobe products?

I’ve learned over the last few years to distrust any _Type Tool_ in an Adobe product (or anywhere else). Yes, those can be very good — like HTML+CSS — for doing simple Latin-based typography for static designs. But then, all of a sudden, they are very bad. You can think of Adobe products as a train that you get on and you can fall asleep in a nice seat and the train will get you where you want to go, except when you wake up and realize you wanted to go somewhere the train doesn't go and then you’re like... _dang, do I have to walk?_ (Walking in this metaphor is when you right click and hit _Convert to Outlines_.)

Walking can be a lot of fun, and you get to see a lot. Drawing is a lot like walking. Fabulous exercise. But sometimes you want to get there faster or you want to go farther. Or sometimes you want to walk to a neighborhood but there's a freeway in between you and where you’re headed. (The freeway in this metaphor is Adobe’s complete lack of support for OpenType features in After Effects.) So instead of walking you try an experimental jetpack to fly over the freeway. (That’s Coldtype.)

## What does a Coldtype program look like?

```python
from coldtype import *

@renderable(rect=(1200, 300))
def render(r):
    return (StyledString("COLDTYPE",
        Style("assets/MutatorSans.ttf", 300))
        .pens()
        .align(r, tv=1)
        .f(hsl(0.95)))
```

You can run that example inside this repo by calling:

`coldtype examples/simplest.py`

When you run this code, it should pop up a window that displays the result of the code.

### Some thoughts about that code

You may look at that code and think to yourself: _wtf_. Yes, that is an appropriate reaction. Conventional wisdom in the programming world is that, when balancing the readability and writeability of code, the scales should be tipped towards _readable_. Here the scales are tipped the other way, because coldtype is meant as a **design idiom** for Python. The output of a coldtype program is not a piece of software that you’ll have to maintain for years to come. The output is a video, or an image, or something like that — an artifact. You may want to read a coldtype program again one day, but only for the purpose of learning from or plagiarizing your past self.

## How does Coldtype work?

The central graphic element of Coldtype (the `DATPen`) is a wrapper around `fontTool`’s `RecordingPen`, and the central typesetting element (`StyledString`) provides access to a rich set of styling options.

## Why is an audio software company releasing a typography library?

Because (__A__) I love fonts and (__B__) audio software interfaces use fonts (and have some unique design constraints for typography), also (__C__) we make lots of ads that feature typography that reacts to audio and midi data. Those reactions and the code to make them happen are all part of Coldtype, although those are advanced topic that aren’t covered in this README. (But they are covered by the example code in the coldtype-examples](https://github.com/goodhertz/coldtype-examples) repo.)

## Why “coldtype”?

Coldtype refers to the short-lived era of early digital typesetting (extending roughly from the late 1940s to the widespread adoption of personal computing in the early 1990s), during which time computers were used to control various analog photographic processes for setting type, technologies now known, usually, as “phototype,” but sometimes also known as “coldtype,” to distinguish it from hot-metal type, which was the previous standard. (And it was hot — Linotype machines were known to squirt molten lead out at the operator.)

Phototype/coldtype was a hybrid moment in typographic history, and a fascinating one — 500 years of metal-type-based assumptions were upended all at once, as letters now did not need to live on a rectangular metal body, meaning they could get really close together. (Which, for me, really helps explain, like, all of graphic design between 1960 and 1980.)

Also originally I thought it was a funny name because I wanted to make a very fast typesetting library using Harfbuzz, and when computers run quickly and efficiently, they remain cold. Of course, I now regularly use all 8 cores of my computer when I use render 1000s of frames at once using coldtype, which gets the fans going, so really it's more like warmtype.

## Is Coldtype capitalized?

I can’t decide, as you may be able to tell from this README’s inconsistent capitalization scheme.

## What are some projects Coldtype has been used on?

- [Lyric](https://youtu.be/b2_CJ_nx-l4?t=21) [videos](https://vimeo.com/377148622)
- [3d type specimens](https://vimeo.com/354292807)
- [All Goodhertz plugin interfaces](https://goodhertz.com)
- [All recent posts on the Goodhertz instagram](https://www.instagram.com/goodhertz/)
- And [all recent posts on Rob’s instagram](https://www.instagram.com/robrushstenson/)

## Acknowledgements

- `coldtype.pens.outlinepen` contains code written by Frederik Berlaen, Copyright (c) 2016
- `coldtype.pens.translationpen` contains code written by Loïc Sander, Copyright (c) 2014
- `coldtype.fontgoggles` contains parts of the [FontGoggles](https://github.com/justvanrossum/fontgoggles) codebase, written by Just van Rossum, Copyright (c) 2019 Google, LLC
- MutatorSans included for testing was written by Erik van Blokland, Copyright (c) 2017