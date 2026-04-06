__⚠️🌋 Disclaimer: this library is alpha-quality; the API is subject to change 🌋⚠️__

---

# Coldtype

_Hello and welcome to `coldtype`, an odd little library for programmatic typography, written for use on [Goodhertz](https://goodhertz.com) projects and [text animations](https://vimeo.com/robstenson)._

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

If you have [uv](https://docs.astral.sh/uv/) installed, saving that code in a file named test.py and running `uvx coldtype test.py` results in this image popping up on your screen in a dedicated window:

![An example](https://raw.githubusercontent.com/goodhertz/coldtype/main/examples/renders/simple_render.png)

## Documentation

Check out [coldtype.xyz](https://coldtype.xyz) for instructions on installing and getting started with coldtype.

## More Examples

The best way to get familiar with Coldtype is to look at and try modifying some example code, like the animating gif below. To try out this example and many more, check out the [examples/animation](https://github.com/goodhertz/coldtype/tree/main/examples/animations) directory in this repo.

## Contributing

To get a development environment for Coldtype:

```
git clone https://github.com/coldtype/coldtype.git
uv run ct examples/animations/808.py
```

To run tests, etc.

```
uv sync --extra dev
```


### Using with Blender

Big thing: match your the Python version in your uv installation (or venv generally-speaking) to the Python version embedded 

- Find the desired Blender version:
    - `uvx b3denv python --version`
- Create a project with that version:
    - `uv init --python 3.XX`
- Add Coldtype:
    - `uv add coldtype`
- Verify Coldtype installation:
    - `uv run coldtype demoblender`
- Try a Blender-enabled Coldtype file:
    - `uv run coldtype demoblender -p b3dlo`