from coldtype import *
from coldtype.blender import *

"""
Some very simple timed-text-in-3d
"""

bt = BlenderTimeline(__BLENDER__, 80)

@b3d_animation((1080, 1080), timeline=bt)
def timed(f:Frame):
    def styler(c):
        return c.text.upper(), Style(Font.MutatorSans(), 250)

    return (f.t.words.currentGroup()
        .pens(f, styler)
        .align(f.a.r)
        .removeFutures()
        .pen()
        | b3d(λ.extrude(2)))