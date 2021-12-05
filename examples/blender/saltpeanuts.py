from coldtype import *
from coldtype.blender import *

bt = BlenderTimeline(__BLENDER__, 400)
ct, styles = bt.interpretClips(exclude=[3])

@b3d_sequencer((1080, 540), timeline=bt, bg=0, render_bg=1)
def lyrics(f):
    styles.hold(f.i)

    def render_clip(tc):
        if "title" in tc.clip.styles:
            return tc.text.upper(), Style(
                Font.Find("smoosh4-u"), 850,
                wght=1,
                wdth=0,
                slnt=1,
                fill=1)
        else:
            return tc.text.upper(), Style(
                Font.Find("Rainer"), 350,
                wght=1,
                wdth=0.5,
                slnt=1,
                fill=1)

    cg = ct.currentGroup(f.i)
    txt = (cg.pens(f, render_clip
        , styles=styles
        , graf_style=GrafStyle(leading=30)
        , use_lines=[cg.currentWord(f.i) if not styles.ki("title").on() else None]
        )
        .removeFutures()
        .removeBlanks()
        .align(f.a.r)
        .f(1))

    return PS([
        P(txt.ambit(th=1)),
        P().gridlines(f.a.r, 5).s(hsl(0.9)),
        txt])