from coldtype.test import *
from coldtype.time.nle.premiere import PremiereTimeline, ClipGroup

json = Path("test/media/test_premiere_multi_coldtype.json")

pt1 = PremiereTimeline(json)
pt2 = PremiereTimeline(json).retime_for_symbol("aaa")

print(pt1.duration, pt2.duration)

@animation(timeline=pt1, bg=0, solo=0)
def t1(f):
    cg:ClipGroup = pt1.clip_group(0, f, [2])

    def render_clip(f, lidx, clip, t):
        return t.upper(), Style(mutator, 200, wght=0, fill=hsl(0.9) if "b" in clip.styles else 1)
    
    return DATText(str(f.i), Style("Times", 100, load_font=0), f.a.r.inset(50).offset(0, 500)) + (cg
        .pens(f, render_clip, f.a.r)
        .xa()
        .align(f.a.r)
        .translate(0, 200)
        .remove_futures())

@animation(timeline=pt2, bg=0.2, solo=1)
def t2(f):
    cg:ClipGroup = pt2.clip_group(1, f, [2])

    def render_clip(f, lidx, clip, t):
        return t.upper(), Style(mutator, 200, wght=1, fill=hsl(0.9) if "b" in clip.styles else 1)
    
    return DATText(str(f.i), Style("Times", 100, load_font=0, fill=hsl(0.3)), f.a.r.inset(50, 50)) + (cg
        .pens(f, render_clip, f.a.r)
        .xa()
        .align(f.a.r)
        .translate(0, -200)
        .remove_futures())
