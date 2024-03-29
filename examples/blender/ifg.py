from coldtype import *
from coldtype.blender import BlenderTimeline, b3d_sequencer

obv = Font.Find("ObviouslyV", "__variables")

bt = BlenderTimeline(__BLENDER__, 5400)

ifg = bt.interpretWords(include="+1")
action = bt.interpretWords(include="+2")
emph = bt.interpretWords(include="+3")

@b3d_sequencer((1920, 1080)
, timeline=bt
, bg=None
, render_bg=False
, live_preview=0
, live_preview_scale=0.25
)
def lyrics(f:Frame):
    r_ifg = f.a.r.inset(770, 446)

    def obvi(c):
        txt = c.text
        return (txt.upper(), Style(obv, 120, wdth=0.35, wght=1, ss01=1, slnt=1, tu=-20))

    top = (ifg.currentGroup(f.i)
        .pens(f.i, obvi, fit=r_ifg.w)
        .align(r_ifg, "N")
        .removeFutures()
        .fssw(1, 0, 10, 1))

    bottom = (action.currentGroup(f.i)
        .pens(f.i, obvi, fit=r_ifg.w)
        .align(r_ifg, "S")
        .removeFutures()
        #.print()
        .fssw(1, 0, 10, 1))
    
    try:
        if "a song" in bottom[0][0][0].data("clip").text:
            bottom[0][0][0].filter(lambda idx, p: idx > 3)
    except Exception as _:
        pass
    
    return P(top, bottom).t(0, -220)