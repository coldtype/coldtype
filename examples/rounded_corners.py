from coldtype import *
from coldtype.fx.skia import round_corners

"""
Use a skia effect to apply round corners
to a sharp-edged shape
"""

@aframe((1080, 540), bg=1)
def rounder(f):
    return (P(Rect(400))
        .align(f.a.r)
        .fssw(-1, 0, 2)
        .pen()
        .remove_overlap()
        .ch(round_corners(60)))
