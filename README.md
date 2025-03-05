__⚠️🌋 Disclaimer: this library is alpha-quality; the API is subject to change 🌋⚠️__

---

# Coldtype

_Hello and welcome to `coldtype`, an odd little library for programmatic typography, written for use on [Goodhertz](https://goodhertz.com) projects and [text animations](https://vimeo.com/robstenson)._

For __installation and tutorials__, check out [coldtype.goodhertz.com](https://coldtype.goodhertz.com)

Here’s a quick example:

```python
from coldtype import *

@renderable((1580, 350))
def render(r):
    return P(
        P(r.inset(10)).outline(10).f(hsl(0.65)),
        StSt("COLDTYPE", Font.ColdtypeObviously()
            , fontSize=250
            , wdth=1
            , tu=-250
            , r=1
            , rotate=15)
            .align(r)
            .fssw(hsl(0.65), 1, 5, 1)
            .translate(0, 5))
```

Saving that code in a file named test.py and running `coldtype test.py` (or `uv run ct test.py` if you’re using `uv`) results in this image popping up on your screen in a dedicated window:

![An example](https://raw.githubusercontent.com/goodhertz/coldtype/main/examples/renders/simple_render.png)

## Documentation

Check out [coldtype.goodhertz.com](https://coldtype.goodhertz.com) for instructions on installing and getting started with coldtype.

## More Examples

The best way to get familiar with Coldtype is to look at and try modifying some example code, like the animating gif below. To try out this example and many more, check out the [examples/animation](https://github.com/goodhertz/coldtype/tree/main/examples/animations) directory in this repo.

## Contributing

To get a development environment for Coldtype:

```
git clone https://github.com/coldtype/coldtype.git
uv sync --extra viewer
uv run ct examples/animations/808.py
```

To run tests, etc.

```
uv sync --extra dev
```