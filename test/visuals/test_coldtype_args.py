# TODO accomplish this by treating the source file as the config file itself, and so would require no special syntax except to say like, WINDOW_PIN = "SE" in this file and then `coldtype this_file.py -c this_file.py`
#coldtype -wp SE -wt

"""
A circle appears with no background
at the bottom right of your screen
"""

WINDOW_PIN = "SE"
WINDOW_PASSTHROUGH = True
WINDOW_TRANSPARENT = True

from coldtype import *

@animation(timeline=120)
def stub(f):
    return (DATPen()
        .oval(f.a.r.inset(f.e("eeio", 1, rng=(50, 250))))
        .f(0, 0.25)
        .s(0)
        .sw(5))
