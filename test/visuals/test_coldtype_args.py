"""
A circle appears with no background
at the bottom right of your screen,
but you cannot click on it
(when run with `-c .`)
"""

# .coldtype
WINDOW_PIN = "SE"
WINDOW_PASSTHROUGH = True
WINDOW_TRANSPARENT = True
WINDOW_CHROMELESS = True

from coldtype import *

@animation(timeline=120)
def stub(f):
    return (DATPen()
        .oval(f.a.r.inset(f.e("eeio", 1, rng=(50, 250))))
        .f(0, 0.25)
        .s(0)
        .sw(5))
