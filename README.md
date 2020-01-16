![Coldtype]( viewer/appicon_layers/appicon_main_frames/appicon_main_1024.png)

---

# What is Coldtype?

# Prerequisites

- Git
- Python >= 3.6
- `virtualenv`
- The `coldtype-viewer` app, [available here](https://github.com/goodhertz/coldtype/releases)
- freetype (`brew install freetype` or something else)

# Setup/Test

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