from coldtype import *
from coldtype.blender import *

@b3d_sequencer(timeline=Timeline(120, 24))
def lyrics(f):
    def render_clip(tc):
        return tc.text.upper(), Style(
            Font.Find("ObviouslyV"), 250,
            wght=1,
            wdth=0,
            slnt=1,
            fill=hsl(0.65))

    cg = f.a.t.clip_group(0, f)
    return PS([
        (P().oval(f.a.r.inset(50)).f(1)),
        (cg.pens(f, render_clip,
                graf_style=GrafStyle(leading=30),
                use_lines=[cg.current_word()])
            .xalign(f.a.r)
            .align(f.a.r)
            .remove_futures())])