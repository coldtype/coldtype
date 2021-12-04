from coldtype import *
from coldtype.blender import *

bt = BlenderTimeline(__BLENDER__)
print(bt.timeables)

@b3d_sequencer(timeline=bt, bg=0.5, render_bg=1)
def lyrics(f):
    #ft:Timeline = f.t
    #ct, styles = ft.interpretClips(exclude=[1])
    #print(ft.start)
    return None

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
                Font.Find("ObviouslyV"), 350,
                wght=1,
                wdth=0,
                slnt=1,
                fill=1)

    # cg = f.a.t.clip_group(0, f, styles=[1])
    cg = ct.currentGroup(f.i)

    return PS([
        (cg.pens(f, render_clip
            , styles=styles
            , graf_style=GrafStyle(leading=30)
            #, use_lines=[cg.current_word() if "title" not in cg.styles() else None]
            )
            .xalign(f.a.r)
            .align(f.a.r)
            .removeFutures())])