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
    c1 = hsl(0.65, 0.7)
    c2 = hsl(0.53, 0.6)

    return P(
        P(r.inset(10))
            .outline(10)
            .f(Gradient.H(r, c2.lighter(0.3), c1.lighter(0.3))),
        StSt("COLDTYPE",
            Font.ColdtypeObviously(), 250
                , wdth=1
                , tu=-170
                , r=1
                , rotate=15)
            .align(r)
            .f(Gradient.H(r, c1, c2))
            .understroke(s=1, sw=5)
            .translate(0, 5))
```

Running that code results in this image popping up on your screen in a dedicated window:

![An example](https://raw.githubusercontent.com/goodhertz/coldtype/main/examples/renders/simple_render.png)

## Documentation

Check out [coldtype.goodhertz.com](https://coldtype.goodhertz.com) for instructions on installing and getting started with coldtype.

## More Examples

The best way to get familiar with Coldtype is to look at and try modifying some example code, like the animating gif below. To try out this example and many more, check out the [examples/animation](https://github.com/goodhertz/coldtype/tree/main/examples/animations) directory in this repo.

## Contributing

To get a development environment for Coldtype:

```
python3.9 -m venv venv --prompt=coldtype
source venv/bin/activate
pip install -e .[viewer]
```