🌋 _Hello! Not sure how you got here unless I gave you the link personally — if I didn’t, you’re welcome to look around, but know that this is alpha-quality software that’s mostly undocumented._ 🌋

__⚠️ Our (Goodhertz’) intention is to ultimately make this library a proper, useable, open-source project, but for the moment — though it is publicly viewable — we are not publicizing it and it is under active development. ⚠️__

---

# Coldtype

## What is Coldtype?

__A cross-platform library to help you precisely & programmatically do high-quality display typography.__

Yes, there are lots of ways to set type with code. Most ways — HTML/CSS/JS, Processing, etc. — are great for 90% of what most people want to do with Latin-based writing systems. Then the road runs out and you can’t do anything else.

Coldtype is a poorly-built but extremely powerful offroad vehicle that lets you keep driving where there are no roads. Like many powerful vehicles, it is not user-friendly. It has no doors (please climb in through the window), and the steering wheel is not very intuitive, also it’s a stick-shift, and you should probably be a mechanic (aka programmer) if you’re going to drive it alone out into the desert. (I apologize for how macho this metaphor is getting — I can’t really think of a better one.)

### What about DrawBot?

If you’ve heard of [DrawBot](http://www.drawbot.com/) — another offroad vehicle that lets you drive where you want — you may be wondering how Coldtype is different. The answer is that Coldtype provides a very different programming idiom, one based around creating and modifying structured data that can be rendered. DrawBot, like most “creative coding” platforms, is based around rendering directly with drawing fuctions.

(I should point out that I love DrawBot very deeply and that Coldtype would not exist without DrawBot, mostly because using DrawBot was my first time driving in the typographical offroad. That said, Coldtype mostly exists as a response to things I found awkward about programming animations and interfaces with DrawBot.)

### What about Adobe products?

I’ve learned over the last few years to deeply distrust any _Type Tool_ in an Adobe product (or anywhere else). Yes, those can be very good — like HTML+CSS — for doing simple Latin-based typography. But then, all of a sudden, they are very bad. You can think of Adobe products as a train that you get on and you can fall asleep in a nice seat and they still get you where you want to go, except when you wake up and realize you wanted to go somewhere the train doesn't go and then you’re like... _dang, do I have to walk?_ (Walking in this metaphor is when you right click and hit _Convert to Outlines_.)

I realize now this metaphor has made me seem very pro-automobile, which... yes I do live in Los Angeles but I work from home, so I’m kind of ambivalent about cars.

But I’m not ambivalent about typesetting with code, so let’s get into it!

## What does a Coldtype program look like?

First, make sure to have the Coldtype desktop app open on your computer, and also have the coldtype virtualenv activated on the command line.

Next, here’s some example code:

```python
from coldtype import *

page = Rect(1920, 1080)

@renderable
async def render():
    return StyledString("COLDTYPE", Style("ç/MutatorSans.ttf", 300, fill="random")).pens().align(page)
```

You can run this with the `render.py` program included in the coldtype repository, e.g.:

`./render.py examples/example.py -w`

The `-w` flag means the process will hang and monitor the file for changes. So if you edit the file and hit save, the changes (or errors) will show up in thd Coldtype app automatically.

## How does Coldtype work?

Coldtype is, more than anything else, a programmatic frontend to high-quality typesetting code, provided — in this latest iteration of Coldtype — by the excellent FontGoggles repository. (This was not always the case, but FontGoggles provides a much better version of some Harfbuzz+Freetype code that )

Coldtype also provides a set of idioms for holding and manipulating typographic data.

The central graphic element of Coldtype (the `DATPen`) is a wrapper around `fontTool`’s `RecordingPen`, and the central typesetting element (`StyledString`) provides access to a rich set of styling options.

For rasterization/output, Coldtype can be used with Cairo cross-platform, or DrawBot on macOS.

## Why is an audio software company releasing a typography library?

Because (__A__) I love fonts and (__B__) audio software interfaces use fonts (and have some unique design constraints for typography), also (__C__) we make lots of ads that feature typography that reacts to audio and midi data. The code that powers the audio/midi data does not live in this library, but those reactions are made possible by the typography features of Coldtype.

## Why “coldtype”?

Coldtype refers to the short-lived era of early digital typesetting (extending roughly from the late 1940s to the widespread adoption of personal computing in the early 1990s), during which time computers were used to control various analog photographic processes for setting type, technologies now known, usually, as “phototype,” but sometimes also known as “coldtype,” to distinguish it from hot-metal type, which was the previous standard. (And it was hot — Linotype machines were known to squirt molten lead out at the operator.)

Phototype/coldtype was a hybrid moment in typographic history, and a fascinating one — 500 years of metal-type-based assumptions were upended all at once, as letters now did not need to live on a rectangular metal body, meaning they could get really close together. (Which, for me, really helps explain, like, all of graphic design between 1960 and 1980.)

Also originally I thought it was a funny name because I wanted to make a very fast typesetting library using Harfbuzz, and when computers run quickly and efficiently, they remain cold. Of course, I know regularly use all 8 cores of my computer when I use render 1000s of frames at once using coldtype, which gets the fans going, so really it's more like warmtype.

## What are some projects Coldtype has been used on?

_As well as_:

- [Lyric videos](https://vimeo.com/377148622)
- [3d type specimens](https://vimeo.com/354292807)
- [All Goodhertz plugin interfaces](https://goodhertz.co)
- [All recent posts on the Goodhertz instagram](https://www.instagram.com/goodhertz/)
- And [all recent posts on Rob’s instagram](https://www.instagram.com/robrushstenson/)

## Programming philosophy

Here is free-associated list of things that I think define the general vibe of programming in Coldtype (a work-in-progress)

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
- Little-to-no image support (some, but it is v primitive)

---

# Installation

## In a virtual environment

If you’re using a version of Python >= 3.7, you should be able to add `coldtype` to your virtual environment with these two commands:

- `pip install git+https://github.com/goodhertz/coldtype`
- `pip install git+https://github.com/goodhertz/fontgoggles`

To test that you have a working installation, try this command with your virtual env activated:

- `coldtype`

## Working on Coldtype

- `cd` into the `coldtype` directory
- `python3.8 -m venv venv --prompt=coldtype`
- `source env/bin/activate`

Now you should see `(coldtype)` prepended to your terminal prompt. If that’s the case, continue with this invocation:

- `pip install -r requirements.txt`
- Open the Coldtype app (just a normal desktop app, you can open it by double-clicking)

- `./render.py example/example.py -w`
- `ctrl+c` to exit


# Other Stuff, Optional

### DrawBot (optional but very useful for image-rendering)

- `pip install git+https://github.com/typemytype/drawbot`

### Cairo (don’t do this is you don’t have to, which, if you’re on a mac, you don’t have to)

- `brew install cairo pkg-config`
- `pip install pycairo`

Then if that doesn’t work, add to your `~/.bash_profile` ([via](https://github.com/3b1b/manim/issues/524)):

```bash
export PKG_CONFIG_PATH="/usr/local/opt/libffi/lib/pkgconfig"
export LDFLAGS="-L/usr/local/opt/libffi/lib"
```

Then with a re-loaded bash you can `pip install pycairo` again — hopefully it works!