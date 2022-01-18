MIDI
====

There are two primary uses for MIDI in Coldtype programs, and they're kind of completely unrelated to each other, though both do use the MIDI protocol. The first is the use of MIDI controllers to set variables and trigger actions on running coldtype scripts. The second is the use of MIDI files (usually exported from audio software) to control animations.

Using MIDI controllers
----------------------

If you launch coldtype with the ``-mi 1`` or ``--midi-info=1`` flag, you should see a list of MIDI controllers/devices currently available on your system.

I always have a `Launch Control XL <https://novationmusic.com/en/launch/launch-control-xl>`_ plugged into my computer, and if you don't already have a MIDI Controller, I highly recommend that one, since it's got faders, which are a lot of fun in combination with real-time dynamic typography, and it's great for mixing in Ableton, which has nothing to do with this.

With that in mind, I'll use the Launch Control as an example. So with that device plugged in, when I run ``coldtype -mi 1`` in my coldtype virtualenv, I see the following print out in my terminal window:

.. code::txt

    0 IAC Driver Bus 1
    1 USB Midi 
    2 Launch Control XL
    3 Launch Control XL HUI

I'm including the unrelated devices because those (or others) might show up on your computer as well, depending on what you have plugged in. Basically, you just want to find the `exact` name of the device you're looking to use with Coldtype. In this case, that’s ``"Launch Control XL"`` (not the one with `HUI` in the name).

Once you know that, create a file at the root of user path (aka ``~``), called ``.coldtype.py``

You can do that with a command line invocation, like this: ``touch ~/.coldtype.py``, and you can open it in a code editor like VS Code with ``code ~/.coldtype.py``

Once you’re there, you’ll want to add some Python code to configure the MIDI device of  your choice. Here’s an example:

.. code:: python

    MIDI = {
        "Launch Control XL": {
            "note_on": {
            }
        }
    }

Now save that file and relaunch coldtype with the same invocation for midi-info, i.e. ``coldtype -mi 1``

Now if you hit some buttons on your midi controller, you should see some identifying information about those buttons, like what number they correspond to.

For instance, if I hit the button labelled 1 on my Launch Control (the button at the bottom left), I see this printed out in my terminal:

``Launch Control XL <NOTE OFF, note: 73 (C#4), channel: 9>``

The pertinent information there is the note number, 73. Now you can go back to ~/.coldtype.py and assign that button to a Coldtype action, like so:

.. code:: python

    MIDI = {
        "Launch Control XL": {
            "note_on": {
                73: "render_all"
            }
        }
    }

Now if you run an animation (like ``coldtype examples/animations/house.py``), when you hit that same button on the Launch Control, it'll start a sequential render of all the frames in the animation.

N.B. The actions defined in the ``"note_on"`` dict are completely optional, but it's a great way to control a Coldtype program without having to rely on app focus on on your computer. That is, if you want to render all the frames of an animation while you have Premiere or VS Code open in the foreground of your application (rather than the coldtype viewer), you can just hit the key that corresponds to midi controller number 73 (for example).

**Faders**: Of course, triggering actions isn't the exciting use of a MIDI controller in Coldtype. The exciting thing is hooking up a knob or fader to a variable, meaning you can quickly and easily modify a design otherwise defined completely in code.

If you run coldtype again with the ``-mi 1`` flag (``coldtype -mi 1``), and move around a fader or a knob on your controller, you should see print outs like this:

``Launch Control XL <CONTROLLER: 77 ("Sound Control 8"), value: 51, channel: 9>``

Again, the only thing we’re interested in is the 77 displayed there, which is the controller id. But this time we're not going to edit the coldtype config, we're going to target this value directly in a script, by constructing a ``Generic`` midi controller object, then querying it based on the number above, 77 in this case. The 0.5 supplied as the second argument is the default value of the slider, which we have to supply, given that MIDI controllers do not have a "memory" of their own, i.e. when the script starts, we have no way of reading current knob/fader positions off of the MIDI device. More on saving state further on down.

.. code:: python

    from coldtype import *
    from coldtype.midi.controllers import Generic

    @animation(rstate=1)
    def use_midi(f, rs):
        controller = Generic("Launch Control XL", rs.midi, channel=9)
        fader = controller(77, 0.5) # returns a value between 0 and 1
        return (P()
            .oval(f.a.r.take(fader, "mdx").square())
            .f(hsl(0.65)))
    
Now if you run that code, you should see a blue circle on your screen — and if you move the first fader on a Launch Control XL, you should see the circle change size.


Reading MIDI files for animations
---------------------------------

Tutorial coming soon... (in the meantime, check out the examples in the sidebar, 808 and house both MIDI for animations extensively)