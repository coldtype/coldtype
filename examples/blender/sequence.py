from coldtype import *
from coldtype.blender import BlenderTimeline, b3d_sequencer

bt = BlenderTimeline(ººBLENDERºº, 120)
channel1 = bt.interpretWords(include="+1 +2")

@b3d_sequencer((1080, 1080)
, timeline=bt
, bg=None
, render_bg=False
, live_preview=1
, live_preview_scale=0.25
)
def sequence(f:Frame):
    def setter(c):
        style = Style(Font.JBMono(), 100, wght=1)
        if "script" in c.styles:
            style = Style(Font.RecMono(), 100, wght=1)
        return [c.text.lower(), style]
    
    return (P(
        channel1
            .currentGroup(f.i)
            .pens(f.i, setter)
            .align(f.a.r)
            .removeFutures()
            .f(1),
        StSt(str(f.i), Font.JBMono(), 72, wght=1)
            .align(f.a.r.take(100, "S"), tx=0)
            .f(1)))