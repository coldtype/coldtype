from coldtype import *
from coldtype.blender import *

bt = BlenderTimeline(__BLENDER__, 400)

@b3d_sequencer((1080, 540), timeline=bt, bg=0, render_bg=1)
def lyrics(f):
    def render_clip(tc):
        if "title" in tc.styles:
            return tc.text.upper(), Style(
                Font.Find("smoosh4"), 600,
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

    cg = f.t.clips.currentGroup()

    txt = (cg.pens(f, render_clip
        , graf_style=GrafStyle(leading=30)
        , use_lines=[cg.currentWord(f.i) if not f.t.clips.styles.ki("title").on() else None]
        )
        .removeFutures()
        .removeBlanks()
        .align(f.a.r)
        .f(1))

    return PS([
        P(txt.ambit(th=1)),
        P().gridlines(f.a.r, 5).s(hsl(0.9)),
        txt])