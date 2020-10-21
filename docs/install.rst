Install
=======

* Install a Python >= 3.7, <= 3.8
    * For the moment, Python 3.9 will not work b/c of an issue with the skia graphics library, though that issue should be resolved soon
    * If you don’t have a Python >= 3.7, I’d recommend Python 3.8.6 (available from `python.org/downloads <https://python.org/downloads>`_ if you scroll down a little)

Option A
--------

If you want to try coldtype in the coldtype repo itself (**recommended**):

* Clone the coldtype repository, ala ``git clone https://github.com/goodhertz/coldtype``
* ``cd`` into the the cloned coldtype repository on your computer
* Create a virtual environment, ala ``python3.8 -m venv venv --prompt=coldtype`` on the command line
* Then ``source venv/bin/activate`` to start your venv
* Then ``pip install -e .`` (This adds the ``coldtype`` command to your virtual environment)
* Then ``coldtype``

That last command should pop up a window that is a random gradient, along with the letters CT and a little message that says ``NOTHING FOUND``.

You can also try running some of the tests that are part of the repo, like:

* ``coldtype test/test_animation.py``

With that window open, try hitting the arrow keys on your keyboard to go backward and forward in time.

Option B
--------

If you want to try coldtype in a blank virtual environment:

Using a virtualenv (based on a python >= 3.8) (aka ``python3.8 -m venv venv --prompt=<your prompt here>`` + ``source venv/bin/activate``), there are two routes: (B.1) the packaged distribution, or (B.2) installing a cloned version of the repo into your project’s venv.

I’d recommend Option B.2 for now if your goal is experimentation, since Coldtype is under active development. That said, you might lose some reproduceability with option B.2 since there's no versioning of coldtype itself with that approach. (If you’re worried about reproduceability, just make sure to note the coldtype sha somewhere so you can restore that state if you need to.)

Option B.1:

* ``pip install coldtype``
* ``coldtype``

Option B.2:

* Do the steps above for cloning the coldtype repo
* ``pip install -e <path/to/the/coldtype/repo>``
* ``coldtype``

That last command should pop up a window that is a random gradient, along with the letters CT and a little message that says ``NOTHING FOUND``.

To write your own script, make a python file in your repo, like `test.py`, and put some code in it, like:

.. code:: python

    from coldtype import *

    @renderable()
    def test(r):
        return DATPen().oval(r)

Then you can run that like so — `coldtype test.py` — and a large pink oval should pop up on your screen.

You may also notice the command is still hanging, meaning it hasn't exited. So if you edit test.py and hit save, you should see the change immediately pop up in the same window. For instance, try insetting the oval and making it a different color, so that your code looks something like this:

.. code:: python

    from coldtype import *

        @renderable()
        def test(r):
            return DATPen().oval(r.inset(100)).f(hsl(0.8))

Now the oval should have some padding and be purple-ish.

To quit the running program, as with all CLI programs, you can hit `ctrl c` and that should kill the program. Or you can type `kill` into the command line while the program is running and it should have the same effect. (That’s not something that’ll usually work, but it works in coldtype.)