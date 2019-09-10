# Coldtype

# Prerequisites

### Python >= 3.6

Install Python, 3.6.8 (the latest 3.6 series) is probably your best bet https://www.python.org/downloads/release/python-368/

### Git + Git LFS

- __Git__
    - If you’re using Windows, when you install [git](https://git-scm.com/download/win), under "Adjusting your PATH" options choose "Use Git and optional Unix tools from the Windows Command Prompt" (this lets you use git inside git bash and inside windows console).
- __Git LFS__
    - [Available here](https://git-lfs.github.com/).
    - This can be installed via homebrew if you want, on Mac. https://brew.sh/ and then `brew install git-lfs`

### Virtualenv
- `which virtualenv` to see if you already have it — if you don’t, continue, working inside the `configs` directory...
- `python3.6 -m pip install virtualenv`
- `virtualenv env`
- `source env/bin/activate`

Now you should see `(env)` prepended to your terminal prompt. If that’s the case, continue with this invocation:
- `pip install -r requirements.txt`

There’s a chance you might be all set now, but probably not, as the coldtype library (a submodule) uses a bleeding-edge version of the freetype-py wrapper, which dynamically loads `libfreetype.6.dylib`, which you may or may not have. So if you see an error about that, just contact Rob.

# Previewing

Activate the virtualenv (if it’s not already activated):
- `source env/bin/activate`

Launch the websocket-previewer, like so:
- `python coldtype/viewer.py`

Now go open `file:///Users/<your-username>/Goodhertz/coldtype/coldtype/_viewer.html` and observe that it connects to your running `viewer.py` process (it should say something like:

```
>>> Listening on 8008
('::1', 59727, 0, 0) connected
```

Now you should be able to run the `coldtype/__init__.py` file and see it attempt to render some stuff, ala `python coldtype/__init__.py`


# Other Stuff, Optional

### Cairo (don’t do this is you don’t have to)

- `brew install cairo pkg-config`
- `pip install pycairo`

Then if that doesn’t work, add to your `~/.bash_profile` ([via](https://github.com/3b1b/manim/issues/524)):

```bash
export PKG_CONFIG_PATH="/usr/local/opt/libffi/lib/pkgconfig"
export LDFLAGS="-L/usr/local/opt/libffi/lib"
```

Then you can `pip install pycairo` again — hopefully it works!

### DrawBot (also completely optional)

- `pip3 install PyObjC`
- `cd` into a drawBot clone and `python setup.py install`
