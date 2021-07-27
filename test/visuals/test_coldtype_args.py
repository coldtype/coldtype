# TODO accomplish this by treating the source file as the config file itself, and so would require no special syntax except to say like, WINDOW_PIN = "SE" in this file and then `coldtype this_file.py -c this_file.py`
#coldtype -wp SE -wt

"""
A circle appears with no background
at the bottom right of your screen
"""

from coldtype import *

@renderable((500, 500))
def stub(r):
    return (DATPen()
        .oval(r.inset(50))
        .f(0, 0.25)
        .s(0)
        .sw(5))
