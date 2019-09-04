# Coldtype

### Testing with livereload

Using `pip install livereload`

- `livereload -p 8000 test/artifacts` or whatever port

# Cairo

- `brew install cairo pkg-config`
- `pip install pycairo`

Then if that doesn’t work, add to your `~/.bash_profile` ([via](https://github.com/3b1b/manim/issues/524)):

```bash
export PKG_CONFIG_PATH="/usr/local/opt/libffi/lib/pkgconfig"
export LDFLAGS="-L/usr/local/opt/libffi/lib"
```

Then you can `pip install pycairo` again — hopefully it works!

# DrawBot

- `pip3 install PyObjC`
- `cd` into a drawBot clone and `python setup.py install`