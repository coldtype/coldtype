from coldtype import *
from coldtype.timing.nle.premiere import PremiereTimeline

pt = PremiereTimeline(
    __sibling__("projs/lyrics_coldtype.json"))

@animation(timeline=pt, bg=0)
def lyrics(f):
    def render_clip_fn(tc):
        ct = "ct" in tc.clip.styles
        return tc.text.upper(), Style(Font.MutatorSans(), 150,
            wght=1 if ct else 0,
            wdth=1,
            fill=hsl(0.65) if ct else 1)

    return (pt.clipGroup(0, f, styles=[1])
        .pens(f, render_clip_fn,
            graf_style=GrafStyle(leading=30),
            fit=f.a.r.w-200
            )
        .xalign(f.a.r)
        .index(0, lambda p: p.translate(0, -10))
        .align(f.a.r)
        .removeFutures())