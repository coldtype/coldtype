This is a test of reading and displaying code embedded in a Markdown document, a literate programming kind of thing.

First we should import everything from coldtype:

```python
from coldtype import *
```

Now we can set up a renderable:

```python
@renderable((500, 500), bg=0)
def embedded(r):
    return (DATPen()
        .oval(r.inset(100))
        .flatten(25)
        .roughen(150)
        .smooth()
        .f(None)
        .s(hsl(0.95, 0.6, 0.6))
        .sw(10))
```

That was some code there, which hopefully worked when you run it as `coldtype test/test_md.md` — there should now be pink-ish circular scribble on your screen.

And that’s not all!

Here’s another one, to make sure multiple blocks are picked up.

```python
@animation((500, 200), bg=0, storyboard=[0])
def animated(f):
    return (StyledString("CDELOPTY",
        Style("assets/ColdtypeObviously-VF.ttf",
            150,
            wdth=0,
            rotate=360*f.a.progress(f.i, easefn="qeio").e))
        .pens()
        .f(Gradient.H(f.a.r, hsl(0.5), hsl(0.6)))
        .align(f.a.r))
```

Also let’s do the contact sheet for that animation.

```python
animated_contact = animated.contactsheet(2, slice(0, None, 1))
```