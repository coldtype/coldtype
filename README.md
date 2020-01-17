<img src="viewer/appicon_layers/appicon_main_frames/appicon_main_1024.png" alt="Coldtype" width=175>

---

_Hello! Not sure how you got here unless I gave you the link personally — if I didn’t, you’re welcome to look around, but know that this is alpha-quality software that’s mostly undocumented._

# What is Coldtype?

Setting type with code may not be a common practice, but it is a good practice, or at least I* enjoy doing it, so this is a library I wrote to make it easier to do, specifically in the context of constrained typographical situations, like frame-wise animations or user interfaces for audio applications.

*“I” here is Rob Stenson, designer/programmer/Goodhertz co-founder.

## What is Coldtype for?

- Quickly setting complex display typography in constrained time and space

((( image here of text-editor & viewer side-by-side, ala drawbot)))

## What is Coldtype _not_?

- Coldtype is not good for setting large amounts of text in a single frame, because Coldtype has no line-breaking algorithms
- Which means Coldtype is probably bad for print (you should use DrawBot for that)
- Coldtype is not good at most things that normal type-setting software is good at. Generally-speaking, the goal of this library is to give you exactly what you want, rather than a "best guess." For example:
    - Coldtype does not implement fallback support (expect to see some `.notdef`s)

## Is Coldtype stable enough to use?

Great question. At the moment, it is definitely not very stable. It is, more than anything else, a collection of programming patterns that I’ve found very useful in quickly developing typographic animations. These animations are usually things I write once and then never read or edit, unless it’s to steal an idea from myself many months later, in which case, what I’m taking is a general idea and probably not the exact code. This makes Coldtype very different from... every programming library I’ve ever used, because most libraries are meant for general use in projects that must be maintained and revisited for months and years. Programming an animation isn't a lot like that — once it’s done, it’s done (released).

That said, the core concepts (`Style`, `StyledString`, `DATPen`, & `DATPenSet`) are fairly stable — for whatever that’s worth.

## How does Coldtype work?

Coldtype is, more than anything else, a small Python library that glues together three other excellent libraries:

