🌋 _Hello! Not sure how you got here unless I gave you the link personally — if I didn’t, you’re welcome to look around, but know that this is alpha-quality software that’s mostly undocumented._ 🌋

__⚠️ Our intention is to ultimately make this library a proper, useable, open-source project, but for the moment — though it is publicly viewable — we are not publicizing it and it is under active development. ⚠️__

---

# Coldtype

_Hello and welcome to `coldtype`, an odd little library for programmatic typography, written by [Rob Stenson](https://robstenson.com), who is me, for use on Goodhertz projects and also other stuff._

## An example

```python
from coldtype import *

mu = Font("assets/MutatorSans.ttf")

@renderable()
def render(r):
    return (StyledString("COLDTYPE",
        Style(mu, 250, wdth=0, wght=1, tu=-350, r=1))
        .pens()
        .align(r)
        .f("hr", 0.8, 0.7)
        .understroke())
```

# Quickstart

- Install a Python >= 3.8
- Clone this repository
- `cd` into the the cloned coldtype repository
- Create a virtual environment, ala `python3.8 -m venv venv --prompt=coldtype` on the command line
- Then `source venv/bin/activate` to start your venv
- Then `pip install -e .` (This adds the `coldtype` command to your virtual environment)

Now you can run coldtype scripts, ala:

`coldtype examples/simple.py`

# More about Coldtype

## An example

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
    return StyledString("COLDTYPE", Style(obvs, 250, fill=0, **state, r=1, ro=1)).pens().align(f.a.r).f(0).understroke(s=1, sw=15)
```
_source code and instructions for running available here:_ [banner.py](https://github.com/goodhertz/coldtype-examples/blob/master/animations/banner.py)

## More Examples

To try out Coldtype and see some examples (like the banner at the top of this README), check out the [coldtype-examples](https://github.com/goodhertz/coldtype-examples) repository.

___

## What is Coldtype?

__A cross-platform library to help you precisely & programmatically do high-quality display typography with Python.__

Yes, there are lots of ways to set type with code. Most ways — HTML/CSS/JS, Processing, etc. — are great for 90% of what most people want to do with Latin-based writing systems. Then the road runs out and you can’t do anything else.

Coldtype is an offroad vehicle that lets you keep driving where there are no roads. Like many vehicles built for specialized use, it is not user-friendly. It has no doors (please climb in through the window), and the steering wheel is not very intuitive, also it’s a stick-shift, and you should probably know how to code (or be willing to learn) if you’re going to drive it alone out into the desert. (I apologize for how automotive this metaphor is getting. Probably should’ve gone with some metaphor about people making custom synthesizers in the 70s.)

### What about DrawBot?

If you’ve heard of [DrawBot](http://www.drawbot.com/) — another offroad vehicle that lets you drive where you want — you may be wondering how Coldtype is different. The answer is that Coldtype provides a very different programming idiom, one based around creating and modifying structured data that can be rendered, rather than — as is common in most “creative coding” platforms (including DrawBot) — providing a metaphorical canvas that you render to directly.

(I should point out that DrawBot is fantastic and that Coldtype would not exist without DrawBot, mostly because using DrawBot was my first time driving in the typographical offroad. That said, Coldtype mostly exists as a response to things I found awkward when programming animations and user interfaces with DrawBot.)

### What about Adobe products?

I’ve learned over the last few years to distrust any _Type Tool_ in an Adobe product (or anywhere else). Yes, those can be very good — like HTML+CSS — for doing simple Latin-based typography for static designs. But then, all of a sudden, they are very bad. You can think of Adobe products as a train that you get on and you can fall asleep in a nice seat and the train will get you where you want to go, except when you wake up and realize you wanted to go somewhere the train doesn't go and then you’re like... _dang, do I have to walk?_ (Walking in this metaphor is when you right click and hit _Convert to Outlines_.)

Walking can be a lot of fun, and you get to see a lot. Drawing is a lot like walking. Fabulous exercise. But sometimes you want to get there faster or you want to go farther.

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

`coldtype examples/simplest.py`

When you run this, it should pop up a window that displays the result of the code.

### Some thoughts about that code

You may look at that code and think to yourself: _wtf_. Yes, that is an appropriate reaction. Conventional wisdom in the programming world is that, when balancing the readability and writeability of code, the scales should be tipped towards _readable_. Here the scales are tipped the other way, because coldtype is meant as a **design idiom** for Python. The output of a coldtype program is not a piece of software that you’ll have to maintain for years to come; the output is a video, or an image, or something like that — an artifact. You may want to read a coldtype program again one day, but only for the purpose of learning or plagiarizing your past self.

## How does Coldtype work?

The central graphic element of Coldtype (the `DATPen`) is a wrapper around `fontTool`’s `RecordingPen`, and the central typesetting element (`StyledString`) provides access to a rich set of styling options.

## Why is an audio software company releasing a typography library?

Because (__A__) I love fonts and (__B__) audio software interfaces use fonts (and have some unique design constraints for typography), also (__C__) we make lots of ads that feature typography that reacts to audio and midi data. The code that powers the audio/midi data does not live in this library, but those reactions are made possible by the typography features of Coldtype.

## Why “coldtype”?

Coldtype refers to the short-lived era of early digital typesetting (extending roughly from the late 1940s to the widespread adoption of personal computing in the early 1990s), during which time computers were used to control various analog photographic processes for setting type, technologies now known, usually, as “phototype,” but sometimes also known as “coldtype,” to distinguish it from hot-metal type, which was the previous standard. (And it was hot — Linotype machines were known to squirt molten lead out at the operator.)

Phototype/coldtype was a hybrid moment in typographic history, and a fascinating one — 500 years of metal-type-based assumptions were upended all at once, as letters now did not need to live on a rectangular metal body, meaning they could get really close together. (Which, for me, really helps explain, like, all of graphic design between 1960 and 1980.)

Also originally I thought it was a funny name because I wanted to make a very fast typesetting library using Harfbuzz, and when computers run quickly and efficiently, they remain cold. Of course, I now regularly use all 8 cores of my computer when I use render 1000s of frames at once using coldtype, which gets the fans going, so really it's more like warmtype.

## What are some projects Coldtype has been used on?

- [Lyric](https://youtu.be/b2_CJ_nx-l4?t=21) [videos](https://vimeo.com/377148622)
- [3d type specimens](https://vimeo.com/354292807)
- [All Goodhertz plugin interfaces](https://goodhertz.co)
- [All recent posts on the Goodhertz instagram](https://www.instagram.com/goodhertz/)
- And [all recent posts on Rob’s instagram](https://www.instagram.com/robrushstenson/)

## Weirdnesses

- __0-1 variation axes value__ — By default, all font variation values (axis values) are scaled to a 0-1 range. I’ve found I almost never want to set a font variation value in the scale set by the font itself, mostly because I’m almost always mapping a 0-1 time (or amplitude) value to the axis. If you’d like to not "(s)cale (v)arations," set `sv=False` when constructing a `Style` object.

## Programming philosophy

Here is a free-associated list of things that I think define the general vibe of programming in Coldtype (a work-in-progress)

- Chained mutation/transformation
    - "Chaining" in this context refers to the programming style favored by libraries like jQuery, which allows you to call multiple methods on a single line, all of which mutate the state of an object and return the object itself in each mutating call. For example:
        - `DATPen().rect(Rect(500, 500)).translate(100, 100).rotate(45)` creates a `DATPen` object, then adds a rectangle bezier to it, then translates it, then rotates it, all in a single line. In normal circumstances, programming like this is called "spaghetti" code because it's long and hard to follow, or something like that. In this case, its brevity is its benefit
        - Yes I know mutation is theoretically “bad” or whatever, yeesh, I just really love how it works in real life.
- Coldtype does not use classic "drawing"-style APIs/graphic state, though the data model of Coldtype can be (and is meant to be) serialized to any number of canvas/drawing APIs, and can be extended to any API that implements `fill`/`stroke` and `moveTo`/`lineTo`/`curveTo`

# Caveats

## What is Coldtype _not_?

- Coldtype is not good for setting large amounts of text in a single frame, because Coldtype has no line-breaking algorithms.
- This means Coldtype is probably bad for most print applications (you should use DrawBot for that, because DrawBot has line-breaking algorithms).
- In fact, Coldtype is not good at most things that normal type-setting software is good at. Generally-speaking, the goal of this library is to give you exactly what you want, rather than a “best guess.” For example:
    - Coldtype does not implement fallback support (expect to see some `.notdef`s)

## How is this different from DrawBot?

- Use whatever text editor you want
- Cross-platform
- Does not rely on Apple’s CoreText engine or the mostly deprecated APIs that DrawBot uses to interact with it
- Really only a small subset of what DrawBot, by leveraging CoreText and CoreImage, can do (which is a good thing to me, because I only ever used DrawBot for typography anyway)
- Little-to-no image support (some, but it is vvv primitive)
