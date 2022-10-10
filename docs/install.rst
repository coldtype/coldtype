Install
=======

.. raw:: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/hCGF6FZCSqc" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

------------------

* Install a Python >= 3.7
* If you don’t have a Python >= 3.7, I’d recommend the latest Python (available from `python.org/downloads <https://python.org/downloads>`_)

If you want to try coldtype in a blank virtual environment:

Using a virtualenv (based on a python >= 3.7) (aka ``python3.10 -m venv venv`` and then ``source venv/bin/activate``), run:

* ``pip install "coldtype[viewer]"``
* ``coldtype demo``

That last command should pop up a window. If you hit the spacebar with that window focused, you should see an animation start playing.

---------------------

To write your own script, make a python file in your repo, like `test.py`, and put some code in it, like:

.. code:: python

    from coldtype import *

    @renderable()
    def test(r):
        return P().oval(r)

Then you can run that like so — `coldtype test.py` — and a large pink oval should pop up on your screen.

You may also notice the command is still hanging, meaning it hasn't exited. So if you edit test.py and hit save, you should see the change immediately pop up in the same window. For instance, try insetting the oval and making it a different color, so that your code looks something like this:

.. code:: python

    from coldtype import *

    @renderable()
    def test(r):
        return P().oval(r.inset(100)).f(hsl(0.8))

Now the oval should have some padding and be purple-ish.

To quit the running program, as with all CLI programs, you can hit `ctrl c` and that should kill the program. Or you can type `kill` into the command line while the program is running and it should have the same effect. (That’s not something that’ll usually work, but it works in coldtype.)