- [fontTools](https://github.com/fonttools/fonttools)
- [harfbuzz](https://github.com/harfbuzz/harfbuzz) (via [uharfbuzz](https://github.com/harfbuzz/uharfbuzz)) (+freetype, via [freetype-py](https://pypi.org/project/freetype-py/))
- [skia-pathops](https://github.com/fonttools/skia-pathops)

The central graphic element of Coldtype (the `DATPen`) is a wrapper around `fontTool`’s `RecordingPen`, and the central typesetting element (`StyledString`) is, for most applications, a thin layer on top of harfbuzz, although it is also possible to set type directly from `.ufo` files and `.glyphs` files. 

For rasterization/output, Coldtype can be used with Cairo cross-platform, or DrawBot on macOS.

(On Mac, the Harfbuzz and FreeType modules can be substituted with DrawBot for type-shaping).

Coldtype is also a few other things
    - a command line tool and viewer application that monitor in-development code and use websockets to display SVG previews of code-in-progress
    - a pair of Adobe CEP extensions to help ease previewing animations in Premiere and After Effects

## What does a Coldtype program look like?

```python
from coldtype.animation import *

def render(f):
    return StyledString("Hello, world".upper(), Style("ç/MutatorSans.ttf", 100, wdth=0.25, wght=0.25)).pens().align(f.a.r)

animation = Animation(render)
```

You can then run this with the `render.py` program included in coldtype, e.g.:

`./render.py examples/simple.py -w`

This is effectively a single-frame animation, because it does not change over time based on the `f`(rame) variable, which encapsulates information about the state of the current frame being drawn.

Here’s another example, from `examples/animation.py`:

```python
from coldtype.animation import *

def render(f):
    at = f.a.progress(f.i, loops=1, easefn="eeio")
    return StyledString("Hello, world".upper(), Style("ç/MutatorSans.ttf", 100, wdth=at.e, wght=at.e)).pens().align(f.a.r)

timeline = Timeline(120, storyboard=[0, 60, 119])
animation = Animation(render, timeline=timeline)
```

## What are some projects Coldtype has been used on?

<iframe src="https://player.vimeo.com/video/377148622?portrait=0" width="640" height="480" frameborder="0" allow="autoplay; fullscreen" allowfullscreen></iframe>

<iframe src="https://player.vimeo.com/video/354292807?title=0&portrait=0" width="640" height="480" frameborder="0" allow="autoplay; fullscreen" allowfullscreen></iframe>

_As well as_:

- [Lyric videos](https://vimeo.com/377148622)
- [3d type specimens](https://vimeo.com/354292807)
- [All Goodhertz plugin interfaces](https://goodhertz.co)
- [All recent posts on the Goodhertz instagram](https://www.instagram.com/goodhertz/)
- And [all recent posts on Rob’s instagram](https://www.instagram.com/robrushstenson/)

## Programming philosophy

- Chained mutation/transformation
    - "Chaining" in this context refers to the programming style favored by libraries like jQuery, which allows you to call multiple methods on a single line, all of which mutate the state of an object and return the object itself in each mutating call. For example:
        - `DATPen().rect(Rect(500, 500)).translate(100, 100).rotate(45)` creates a `DATPen` object, then adds a rectangle bezier to it, then translates it, then rotates it, all in a single line. In normal circumstances, programming like this is called "spaghetti" code because it's long and hard to follow, or something like that. In this case, its brevity is its benefit
- Does not use classic "drawing"-style APIs/graphic state, though the data model of Coldtype can be (and is meant to be) serialized to any number of canvas/drawing APIs, and can be extended to any API that implements `fill`/`stroke` and `moveTo`/`lineTo`/`curveTo`

## How is this different from DrawBot?

- Use whatever text editor you want
- Cross-platform
- Does not rely on Apple’s CoreText engine or the mostly deprecated APIs that DrawBot uses to interact with it
- Really only a small subset of what DrawBot, by leveraging CoreText and CoreImage, can do (which is a good thing to me, because I only ever used DrawBot for typography anyway)
- Little-to-no image support (some, but it is v primitive)

## Why is an audio software company releasing a typography library?

Because (__A__) I love fonts and (__B__) audio software interfaces use fonts (and have some unique design constraints for typography).

## Why “coldtype”?

Coldtype refers to the short-lived era of early digital typesetting (extending roughly from the late 1940s to the widespread adoption of personal computing in the early 1990s), during which time computers were used to control various analog photographic processes for setting type, technologies no known, usually, as "phototype," but sometimes also known as "coldtype," to distinguish it from hot-metal type, which was the previous standard. (And it was hot — Linotype machines were known to squirt molten lead out at the operator.)

Phototype/coldtype was a hybrid moment in typographic history, and a fascinating one — all 500 years of metal-type-based assumptions were upended, as letters now did not need to live on a rectangular metal body, meaning they could get really close together.

Also originally I thought it was a funny name because I wanted to make a very fast typesetting library using Harfbuzz, and when computers run quickly and efficiently, they remain cold. Of course, I know regularly use all 8 cores of my computer when I use render 1000s of frames at once using coldtype, which gets the fans going, so really it's more like warmtype.

---

# Installation

## Prerequisites

- Git
- Python >= 3.6
- `virtualenv`
- The `coldtype-viewer` app, [available here](https://github.com/goodhertz/coldtype/releases)
- freetype (`brew install freetype` or something else)

## Setup/Test

- Open the `coldtype-viewer` app (just a normal OSX app)
- `cd` into the directory
- `source env/bin/activate`
- `pip install -r requirements.txt`
- `./render.py test/test_animation.py`


# Other Stuff, Optional

### DrawBot (optional but very useful for image-rendering)

- `pip install git+https://github.com/typemytype/drawbot`

### Cairo (don’t do this is you don’t have to)

- `brew install cairo pkg-config`
- `pip install pycairo`

Then if that doesn’t work, add to your `~/.bash_profile` ([via](https://github.com/3b1b/manim/issues/524)):

```bash
export PKG_CONFIG_PATH="/usr/local/opt/libffi/lib/pkgconfig"
export LDFLAGS="-L/usr/local/opt/libffi/lib"
```

Then you can `pip install pycairo` again — hopefully it works!

# Notes on Prereqs

### Python >= 3.6

Install Python, 3.6.8 (the latest 3.6 series) is probably your best bet https://www.python.org/downloads/release/python-368/

### Git

- __Git__
    - If you’re using Windows, when you install [git](https://git-scm.com/download/win), under "Adjusting your PATH" options choose "Use Git and optional Unix tools from the Windows Command Prompt" (this lets you use git inside git bash and inside windows console).

### Virtualenv

- `which virtualenv` to see if you already have it — if you don’t, continue, working inside the `configs` directory...
- `python3.6 -m pip install virtualenv`
- `virtualenv env`
- `source env/bin/activate`

Now you should see `(env)` prepended to your terminal prompt. If that’s the case, continue with this invocation:
- `pip install -r requirements.txt`

### Freetype

There’s a chance you might be all set now, but probably not, as the coldtype library (a submodule) uses a bleeding-edge version of the freetype-py wrapper, which dynamically loads `libfreetype.6.dylib`, which you may or may not have. The easiest way to install it on a Mac is with homebrew, using the command `brew install freetype`, though if you’d rather not, let me (Rob) know and I can send you a pre-built freetype binary.
